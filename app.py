import os
import re
import shutil
import zipfile
import posixpath
from urllib.parse import quote
from datetime import datetime
from flask import Flask, jsonify, send_file, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_MD = os.path.join(BASE_DIR, 'sample.md')
SLIDES_MD = os.path.join(BASE_DIR, 'slides.md')
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

def rewrite_image_paths(md_text: str, base_path: str, md_rel_dir: str = '', mapping: dict | None = None) -> str:
    # 将相对图片路径改为以 /uploads/<id>/ 为前缀的绝对路径；对路径进行 URL 编码
    # md_rel_dir 以 up_dir 为根的 md 所在目录的相对路径；mapping 是 原始相对路径(相对于 up_dir) -> 目标相对路径（URL 编码后）的映射
    mapping = mapping or {}
    md_rel_dir = md_rel_dir.replace('\\', '/')
    def build_target(rel_path_from_md: str) -> str:
        p = rel_path_from_md.strip().replace('\\', '/')
        # 归一化为相对于 up_dir 的路径
        norm_rel = posixpath.normpath(posixpath.join(md_rel_dir, p)).lstrip('./')
        # 查映射，否则按段编码
        target_rel = mapping.get(norm_rel)
        if not target_rel:
            parts = [quote(seg, safe='._-') for seg in norm_rel.split('/')]
            target_rel = '/'.join(parts)
        return f'{base_path}{target_rel}'
    def repl_md(m):
        alt, path = m.group(1), m.group(2)
        if re.match(r'^https?://', path) or path.startswith('/'):
            return f'![{alt}]({path})'
        return f'![{alt}]({build_target(path)})'
    def repl_html(m):
        src = m.group(1)
        if re.match(r'^https?://', src) or src.startswith('/'):
            return f'<img src="{src}"'
        return f'<img src="{build_target(src)}"'
    md_text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', repl_md, md_text)
    md_text = re.sub(r'<img\s+src=\"([^\"]+)\"', repl_html, md_text)
    return md_text

def latest_uploaded_md() -> str | None:
    if not os.path.isdir(UPLOADS_DIR):
        return None
    entries = []
    for name in os.listdir(UPLOADS_DIR):
        p = os.path.join(UPLOADS_DIR, name)
        if os.path.isdir(p):
            try:
                mtime = os.path.getmtime(p)
            except Exception:
                mtime = 0
            entries.append((mtime, p))
    if not entries:
        return None
    entries.sort(reverse=True)
    for _, p in entries:
        candidate = os.path.join(p, 'input.md')
        if os.path.isfile(candidate):
            return candidate
    return None

def generate_slides_with_gemini(md: str) -> str:
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise RuntimeError('GOOGLE_API_KEY 未设置')
    from google import genai
    client = genai.Client(api_key=api_key)
    model = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')
    prompt = (
        '你是一个 Slidev 幻灯片生成器。请将输入的 Markdown 转换为适合 Slidev 的 slides.md，'
        '使用 --- 分隔页面，并在每页前添加简洁的 frontmatter（如 title、transition）。'
        '不要输出解释，且不要用 ``` 包裹整段内容，只输出纯 slides.md。'
        '布局与内容密度要求：\n'
        '1) 封面页：仅标题与一句话概述，可使用 transition: slide-left。\n'
        '2) 普通页面：每页不超过 3–6 条要点或 1 段说明 + 1 个代码块；过长代码分成多页，每页最多 12 行。\n'
        '3) 图片页面：保持图片链接不变，配合不超过 3 条说明；图片可单独成页。\n'
        '4) 标题简短，避免多级标题堆叠。\n'
        '路径保持：严格保留原 Markdown 中的图片链接路径，不要更改、简化或移除任何目录段（尤其是上层目录名）。\n'
        '示例：原文中的 ![图](/uploads/<id>/<dir>/c.png) 必须保持为 ![图](/uploads/<id>/<dir>/c.png)。\n\n' + md
    )
    resp = client.models.generate_content(model=model, contents=prompt)
    text = getattr(resp, 'text', '')
    # 清理可能的外层围栏
    t = text.strip()
    if t.startswith('```') and t.endswith('```'):
        first_newline = t.find('\n')
        if first_newline != -1:
            t = t[first_newline+1:-3]
    text = t
    if not text or not text.strip():
        raise RuntimeError('Gemini 未返回内容')
    return text

@app.route('/', methods=['GET'])
def home():
    return send_file(os.path.join(BASE_DIR, 'home.html'), mimetype='text/html; charset=utf-8')

@app.route('/sample.md', methods=['GET'])
def sample():
    return send_file(SAMPLE_MD, mimetype='text/markdown; charset=utf-8')

@app.route('/api/convert', methods=['POST'])
def convert():
    try:
        md_path = request.form.get('md_path') or (request.json.get('md_path') if request.is_json else None)
        if not md_path:
            md_path = latest_uploaded_md()
        if md_path and os.path.isfile(md_path):
            with open(md_path, 'r', encoding='utf-8') as f:
                md = f.read()
        else:
            with open(SAMPLE_MD, 'r', encoding='utf-8') as f:
                md = f.read()
        slides = generate_slides_with_gemini(md)
        with open(SLIDES_MD, 'w', encoding='utf-8') as f:
            f.write(slides)
        return jsonify({ 'ok': True, 'output': 'slides.md', 'source': 'gemini' })
    except Exception as e:
        return jsonify({ 'ok': False, 'error': str(e) }), 500

@app.route('/slidev', methods=['GET'])
def slidev():
    html = (
        '<!doctype html><html><head><meta charset="utf-8" />'
        '<meta name="viewport" content="width=device-width, initial-scale=1" />'
        '<title>Slidev 预览</title>'
        '<style>body,html{height:100%;margin:0}iframe{border:0;width:100%;height:100%}</style>'
        '</head><body>'
        '<iframe src="http://localhost:3030/"></iframe>'
        '</body></html>'
    )
    return html

@app.route('/uploads/<path:subpath>', methods=['GET'])
def serve_uploads(subpath: str):
    target = os.path.join(PUBLIC_DIR, 'uploads', subpath)
    if not os.path.isfile(target):
        return jsonify({ 'ok': False, 'error': '资源不存在' }), 404
    return send_file(target)

@app.route('/logo.png', methods=['GET'])
def logo_png():
    target = os.path.join(BASE_DIR, 'logo.png')
    if not os.path.isfile(target):
        return jsonify({ 'ok': False, 'error': 'logo 不存在' }), 404
    return send_file(target)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({ 'ok': False, 'error': '缺少文件字段 file' }), 400
        file = request.files['file']
        if not file.filename:
            return jsonify({ 'ok': False, 'error': '文件名为空' }), 400
        ts = datetime.now().strftime('%Y%m%d-%H%M%S')
        base_id = f'up-{ts}'
        up_dir = os.path.join(UPLOADS_DIR, base_id)
        pub_base = os.path.join(PUBLIC_DIR, 'uploads', base_id)
        os.makedirs(up_dir, exist_ok=True)
        os.makedirs(pub_base, exist_ok=True)
        filename = file.filename.lower()
        saved_path = os.path.join(up_dir, file.filename)
        file.save(saved_path)

        md_text = None
        md_path = None
        public_base_url = f'/uploads/{base_id}/'

        if filename.endswith('.md'):
            with open(saved_path, 'r', encoding='utf-8') as f:
                md_text = f.read()
            md_text = rewrite_image_paths(md_text, public_base_url)
            md_path = os.path.join(up_dir, 'input.md')
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_text)
        elif filename.endswith('.zip'):
            zip_stem = os.path.splitext(os.path.basename(file.filename))[0]
            extract_root = os.path.join(up_dir, zip_stem)
            os.makedirs(extract_root, exist_ok=True)
            with zipfile.ZipFile(saved_path, 'r') as zip_ref:
                zip_ref.extractall(extract_root)
            # 构建资源映射并将非 md 文件拷贝到 public（URL 段编码）
            mapping: dict[str, str] = {}
            encoded_zip = quote(zip_stem, safe='._-')
            for root, _, files in os.walk(extract_root):
                for name in files:
                    if not name.lower().endswith('.md'):
                        src = os.path.join(root, name)
                        rel = os.path.relpath(src, extract_root)
                        rel_posix = rel.replace('\\', '/')
                        encoded_rel = '/'.join(quote(seg, safe='._-') for seg in rel_posix.split('/'))
                        mapping_key = f'{zip_stem}/{rel_posix}'
                        mapping_val = f'{encoded_zip}/{encoded_rel}'
                        mapping[mapping_key] = mapping_val
                        dst = os.path.join(pub_base, *mapping_val.split('/'))
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst)
            # 选择主 md
            candidates = []
            for root, _, files in os.walk(extract_root):
                for name in files:
                    if name.lower().endswith('.md'):
                        candidates.append(os.path.join(root, name))
            # 优先 slides.md / index.md
            pri = [p for p in candidates if os.path.basename(p).lower() in ('slides.md', 'index.md')]
            md_path = pri[0] if pri else (candidates[0] if candidates else None)
            if not md_path:
                return jsonify({ 'ok': False, 'error': '压缩包内未找到 md 文件' }), 400
            with open(md_path, 'r', encoding='utf-8') as f:
                md_text = f.read()
            # 计算 md 相对目录（相对于 up_dir）用于规范相对引用
            md_rel_dir = os.path.relpath(os.path.dirname(md_path), up_dir).replace('\\', '/')
            md_text = rewrite_image_paths(md_text, public_base_url, md_rel_dir=md_rel_dir, mapping=mapping)
            # 标准化为 input.md
            md_path = os.path.join(up_dir, 'input.md')
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_text)
        else:
            return jsonify({ 'ok': False, 'error': '仅支持 .md 或 .zip 文件' }), 400

        return jsonify({ 'ok': True, 'md_path': md_path, 'public_base': public_base_url })
    except Exception as e:
        return jsonify({ 'ok': False, 'error': str(e) }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PY_PORT') or os.environ.get('PORT') or 5181)
    app.run(host='0.0.0.0', port=port)
