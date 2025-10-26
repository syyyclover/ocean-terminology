#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF文档解析模块
解析PDF文档，提取文本内容和结构信息
"""

import os
import logging
import pdfplumber
from pathlib import Path
from typing import List, Dict, Any, Optional


class PDFParser:
    """PDF文档解析器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化PDF解析器"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 获取数据目录
        self.data_dir = self.config.get('data_dir', 'data/raw')
        
    def parse_pdf(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """
        解析单个PDF文档
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            解析结果字典
        """
        if not os.path.exists(pdf_path):
            self.logger.error(f"PDF文件不存在: {pdf_path}")
            return None
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                document_info = {
                    'file_path': pdf_path,
                    'file_name': Path(pdf_path).name,
                    'file_stem': Path(pdf_path).stem,
                    'page_count': len(pdf.pages),
                    'pages': [],
                    'full_text': '',
                    'metadata': pdf.metadata or {}
                }
                
                # 逐页解析
                for page_num, page in enumerate(pdf.pages, 1):
                    page_info = self._parse_page(page, page_num)
                    document_info['pages'].append(page_info)
                    
                    # 累积全文
                    document_info['full_text'] += f"\n\n--- 第{page_num}页 ---\n{page_info['text']}"
                
                self.logger.info(f"成功解析PDF: {pdf_path}, 共{document_info['page_count']}页")
                return document_info
                
        except Exception as e:
            self.logger.error(f"解析PDF失败 {pdf_path}: {e}")
            return None
    
    def _parse_page(self, page, page_num: int) -> Dict[str, Any]:
        """
        解析单个页面
        
        Args:
            page: PDF页面对象
            page_num: 页码
            
        Returns:
            页面信息字典
        """
        page_info = {
            'page_number': page_num,
            'text': '',
            'tables': [],
            'images': [],
            'bbox': page.bbox if hasattr(page, 'bbox') else None
        }
        
        try:
            # 提取文本
            text = page.extract_text() or ""
            page_info['text'] = text.strip()
            
            # 提取表格（如果配置需要）
            if self.config.get('pdf_parser', {}).get('extract_tables', False):
                tables = page.extract_tables()
                if tables:
                    page_info['tables'] = tables
            
            # 提取图像信息（如果配置需要）
            if self.config.get('pdf_parser', {}).get('extract_images', False):
                images = page.images
                if images:
                    page_info['images'] = images
                    
        except Exception as e:
            self.logger.warning(f"解析PDF页面 {page_num} 失败: {e}")
            page_info['text'] = ""
        
        return page_info
    
    def parse_all_pdfs(self, pdf_dir: str = None) -> List[Dict[str, Any]]:
        """
        解析目录中的所有PDF文档
        
        Args:
            pdf_dir: PDF目录路径
            
        Returns:
            所有PDF文档的解析结果列表
        """
        if pdf_dir is None:
            pdf_dir = self.data_dir
        
        if not os.path.exists(pdf_dir):
            self.logger.error(f"PDF目录不存在: {pdf_dir}")
            return []
        
        pdf_documents = []
        pdf_files = list(Path(pdf_dir).glob("*.pdf"))
        
        self.logger.info(f"开始解析目录中的PDF文件: {pdf_dir}")
        self.logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        
        for pdf_file in pdf_files:
            document = self.parse_pdf(str(pdf_file))
            if document:
                pdf_documents.append(document)
        
        self.logger.info(f"成功解析 {len(pdf_documents)} 个PDF文档")
        return pdf_documents
    
    def search_text_in_pdfs(self, search_term: str, pdf_documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        在PDF文档中搜索文本
        
        Args:
            search_term: 搜索词
            pdf_documents: PDF文档列表
            
        Returns:
            搜索结果列表
        """
        results = []
        
        for doc in pdf_documents:
            for page in doc['pages']:
                if search_term in page['text']:
                    result = {
                        'document': doc['file_stem'],
                        'page_number': page['page_number'],
                        'text_snippet': self._extract_context(page['text'], search_term),
                        'full_text': page['text']
                    }
                    results.append(result)
        
        return results
    
    def _extract_context(self, text: str, search_term: str, context_length: int = 200) -> str:
        """
        提取搜索词周围的上下文
        
        Args:
            text: 文本
            search_term: 搜索词
            context_length: 上下文长度
            
        Returns:
            上下文片段
        """
        if search_term not in text:
            return ""
        
        index = text.find(search_term)
        if index == -1:
            return ""
        
        start = max(0, index - context_length // 2)
        end = min(len(text), index + len(search_term) + context_length // 2)
        
        context = text[start:end]
        
        # 确保上下文以完整句子开始和结束（如果可能）
        if start > 0:
            # 查找前一个句子结束位置
            sentence_end = max(text.rfind('。', 0, start), 
                             text.rfind('！', 0, start), 
                             text.rfind('？', 0, start))
            if sentence_end != -1:
                context = text[sentence_end + 1:end]
        
        return context.strip()
    
    def get_document_statistics(self, pdf_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取文档统计信息
        
        Args:
            pdf_documents: PDF文档列表
            
        Returns:
            统计信息字典
        """
        total_pages = 0
        total_text_length = 0
        document_types = {}
        
        for doc in pdf_documents:
            total_pages += doc['page_count']
            total_text_length += len(doc.get('full_text', ''))
            
            # 统计文档类型
            file_name = doc['file_name']
            if 'GB_T' in file_name:
                doc_type = '国家标准'
            elif 'HY_T' in file_name:
                doc_type = '行业标准'
            elif 'GB' in file_name:
                doc_type = '国家标准'
            else:
                doc_type = '其他'
            
            document_types[doc_type] = document_types.get(doc_type, 0) + 1
        
        return {
            'total_documents': len(pdf_documents),
            'total_pages': total_pages,
            'total_text_length': total_text_length,
            'document_types': document_types,
            'average_pages_per_document': total_pages / len(pdf_documents) if pdf_documents else 0,
            'average_text_length_per_document': total_text_length / len(pdf_documents) if pdf_documents else 0
        }