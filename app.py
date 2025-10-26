#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海洋防灾减灾知识库术语识别系统
统一入口程序 - 接收参数并执行术语识别和关联分析
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils import load_config, setup_logging
from scripts.parse_pdfs import PDFParser
from scripts.extract_terms import TermExtractor
from scripts.associate_terms import TermAssociator
from scripts.validate_output import OutputValidator


class OceanTerminologySystem:
    """海洋防灾减灾知识库术语识别系统"""
    
    def __init__(self, config_path: str = None):
        """初始化系统"""
        self.config = load_config(config_path)
        self.logger = setup_logging()
        
        # 初始化组件
        self.pdf_parser = PDFParser(self.config)
        self.term_extractor = TermExtractor(self.config)
        self.term_associator = TermAssociator(self.config)
        self.validator = OutputValidator(self.config)
        
    def run_task1(self, task_json_path: str) -> Dict[str, Any]:
        """
        执行基础任务1：术语识别
        
        Args:
            task_json_path: 任务JSON文件路径
            
        Returns:
            术语识别结果
        """
        self.logger.info(f"开始执行基础任务1：术语识别")
        
        # 加载任务术语列表
        with open(task_json_path, 'r', encoding='utf-8') as f:
            terms_list = json.load(f)
        
        self.logger.info(f"需要识别的术语数量: {len(terms_list)}")
        
        # 解析PDF文档
        pdf_documents = self.pdf_parser.parse_all_pdfs()
        
        # 提取术语信息
        term_results = self.term_extractor.extract_terms(terms_list, pdf_documents)
        
        # 验证输出
        validated_results = self.validator.validate_task1_output(term_results)
        
        self.logger.info(f"基础任务1完成，成功识别 {len(validated_results)} 个术语")
        
        return validated_results
    
    def run_task2(self, task_json_path: str) -> Dict[str, Any]:
        """
        执行进阶任务2：术语关联关系
        
        Args:
            task_json_path: 任务JSON文件路径
            
        Returns:
            术语关联关系结果
        """
        self.logger.info(f"开始执行进阶任务2：术语关联关系")
        
        # 加载任务术语列表
        with open(task_json_path, 'r', encoding='utf-8') as f:
            terms_list = json.load(f)
        
        self.logger.info(f"需要分析关联关系的术语数量: {len(terms_list)}")
        
        # 解析PDF文档
        pdf_documents = self.pdf_parser.parse_all_pdfs()
        
        # 分析术语关联关系
        association_results = self.term_associator.analyze_associations(terms_list, pdf_documents)
        
        # 验证输出
        validated_results = self.validator.validate_task2_output(association_results)
        
        self.logger.info(f"进阶任务2完成，识别出 {len(validated_results)} 组关联关系")
        
        return validated_results
    
    def run_pipeline(self, task_json_path: str, output_dir: str = None):
        """
        运行完整管道：任务1 + 任务2
        
        Args:
            task_json_path: 任务JSON文件路径
            output_dir: 输出目录
        """
        if output_dir is None:
            output_dir = self.config.get('output_dir', 'output')
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 执行任务1
        task1_results = self.run_task1(task_json_path)
        
        # 保存任务1结果
        task1_output_path = Path(output_dir) / "task1_results.json"
        with open(task1_output_path, 'w', encoding='utf-8') as f:
            json.dump(task1_results, f, ensure_ascii=False, indent=2)
        
        # 执行任务2
        task2_results = self.run_task2(task_json_path)
        
        # 保存任务2结果
        task2_output_path = Path(output_dir) / "task2_results.json"
        with open(task2_output_path, 'w', encoding='utf-8') as f:
            json.dump(task2_results, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"完整管道执行完成，结果已保存到: {output_dir}")
        
        return {
            "task1": task1_results,
            "task2": task2_results
        }


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='海洋防灾减灾知识库术语识别系统')
    parser.add_argument('task_json', help='任务JSON文件路径')
    parser.add_argument('--task', choices=['1', '2', 'all'], default='all', 
                       help='执行任务: 1(术语识别), 2(术语关联), all(全部)')
    parser.add_argument('--output', help='输出目录')
    parser.add_argument('--config', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 初始化系统
    system = OceanTerminologySystem(args.config)
    
    try:
        if args.task == '1':
            results = system.run_task1(args.task_json)
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif args.task == '2':
            results = system.run_task2(args.task_json)
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            results = system.run_pipeline(args.task_json, args.output)
            print("完整管道执行完成")
            
    except Exception as e:
        print(f"执行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()