#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
术语抽取模块
从PDF文档中提取标准化术语及其定义
"""

import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.utils import clean_text, format_page_number, standardize_document_name, extract_term_definition
from src.rules import ExtractionRules


class TermExtractor:
    """术语抽取器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化术语抽取器"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.rules = ExtractionRules()
        
        # 获取配置参数
        self.similarity_threshold = self.config.get('term_extraction', {}).get('similarity_threshold', 0.8)
        self.max_definition_length = self.config.get('term_extraction', {}).get('max_definition_length', 500)
        self.min_definition_length = self.config.get('term_extraction', {}).get('min_definition_length', 10)
    
    def extract_terms(self, target_terms: List[str], pdf_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        从PDF文档中提取目标术语
        
        Args:
            target_terms: 目标术语列表
            pdf_documents: PDF文档列表
            
        Returns:
            术语提取结果
        """
        self.logger.info(f"开始提取 {len(target_terms)} 个目标术语")
        
        results = {}
        
        for i, term in enumerate(target_terms, 1):
            term_key = f"W{i:02d}"
            term_result = self._extract_single_term(term, pdf_documents)
            
            if term_result:
                results[term_key] = term_result
                self.logger.info(f"成功提取术语: {term}")
            else:
                self.logger.warning(f"未找到术语定义: {term}")
                # 创建空结果以保持结构
                results[term_key] = {
                    "术语名称": term,
                    "术语定义": "",
                    "文档出处": "",
                    "文档页数": ""
                }
        
        self.logger.info(f"术语提取完成，成功提取 {len([r for r in results.values() if r['术语定义']])} 个术语")
        return results
    
    def _extract_single_term(self, term: str, pdf_documents: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """
        提取单个术语的定义信息
        
        Args:
            term: 术语名称
            pdf_documents: PDF文档列表
            
        Returns:
            术语信息字典
        """
        best_result = None
        best_confidence = 0.0
        
        for doc in pdf_documents:
            for page in doc['pages']:
                page_text = page['text']
                
                # 检查术语是否出现在页面中
                if term not in page_text:
                    continue
                
                # 尝试提取定义
                definition = extract_term_definition(page_text, term)
                
                if definition:
                    # 计算置信度
                    confidence = self._calculate_definition_confidence(definition, term)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_result = {
                            "术语名称": term,
                            "术语定义": definition,
                            "文档出处": standardize_document_name(doc['file_name']),
                            "文档页数": format_page_number(f"第{page['page_number']}页")
                        }
        
        return best_result if best_confidence >= self.similarity_threshold else None
    
    def _calculate_definition_confidence(self, definition: str, term: str) -> float:
        """
        计算定义置信度
        
        Args:
            definition: 术语定义
            term: 术语名称
            
        Returns:
            置信度分数 (0-1)
        """
        confidence = 0.0
        
        # 检查定义长度
        definition_length = len(definition)
        if self.min_definition_length <= definition_length <= self.max_definition_length:
            confidence += 0.3
        
        # 检查是否包含术语本身
        if term in definition:
            confidence += 0.2
        
        # 检查定义格式（是否以完整句子结束）
        if definition.endswith(('。', '！', '？')):
            confidence += 0.2
        
        # 检查是否包含定义关键词
        definition_keywords = ['是指', '定义为', '为', '即', '指的是', '表示']
        if any(keyword in definition for keyword in definition_keywords):
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def extract_all_terms_from_documents(self, pdf_documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        从所有文档中自动提取所有术语
        
        Args:
            pdf_documents: PDF文档列表
            
        Returns:
            所有提取的术语列表
        """
        all_terms = []
        
        for doc in pdf_documents:
            for page in doc['pages']:
                page_text = page['text']
                
                # 使用规则提取术语定义
                definitions = self.rules.extract_term_definitions(page_text)
                
                for definition_info in definitions:
                    term = definition_info['term']
                    definition = definition_info['definition']
                    
                    # 过滤非海洋相关术语
                    if not self.rules.is_ocean_related_term(term):
                        continue
                    
                    # 创建术语记录
                    term_record = {
                        "术语名称": term,
                        "术语定义": definition,
                        "文档出处": standardize_document_name(doc['file_name']),
                        "文档页数": format_page_number(f"第{page['page_number']}页"),
                        "置信度": self._calculate_definition_confidence(definition, term)
                    }
                    
                    all_terms.append(term_record)
        
        # 去重（基于术语名称）
        unique_terms = {}
        for term in all_terms:
            term_name = term["术语名称"]
            if term_name not in unique_terms or term["置信度"] > unique_terms[term_name]["置信度"]:
                unique_terms[term_name] = term
        
        self.logger.info(f"从文档中自动提取了 {len(unique_terms)} 个唯一术语")
        return list(unique_terms.values())
    
    def validate_term_extraction(self, extracted_terms: Dict[str, Any], 
                               reference_terms: List[str]) -> Dict[str, Any]:
        """
        验证术语提取结果
        
        Args:
            extracted_terms: 提取的术语结果
            reference_terms: 参考术语列表
            
        Returns:
            验证结果
        """
        validation_results = {
            "total_target_terms": len(reference_terms),
            "successfully_extracted": 0,
            "missing_terms": [],
            "extraction_quality": {},
            "overall_accuracy": 0.0
        }
        
        for term in reference_terms:
            # 查找对应的提取结果
            extracted_term = None
            for key, value in extracted_terms.items():
                if value["术语名称"] == term:
                    extracted_term = value
                    break
            
            if extracted_term and extracted_term["术语定义"]:
                validation_results["successfully_extracted"] += 1
                
                # 评估提取质量
                quality_score = self._evaluate_extraction_quality(extracted_term)
                validation_results["extraction_quality"][term] = quality_score
            else:
                validation_results["missing_terms"].append(term)
        
        # 计算总体准确率
        if reference_terms:
            validation_results["overall_accuracy"] = (
                validation_results["successfully_extracted"] / len(reference_terms)
            )
        
        return validation_results
    
    def _evaluate_extraction_quality(self, term_info: Dict[str, str]) -> Dict[str, Any]:
        """
        评估单个术语提取质量
        
        Args:
            term_info: 术语信息
            
        Returns:
            质量评估结果
        """
        quality = {
            "definition_present": bool(term_info.get("术语定义")),
            "document_present": bool(term_info.get("文档出处")),
            "page_present": bool(term_info.get("文档页数")),
            "definition_length": len(term_info.get("术语定义", "")),
            "format_correct": True
        }
        
        # 检查格式是否正确
        if term_info.get("文档页数"):
            if not term_info["文档页数"].startswith("第") or not term_info["文档页数"].endswith("页"):
                quality["format_correct"] = False
        
        # 计算总体质量分数
        quality_score = sum([
            quality["definition_present"],
            quality["document_present"],
            quality["page_present"],
            quality["format_correct"]
        ]) / 4.0
        
        quality["overall_score"] = quality_score
        
        return quality