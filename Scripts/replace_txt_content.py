import os

# 指定要处理的目录
directory = "path/to/directory"

# 遍历目录下的所有文件
for filename in os.listdir(directory):
    # 检查文件是否为.txt文件
    if filename.endswith(".txt"):
        # 构建文件路径
        filepath = os.path.join(directory, filename)

        # 读取文件内容
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # 替换内容
        new_content = content.replace("pepper", "chilli")

        # 如果内容发生了变化，则写回文件
        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(new_content)
            print(f"已处理文件: {filename}")
