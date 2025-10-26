#!/bin/bash

# 海洋防灾减灾知识库术语识别系统 - Docker入口点脚本

set -e

echo "=========================================="
echo "海洋防灾减灾知识库术语识别系统"
echo "Docker容器启动"
echo "=========================================="

# 检查数据目录
if [ ! -d "/app/data/raw" ]; then
    echo "创建数据目录..."
    mkdir -p /app/data/raw
fi

# 检查输出目录
if [ ! -d "/app/output" ]; then
    echo "创建输出目录..."
    mkdir -p /app/output
fi

echo "当前工作目录: $(pwd)"
echo "Python路径: $PYTHONPATH"

# 检查是否有任务文件参数
if [ $# -eq 0 ]; then
    echo ""
    echo "用法:"
    echo "  docker run -v /host/data:/app/data -v /host/output:/app/output <image> <参数>"
    echo ""
    echo "参数:"
    echo "  --help                   显示帮助信息"
    echo "  <任务文件>               执行指定任务文件"
    echo "  --task <1|2|all>        执行特定任务"
    echo "  --output <目录>         输出目录"
    echo ""
    echo "示例:"
    echo "  docker run -v ./data:/app/data -v ./output:/app/output ocean-terminology data/task.json"
    echo "  docker run -v ./data:/app/data -v ./output:/app/output ocean-terminology --task 1 data/task.json"
    echo ""
    exit 0
fi

# 如果第一个参数是--help，显示帮助
if [ "$1" = "--help" ]; then
    echo "显示帮助信息..."
    python3 /app/app.py --help
    exit 0
fi

# 执行应用程序
echo "执行应用程序..."
echo "参数: $@"
echo ""

python3 /app/app.py "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "执行成功!"
    echo "结果保存在输出目录中"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "执行失败! (退出码: $EXIT_CODE)"
    echo "请检查日志文件"
    echo "=========================================="
fi

exit $EXIT_CODE