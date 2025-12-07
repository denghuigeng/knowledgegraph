#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j 图谱构建主脚本
整合所有功能：JSON转CSV、生成Embedding、质量检查、统计验证
"""

import os
import sys
import argparse
from pathlib import Path


def run_step(script_name: str, description: str):
    """运行一个步骤"""
    print("\n" + "=" * 60)
    print(f"📌 {description}")
    print("=" * 60)
    
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    if not os.path.exists(script_path):
        print(f"❌ 脚本不存在: {script_path}")
        return False
    
    # 执行脚本
    import subprocess
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=os.path.dirname(script_path)
    )
    
    if result.returncode == 0:
        print(f"✅ {description} 完成")
        return True
    else:
        print(f"❌ {description} 失败 (退出码: {result.returncode})")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Neo4j 图谱构建工具')
    parser.add_argument('--skip-embedding', action='store_true',
                       help='跳过 embedding 生成（耗时较长）')
    parser.add_argument('--skip-quality', action='store_true',
                       help='跳过质量检查')
    parser.add_argument('--skip-statistics', action='store_true',
                       help='跳过统计验证')
    parser.add_argument('--steps', nargs='+',
                       choices=['csv', 'embedding', 'quality', 'statistics'],
                       help='只执行指定的步骤')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 Neo4j 图谱构建工具")
    print("=" * 60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_dir = os.path.join(script_dir, 'csv')
    
    # 确保 CSV 目录存在
    os.makedirs(csv_dir, exist_ok=True)
    
    steps_to_run = []
    
    if args.steps:
        # 用户指定了步骤
        if 'csv' in args.steps:
            steps_to_run.append(('json_to_csv.py', 'JSON 转 CSV'))
        if 'embedding' in args.steps and not args.skip_embedding:
            steps_to_run.append(('generate_embeddings.py', '生成 Embedding'))
        if 'quality' in args.steps and not args.skip_quality:
            steps_to_run.append(('quality_check.py', '质量检查'))
        if 'statistics' in args.steps and not args.skip_statistics:
            steps_to_run.append(('statistics.py', '统计验证'))
    else:
        # 默认执行所有步骤
        steps_to_run.append(('json_to_csv.py', 'JSON 转 CSV'))
        
        if not args.skip_embedding:
            steps_to_run.append(('generate_embeddings.py', '生成 Embedding'))
        else:
            print("\n⚠ 跳过 Embedding 生成（使用 --skip-embedding）")
        
        if not args.skip_quality:
            steps_to_run.append(('quality_check.py', '质量检查'))
        else:
            print("\n⚠ 跳过质量检查（使用 --skip-quality）")
        
        if not args.skip_statistics:
            steps_to_run.append(('statistics.py', '统计验证'))
        else:
            print("\n⚠ 跳过统计验证（使用 --skip-statistics）")
    
    # 执行步骤
    success_count = 0
    for script_name, description in steps_to_run:
        if run_step(script_name, description):
            success_count += 1
        else:
            print(f"\n❌ 步骤失败: {description}")
            response = input("是否继续执行后续步骤? (y/n): ")
            if response.lower() != 'y':
                break
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 执行总结")
    print("=" * 60)
    print(f"   成功步骤: {success_count}/{len(steps_to_run)}")
    
    if success_count == len(steps_to_run):
        print("\n✅ 所有步骤执行完成！")
        print(f"\n📁 输出文件位置:")
        print(f"   CSV 文件: {csv_dir}/")
        print(f"   Cypher 脚本: {script_dir}/cypher_scripts/")
        print(f"\n📝 下一步:")
        print(f"   1. 查看质量检查报告: {script_dir}/quality_report.json")
        print(f"   2. 查看统计报告: {script_dir}/statistics_report.json")
        print(f"   3. 导入到 Neo4j:")
        print(f"      - 使用 Cypher 脚本: {script_dir}/cypher_scripts/import_nodes_and_relations.cypher")
        print(f"      - 或使用 Python 脚本: python {script_dir}/cypher_scripts/import_to_cloud.py")
    else:
        print(f"\n⚠ 部分步骤未完成，请检查错误信息")


if __name__ == '__main__':
    main()

