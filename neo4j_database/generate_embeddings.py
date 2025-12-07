#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为节点生成 embedding，使用 bge-multilingual-gemma2 模型
参考: https://github.com/FlagOpen/FlagEmbedding/blob/master/README_zh.md
"""

import os
import csv
import json
import numpy as np
from typing import List, Dict
from tqdm import tqdm
import torch

os.environ["CUDA_VISIBLE_DEVICES"] = "0,2,5"
os.environ["BGE_MODEL_PATH"] = "/data/gdh/knowledgegraph/models/bge-multilingual-gemma2"
def load_model():
    """加载 bge-multilingual-gemma2 模型

    优先从本地路径加载，以避免每次都从 HuggingFace 下载：
    - 如果设置了环境变量 BGE_MODEL_PATH 且目录存在，则从该目录加载
    - 否则从 HuggingFace Hub 加载: 'BAAI/bge-multilingual-gemma2'
    """
    try:
        from FlagEmbedding import FlagModel

        # 优先使用本地模型目录（例如: /data/models/bge-multilingual-gemma2）
        local_model_path = os.getenv("BGE_MODEL_PATH", "").strip()
        if local_model_path and os.path.isdir(local_model_path):
            print(f"📦 从本地目录加载 bge-multilingual-gemma2 模型: {local_model_path}")
            model_name_or_path = local_model_path
        else:
            # 退回到在线加载
            model_name_or_path = "BAAI/bge-multilingual-gemma2"
            print("📦 从 HuggingFace Hub 加载 bge-multilingual-gemma2 模型...")
            print("   如需本地加载，可先下载模型并设置环境变量 BGE_MODEL_PATH=本地模型目录")

        model = FlagModel(model_name_or_path, use_fp16=True)
        print("✅ 模型加载成功")
        return model
    except ImportError:
        print("❌ 错误: 请先安装 FlagEmbedding")
        print("   安装命令: pip install FlagEmbedding")
        raise
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        raise


def generate_text_for_embedding(node: Dict, node_type: str) -> str:
    """根据节点类型生成用于 embedding 的文本"""
    if node_type == 'Paper':
        # 论文节点：使用标题和类别
        title = node.get('title', '')
        category = node.get('category', '')
        return f"{title} {category}".strip()
    
    elif node_type == 'Task':
        return node.get('name', '')
    
    elif node_type == 'ImagingModality':
        return node.get('name', '')
    
    elif node_type == 'AnatomicalStructure':
        return node.get('name', '')
    
    elif node_type == 'Method':
        name = node.get('name', '')
        method_type = node.get('method_type', '')
        return f"{name} {method_type}".strip()
    
    elif node_type == 'Dataset':
        return node.get('name', '')
    
    elif node_type == 'Metric':
        return node.get('name', '')
    
    elif node_type == 'Innovation':
        description = node.get('description', '')
        innovation_type = node.get('innovation_type', '')
        return f"{description} {innovation_type}".strip()
    
    return ""


def l2_normalize(vectors: np.ndarray) -> np.ndarray:
    """对向量进行 L2 归一化"""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-12, None)
    return vectors / norms


def update_csv_with_embeddings(csv_dir: str, model, batch_size: int = 16):
    """为所有节点 CSV 文件添加 embedding"""
    node_types = ['Paper', 'Task', 'ImagingModality', 'AnatomicalStructure', 
                  'Method', 'Dataset', 'Metric', 'Innovation']
    
    for node_type in node_types:
        csv_file = os.path.join(csv_dir, f'nodes_{node_type}.csv')
        
        if not os.path.exists(csv_file):
            print(f"⚠ 跳过不存在的文件: {csv_file}")
            continue
        
        print(f"\n🔄 处理 {node_type} 节点...")
        
        # 读取 CSV
        rows = []
        texts = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
                text = generate_text_for_embedding(row, node_type)
                texts.append(text if text else " ")  # 空文本用空格代替
        
        if not rows:
            print(f"   ⚠ {node_type} 节点为空，跳过")
            continue
        
        # 批量生成 embedding
        print(f"   📊 生成 {len(texts)} 个节点的 embedding...")
        embeddings: List[np.ndarray] = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc=f"   Processing {node_type}"):
            batch_texts = texts[i:i+batch_size]
            # 不再向 FlagEmbedding 传递 normalize_embeddings，避免与内部实现冲突
            batch_embeddings = model.encode(batch_texts)
            batch_embeddings = np.asarray(batch_embeddings, dtype="float32")
            batch_embeddings = l2_normalize(batch_embeddings)
            embeddings.extend(batch_embeddings)
        
        # 更新 CSV 文件
        print(f"   💾 更新 CSV 文件...")
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(rows[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for row, embedding in zip(rows, embeddings):
                # 将 embedding 转换为字符串（逗号分隔）
                row['embedding'] = ','.join(map(str, embedding.tolist()))
                writer.writerow(row)
        
        print(f"   ✅ {node_type} 节点处理完成 ({len(rows)} 个节点)")


def main():
    """主函数"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_dir = os.path.join(script_dir, 'csv')
    
    if not os.path.exists(csv_dir):
        print(f"❌ CSV 目录不存在: {csv_dir}")
        print("   请先运行 json_to_csv.py 生成 CSV 文件")
        return
    
    # 加载模型
    model = load_model()
    
    # 生成 embedding
    update_csv_with_embeddings(csv_dir, model, batch_size=32)
    
    print("\n✅ Embedding 生成完成!")


if __name__ == '__main__':
    main()

