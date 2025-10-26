#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
文本清洗、页码格式化、文档出处标准化等工具函数
"""

import re
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """设置日志配置"""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('ocean_terminology.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """加载配置文件"""
    default_config = {
        "data_dir": "data/raw",
        "output_dir": "output",
        "pdf_parser": {
            "extract_text": True,
            "extract_tables": False,
            "language": "chinese"
        },
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
    
    if config_path and Path(config_path).exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            # 合并配置
            default_config.update(user_config)
    
    return default_config


def clean_text(text: str) -> str:
    """
    清洗文本
    
    Args:
        text: 原始文本
        
    Returns:
        清洗后的文本
    """
    if not text:
        return ""
    
    # 移除多余空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 移除特殊字符但保留中文标点
    text = re.sub(r'[^\u4e00-\u9fff\w\s，。！？；：（）《》【】""'']', '', text)
    
    # 标准化引号
    text = text.replace('"', '"')
    text = text.replace('\'', '\'')
    
    return text.strip()


def format_page_number(page_info: str) -> str:
    """
    格式化页码信息
    
    Args:
        page_info: 原始页码信息
        
    Returns:
        格式化后的页码信息
    """
    if not page_info:
        return ""
    
    # 匹配页码格式
    page_patterns = [
        r'(?:第)?(\d+)(?:[-~](\d+))?(?:页)?',
        r'page\s*(\d+)(?:[-~](\d+))?',
        r'p\.?\s*(\d+)(?:[-~](\d+))?'
    ]
    
    for pattern in page_patterns:
        match = re.search(pattern, page_info, re.IGNORECASE)
        if match:
            start_page = match.group(1)
            end_page = match.group(2) if match.group(2) else None
            
            if end_page:
                return f"第{start_page}-{end_page}页"
            else:
                return f"第{start_page}页"
    
    # 如果无法匹配，返回原始信息
    return page_info


def standardize_document_name(filename: str) -> str:
    """
    标准化文档出处名称
    
    Args:
        filename: 文件名
        
    Returns:
        标准化后的文档名称
    """
    if not filename:
        return ""
    
    # 移除文件扩展名
    name_without_ext = Path(filename).stem
    
    # 标准化分隔符
    name_standardized = name_without_ext.replace('_', '-')
    
    # 确保格式一致
    return name_standardized


def extract_term_definition(text: str, term: str) -> Optional[str]:
    """
    从文本中提取术语定义
    
    Args:
        text: 包含术语的文本
        term: 术语名称
        
    Returns:
        术语定义或None
    """
    if not text or not term:
        return None
    
    # 常见的定义模式
    definition_patterns = [
        rf'{re.escape(term)}\s*[：:]\s*([^。！？]+[。！？])',
        rf'{re.escape(term)}\s*是指\s*([^。！？]+[。！？])',
        rf'{re.escape(term)}\s*定义为\s*([^。！？]+[。！？])',
        rf'{re.escape(term)}\s*为\s*([^。！？]+[。！？])',
        rf'{re.escape(term)}\s*即\s*([^。！？]+[。！？])'
    ]
    
    for pattern in definition_patterns:
        match = re.search(pattern, text)
        if match:
            definition = match.group(1).strip()
            # 清理定义文本
            definition = clean_text(definition)
            if len(definition) >= 10:  # 最小长度要求
                return definition
    
    return None


def calculate_similarity(text1: str, text2: str) -> float:
    """
    计算两个文本的相似度（基于Jaccard相似度）
    
    Args:
        text1: 文本1
        text2: 文本2
        
    Returns:
        相似度分数 (0-1)
    """
    if not text1 or not text2:
        return 0.0
    
    # 简单的基于字符的相似度计算
    set1 = set(text1)
    set2 = set(text2)
    
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0


def validate_output_format(data: Dict[str, Any], task_type: str = "task1") -> bool:
    """
    验证输出格式是否符合要求
    
    Args:
        data: 输出数据
        task_type: 任务类型
        
    Returns:
        是否通过验证
    """
    if task_type == "task1":
        required_fields = ["术语名称", "术语定义", "文档出处", "文档页数"]
        
        for key, value in data.items():
            if not key.startswith("W"):
                return False
            
            for field in required_fields:
                if field not in value:
                    return False
                if not value[field]:
                    return False
    
    elif task_type == "task2":
        required_fields = ["术语关联", "关联关系", "关联描述"]
        
        for key, value in data.items():
            if not key.startswith("R"):
                return False
            
            for field in required_fields:
                if field not in value:
                    return False
                if not value[field]:
                    return False
    
    return True


def save_json_output(data: Dict[str, Any], output_path: str) -> bool:
    """
    保存JSON格式输出
    
    Args:
        data: 要保存的数据
        output_path: 输出路径
        
    Returns:
        是否保存成功
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"保存JSON输出失败: {e}")
        return False