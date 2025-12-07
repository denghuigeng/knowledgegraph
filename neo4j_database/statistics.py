#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图谱统计和验证脚本
- 节点统计
- 关系统计
- 结构验证
"""

import os
import csv
import json
from collections import Counter, defaultdict
from typing import Dict, List


def count_nodes(csv_dir: str) -> Dict[str, int]:
    """统计各类型节点数量"""
    print("=" * 60)
    print("📊 节点统计")
    print("=" * 60)
    
    node_types = ['Paper', 'Task', 'ImagingModality', 'AnatomicalStructure',
                 'Method', 'Dataset', 'Metric', 'Innovation']
    
    node_counts = {}
    total = 0
    
    for node_type in node_types:
        csv_file = os.path.join(csv_dir, f'nodes_{node_type}.csv')
        
        if not os.path.exists(csv_file):
            node_counts[node_type] = 0
            continue
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = sum(1 for _ in reader)
        
        node_counts[node_type] = count
        total += count
        print(f"   {node_type:20s}: {count:6d} 个节点")
    
    print(f"   {'总计':20s}: {total:6d} 个节点")
    print()
    
    return node_counts


def count_relations(csv_dir: str) -> Dict:
    """统计关系"""
    print("=" * 60)
    print("📊 关系统计")
    print("=" * 60)
    
    relations_file = os.path.join(csv_dir, 'relations.csv')
    
    if not os.path.exists(relations_file):
        print("⚠ 关系文件不存在")
        return {}
    
    relation_types = Counter()
    total = 0
    
    with open(relations_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel_type = row.get('type', 'UNKNOWN')
            relation_types[rel_type] += 1
            total += 1
    
    print(f"   总关系数: {total}")
    print(f"\n   关系类型分布:")
    for rel_type, count in relation_types.most_common():
        percentage = count / total * 100 if total > 0 else 0
        print(f"      {rel_type:30s}: {count:6d} 条 ({percentage:5.1f}%)")
    print()
    
    return {
        'total': total,
        'by_type': dict(relation_types)
    }


def analyze_paper_statistics(csv_dir: str) -> Dict:
    """分析论文统计信息"""
    print("=" * 60)
    print("📊 论文统计")
    print("=" * 60)
    
    csv_file = os.path.join(csv_dir, 'nodes_Paper.csv')
    
    if not os.path.exists(csv_file):
        print("⚠ 论文文件不存在")
        return {}
    
    papers = []
    years = []
    categories = Counter()
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            papers.append(row)
            year = row.get('year', '')
            if year and year.isdigit():
                years.append(int(year))
            category = row.get('category', '')
            if category:
                categories[category] += 1
    
    stats = {
        'total_papers': len(papers),
        'year_range': {
            'min': min(years) if years else None,
            'max': max(years) if years else None
        },
        'year_distribution': Counter(years),
        'top_categories': dict(categories.most_common(10))
    }
    
    print(f"   总论文数: {stats['total_papers']}")
    if stats['year_range']['min']:
        print(f"   年份范围: {stats['year_range']['min']} - {stats['year_range']['max']}")
    
    print(f"\n   热门类别 (Top 10):")
    for category, count in list(categories.most_common(10)):
        print(f"      {category:40s}: {count:4d} 篇")
    print()
    
    return stats


def analyze_node_connectivity(csv_dir: str) -> Dict:
    """分析节点连接度"""
    print("=" * 60)
    print("📊 节点连接度分析")
    print("=" * 60)
    
    relations_file = os.path.join(csv_dir, 'relations.csv')
    
    if not os.path.exists(relations_file):
        print("⚠ 关系文件不存在")
        return {}
    
    # 统计每个节点的连接数
    node_degrees = defaultdict(int)
    
    with open(relations_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            from_id = row.get('from_id', '')
            to_id = row.get('to_id', '')
            node_degrees[from_id] += 1
            node_degrees[to_id] += 1
    
    if not node_degrees:
        print("⚠ 没有关系数据")
        return {}
    
    degrees = list(node_degrees.values())
    stats = {
        'total_nodes_with_relations': len(node_degrees),
        'max_degree': max(degrees),
        'min_degree': min(degrees),
        'avg_degree': sum(degrees) / len(degrees) if degrees else 0,
        'median_degree': sorted(degrees)[len(degrees) // 2] if degrees else 0
    }
    
    print(f"   有连接的节点数: {stats['total_nodes_with_relations']}")
    print(f"   最大连接度: {stats['max_degree']}")
    print(f"   最小连接度: {stats['min_degree']}")
    print(f"   平均连接度: {stats['avg_degree']:.2f}")
    print(f"   中位数连接度: {stats['median_degree']}")
    print()
    
    # 找出连接度最高的节点
    top_nodes = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"   连接度最高的节点 (Top 10):")
    for node_id, degree in top_nodes:
        print(f"      {node_id[:20]:20s}: {degree:4d} 条连接")
    print()
    
    return stats


def validate_structure(csv_dir: str) -> Dict:
    """验证图谱结构"""
    print("=" * 60)
    print("🔍 结构验证")
    print("=" * 60)
    
    issues = []
    
    # 检查必需的文件
    required_files = [
        'nodes_Paper.csv',
        'relations.csv'
    ]
    
    for filename in required_files:
        filepath = os.path.join(csv_dir, filename)
        if not os.path.exists(filepath):
            issues.append(f"缺失必需文件: {filename}")
    
    # 检查节点ID唯一性
    all_node_ids = set()
    node_types = ['Paper', 'Task', 'ImagingModality', 'AnatomicalStructure',
                 'Method', 'Dataset', 'Metric', 'Innovation']
    
    for node_type in node_types:
        csv_file = os.path.join(csv_dir, f'nodes_{node_type}.csv')
        if os.path.exists(csv_file):
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    node_id = row.get('id', '')
                    if node_id:
                        if node_id in all_node_ids:
                            issues.append(f"重复的节点ID: {node_id} (类型: {node_type})")
                        all_node_ids.add(node_id)
    
    # 检查关系中的节点ID是否存在
    relations_file = os.path.join(csv_dir, 'relations.csv')
    if os.path.exists(relations_file):
        with open(relations_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                from_id = row.get('from_id', '')
                to_id = row.get('to_id', '')
                
                if from_id and from_id not in all_node_ids:
                    issues.append(f"关系 {i}: 起始节点不存在 ({from_id})")
                if to_id and to_id not in all_node_ids:
                    issues.append(f"关系 {i}: 目标节点不存在 ({to_id})")
                
                if len(issues) >= 20:  # 只报告前20个问题
                    break
    
    if issues:
        print(f"❌ 发现 {len(issues)} 个结构问题:")
        for issue in issues[:20]:
            print(f"   - {issue}")
        if len(issues) > 20:
            print(f"   ... 还有 {len(issues) - 20} 个问题")
    else:
        print("✅ 结构验证通过")
    print()
    
    return {
        'issues': issues,
        'total_issues': len(issues)
    }


def generate_statistics_report(csv_dir: str, output_file: str = None):
    """生成统计报告"""
    print("\n" + "=" * 60)
    print("📋 生成统计报告")
    print("=" * 60)
    
    node_counts = count_nodes(csv_dir)
    relation_stats = count_relations(csv_dir)
    paper_stats = analyze_paper_statistics(csv_dir)
    connectivity_stats = analyze_node_connectivity(csv_dir)
    structure_validation = validate_structure(csv_dir)
    
    report = {
        'node_counts': node_counts,
        'relation_stats': relation_stats,
        'paper_stats': paper_stats,
        'connectivity_stats': connectivity_stats,
        'structure_validation': structure_validation
    }
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n✅ 报告已保存到: {output_file}")
    
    return report


def main():
    """主函数"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_dir = os.path.join(script_dir, 'csv')
    
    if not os.path.exists(csv_dir):
        print(f"❌ CSV 目录不存在: {csv_dir}")
        print("   请先运行 json_to_csv.py 生成 CSV 文件")
        return
    
    output_file = os.path.join(script_dir, 'statistics_report.json')
    generate_statistics_report(csv_dir, output_file)


if __name__ == '__main__':
    main()

