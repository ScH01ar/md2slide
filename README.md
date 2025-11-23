# md2slide

一个使用 Gemini 大模型与 Slidev 的 Markdown → 幻灯片转换网站。支持上传 `.md` 或包含图片资源的 `.zip`，自动处理图片路径并生成可预览的 `slides.md`。

## 特性
- 上传 `.md` 或 `.zip`（含图片资源）
- 自动重写相对图片路径为可访问的公共资源地址（支持中文与特殊字符）
- 调用 Gemini（`google-genai`）生成符合 Slidev 的分页与版式
- 一键预览：集成 Slidev 开发服务器

## 目录结构
- `app.py`：Flask 后端（上传、转换、预览路由）
- `home.html`：主页（上传与转换操作界面）
- `slides.md`：Slidev 幻灯片入口文件（转换输出）
- `sample.md`：示例 Markdown
- `public/uploads/<id>/...`：上传的公共资源（图片等）
- `uploads/<id>/input.md`：标准化后的待转换 Markdown

## 环境依赖
- Python 3.12（示例使用 Conda 环境 `py12`）
- Node.js（用于运行 Slidev）
- 已安装依赖：
  - Python：`flask`、`google-genai`
  - Node：`@slidev/cli`、`@slidev/theme-default`

## 启动步骤
1. 启动 Flask 后端（确保已设置密钥并在目标 Python 环境中）：
   - `GOOGLE_API_KEY=<你的密钥> conda run -n py12 python app.py`
   - 或激活环境后：`export GOOGLE_API_KEY=<你的密钥>; python app.py`
2. 启动 Slidev 预览：
   - `npx slidev --open false`
3. 打开主页：
   - `http://localhost:5181/`（上传并转换）
- 预览页：`http://localhost:5181/slidev` 或 `http://localhost:3030/`

## 使用说明
- 上传 `.md`：直接转换为 `slides.md`
- 上传 `.zip`：
  - 解压到 `uploads/<id>/<zip_name>/...`
  - 将非 `.md` 资源复制到 `public/uploads/<id>/<zip_name>/...`（按路径分段做 URL 编码）
  - 自动重写 `.md` 内相对图片路径为 `/uploads/<id>/<zip_name>/...`
  - 主 `.md` 优先选择 `slides.md` / `index.md`，否则取首个 `.md`
- 未显式提供 `md_path` 时，转换接口会自动选用最近一次上传的 `uploads/<latest>/input.md`

## 转换与版式规则（提示词摘要）
- 使用 `---` 分隔页面；每页添加简洁前言（如 `title`、`transition`）
- 封面页仅标题与一句话概述；普通页每页不超过 3–6 条要点或 1 段说明 + 1 代码块
- 长代码分成多页，每页最多约 12 行
- 图片页保持链接路径不变，并配合不超过 3 条说明
- 严格保留图片路径的目录段（不修改 `/uploads/<id>/<dir>/file` 结构）
- 输出为纯 `slides.md` 内容，不使用外层代码围栏

## 常见问题
- 预览拒绝连接：确保 Slidev 在 `http://localhost:3030/` 运行
- 首屏空白：避免 `slides.md` 以 `---` 开头（已在逻辑中规避）
- 中文/特殊字符路径：已按分段 URL 编码复制到 `public/uploads/...`，并在 Markdown 中重写

## NPM 脚本
- `npm run flask`：启动 Flask（需在正确 Python 环境中）
- `npm run slidev`：启动 Slidev

## 许可证
本项目示例代码用于演示与评估，具体授权请根据你的使用场景自行决定。
