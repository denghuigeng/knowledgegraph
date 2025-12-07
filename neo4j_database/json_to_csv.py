#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 standard.json 转换为 Neo4j 节点 CSV 和关系 CSV
"""

import json
import csv
import os
from collections import defaultdict
from typing import Dict, List, Set, Any
import hashlib


def normalize_string(s: str) -> str:
    """规范化字符串，用于生成唯一ID"""
    if not s:
        return ""
    return s.strip()


def generate_node_id(node_type: str, name: str) -> str:
    """生成节点唯一ID"""
    normalized_name = normalize_string(name)
    # 使用类型和名称生成唯一ID
    unique_str = f"{node_type}:{normalized_name}"
    # 使用哈希确保ID唯一且固定长度
    return hashlib.md5(unique_str.encode('utf-8')).hexdigest()[:16]


def extract_nodes_and_relations(data: List[Dict]) -> tuple:
    """从 JSON 数据中提取所有节点和关系"""
    nodes = {
        'Paper': [],
        'Task': [],
        'ImagingModality': [],
        'AnatomicalStructure': [],
        'Method': [],
        'Dataset': [],
        'Metric': [],
        'Innovation': []
    }
    
    relations = []
    node_set = defaultdict(set)  # 用于去重
    node_name_to_id = {}  # 节点名称到ID的映射
    
    for paper in data:
        paper_id = paper.get('paper_id', '')
        
        # 1. 创建 Paper 节点
        if paper_id:
            paper_node = {
                'id': paper_id,
                'paper_id': paper_id,
                'title': paper.get('title', ''),
                'doi': paper.get('doi', ''),
                'year': paper.get('year', ''),
                'category': paper.get('category', ''),
                'authors': '|'.join(paper.get('authors', [])),
                'embedding': ''  # 稍后填充
            }
            if paper_id not in node_set['Paper']:
                nodes['Paper'].append(paper_node)
                node_set['Paper'].add(paper_id)
        
        # 2. 提取 Task 节点
        for task in paper.get('tasks', []):
            task_normalized = normalize_string(task)
            if task_normalized and task_normalized not in node_set['Task']:
                task_id = generate_node_id('Task', task_normalized)
                nodes['Task'].append({
                    'id': task_id,
                    'name': task_normalized,
                    'type': 'Task',
                    'embedding': ''
                })
                node_set['Task'].add(task_normalized)
                node_name_to_id[f'Task:{task_normalized}'] = task_id
        
        # 3. 提取 ImagingModality 节点
        for modality in paper.get('imaging_modalities', []):
            modality_normalized = normalize_string(modality)
            if modality_normalized and modality_normalized not in node_set['ImagingModality']:
                modality_id = generate_node_id('ImagingModality', modality_normalized)
                nodes['ImagingModality'].append({
                    'id': modality_id,
                    'name': modality_normalized,
                    'type': 'ImagingModality',
                    'embedding': ''
                })
                node_set['ImagingModality'].add(modality_normalized)
                node_name_to_id[f'ImagingModality:{modality_normalized}'] = modality_id
        
        # 4. 提取 AnatomicalStructure 节点
        for structure in paper.get('anatomical_structures', []):
            structure_normalized = normalize_string(structure)
            if structure_normalized and structure_normalized not in node_set['AnatomicalStructure']:
                structure_id = generate_node_id('AnatomicalStructure', structure_normalized)
                nodes['AnatomicalStructure'].append({
                    'id': structure_id,
                    'name': structure_normalized,
                    'type': 'AnatomicalStructure',
                    'embedding': ''
                })
                node_set['AnatomicalStructure'].add(structure_normalized)
                node_name_to_id[f'AnatomicalStructure:{structure_normalized}'] = structure_id
        
        # 5. 提取 Method 节点
        for method in paper.get('methods', []):
            method_name = normalize_string(method.get('name', ''))
            if method_name and method_name not in node_set['Method']:
                method_id = generate_node_id('Method', method_name)
                nodes['Method'].append({
                    'id': method_id,
                    'name': method_name,
                    'method_type': method.get('type', ''),
                    'type': 'Method',
                    'embedding': ''
                })
                node_set['Method'].add(method_name)
                node_name_to_id[f'Method:{method_name}'] = method_id
        
        # 6. 提取 Dataset 节点
        for dataset in paper.get('datasets', []):
            dataset_normalized = normalize_string(dataset)
            if dataset_normalized and dataset_normalized not in node_set['Dataset']:
                dataset_id = generate_node_id('Dataset', dataset_normalized)
                nodes['Dataset'].append({
                    'id': dataset_id,
                    'name': dataset_normalized,
                    'type': 'Dataset',
                    'embedding': ''
                })
                node_set['Dataset'].add(dataset_normalized)
                node_name_to_id[f'Dataset:{dataset_normalized}'] = dataset_id
        
        # 7. 提取 Metric 节点
        for metric in paper.get('metrics', []):
            metric_name = normalize_string(metric.get('name', ''))
            if metric_name:
                metric_key = f"{metric_name}"  # 使用名称作为唯一键
                if metric_key not in node_set['Metric']:
                    metric_id = generate_node_id('Metric', metric_name)
                    nodes['Metric'].append({
                        'id': metric_id,
                        'name': metric_name,
                        'type': 'Metric',
                        'embedding': ''
                    })
                    node_set['Metric'].add(metric_key)
                    node_name_to_id[f'Metric:{metric_name}'] = metric_id
        
        # 8. 提取 Innovation 节点
        for innovation in paper.get('innovations', []):
            innovation_desc = normalize_string(innovation.get('description', ''))
            if innovation_desc:
                innovation_key = innovation_desc  # 使用描述作为唯一键
                if innovation_key not in node_set['Innovation']:
                    innovation_id = generate_node_id('Innovation', innovation_desc)
                    nodes['Innovation'].append({
                        'id': innovation_id,
                        'description': innovation_desc,
                        'innovation_type': innovation.get('type', ''),
                        'type': 'Innovation',
                        'embedding': ''
                    })
                    node_set['Innovation'].add(innovation_key)
                    node_name_to_id[f'Innovation:{innovation_desc}'] = innovation_id
        
        # 9. 提取关系
        for relation in paper.get('relations', []):
            rel_type = relation.get('type', '')
            from_entity = relation.get('from', '')
            to_entity = relation.get('to', '')
            value = relation.get('value', '')
            note = relation.get('note', '')
            
            if not rel_type or not from_entity or not to_entity:
                continue
            
            # 确定 from 和 to 的节点ID
            from_id = None
            to_id = None
            
            # 处理 from 节点
            if from_entity == paper_id:
                from_id = paper_id
            else:
                # 尝试匹配各种节点类型
                from_normalized = normalize_string(from_entity)
                for node_type in ['Task', 'ImagingModality', 'AnatomicalStructure', 
                                 'Method', 'Dataset', 'Metric', 'Innovation']:
                    key = f'{node_type}:{from_normalized}'
                    if key in node_name_to_id:
                        from_id = node_name_to_id[key]
                        break
            
            # 处理 to 节点
            to_normalized = normalize_string(to_entity)
            for node_type in ['Task', 'ImagingModality', 'AnatomicalStructure', 
                             'Method', 'Dataset', 'Metric', 'Innovation']:
                key = f'{node_type}:{to_normalized}'
                if key in node_name_to_id:
                    to_id = node_name_to_id[key]
                    break
            
            if from_id and to_id:
                rel_row = {
                    'from_id': from_id,
                    'to_id': to_id,
                    'type': rel_type,
                    'value': value if value else '',
                    'note': note if note else ''
                }
                relations.append(rel_row)
    
    return nodes, relations


def write_nodes_csv(nodes: Dict[str, List[Dict]], output_dir: str):
    """将节点写入 CSV 文件"""
    for node_type, node_list in nodes.items():
        if not node_list:
            continue
        
        filename = os.path.join(output_dir, f'nodes_{node_type}.csv')
        fieldnames = list(node_list[0].keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(node_list)
        
        print(f"✓ 已生成节点文件: {filename} ({len(node_list)} 个节点)")


def write_relations_csv(relations: List[Dict], output_dir: str):
    """将关系写入 CSV 文件"""
    if not relations:
        print("⚠ 没有关系数据")
        return
    
    filename = os.path.join(output_dir, 'relations.csv')
    fieldnames = ['from_id', 'to_id', 'type', 'value', 'note']
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(relations)
    
    print(f"✓ 已生成关系文件: {filename} ({len(relations)} 条关系)")


def main():
    """主函数"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    input_file = os.path.join(project_root, 'standard.json')
    output_dir = os.path.join(script_dir, 'csv')
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📖 读取文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 处理 {len(data)} 篇论文...")
    nodes, relations = extract_nodes_and_relations(data)
    
    print(f"\n📝 生成 CSV 文件...")
    write_nodes_csv(nodes, output_dir)
    write_relations_csv(relations, output_dir)
    
    # 统计信息
    total_nodes = sum(len(v) for v in nodes.values())
    print(f"\n✅ 转换完成!")
    print(f"   总节点数: {total_nodes}")
    print(f"   总关系数: {len(relations)}")
    print(f"   节点类型分布:")
    for node_type, node_list in nodes.items():
        print(f"     - {node_type}: {len(node_list)}")


if __name__ == '__main__':
    main()

