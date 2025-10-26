#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抽取规则集合
术语识别、关联关系分析等规则定义
"""

import re
from typing import List, Dict, Any, Tuple, Optional


class ExtractionRules:
    """术语抽取规则类"""
    
    def __init__(self):
        """初始化抽取规则"""
        # 术语定义模式
        self.definition_patterns = [
            # 标准定义模式
            r'(?P<term>[^，。！？：；\s]+)\s*[：:]\s*(?P<definition>[^。！？]+[。！？])',
            
            # "是指"模式
            r'(?P<term>[^，。！？：；\s]+)\s*是指\s*(?P<definition>[^。！？]+[。！？])',
            
            # "定义为"模式
            r'(?P<term>[^，。！？：；\s]+)\s*定义为\s*(?P<definition>[^。！？]+[。！？])',
            
            # "为"模式
            r'(?P<term>[^，。！？：；\s]+)\s*为\s*(?P<definition>[^。！？]+[。！？])',
            
            # "即"模式
            r'(?P<term>[^，。！？：；\s]+)\s*即\s*(?P<definition>[^。！？]+[。！？])',
            
            # "指的是"模式
            r'(?P<term>[^，。！？：；\s]+)\s*指的是\s*(?P<definition>[^。！？]+[。！？])',
            
            # "表示"模式
            r'(?P<term>[^，。！？：；\s]+)\s*表示\s*(?P<definition>[^。！？]+[。！？])'
        ]
        
        # 章节标题模式
        self.section_patterns = [
            r'^\s*[一二三四五六七八九十]+[、.]\s*',
            r'^\s*\d+[、.]\s*',
            r'^\s*[（(]\d+[）)]\s*',
            r'^\s*第[一二三四五六七八九十\d]+[章节条款项]\s*'
        ]
        
        # 页码模式
        self.page_patterns = [
            r'(?:第)?(\d+)(?:[-~](\d+))?(?:页)?',
            r'page\s*(\d+)(?:[-~](\d+))?',
            r'p\.?\s*(\d+)(?:[-~](\d+))?'
        ]
        
        # 海洋领域特定术语模式
        self.ocean_term_patterns = [
            r'海洋[^，。！？：；\s]*',
            r'[^，。！？：；\s]*灾害',
            r'[^，。！？：；\s]*观测',
            r'[^，。！？：；\s]*预警',
            r'[^，。！？：；\s]*浮标',
            r'[^，。！？：；\s]*潜标',
            r'[^，。！？：；\s]*雷达',
            r'[^，。！？：；\s]*卫星',
            r'[^，。！？：；\s]*数据',
            r'[^，。！？：；\s]*质量',
            r'[^，。！？：；\s]*标准',
            r'[^，。！？：；\s]*规范',
            r'[^，。！？：；\s]*技术',
            r'[^，。！？：；\s]*方法'
        ]
    
    def extract_term_definitions(self, text: str) -> List[Dict[str, str]]:
        """
        从文本中提取术语定义
        
        Args:
            text: 输入文本
            
        Returns:
            术语定义列表
        """
        definitions = []
        
        for pattern in self.definition_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                term = match.group('term').strip()
                definition = match.group('definition').strip()
                
                # 过滤太短或太长的术语
                if 2 <= len(term) <= 50 and 10 <= len(definition) <= 500:
                    definitions.append({
                        'term': term,
                        'definition': definition,
                        'pattern': pattern
                    })
        
        return definitions
    
    def is_ocean_related_term(self, term: str) -> bool:
        """
        判断术语是否与海洋领域相关
        
        Args:
            term: 术语
            
        Returns:
            是否相关
        """
        if not term:
            return False
        
        # 检查是否匹配海洋领域术语模式
        for pattern in self.ocean_term_patterns:
            if re.search(pattern, term):
                return True
        
        # 检查是否包含海洋相关关键词
        ocean_keywords = [
            '海洋', '海', '潮', '浪', '波', '流', '风', '气', '水', '冰',
            '灾害', '防灾', '减灾', '观测', '监测', '预警', '预报',
            '浮标', '潜标', '雷达', '卫星', '数据', '质量', '标准'
        ]
        
        for keyword in ocean_keywords:
            if keyword in term:
                return True
        
        return False
    
    def extract_page_info(self, text: str) -> Optional[str]:
        """
        从文本中提取页码信息
        
        Args:
            text: 输入文本
            
        Returns:
            页码信息
        """
        for pattern in self.page_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start_page = match.group(1)
                end_page = match.group(2) if match.group(2) else None
                
                if end_page:
                    return f"第{start_page}-{end_page}页"
                else:
                    return f"第{start_page}页"
        
        return None


class AssociationRules:
    """关联关系分析规则类"""
    
    def __init__(self):
        """初始化关联规则"""
        # 主从关系关键词
        self.hierarchical_keywords = {
            '包含': ['包括', '包含', '涵盖', '由...组成'],
            '分类': ['分为', '分类', '类别', '类型', '层次', '级别'],
            '从属': ['属于', '隶属于', '归入', '纳入'],
            '组成': ['组成', '构成', '形成'],
            '子类': ['子类', '亚类', '下级', '下位']
        }
        
        # 因果关系关键词
        self.causal_keywords = {
            '导致': ['导致', '引起', '造成', '产生', '引发'],
            '因为': ['因为', '由于', '鉴于', '基于'],
            '所以': ['所以', '因此', '因而', '故而', '于是'],
            '影响': ['影响', '作用', '效应', '效果'],
            '关联': ['关联', '关系', '联系', '相关']
        }
        
        # 关联关系模式
        self.association_patterns = [
            # A导致B
            r'(?P<term1>[^，。！？：；\s]+)\s*(?:导致|引起|造成)\s*(?P<term2>[^，。！？：；\s]+)',
            
            # A包含B
            r'(?P<term1>[^，。！？：；\s]+)\s*(?:包括|包含)\s*(?P<term2>[^，。！？：；\s]+)',
            
            # A属于B
            r'(?P<term1>[^，。！？：；\s]+)\s*(?:属于|隶属于)\s*(?P<term2>[^，。！？：；\s]+)',
            
            # A分为B
            r'(?P<term1>[^，。！？：；\s]+)\s*(?:分为|分类为)\s*(?P<term2>[^，。！？：；\s]+)',
            
            # A与B的关系
            r'(?P<term1>[^，。！？：；\s]+)\s*(?:与|和)\s*(?P<term2>[^，。！？：；\s]+)\s*(?:的)?关系'
        ]
    
    def analyze_relationship(self, term1: str, term2: str, context: str) -> Tuple[str, float, str]:
        """
        分析两个术语之间的关系
        
        Args:
            term1: 术语1
            term2: 术语2
            context: 上下文文本
            
        Returns:
            关系类型、置信度、描述
        """
        if not term1 or not term2 or not context:
            return "未知关系", 0.0, ""
        
        # 检查主从关系
        hierarchical_score, hierarchical_desc = self._check_hierarchical_relationship(
            term1, term2, context
        )
        
        # 检查因果关系
        causal_score, causal_desc = self._check_causal_relationship(
            term1, term2, context
        )
        
        # 确定关系类型
        if hierarchical_score > causal_score and hierarchical_score > 0.5:
            return "主从关系", hierarchical_score, hierarchical_desc
        elif causal_score > hierarchical_score and causal_score > 0.5:
            return "因果关系", causal_score, causal_desc
        else:
            return "未知关系", max(hierarchical_score, causal_score), ""
    
    def _check_hierarchical_relationship(self, term1: str, term2: str, context: str) -> Tuple[float, str]:
        """检查主从关系"""
        score = 0.0
        description = ""
        
        # 检查包含关系
        if any(keyword in context for keyword in self.hierarchical_keywords['包含']):
            score += 0.3
            description = f"{term1}包含{term2}"
        
        # 检查分类关系
        if any(keyword in context for keyword in self.hierarchical_keywords['分类']):
            score += 0.3
            description = f"{term1}分为{term2}"
        
        # 检查从属关系
        if any(keyword in context for keyword in self.hierarchical_keywords['从属']):
            score += 0.2
            description = f"{term2}属于{term1}"
        
        # 检查模式匹配
        for pattern in self.association_patterns:
            matches = re.finditer(pattern, context)
            for match in matches:
                found_term1 = match.group('term1')
                found_term2 = match.group('term2')
                
                if (term1 in found_term1 and term2 in found_term2) or \
                   (term2 in found_term1 and term1 in found_term2):
                    score += 0.2
        
        return min(score, 1.0), description
    
    def _check_causal_relationship(self, term1: str, term2: str, context: str) -> Tuple[float, str]:
        """检查因果关系"""
        score = 0.0
        description = ""
        
        # 检查导致关系
        if any(keyword in context for keyword in self.causal_keywords['导致']):
            score += 0.4
            description = f"{term1}导致{term2}"
        
        # 检查因为关系
        if any(keyword in context for keyword in self.causal_keywords['因为']):
            score += 0.3
            description = f"因为{term1}所以{term2}"
        
        # 检查影响关系
        if any(keyword in context for keyword in self.causal_keywords['影响']):
            score += 0.2
            description = f"{term1}影响{term2}"
        
        # 检查模式匹配
        for pattern in self.association_patterns:
            matches = re.finditer(pattern, context)
            for match in matches:
                found_term1 = match.group('term1')
                found_term2 = match.group('term2')
                
                if (term1 in found_term1 and term2 in found_term2) or \
                   (term2 in found_term1 and term1 in found_term2):
                    score += 0.1
        
        return min(score, 1.0), description
    
    def extract_association_context(self, text: str, term1: str, term2: str) -> List[str]:
        """
        提取包含两个术语的上下文片段
        
        Args:
            text: 输入文本
            term1: 术语1
            term2: 术语2
            
        Returns:
            上下文片段列表
        """
        contexts = []
        
        # 查找同时包含两个术语的句子
        sentences = re.split(r'[。！？]', text)
        
        for sentence in sentences:
            if term1 in sentence and term2 in sentence:
                # 提取包含两个术语的上下文（前后各2个句子）
                sentence_index = sentences.index(sentence)
                start_idx = max(0, sentence_index - 2)
                end_idx = min(len(sentences), sentence_index + 3)
                
                context = ''.join(sentences[start_idx:end_idx])
                contexts.append(context.strip())
        
        return contexts