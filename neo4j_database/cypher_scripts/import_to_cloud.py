#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 CSV 文件导入到 Neo4j Cloud 实例
支持通过 Neo4j Python Driver 或 HTTP API 导入
"""


import os
import csv
from neo4j import GraphDatabase
from typing import Dict, List
import time

os.environ["NEO4J_URI"]="neo4j+s://e96b056a.databases.neo4j.io"
os.environ["NEO4J_USER"]="neo4j"
os.environ["NEO4J_PASSWORD"]="l_Xozo1gLym66VVmHMXa9WMNmpju9uUsScSXtYy-elc"
class Neo4jImporter:
    def __init__(self, uri: str, user: str, password: str):
        """初始化 Neo4j 连接"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.session = self.driver.session()
    
    def close(self):
        """关闭连接"""
        self.session.close()
        self.driver.close()
    
    def create_constraints_and_indexes(self):
        """创建约束和索引"""
        print("📋 创建约束和索引...")
        
        constraints = [
            "CREATE CONSTRAINT paper_id IF NOT EXISTS FOR (p:Paper) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT task_id IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT modality_id IF NOT EXISTS FOR (m:ImagingModality) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT structure_id IF NOT EXISTS FOR (s:AnatomicalStructure) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT method_id IF NOT EXISTS FOR (m:Method) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT dataset_id IF NOT EXISTS FOR (d:Dataset) REQUIRE d.id IS UNIQUE",
            "CREATE CONSTRAINT metric_id IF NOT EXISTS FOR (m:Metric) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT innovation_id IF NOT EXISTS FOR (i:Innovation) REQUIRE i.id IS UNIQUE",
        ]
        
        for constraint in constraints:
            try:
                self.session.run(constraint)
            except Exception as e:
                print(f"   ⚠ {constraint[:50]}... 可能已存在: {e}")
        
        print("✅ 约束和索引创建完成")
    
    def import_nodes(self, csv_file: str, node_type: str):
        """导入节点"""
        if not os.path.exists(csv_file):
            print(f"⚠ 跳过不存在的文件: {csv_file}")
            return 0
        
        print(f"📥 导入 {node_type} 节点...")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            nodes = list(reader)
        
        if not nodes:
            return 0
        
        # 根据节点类型构建 Cypher 查询
        if node_type == 'Paper':
            query = """
            UNWIND $nodes AS node
            CREATE (p:Paper {
                id: node.id,
                paper_id: node.paper_id,
                title: node.title,
                doi: node.doi,
                year: CASE WHEN node.year <> '' THEN toInteger(node.year) ELSE null END,
                category: node.category,
                authors: node.authors,
                embedding: CASE WHEN node.embedding <> '' THEN [x IN split(node.embedding, ',') | toFloat(x)] ELSE [] END
            })
            """
        elif node_type == 'Task':
            query = """
            UNWIND $nodes AS node
            CREATE (t:Task {
                id: node.id,
                name: node.name,
                type: node.type,
                embedding: CASE WHEN node.embedding <> '' THEN [x IN split(node.embedding, ',') | toFloat(x)] ELSE [] END
            })
            """
        elif node_type == 'ImagingModality':
            query = """
            UNWIND $nodes AS node
            CREATE (m:ImagingModality {
                id: node.id,
                name: node.name,
                type: node.type,
                embedding: CASE WHEN node.embedding <> '' THEN [x IN split(node.embedding, ',') | toFloat(x)] ELSE [] END
            })
            """
        elif node_type == 'AnatomicalStructure':
            query = """
            UNWIND $nodes AS node
            CREATE (s:AnatomicalStructure {
                id: node.id,
                name: node.name,
                type: node.type,
                embedding: CASE WHEN node.embedding <> '' THEN [x IN split(node.embedding, ',') | toFloat(x)] ELSE [] END
            })
            """
        elif node_type == 'Method':
            query = """
            UNWIND $nodes AS node
            CREATE (m:Method {
                id: node.id,
                name: node.name,
                method_type: node.method_type,
                type: node.type,
                embedding: CASE WHEN node.embedding <> '' THEN [x IN split(node.embedding, ',') | toFloat(x)] ELSE [] END
            })
            """
        elif node_type == 'Dataset':
            query = """
            UNWIND $nodes AS node
            CREATE (d:Dataset {
                id: node.id,
                name: node.name,
                type: node.type,
                embedding: CASE WHEN node.embedding <> '' THEN [x IN split(node.embedding, ',') | toFloat(x)] ELSE [] END
            })
            """
        elif node_type == 'Metric':
            query = """
            UNWIND $nodes AS node
            CREATE (m:Metric {
                id: node.id,
                name: node.name,
                type: node.type,
                embedding: CASE WHEN node.embedding <> '' THEN [x IN split(node.embedding, ',') | toFloat(x)] ELSE [] END
            })
            """
        elif node_type == 'Innovation':
            query = """
            UNWIND $nodes AS node
            CREATE (i:Innovation {
                id: node.id,
                description: node.description,
                innovation_type: node.innovation_type,
                type: node.type,
                embedding: CASE WHEN node.embedding <> '' THEN [x IN split(node.embedding, ',') | toFloat(x)] ELSE [] END
            })
            """
        else:
            return 0
        
        # 批量导入（每批 1000 个）
        batch_size = 50
        total = 0
        
        for i in range(0, len(nodes), batch_size):
            batch = nodes[i:i+batch_size]
            try:
                result = self.session.run(query, nodes=batch)
                count = result.consume().counters.nodes_created
                total += count
                print(f"   ✓ 已导入 {min(i+batch_size, len(nodes))}/{len(nodes)} 个节点")
            except Exception as e:
                print(f"   ❌ 导入失败: {e}")
                raise
        
        print(f"✅ {node_type} 节点导入完成 ({total} 个节点)")
        return total
    
    def import_relations(self, csv_file: str):
        """导入关系"""
        if not os.path.exists(csv_file):
            print(f"⚠ 关系文件不存在: {csv_file}")
            return 0
        
        print(f"📥 导入关系...")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            relations = list(reader)
        
        if not relations:
            return 0
        
        # 使用动态关系类型创建
        query = """
        UNWIND $relations AS rel
        MATCH (from {id: rel.from_id})
        MATCH (to {id: rel.to_id})
        CALL apoc.create.relationship(from, rel.type, {
            value: CASE WHEN rel.value <> '' THEN toFloat(rel.value) ELSE null END,
            note: rel.note
        }, to) YIELD rel AS r
        RETURN count(r) AS count
        """
        
        # 如果没有 apoc，使用备用方法
        query_fallback = """
        UNWIND $relations AS rel
        MATCH (from {id: rel.from_id})
        MATCH (to {id: rel.to_id})
        MERGE (from)-[r:RELATED_TO]->(to)
        SET r.type = rel.type,
            r.value = CASE WHEN rel.value <> '' THEN toFloat(rel.value) ELSE null END,
            r.note = rel.note
        RETURN count(r) AS count
        """
        
        batch_size = 1000
        total = 0
        
        for i in range(0, len(relations), batch_size):
            batch = relations[i:i+batch_size]
            try:
                # 尝试使用 apoc
                result = self.session.run(query, relations=batch)
                count = result.single()['count'] if result.peek() else 0
                total += count
            except Exception:
                # 使用备用方法
                try:
                    result = self.session.run(query_fallback, relations=batch)
                    count = result.single()['count'] if result.peek() else 0
                    total += count
                except Exception as e:
                    print(f"   ❌ 导入失败: {e}")
                    raise
            
            print(f"   ✓ 已导入 {min(i+batch_size, len(relations))}/{len(relations)} 条关系")
        
        print(f"✅ 关系导入完成 ({total} 条关系)")
        return total


def main():
    """主函数"""
    import sys
    
    # 从环境变量或命令行参数获取连接信息
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', '')
    
    if len(sys.argv) >= 4:
        uri = sys.argv[1]
        user = sys.argv[2]
        password = sys.argv[3]
    elif not password:
        password = input("请输入 Neo4j 密码: ")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_dir = os.path.join(script_dir, '..', 'csv')
    
    print("=" * 50)
    print("Neo4j Cloud 导入工具")
    print("=" * 50)
    print(f"URI: {uri}")
    print(f"用户: {user}")
    print(f"CSV 目录: {csv_dir}")
    print()
    
    importer = Neo4jImporter(uri, user, password)
    
    try:
        # 创建约束和索引
        importer.create_constraints_and_indexes()
        
        # 导入节点
        node_types = ['Paper', 'Task', 'ImagingModality', 'AnatomicalStructure',
                     'Method', 'Dataset', 'Metric', 'Innovation']
        
        for node_type in node_types:
            csv_file = os.path.join(csv_dir, f'nodes_{node_type}.csv')
            importer.import_nodes(csv_file, node_type)
        
        # 导入关系
        relations_file = os.path.join(csv_dir, 'relations.csv')
        importer.import_relations(relations_file)
        
        print("\n✅ 导入完成!")
        
    finally:
        importer.close()


if __name__ == '__main__':
    main()

