#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图谱质量检查脚本
- 检查重复节点
- 检查孤立节点
- 检查关系完整性
"""

import os
import csv
from collections import defaultdict, Counter
from typing import Dict, List, Set


def check_duplicate_nodes(csv_dir: str) -> Dict[str, List]:
    """检查重复节点"""
    print("=" * 60)
    print("🔍 检查重复节点...")
    print("=" * 60)
    
    node_types = ['Paper', 'Task', 'ImagingModality', 'AnatomicalStructure',
                 'Method', 'Dataset', 'Metric', 'Innovation']
    
    duplicates = {}
    
    for node_type in node_types:
        csv_file = os.path.join(csv_dir, f'nodes_{node_type}.csv')
        
        if not os.path.exists(csv_file):
            continue
        
        # 读取节点
        nodes = []
        name_to_ids = defaultdict(list)
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                nodes.append(row)
                
                # 根据节点类型选择唯一标识字段
                if node_type == 'Paper':
                    key = row.get('paper_id', '')
                elif node_type == 'Task':
                    key = row.get('name', '')
                elif node_type == 'ImagingModality':
                    key = row.get('name', '')
                elif node_type == 'AnatomicalStructure':
                    key = row.get('name', '')
                elif node_type == 'Method':
                    key = row.get('name', '')
                elif node_type == 'Dataset':
                    key = row.get('name', '')
                elif node_type == 'Metric':
                    key = row.get('name', '')
                elif node_type == 'Innovation':
                    key = row.get('description', '')
                else:
                    key = row.get('id', '')
                
                if key:
                    name_to_ids[key].append(row.get('id', ''))
        
        # 查找重复
        node_duplicates = []
        for name, ids in name_to_ids.items():
            if len(ids) > 1:
                node_duplicates.append({
                    'name': name,
                    'ids': ids,
                    'count': len(ids)
                })
        
        if node_duplicates:
            duplicates[node_type] = node_duplicates
            print(f"\n❌ {node_type}: 发现 {len(node_duplicates)} 个重复节点")
            for dup in node_duplicates[:10]:  # 只显示前10个
                print(f"   - '{dup['name']}': {dup['count']} 个重复 (IDs: {dup['ids'][:3]}...)")
            if len(node_duplicates) > 10:
                print(f"   ... 还有 {len(node_duplicates) - 10} 个重复节点")
        else:
            print(f"✅ {node_type}: 无重复节点 ({len(nodes)} 个节点)")
    
    return duplicates


def check_orphan_nodes(csv_dir: str) -> Dict[str, int]:
    """检查孤立节点（没有关系的节点）"""
    print("\n" + "=" * 60)
    print("🔍 检查孤立节点...")
    print("=" * 60)
    
    # 读取所有关系
    relations_file = os.path.join(csv_dir, 'relations.csv')
    if not os.path.exists(relations_file):
        print("⚠ 关系文件不存在，跳过孤立节点检查")
        return {}
    
    connected_nodes = set()
    with open(relations_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            connected_nodes.add(row.get('from_id', ''))
            connected_nodes.add(row.get('to_id', ''))
    
    # 检查各类型节点
    node_types = ['Paper', 'Task', 'ImagingModality', 'AnatomicalStructure',
                 'Method', 'Dataset', 'Metric', 'Innovation']
    
    orphan_counts = {}
    
    for node_type in node_types:
        csv_file = os.path.join(csv_dir, f'nodes_{node_type}.csv')
        
        if not os.path.exists(csv_file):
            continue
        
        total_nodes = 0
        orphan_nodes = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_nodes += 1
                node_id = row.get('id', '')
                if node_id and node_id not in connected_nodes:
                    orphan_nodes += 1
        
        orphan_counts[node_type] = {
            'total': total_nodes,
            'orphan': orphan_nodes,
            'connected': total_nodes - orphan_nodes
        }
        
        if orphan_nodes > 0:
            print(f"⚠ {node_type}: {orphan_nodes}/{total_nodes} 个孤立节点 ({orphan_nodes/total_nodes*100:.1f}%)")
        else:
            print(f"✅ {node_type}: 所有节点都有连接 ({total_nodes} 个节点)")
    
    return orphan_counts


def check_relation_integrity(csv_dir: str) -> Dict:
    """检查关系完整性"""
    print("\n" + "=" * 60)
    print("🔍 检查关系完整性...")
    print("=" * 60)
    
    relations_file = os.path.join(csv_dir, 'relations.csv')
    if not os.path.exists(relations_file):
        print("⚠ 关系文件不存在")
        return {}
    
    # 读取所有节点ID
    node_ids = set()
    node_types = ['Paper', 'Task', 'ImagingModality', 'AnatomicalStructure',
                 'Method', 'Dataset', 'Metric', 'Innovation']
    
    for node_type in node_types:
        csv_file = os.path.join(csv_dir, f'nodes_{node_type}.csv')
        if os.path.exists(csv_file):
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    node_ids.add(row.get('id', ''))
    
    # 检查关系
    invalid_relations = []
    relation_types = Counter()
    
    with open(relations_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            from_id = row.get('from_id', '')
            to_id = row.get('to_id', '')
            rel_type = row.get('type', '')
            
            relation_types[rel_type] += 1
            
            if from_id not in node_ids:
                invalid_relations.append({
                    'type': 'missing_from',
                    'from_id': from_id,
                    'to_id': to_id,
                    'rel_type': rel_type
                })
            if to_id not in node_ids:
                invalid_relations.append({
                    'type': 'missing_to',
                    'from_id': from_id,
                    'to_id': to_id,
                    'rel_type': rel_type
                })
    
    print(f"\n📊 关系类型统计:")
    for rel_type, count in relation_types.most_common():
        print(f"   - {rel_type}: {count} 条")
    
    if invalid_relations:
        print(f"\n❌ 发现 {len(invalid_relations)} 条无效关系:")
        missing_from = sum(1 for r in invalid_relations if r['type'] == 'missing_from')
        missing_to = sum(1 for r in invalid_relations if r['type'] == 'missing_to')
        print(f"   - 缺失起始节点: {missing_from} 条")
        print(f"   - 缺失目标节点: {missing_to} 条")
    else:
        print(f"\n✅ 所有关系都有效")
    
    return {
        'total_relations': sum(relation_types.values()),
        'relation_types': dict(relation_types),
        'invalid_relations': len(invalid_relations),
        'invalid_details': invalid_relations[:20]  # 只保存前20个
    }


def check_embedding_coverage(csv_dir: str) -> Dict[str, Dict]:
    """检查 embedding 覆盖率"""
    print("\n" + "=" * 60)
    print("🔍 检查 Embedding 覆盖率...")
    print("=" * 60)
    
    node_types = ['Paper', 'Task', 'ImagingModality', 'AnatomicalStructure',
                 'Method', 'Dataset', 'Metric', 'Innovation']
    
    embedding_stats = {}
    
    for node_type in node_types:
        csv_file = os.path.join(csv_dir, f'nodes_{node_type}.csv')
        
        if not os.path.exists(csv_file):
            continue
        
        total = 0
        with_embedding = 0
        empty_embedding = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += 1
                embedding = row.get('embedding', '').strip()
                if embedding and embedding != '':
                    with_embedding += 1
                else:
                    empty_embedding += 1
        
        embedding_stats[node_type] = {
            'total': total,
            'with_embedding': with_embedding,
            'empty_embedding': empty_embedding,
            'coverage': with_embedding / total * 100 if total > 0 else 0
        }
        
        if empty_embedding > 0:
            print(f"⚠ {node_type}: {with_embedding}/{total} 个节点有 embedding ({embedding_stats[node_type]['coverage']:.1f}%)")
        else:
            print(f"✅ {node_type}: 所有节点都有 embedding ({total} 个节点)")
    
    return embedding_stats


def generate_quality_report(csv_dir: str, output_file: str = None):
    """生成质量检查报告"""
    print("\n" + "=" * 60)
    print("📋 生成质量检查报告...")
    print("=" * 60)
    
    duplicates = check_duplicate_nodes(csv_dir)
    orphans = check_orphan_nodes(csv_dir)
    relations = check_relation_integrity(csv_dir)
    embeddings = check_embedding_coverage(csv_dir)
    
    # 生成报告
    report = {
        'duplicates': duplicates,
        'orphans': orphans,
        'relations': relations,
        'embeddings': embeddings
    }
    
    if output_file:
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 报告已保存到: {output_file}")
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 质量检查总结")
    print("=" * 60)
    
    total_duplicates = sum(len(v) for v in duplicates.values())
    total_orphans = sum(v.get('orphan', 0) for v in orphans.values())
    invalid_rels = relations.get('invalid_relations', 0)
    
    if total_duplicates == 0 and total_orphans == 0 and invalid_rels == 0:
        print("✅ 图谱质量良好！")
    else:
        if total_duplicates > 0:
            print(f"⚠ 发现 {total_duplicates} 组重复节点")
        if total_orphans > 0:
            print(f"⚠ 发现 {total_orphans} 个孤立节点")
        if invalid_rels > 0:
            print(f"⚠ 发现 {invalid_rels} 条无效关系")
    
    return report


def main():
    """主函数"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_dir = os.path.join(script_dir, 'csv')
    
    if not os.path.exists(csv_dir):
        print(f"❌ CSV 目录不存在: {csv_dir}")
        print("   请先运行 json_to_csv.py 生成 CSV 文件")
        return
    
    output_file = os.path.join(script_dir, 'quality_report.json')
    generate_quality_report(csv_dir, output_file)


if __name__ == '__main__':
    main()

