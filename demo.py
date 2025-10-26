#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统演示脚本
展示海洋防灾减灾知识库术语识别系统的核心功能
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

def demo_utils():
    """演示工具函数"""
    print("=" * 50)
    print("工具函数演示")
    print("=" * 50)
    
    from src.utils import clean_text, format_page_number, standardize_document_name
    
    # 演示文本清洗
    test_text = "   海洋  灾害 是指由海洋自然环境异常或剧烈变化导致的灾害。  "
    cleaned = clean_text(test_text)
    print(f"原始文本: '{test_text}'")
    print(f"清洗后: '{cleaned}'")
    print()
    
    # 演示页码格式化
    page_examples = ["第12页", "page 15", "p. 20-21", "第5-6页"]
    for page in page_examples:
        formatted = format_page_number(page)
        print(f"原始页码: '{page}' -> 格式化: '{formatted}'")
    print()
    
    # 演示文档名称标准化
    filename = "GB_T_39419-2020-海啸等级-2020-11-19.pdf"
    standardized = standardize_document_name(filename)
    print(f"原始文件名: '{filename}'")
    print(f"标准化后: '{standardized}'")
    print()

def demo_rules():
    """演示规则模块"""
    print("=" * 50)
    print("规则模块演示")
    print("=" * 50)
    
    from src.rules import ExtractionRules, AssociationRules
    
    # 演示术语抽取规则
    extraction_rules = ExtractionRules()
    
    test_texts = [
        "海洋灾害是指由海洋自然环境异常或剧烈变化导致的灾害。",
        "海浪定义为海面在外力作用下产生的波动现象。",
        "风暴潮即由强烈大气扰动引起的海面异常升高现象。"
    ]
    
    for text in test_texts:
        definitions = extraction_rules.extract_term_definitions(text)
        print(f"文本: '{text}'")
        if definitions:
            for def_info in definitions:
                print(f"  提取到术语: '{def_info['term']}'")
                print(f"  定义: '{def_info['definition']}'")
        else:
            print("  未提取到术语定义")
        print()
    
    # 演示关联关系规则
    association_rules = AssociationRules()
    
    test_contexts = [
        ("风暴潮", "海岸侵蚀", "风暴潮会导致海岸侵蚀"),
        ("海洋灾害", "风暴潮", "海洋灾害包括风暴潮、海浪和海啸"),
        ("浮标观测", "海洋观测", "浮标观测属于海洋观测的一种方式")
    ]
    
    for term1, term2, context in test_contexts:
        relationship, confidence, description = association_rules.analyze_relationship(
            term1, term2, context
        )
        print(f"术语对: '{term1}' - '{term2}'")
        print(f"上下文: '{context}'")
        print(f"关联关系: {relationship} (置信度: {confidence:.2f})")
        print(f"描述: {description}")
        print()

def demo_system_overview():
    """演示系统概览"""
    print("=" * 50)
    print("系统概览演示")
    print("=" * 50)
    
    # 检查数据目录
    data_dir = Path("data/raw")
    if data_dir.exists():
        pdf_files = list(data_dir.glob("*.pdf"))
        print(f"数据目录包含 {len(pdf_files)} 个PDF文档")
        
        # 显示部分文档
        print("部分文档示例:")
        for pdf in pdf_files[:5]:
            print(f"  - {pdf.name}")
        if len(pdf_files) > 5:
            print(f"  - ... 还有 {len(pdf_files) - 5} 个文档")
    else:
        print("数据目录不存在")
    print()
    
    # 检查任务文件
    task_file = Path("data/task.json")
    if task_file.exists():
        import json
        with open(task_file, 'r', encoding='utf-8') as f:
            terms = json.load(f)
        print(f"任务文件包含 {len(terms)} 个目标术语")
        print("术语示例:")
        for term in terms[:10]:
            print(f"  - {term}")
        if len(terms) > 10:
            print(f"  - ... 还有 {len(terms) - 10} 个术语")
    else:
        print("任务文件不存在")
    print()

def main():
    """主演示函数"""
    print("海洋防灾减灾知识库术语识别系统 - 功能演示")
    print()
    
    try:
        demo_utils()
        demo_rules()
        demo_system_overview()
        
        print("=" * 50)
        print("演示完成!")
        print("=" * 50)
        print()
        print("下一步操作建议:")
        print("1. 运行完整系统: python app.py data/task.json")
        print("2. 仅运行术语识别: python app.py data/task.json --task 1")
        print("3. 仅运行关联分析: python app.py data/task.json --task 2")
        print("4. 使用Docker运行: docker build -t ocean-terminology . && docker run -v ./data:/app/data -v ./output:/app/output ocean-terminology data/task.json")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()