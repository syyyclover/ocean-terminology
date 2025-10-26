#!/bin/bash

# 海洋防灾减灾知识库术语识别系统 - 运行管道脚本

# 设置工作目录
WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORK_DIR"

echo "=========================================="
echo "海洋防灾减灾知识库术语识别系统"
echo "=========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请安装Python3"
    exit 1
fi

# 检查依赖
if [ ! -f "requirements.txt" ]; then
    echo "错误: 未找到requirements.txt文件"
    exit 1
fi

echo "检查Python依赖..."
python3 -c "import pdfplumber" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "安装Python依赖..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 依赖安装失败"
        exit 1
    fi
fi

# 检查数据目录
if [ ! -d "data/raw" ]; then
    echo "错误: 数据目录 data/raw 不存在"
    echo "请将PDF文档放入 data/raw 目录"
    exit 1
fi

# 检查任务文件
TASK_FILE=""
if [ -f "data/task.json" ]; then
    TASK_FILE="data/task.json"
elif [ -f "task.json" ]; then
    TASK_FILE="task.json"
else
    echo "警告: 未找到任务文件 task.json"
    echo "请创建任务文件或指定任务文件路径"
fi

# 解析命令行参数
TASK_TYPE="all"
OUTPUT_DIR="output"
CONFIG_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --task)
            TASK_TYPE="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --help)
            echo "用法: $0 [选项] [任务文件]"
            echo ""
            echo "选项:"
            echo "  --task <1|2|all>     执行任务: 1(术语识别), 2(术语关联), all(全部)"
            echo "  --output <目录>      输出目录 (默认: output)"
            echo "  --config <文件>      配置文件路径"
            echo "  --help               显示此帮助信息"
            echo ""
            echo "示例:"
            echo "  $0 --task 1 data/task.json"
            echo "  $0 --output results --config config.json"
            exit 0
            ;;
        *)
            if [[ -f "$1" ]]; then
                TASK_FILE="$1"
            fi
            shift
            ;;
    esac
done

# 检查任务文件
if [ -z "$TASK_FILE" ]; then
    echo "错误: 未指定任务文件"
    echo "用法: $0 [任务文件路径]"
    exit 1
fi

if [ ! -f "$TASK_FILE" ]; then
    echo "错误: 任务文件不存在: $TASK_FILE"
    exit 1
fi

echo "任务文件: $TASK_FILE"
echo "任务类型: $TASK_TYPE"
echo "输出目录: $OUTPUT_DIR"

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 构建Python命令
PYTHON_CMD="python3 app.py \"$TASK_FILE\" --task $TASK_TYPE --output \"$OUTPUT_DIR\""

if [ -n "$CONFIG_FILE" ]; then
    PYTHON_CMD="$PYTHON_CMD --config \"$CONFIG_FILE\""
fi

echo ""
echo "开始执行..."
echo "=========================================="

# 执行Python程序
eval $PYTHON_CMD

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "执行成功!"
    echo "结果保存在: $OUTPUT_DIR"
    echo ""
    
    # 显示生成的文件
    if [ -f "$OUTPUT_DIR/task1_results.json" ]; then
        echo "- 任务1结果: $OUTPUT_DIR/task1_results.json"
    fi
    
    if [ -f "$OUTPUT_DIR/task2_results.json" ]; then
        echo "- 任务2结果: $OUTPUT_DIR/task2_results.json"
    fi
    
    if [ -f "ocean_terminology.log" ]; then
        echo "- 日志文件: ocean_terminology.log"
    fi
    
else
    echo ""
    echo "=========================================="
    echo "执行失败! (退出码: $EXIT_CODE)"
    echo "请检查日志文件: ocean_terminology.log"
fi

echo "=========================================="