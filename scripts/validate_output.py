#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输出验证模块
验证输出格式和内容是否符合要求
"""

import logging
import re
from typing import Dict, Any, List, Tuple

from src.utils import validate_output_format


class OutputValidator:
    """输出验证器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化输出验证器"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
    
    def validate_task1_output(self, task1_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证任务1输出格式
        
        Args:
            task1_results: 任务1结果
            
        Returns:
            验证后的结果
        """
        self.logger.info("开始验证任务1输出格式")
        
        validated_results = {}
        validation_errors = []
        
        for key, value in task1_results.items():
            # 检查键格式
            if not key.startswith("W"):
                validation_errors.append(f"键格式错误: {key}")
                continue
            
            # 检查必需字段
            required_fields = ["术语名称", "术语定义", "文档出处", "文档页数"]
            missing_fields = [field for field in required_fields if field not in value]
            
            if missing_fields:
                validation_errors.append(f"{key} 缺少字段: {missing_fields}")
                continue
            
            # 检查字段内容
            field_errors = self._validate_task1_fields(key, value)
            validation_errors.extend(field_errors)
            
            # 如果通过验证，添加到结果中
            if not field_errors:
                validated_results[key] = value
        
        if validation_errors:
            self.logger.warning(f"任务1验证发现 {len(validation_errors)} 个错误: {validation_errors}")
        else:
            self.logger.info("任务1输出格式验证通过")
        
        return validated_results
    
    def _validate_task1_fields(self, key: str, term_info: Dict[str, str]) -> List[str]:
        """
        验证任务1单个术语的字段
        
        Args:
            key: 术语键
            term_info: 术语信息
            
        Returns:
            错误列表
        """
        errors = []
        
        # 验证术语名称
        term_name = term_info.get("术语名称", "")
        if not term_name or not term_name.strip():
            errors.append(f"{key} 术语名称为空")
        
        # 验证术语定义
        term_definition = term_info.get("术语定义", "")
        if not term_definition or not term_definition.strip():
            errors.append(f"{key} 术语定义为空")
        elif len(term_definition) < 10:
            errors.append(f"{key} 术语定义过短: {term_definition}")
        
        # 验证文档出处
        document_source = term_info.get("文档出处", "")
        if not document_source or not document_source.strip():
            errors.append(f"{key} 文档出处为空")
        elif not self._validate_document_source_format(document_source):
            errors.append(f"{key} 文档出处格式不正确: {document_source}")
        
        # 验证文档页数
        page_info = term_info.get("文档页数", "")
        if not page_info or not page_info.strip():
            errors.append(f"{key} 文档页数为空")
        elif not self._validate_page_format(page_info):
            errors.append(f"{key} 文档页数格式不正确: {page_info}")
        
        return errors
    
    def validate_task2_output(self, task2_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证任务2输出格式
        
        Args:
            task2_results: 任务2结果
            
        Returns:
            验证后的结果
        """
        self.logger.info("开始验证任务2输出格式")
        
        validated_results = {}
        validation_errors = []
        
        for key, value in task2_results.items():
            # 检查键格式
            if not key.startswith("R"):
                validation_errors.append(f"键格式错误: {key}")
                continue
            
            # 检查必需字段
            required_fields = ["术语关联", "关联关系", "关联描述"]
            missing_fields = [field for field in required_fields if field not in value]
            
            if missing_fields:
                validation_errors.append(f"{key} 缺少字段: {missing_fields}")
                continue
            
            # 检查字段内容
            field_errors = self._validate_task2_fields(key, value)
            validation_errors.extend(field_errors)
            
            # 如果通过验证，添加到结果中
            if not field_errors:
                validated_results[key] = value
        
        if validation_errors:
            self.logger.warning(f"任务2验证发现 {len(validation_errors)} 个错误: {validation_errors}")
        else:
            self.logger.info("任务2输出格式验证通过")
        
        return validated_results
    
    def _validate_task2_fields(self, key: str, association_info: Dict[str, Any]) -> List[str]:
        """
        验证任务2单个关联关系的字段
        
        Args:
            key: 关联关系键
            association_info: 关联关系信息
            
        Returns:
            错误列表
        """
        errors = []
        
        # 验证术语关联
        term_association = association_info.get("术语关联", [])
        if not isinstance(term_association, list) or len(term_association) != 2:
            errors.append(f"{key} 术语关联格式不正确: {term_association}")
        else:
            for term in term_association:
                if not term or not isinstance(term, str):
                    errors.append(f"{key} 术语关联包含无效术语: {term}")
        
        # 验证关联关系
        relationship = association_info.get("关联关系", "")
        valid_relationships = ["主从关系", "因果关系"]
        if relationship not in valid_relationships:
            errors.append(f"{key} 关联关系无效: {relationship}")
        
        # 验证关联描述
        association_description = association_info.get("关联描述", [])
        if not isinstance(association_description, list):
            errors.append(f"{key} 关联描述格式不正确")
        else:
            for desc in association_description:
                if not isinstance(desc, dict):
                    errors.append(f"{key} 关联描述项格式不正确")
                else:
                    # 检查描述中的文档出处和页数
                    doc_source = desc.get("文档出处", "")
                    page_info = desc.get("文档页数", "")
                    
                    if not doc_source:
                        errors.append(f"{key} 关联描述中文档出处为空")
                    if not page_info:
                        errors.append(f"{key} 关联描述中文档页数为空")
        
        return errors
    
    def _validate_document_source_format(self, document_source: str) -> bool:
        """
        验证文档出处格式
        
        Args:
            document_source: 文档出处
            
        Returns:
            格式是否正确
        """
        # 检查是否包含.pdf后缀
        if document_source.endswith('.pdf'):
            return False
        
        # 检查是否包含特殊字符
        if re.search(r'[<>:"/\\|?*]', document_source):
            return False
        
        return True
    
    def _validate_page_format(self, page_info: str) -> bool:
        """
        验证页码格式
        
        Args:
            page_info: 页码信息
            
        Returns:
            格式是否正确
        """
        # 检查标准格式: "第X页" 或 "第X-Y页"
        pattern1 = r'^第\d+页$'  # 第3页
        pattern2 = r'^第\d+-\d+页$'  # 第12-13页
        
        return bool(re.match(pattern1, page_info) or re.match(pattern2, page_info))
    
    def generate_validation_report(self, task1_results: Dict[str, Any], 
                                 task2_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成验证报告
        
        Args:
            task1_results: 任务1结果
            task2_results: 任务2结果
            
        Returns:
            验证报告
        """
        report = {
            "task1_validation": self._analyze_task1_results(task1_results),
            "task2_validation": self._analyze_task2_results(task2_results),
            "overall_assessment": {},
            "recommendations": []
        }
        
        # 总体评估
        task1_score = report["task1_validation"]["completeness_score"]
        task2_score = report["task2_validation"]["completeness_score"]
        
        overall_score = (task1_score + task2_score) / 2 if task2_results else task1_score
        
        report["overall_assessment"] = {
            "overall_score": overall_score,
            "status": "通过" if overall_score >= 0.8 else "需要改进",
            "task1_status": "通过" if task1_score >= 0.8 else "需要改进",
            "task2_status": "通过" if task2_score >= 0.8 else "需要改进"
        }
        
        # 生成建议
        if task1_score < 0.8:
            report["recommendations"].append("任务1: 检查术语定义完整性和文档出处格式")
        
        if task2_results and task2_score < 0.8:
            report["recommendations"].append("任务2: 检查关联关系类型和描述完整性")
        
        if not report["recommendations"]:
            report["recommendations"].append("所有任务输出格式正确，可以提交")
        
        return report
    
    def _analyze_task1_results(self, task1_results: Dict[str, Any]) -> Dict[str, Any]:
        """分析任务1结果"""
        analysis = {
            "total_terms": len(task1_results),
            "complete_terms": 0,
            "incomplete_terms": [],
            "completeness_score": 0.0
        }
        
        for key, value in task1_results.items():
            # 检查术语是否完整
            is_complete = all([
                value.get("术语名称"),
                value.get("术语定义"),
                value.get("文档出处"),
                value.get("文档页数")
            ])
            
            if is_complete:
                analysis["complete_terms"] += 1
            else:
                analysis["incomplete_terms"].append(key)
        
        # 计算完整性分数
        if analysis["total_terms"] > 0:
            analysis["completeness_score"] = analysis["complete_terms"] / analysis["total_terms"]
        
        return analysis
    
    def _analyze_task2_results(self, task2_results: Dict[str, Any]) -> Dict[str, Any]:
        """分析任务2结果"""
        if not task2_results:
            return {
                "total_associations": 0,
                "complete_associations": 0,
                "incomplete_associations": [],
                "completeness_score": 0.0
            }
        
        analysis = {
            "total_associations": len(task2_results),
            "complete_associations": 0,
            "incomplete_associations": [],
            "completeness_score": 0.0
        }
        
        for key, value in task2_results.items():
            # 检查关联关系是否完整
            is_complete = all([
                value.get("术语关联") and len(value["术语关联"]) == 2,
                value.get("关联关系") in ["主从关系", "因果关系"],
                value.get("关联描述") and len(value["关联描述"]) > 0
            ])
            
            if is_complete:
                analysis["complete_associations"] += 1
            else:
                analysis["incomplete_associations"].append(key)
        
        # 计算完整性分数
        if analysis["total_associations"] > 0:
            analysis["completeness_score"] = analysis["complete_associations"] / analysis["total_associations"]
        
        return analysis