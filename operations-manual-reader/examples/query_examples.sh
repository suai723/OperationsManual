#!/bin/bash

# 工作手册查询示例脚本
# 演示如何使用 query_workbook.py 工具进行查询操作

# 显示脚本信息
echo "工作手册查询示例脚本"
echo "=================="
echo ""

# 获取脚本所在目录
SCRIPT_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# 检查 Python 脚本是否存在
QUERY_SCRIPT="$SCRIPT_DIR/../scripts/query_workbook.py"
if [ ! -f "$QUERY_SCRIPT" ]; then
    echo "错误：未找到查询脚本 $QUERY_SCRIPT"
    exit 1
fi

# 检查 Python 是否可用
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到 python3 命令"
    exit 1
fi

# 示例1：查看工作手册概览
echo "示例1：查看工作手册概览"
echo "------------------------"
python3 "$QUERY_SCRIPT" list
echo ""
echo "=================="
echo ""

# 示例2：搜索包含 MySQL 的条目
echo "示例2：搜索包含 MySQL 的条目"
echo "------------------------"
python3 "$QUERY_SCRIPT" search -k "MySQL"
echo ""
echo "=================="
echo ""

# 示例3：读取指定条目
echo "示例3：读取指定条目"
echo "------------------------"
python3 "$QUERY_SCRIPT" read -i "abc12345"
echo ""
echo "=================="
echo ""

echo "查询操作完成！"
echo ""
echo "更多查询示例："
echo "  - python3 query_workbook.py search -k \"备份\""
echo "  - python3 query_workbook.py list"
echo "  - python3 query_workbook.py read -i \"def67890\""
