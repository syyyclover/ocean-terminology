# 海洋防灾减灾知识库术语识别系统

## 项目概述

本项目是一个基于人工智能的海洋防灾减灾知识库术语识别系统，专门用于从海洋领域的标准文档中提取标准化术语及其关联关系。系统支持术语识别和术语关联关系分析两大核心功能。

## 功能特性

### 基础任务1：术语识别（40分）
- 从PDF文档中完整提取20个明确定义的标准化术语
- 按"术语名称-术语定义-文档出处-文档页数"四字段结构化输出
- 确保提取信息与文档原文完全匹配

### 进阶任务2：术语关联关系（30分，选做）
- 分析20个术语的关联关系
- 提取术语关联的描述（含源文档出处、页数信息）
- 判断关联关系类型（主从关系或因果关系）

## 系统架构

```
工作目录：
E:\huiyi\10.26\work/
├─ data/                   # 数据目录
│  ├─ raw/                 # 原始PDF文档
│  └─ processed/           # 处理后的数据
├─ docs/                   # 说明文档
├─ scripts/                # 处理脚本
│  ├─ parse_pdfs.py        # PDF解析
│  ├─ extract_terms.py     # 术语抽取
│  ├─ associate_terms.py   # 术语关联
│  ├─ validate_output.py   # 输出验证
│  └─ run_pipeline.sh      # 运行管道
├─ src/                    # 源代码
│  ├─ utils.py             # 工具函数
│  ├─ nlp_models.py        # NLP模型
│  └─ rules.py             # 抽取规则
├─ Dockerfile              # Docker配置
├─ app.py                  # 统一入口
├─ entrypoint.sh           # 入口脚本
├─ requirements.txt        # 依赖列表
└─ README.md               # 说明文档
```

## 快速开始

### 环境要求
- Python 3.8+
- 依赖包：见 `requirements.txt`

### 安装依赖
```bash
pip install -r requirements.txt
```

### 准备数据
1. 将PDF文档放入 `data/raw/` 目录
2. 创建任务文件 `data/task.json`，内容示例：
```json
["海洋灾害", "海浪", "风暴潮", "海啸", "其他16个术语"]
```

### 运行系统

#### 方式1：使用Python直接运行
```bash
# 运行全部任务
python app.py data/task.json

# 仅运行任务1（术语识别）
python app.py data/task.json --task 1

# 仅运行任务2（术语关联）
python app.py data/task.json --task 2

# 指定输出目录
python app.py data/task.json --output results
```

#### 方式2：使用Shell脚本
```bash
# 运行全部任务
./scripts/run_pipeline.sh data/task.json

# 运行特定任务
./scripts/run_pipeline.sh --task 1 data/task.json
```

#### 方式3：使用Docker
```bash
# 构建镜像
docker build -t ocean-terminology .

# 运行容器
docker run -v ./data:/app/data -v ./output:/app/output ocean-terminology data/task.json
```

## 输出格式

### 任务1输出格式
```json
[
  "W01": {
    "术语名称": "海洋灾害",
    "术语定义": "海洋灾害是指...",
    "文档出处": "GB_T_39632-2020-海洋防灾减灾术语-2020-12-14",
    "文档页数": "第3页"
  },
  "W02": {
    "术语名称": "海浪",
    "术语定义": "海浪是指...",
    "文档出处": "GB_T_42176-2022-海浪等级-2022-12-30", 
    "文档页数": "第5页"
  }
  // 其他18个术语信息
]
```

### 任务2输出格式
```json
[
  "R01": {
    "术语关联": ["术语A", "术语B"],
    "关联关系": "主从关系",
    "关联描述": [
      {
        "文档出处": "文档名称", 
        "文档页数": "第X页"
      }
    ]
  },
  "R02": {
    "术语关联": ["术语C", "术语D"],
    "关联关系": "因果关系",
    "关联描述": [
      {
        "文档出处": "文档名称",
        "文档页数": "第X页"
      }
    ]
  }
  // 其他关联关系
]
```

## 技术特点

### 1. 智能术语识别
- 基于规则的模式匹配
- 上下文语义分析
- 多文档交叉验证

### 2. 关联关系分析
- 主从关系检测
- 因果关系识别
- 关联网络构建

### 3. 输出验证
- 格式完整性检查
- 内容准确性验证
- 质量评估报告

### 4. 可扩展架构
- 模块化设计
- 配置驱动
- Docker容器化

## 配置说明

系统支持通过配置文件进行参数调整，创建 `config.json`：

```json
{
  "data_dir": "data/raw",
  "output_dir": "output",
  "term_extraction": {
    "similarity_threshold": 0.8,
    "max_definition_length": 500,
    "min_definition_length": 10
  },
  "association_analysis": {
    "relationship_types": ["主从关系", "因果关系"],
    "min_confidence": 0.7
  }
}
```

## 开发说明

### 代码结构
- `src/utils.py` - 通用工具函数
- `src/nlp_models.py` - NLP模型接口
- `src/rules.py` - 抽取规则集合
- `scripts/` - 处理管道各阶段
- `app.py` - 统一入口程序

### 扩展开发
1. 添加新的术语抽取规则：修改 `src/rules.py`
2. 增加新的关联关系类型：扩展 `AssociationRules` 类
3. 集成新的NLP模型：实现 `NLPModels` 接口

## 性能优化

- PDF解析使用 `pdfplumber` 库，支持高效文本提取
- 术语匹配采用多模式正则表达式
- 关联分析使用组合优化，避免重复计算
- 支持大文档分批处理

## 故障排除

### 常见问题
1. **PDF解析失败**：检查PDF文件是否损坏或加密
2. **术语识别不全**：调整相似度阈值或扩展规则
3. **内存不足**：使用Docker运行或分批处理

### 日志查看
系统运行日志保存在 `ocean_terminology.log` 文件中。

## 许可证

本项目基于MIT许可证开源。

## 联系我们

如有问题或建议，请通过项目Issue反馈。