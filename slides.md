---
theme: seriph
highlighter: shiki
lineNumbers: false
drawings:
  present: true
transition: slide-left
css: unocss
---

# 💡 C语言指针
## 内存地址的“遥控器”

<div class="pt-12">
  <span class="px-2 py-1 rounded">C语言的<b>指针 (Pointer)</b> 是其强大和灵活性的核心，但也是许多初学者的难点。</span>
</div>

---
layout: default
---

### 1. 什么是指针？

指针本质上是一个**变量**，它存储的不是数据本身，而是**另一个变量在内存中的地址**。

<br>

> 📌 **可以把它想象成一个房子的地址牌。**

<div class="mt-8" v-clicks>

- **普通变量**：房子本身（存储数据）
- **指针变量**：地址牌（存储房子的地址）

</div>

---
layout: default
---

### 2. 核心概念与符号

<div v-clicks class="space-y-4">

- **声明 (`int *p;`)**
  <br>
  声明一个名为 `p` 的指针变量，它“指向”一个整数 (`int`)。

- **`&` 取地址符**
  <br>
  用来获取变量的内存地址。例：`p = &x;`（将变量 `x` 的地址存入指针 `p`）。

- **`*` 解引用符**
  <br>
  用来访问指针所指向的地址中存储的实际数据。例：`*p = 10;`（通过指针 `p`，将 `x` 的值改为 10）。

</div>

---
layout: default
---

### 3. 示例代码

```c {all|4|5|7|9-12|14|16}
#include <stdio.h>

int main() {
    int x = 42;       // 1. 定义一个整数变量 x
    int *p;           // 2. 声明一个指向整数的指针 p

    p = &x;           // 3. 将 x 的地址赋给指针 p

    printf("x 的值是: %d\n", x);
    printf("x 的地址是: %p\n", &x);
    printf("p 存储的地址是: %p\n", p);
    printf("p 指向的值是: %d\n", *p);     // 4. 解引用，访问 x 的值

    *p = 100;         // 5. 通过指针修改 x 的值

    printf("x 现在的值是: %d\n", x);      // 输出: 100

    return 0;
}
```

---
layout: image-right
image: /uploads/up-20251126-112901/ccc/ccc/c.png
---

### 指针概念图解

<div v-clicks class="space-y-4">

- 变量 `x` 存储了值 `42`，并占据一块内存空间。

- 指针 `p` 是另一个变量，它存储的内容恰好是 `x` 的**内存地址**。

- 我们说 `p` **指向 (points to)** `x`。

- 通过 **解引用 (`*p`)** 操作，我们可以从 `p` 出发，访问并操作 `x` 存储的数据。

</div>
