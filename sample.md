# Python 列表（数组）速览

Python 中的列表（list）是最常用的可变序列，用于存储有序元素集合。

## 创建与访问

```python
# 创建
nums = [1, 2, 3]
mix = [1, 'a', True]
empty = []

# 访问与修改
print(nums[0])  # 1
nums[1] = 20
print(nums[-1])  # 3
```

## 常用操作

```python
nums = [1, 2, 3]
nums.append(4)       # 末尾追加
nums.extend([5, 6])  # 扩展多个元素
nums.insert(1, 99)   # 指定位置插入
nums.pop()           # 弹出末尾元素
nums.remove(2)       # 删除首个匹配元素 2

# 切片
print(nums[1:4])     # 取 1..3 索引的子列表
print(nums[::-1])    # 反转视图（切片返回新列表）
```

## 列表推导式

```python
squares = [x * x for x in range(5)]
evens = [x for x in range(10) if x % 2 == 0]
```

## 嵌套列表

```python
matrix = [
    [1, 2, 3],
    [4, 5, 6],
]
col1 = [row[0] for row in matrix]
```

## 排序与复制

```python
data = [3, 1, 2]
data.sort()                # 就地排序
sorted_data = sorted(data) # 返回新列表

# 浅拷贝
copy1 = data[:] 
copy2 = list(data)
```

## 注意事项

```python
# 乘法复制会复用同一子列表引用
rows = [[0] * 3] * 2
rows[0][0] = 1
print(rows)  # [[1, 0, 0], [1, 0, 0]]

# 正确做法：使用推导式生成独立子列表
rows = [[0 for _ in range(3)] for _ in range(2)]
rows[0][0] = 1
print(rows)  # [[1, 0, 0], [0, 0, 0]]
```
