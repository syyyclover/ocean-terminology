#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NLP模型模块
相似度计算、问答、词向量嵌入等接口
"""

import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class NLPModels:
    """NLP模型管理类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化NLP模型"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化TF-IDF向量化器
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            min_df=1,
            max_df=0.8,
            stop_words=None,  # 中文需要自定义停用词
            ngram_range=(1, 2)
        )
        
        self.is_fitted = False
        self.vocabulary_ = None
        
    def fit_tfidf(self, documents: List[str]) -> None:
        """
        训练TF-IDF模型
        
        Args:
            documents: 文档列表
        """
        if not documents:
            self.logger.warning("没有文档用于训练TF-IDF模型")
            return
        
        try:
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            self.vocabulary_ = self.tfidf_vectorizer.vocabulary_
            self.is_fitted = True
            self.logger.info(f"TF-IDF模型训练完成，词汇表大小: {len(self.vocabulary_)}")
        except Exception as e:
            self.logger.error(f"TF-IDF模型训练失败: {e}")
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度分数 (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # 方法1: 基于TF-IDF的余弦相似度
        if self.is_fitted:
            try:
                vectors = self.tfidf_vectorizer.transform([text1, text2])
                similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
                return float(similarity)
            except Exception as e:
                self.logger.warning(f"TF-IDF相似度计算失败，使用备用方法: {e}")
        
        # 方法2: 基于Jaccard相似度的备用方法
        return self._jaccard_similarity(text1, text2)
    
    def _jaccard_similarity(self, text1: str, text2: str) -> float:
        """
        计算Jaccard相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            Jaccard相似度分数
        """
        # 简单的基于字符的Jaccard相似度
        set1 = set(text1)
        set2 = set(text2)
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def find_similar_documents(self, query: str, documents: List[str], 
                              top_k: int = 5) -> List[Tuple[int, float]]:
        """
        查找与查询最相似的文档
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回前k个结果
            
        Returns:
            相似文档索引和分数列表
        """
        if not query or not documents:
            return []
        
        similarities = []
        for i, doc in enumerate(documents):
            similarity = self.calculate_similarity(query, doc)
            similarities.append((i, similarity))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def extract_key_terms(self, text: str, max_terms: int = 10) -> List[str]:
        """
        从文本中提取关键术语
        
        Args:
            text: 输入文本
            max_terms: 最大术语数量
            
        Returns:
            关键术语列表
        """
        if not text:
            return []
        
        # 简单的基于频率的术语提取
        words = self._tokenize_chinese(text)
        
        # 计算词频
        from collections import Counter
        word_freq = Counter(words)
        
        # 过滤停用词和短词
        stop_words = self._get_chinese_stopwords()
        filtered_terms = [
            word for word, freq in word_freq.most_common()
            if len(word) > 1 and word not in stop_words and freq > 1
        ]
        
        return filtered_terms[:max_terms]
    
    def _tokenize_chinese(self, text: str) -> List[str]:
        """
        中文分词
        
        Args:
            text: 中文文本
            
        Returns:
            分词结果
        """
        # 简单的基于规则的分词
        # 在实际应用中应该使用jieba等分词工具
        import re
        
        # 匹配中文词语（2个或更多中文字符）
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        
        return chinese_words
    
    def _get_chinese_stopwords(self) -> set:
        """获取中文停用词列表"""
        # 基础中文停用词
        stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都',
            '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会',
            '着', '没有', '看', '好', '自己', '这', '那', '他', '她', '它',
            '我们', '你们', '他们', '这个', '那个', '这些', '那些', '什么',
            '怎么', '为什么', '因为', '所以', '但是', '然后', '如果', '可以',
            '应该', '可能', '已经', '还是', '或者', '而且', '虽然', '尽管',
            '为了', '关于', '对于', '通过', '根据', '按照', '由于', '因此'
        }
        
        return stopwords
    
    def analyze_relationship(self, term1: str, term2: str, context: str) -> Tuple[str, float]:
        """
        分析两个术语之间的关系
        
        Args:
            term1: 术语1
            term2: 术语2
            context: 上下文文本
            
        Returns:
            关系类型和置信度
        """
        if not term1 or not term2 or not context:
            return "未知关系", 0.0
        
        # 关系关键词模式
        hierarchical_keywords = [
            '包括', '包含', '分为', '分类', '类别', '类型', '层次', '级别',
            '子类', '父类', '上位', '下位', '属于', '隶属于'
        ]
        
        causal_keywords = [
            '导致', '引起', '造成', '产生', '引发', '因为', '所以', '因此',
            '由于', '致使', '使得', '造成', '影响', '作用', '关系'
        ]
        
        # 检查层次关系
        hierarchical_score = 0
        for keyword in hierarchical_keywords:
            if keyword in context:
                hierarchical_score += 1
        
        # 检查因果关系
        causal_score = 0
        for keyword in causal_keywords:
            if keyword in context:
                causal_score += 1
        
        # 确定关系类型
        if hierarchical_score > causal_score and hierarchical_score > 0:
            return "主从关系", hierarchical_score / len(hierarchical_keywords)
        elif causal_score > hierarchical_score and causal_score > 0:
            return "因果关系", causal_score / len(causal_keywords)
        else:
            return "未知关系", 0.0


class QASystem:
    """简单的问答系统"""
    
    def __init__(self, nlp_models: NLPModels):
        """初始化问答系统"""
        self.nlp_models = nlp_models
        self.logger = logging.getLogger(__name__)
    
    def find_answer(self, question: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        在文档中查找问题的答案
        
        Args:
            question: 问题
            documents: 文档列表
            
        Returns:
            答案信息
        """
        if not question or not documents:
            return {"answer": "", "confidence": 0.0, "source": ""}
        
        # 提取文档文本
        doc_texts = [doc.get('text', '') for doc in documents]
        
        # 查找最相关的文档
        similar_docs = self.nlp_models.find_similar_documents(question, doc_texts, top_k=3)
        
        if not similar_docs:
            return {"answer": "", "confidence": 0.0, "source": ""}
        
        # 返回最相关的文档信息
        best_doc_idx, confidence = similar_docs[0]
        best_doc = documents[best_doc_idx]
        
        return {
            "answer": best_doc.get('text', '')[:200],  # 截取前200字符
            "confidence": confidence,
            "source": best_doc.get('source', '')
        }