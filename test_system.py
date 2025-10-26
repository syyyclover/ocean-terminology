#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统功能测试脚本
用于验证海洋防灾减灾知识库术语识别系统的核心功能
"""

import os
import sys
import json
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        from src.utils import clean_text, format_page_number, standardize_document_name
        from src.rules import ExtractionRules, AssociationRules
        print("✓ 基础模块导入成功")
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return False
    
    try:
        from scripts.parse_pdfs import PDFParser
        from scripts.extract_terms import TermExtractor
        from scripts.associate_terms import TermAssociator
        from scripts.validate_output import OutputValidator
        print("✓ 脚本模块导入成功")
    except ImportError as e:
        print(f"✗ 脚本模块导入失败: {e}")
        return False
    
    return True

def test_utils():
    """测试工具函数"""
    print("\n测试工具函数...")
    
    from src.utils import clean_text, format_page_number, standardize_document_name
    
    # 测试文本清洗
    test_text = "  海洋  灾害 是指...  "
    cleaned = clean_text(test_text)
    assert "海洋 灾害 是指..." == cleaned
    print("✓ 文本清洗功能正常")
    
    # 测试页码格式化
    page_info = format_page_number("第12页")
    assert page_info == "第12页"
    print("✓ 页码格式化功能正常")
    
    # 测试文档名称标准化
    doc_name = standardize_document_name("GB_T_39419-2020-海啸等级-2020-11-19.pdf")
    assert doc_name == "GB-T-39419-2020-海啸等级-2020-11-19"
    print("✓ 文档名称标准化功能正常")
    
    return True

def test_rules():
    """测试规则模块"""
    print("\n测试规则模块...")
    
    from src.rules import ExtractionRules, AssociationRules
    
    # 测试术语抽取规则
    extraction_rules = ExtractionRules()
    
    test_text = "海洋灾害是指由海洋自然环境异常或剧烈变化导致的灾害。"
    definitions = extraction_rules.extract_term_definitions(test_text)
    
    assert len(definitions) > 0
    assert definitions[0]['term'] == "海洋灾害"
    print("✓ 术语抽取规则功能正常")
    
    # 测试关联关系规则
    association_rules = AssociationRules()
    
    context = "风暴潮会导致海岸侵蚀"
    relationship, confidence, description = association_rules.analyze_relationship(
        "风暴潮", "海岸侵蚀", context
    )
    
    assert relationship == "因果关系"
    assert confidence > 0
    print("✓ 关联关系规则功能正常")
    
    return True

def test_config():
    """测试配置加载"""
    print("\n测试配置加载...")
    
    from src.utils import load_config
    
    # 测试默认配置
    config = load_config()
    assert 'data_dir' in config
    assert 'output_dir' in config
    print("✓ 默认配置加载正常")
    
    # 测试自定义配置
    if os.path.exists('config.json'):
        config = load_config('config.json')
        assert 'term_extraction' in config
        print("✓ 自定义配置加载正常")
    
    return True

def test_task_file():
    """测试任务文件"""
    print("\n测试任务文件...")
    
    task_file = 'data/task.json'
    
    if not os.path.exists(task_file):
        print("⚠ 任务文件不存在，跳过测试")
        return True
    
    try:
        with open(task_file, 'r', encoding='utf-8') as f:
            terms = json.load(f)
        
        assert isinstance(terms, list)
        assert len(terms) > 0
        print(f"✓ 任务文件格式正确，包含 {len(terms)} 个术语")
        
        return True
    except Exception as e:
        print(f"✗ 任务文件读取失败: {e}")
        return False

def test_data_directory():
    """测试数据目录"""
    print("\n测试数据目录...")
    
    data_dir = 'data/raw'
    
    if not os.path.exists(data_dir):
        print("⚠ 数据目录不存在，跳过测试")
        return True
    
    pdf_files = list(Path(data_dir).glob("*.pdf"))
    
    if len(pdf_files) > 0:
        print(f"✓ 数据目录包含 {len(pdf_files)} 个PDF文件")
        return True
    else:
        print("⚠ 数据目录中没有PDF文件")
        return True

def main():
    """主测试函数"""
    print("=" * 50)
    print("海洋防灾减灾知识库术语识别系统 - 功能测试")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_utils,
        test_rules,
        test_config,
        test_task_file,
        test_data_directory
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ 测试 {test.__name__} 失败: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过，系统可以正常运行")
        return 0
    else:
        print("⚠ 部分测试失败，请检查系统配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())