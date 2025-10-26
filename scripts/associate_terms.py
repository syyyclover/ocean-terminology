#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
术语关联关系分析模块
分析术语之间的关联关系（主从关系、因果关系）
"""

import logging
import itertools
from typing import List, Dict, Any, Tuple, Optional

from src.utils import standardize_document_name, format_page_number
from src.rules import AssociationRules


class TermAssociator:
    """术语关联分析器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化术语关联分析器"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.rules = AssociationRules()
        
        # 获取配置参数
        self.min_confidence = self.config.get('association_analysis', {}).get('min_confidence', 0.7)
        self.relationship_types = self.config.get('association_analysis', {}).get('relationship_types', 
                                                                                 ["主从关系", "因果关系"])
    
    def analyze_associations(self, terms: List[str], pdf_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析术语之间的关联关系
        
        Args:
            terms: 术语列表
            pdf_documents: PDF文档列表
            
        Returns:
            关联关系分析结果
        """
        self.logger.info(f"开始分析 {len(terms)} 个术语之间的关联关系")
        
        results = {}
        association_count = 0
        
        # 生成所有可能的术语对
        term_pairs = list(itertools.combinations(terms, 2))
        
        self.logger.info(f"需要分析 {len(term_pairs)} 个术语对")
        
        for term1, term2 in term_pairs:
            association_result = self._analyze_term_pair_association(term1, term2, pdf_documents)
            
            if association_result and association_result["关联关系"] != "未知关系":
                association_count += 1
                result_key = f"R{association_count:02d}"
                results[result_key] = association_result
                
                self.logger.info(f"发现关联关系 {result_key}: {term1} - {term2} - {association_result['关联关系']}")
        
        self.logger.info(f"关联关系分析完成，发现 {association_count} 组关联关系")
        return results
    
    def _analyze_term_pair_association(self, term1: str, term2: str, 
                                      pdf_documents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        分析术语对的关联关系
        
        Args:
            term1: 术语1
            term2: 术语2
            pdf_documents: PDF文档列表
            
        Returns:
            关联关系信息
        """
        best_association = None
        best_confidence = 0.0
        
        for doc in pdf_documents:
            for page in doc['pages']:
                page_text = page['text']
                
                # 检查两个术语是否同时出现在页面中
                if term1 not in page_text or term2 not in page_text:
                    continue
                
                # 提取包含两个术语的上下文
                contexts = self.rules.extract_association_context(page_text, term1, term2)
                
                for context in contexts:
                    # 分析关联关系
                    relationship_type, confidence, description = self.rules.analyze_relationship(
                        term1, term2, context
                    )
                    
                    if confidence > best_confidence and confidence >= self.min_confidence:
                        best_confidence = confidence
                        best_association = {
                            "术语关联": [term1, term2],
                            "关联关系": relationship_type,
                            "关联描述": [{
                                "文档出处": standardize_document_name(doc['file_name']),
                                "文档页数": format_page_number(f"第{page['page_number']}页")
                            }],
                            "置信度": confidence,
                            "上下文": context[:500]  # 截取前500字符
                        }
        
        return best_association
    
    def find_direct_associations(self, term: str, pdf_documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        查找与指定术语直接关联的其他术语
        
        Args:
            term: 目标术语
            pdf_documents: PDF文档列表
            
        Returns:
            直接关联术语列表
        """
        associations = []
        
        for doc in pdf_documents:
            for page in doc['pages']:
                page_text = page['text']
                
                if term not in page_text:
                    continue
                
                # 查找与目标术语出现在同一句子中的其他术语
                sentences = page_text.split('。')
                
                for sentence in sentences:
                    if term in sentence:
                        # 提取句子中的其他潜在术语
                        potential_terms = self._extract_potential_terms(sentence, exclude_term=term)
                        
                        for other_term in potential_terms:
                            # 分析关联关系
                            relationship_type, confidence, description = self.rules.analyze_relationship(
                                term, other_term, sentence
                            )
                            
                            if confidence >= self.min_confidence:
                                association = {
                                    "关联术语": other_term,
                                    "关联关系": relationship_type,
                                    "置信度": confidence,
                                    "上下文": sentence,
                                    "文档出处": standardize_document_name(doc['file_name']),
                                    "文档页数": format_page_number(f"第{page['page_number']}页")
                                }
                                associations.append(association)
        
        # 去重和排序
        unique_associations = {}
        for assoc in associations:
            key = (assoc["关联术语"], assoc["关联关系"])
            if key not in unique_associations or assoc["置信度"] > unique_associations[key]["置信度"]:
                unique_associations[key] = assoc
        
        sorted_associations = sorted(
            unique_associations.values(), 
            key=lambda x: x["置信度"], 
            reverse=True
        )
        
        return sorted_associations
    
    def _extract_potential_terms(self, text: str, exclude_term: str = None) -> List[str]:
        """
        从文本中提取潜在术语
        
        Args:
            text: 输入文本
            exclude_term: 要排除的术语
            
        Returns:
            潜在术语列表
        """
        # 简单的基于规则的术语提取
        import re
        
        # 匹配可能的中文术语（2-10个中文字符）
        potential_terms = re.findall(r'[\u4e00-\u9fff]{2,10}', text)
        
        # 过滤
        filtered_terms = []
        for term in potential_terms:
            # 排除常见虚词和短词
            if len(term) < 2:
                continue
            
            # 排除排除术语
            if exclude_term and term == exclude_term:
                continue
            
            # 排除常见虚词
            common_particles = {'的', '了', '在', '是', '有', '和', '就', '不', '人', '都'}
            if term in common_particles:
                continue
            
            filtered_terms.append(term)
        
        return list(set(filtered_terms))
    
    def build_association_network(self, terms: List[str], pdf_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        构建术语关联网络
        
        Args:
            terms: 术语列表
            pdf_documents: PDF文档列表
            
        Returns:
            关联网络数据
        """
        network = {
            "nodes": [],
            "links": [],
            "communities": {}
        }
        
        # 添加节点
        for term in terms:
            network["nodes"].append({
                "id": term,
                "name": term,
                "group": 1  # 默认分组
            })
        
        # 分析关联关系并添加链接
        associations = self.analyze_associations(terms, pdf_documents)
        
        for assoc_id, assoc_info in associations.items():
            term1, term2 = assoc_info["术语关联"]
            relationship = assoc_info["关联关系"]
            confidence = assoc_info["置信度"]
            
            # 确定链接类型
            if relationship == "主从关系":
                link_type = "hierarchical"
            elif relationship == "因果关系":
                link_type = "causal"
            else:
                link_type = "other"
            
            network["links"].append({
                "source": term1,
                "target": term2,
                "type": link_type,
                "relationship": relationship,
                "confidence": confidence
            })
        
        # 简单的社区检测（基于连接度）
        self._detect_communities(network)
        
        return network
    
    def _detect_communities(self, network: Dict[str, Any]) -> None:
        """
        检测关联网络中的社区
        
        Args:
            network: 关联网络数据
        """
        # 简单的基于连接度的社区检测
        node_degrees = {}
        
        for node in network["nodes"]:
            node_id = node["id"]
            degree = sum(1 for link in network["links"] 
                        if link["source"] == node_id or link["target"] == node_id)
            node_degrees[node_id] = degree
        
        # 根据连接度分组
        high_degree_nodes = [node_id for node_id, degree in node_degrees.items() if degree >= 3]
        medium_degree_nodes = [node_id for node_id, degree in node_degrees.items() if 1 <= degree < 3]
        low_degree_nodes = [node_id for node_id, degree in node_degrees.items() if degree == 0]
        
        # 更新节点分组
        for node in network["nodes"]:
            if node["id"] in high_degree_nodes:
                node["group"] = 1  # 核心节点
            elif node["id"] in medium_degree_nodes:
                node["group"] = 2  # 中等连接节点
            else:
                node["group"] = 3  # 孤立节点
        
        network["communities"] = {
            "core_nodes": high_degree_nodes,
            "medium_nodes": medium_degree_nodes,
            "isolated_nodes": low_degree_nodes
        }