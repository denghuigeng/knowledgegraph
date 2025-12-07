# 🚀 快速开始指南

## 前置要求

1. **Python 3.8+**
2. **Neo4j 实例**（本地或云端）
3. **足够的磁盘空间**（用于存储模型和 CSV 文件）

## 安装步骤

### 1. 安装 Python 依赖

```bash
cd /data/gdh/knowledgegraph/neo4j_database

# 首先安装 PyTorch (CUDA 版本，使用清华镜像源，根据你的 CUDA 版本选择)
# CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://mirrors.tuna.tsinghua.edu.cn/pytorch-wheels/cu118

# CUDA 12.1:
# pip install torch torchvision torchaudio --index-url https://mirrors.tuna.tsinghua.edu.cn/pytorch-wheels/cu121

# CUDA 12.4:
# pip install torch torchvision torchaudio --index-url https://mirrors.tuna.tsinghua.edu.cn/pytorch-wheels/cu124

# 然后安装其他依赖
pip install -r requirements.txt
```

**提示：** 
- 使用清华镜像源加速下载
- 如果不确定 CUDA 版本，运行 `nvidia-smi` 查看

### 2. 运行完整流程

```bash
python main.py
```

这将自动执行：
- ✅ JSON 转 CSV
- ✅ 生成 Embedding（可能需要较长时间）
- ✅ 质量检查
- ✅ 统计验证

### 3. 导入到 Neo4j

#### 选项 A: 使用 Python 脚本（推荐，适用于 Neo4j Cloud）

```bash
# 设置环境变量
export NEO4J_URI="bolt://your-instance.databases.neo4j.io:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-password"

# 运行导入脚本
python cypher_scripts/import_to_cloud.py
```

#### 选项 B: 使用 Cypher 脚本（适用于本地 Neo4j）

1. 将 CSV 文件复制到 Neo4j 的 `import` 目录
2. 在 Neo4j Browser 中执行 `cypher_scripts/import_nodes_and_relations.cypher`

## 常见问题

### Q: Embedding 生成很慢怎么办？

A: 
- 使用 GPU 加速（自动检测）
- 减小 batch_size（在 `generate_embeddings.py` 中）
- 可以先跳过 embedding，后续再生成：`python main.py --skip-embedding`

### Q: 如何只生成 CSV 不生成 Embedding？

A: 
```bash
python main.py --skip-embedding
```

### Q: 如何查看质量检查报告？

A: 
```bash
cat quality_report.json
```

### Q: 如何查看统计报告？

A: 
```bash
cat statistics_report.json
```

## 输出文件说明

- `csv/` - 所有节点和关系的 CSV 文件
- `quality_report.json` - 质量检查报告
- `statistics_report.json` - 统计报告
- `cypher_scripts/` - Neo4j 导入脚本

## 下一步

导入完成后，你可以在 Neo4j Browser 中查询图谱：

```cypher
// 查看节点统计
MATCH (n)
RETURN labels(n)[0] AS type, count(n) AS count
ORDER BY count DESC;

// 查看关系统计
MATCH ()-[r]->()
RETURN type(r) AS type, count(r) AS count
ORDER BY count DESC;

// 查看一篇论文及其关系
MATCH (p:Paper {paper_id: "paper_1"})-[r]->(n)
RETURN p, r, n
LIMIT 50;
```

