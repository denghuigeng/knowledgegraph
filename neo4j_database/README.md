# Neo4j 知识图谱构建工具

本工具用于将 `standard.json` 转换为 Neo4j 知识图谱，包括节点、关系和 embedding 生成。

## 📁 目录结构

```
neo4j_database/
├── csv/                          # 生成的 CSV 文件（节点和关系）
├── cypher_scripts/               # Cypher 导入脚本
│   ├── import_nodes_and_relations.cypher
│   ├── import_with_neo4j_import_tool.sh
│   └── import_to_cloud.py
├── json_to_csv.py               # JSON 转 CSV 脚本
├── generate_embeddings.py       # Embedding 生成脚本
├── quality_check.py             # 质量检查脚本
├── statistics.py                # 统计验证脚本
├── main.py                      # 主脚本（整合所有功能）
└── README.md                    # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
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

**注意：** 
- 使用清华镜像源加速下载
- 请根据你的 CUDA 版本选择合适的 PyTorch 安装命令
- 查看支持的 CUDA 版本: https://pytorch.org/get-started/locally/
- 如果不确定 CUDA 版本，可以运行 `nvidia-smi` 查看

### 2. 运行完整流程

```bash
cd neo4j_database
python main.py
```

这将执行以下步骤：
1. ✅ JSON 转 CSV（节点表和关系表）
2. ✅ 生成 Embedding（使用 bge-multilingual-gemma2）
3. ✅ 质量检查（重复节点、孤立节点等）
4. ✅ 统计验证（节点统计、关系统计等）

### 3. 分步执行

如果只想执行特定步骤：

```bash
# 只生成 CSV（不生成 embedding）
python main.py --skip-embedding

# 只执行 CSV 转换和 embedding 生成
python main.py --steps csv embedding

# 跳过质量检查和统计
python main.py --skip-quality --skip-statistics
```

## 📝 详细说明

### 步骤 1: JSON 转 CSV

```bash
python json_to_csv.py
```

**功能：**
- 从 `standard.json` 提取所有节点（Paper, Task, ImagingModality, AnatomicalStructure, Method, Dataset, Metric, Innovation）
- 提取所有关系
- 生成节点 CSV 文件（`csv/nodes_*.csv`）和关系 CSV 文件（`csv/relations.csv`）
- 自动去重，确保节点唯一性

**输出：**
- `csv/nodes_Paper.csv`
- `csv/nodes_Task.csv`
- `csv/nodes_ImagingModality.csv`
- `csv/nodes_AnatomicalStructure.csv`
- `csv/nodes_Method.csv`
- `csv/nodes_Dataset.csv`
- `csv/nodes_Metric.csv`
- `csv/nodes_Innovation.csv`
- `csv/relations.csv`

### 步骤 2: 生成 Embedding

```bash
python generate_embeddings.py
```

**功能：**
- 使用 `BAAI/bge-multilingual-gemma2` 模型为所有节点生成 embedding
- 支持中英文混合文本
- 批量处理，自动更新 CSV 文件

**注意：**
- 首次运行会下载模型（约几 GB）
- 生成 embedding 需要较长时间（取决于节点数量）
- 建议使用 GPU 加速

**模型参考：**
- [FlagEmbedding GitHub](https://github.com/FlagOpen/FlagEmbedding)
- 模型：`BAAI/bge-multilingual-gemma2`

**本地加载模型（推荐）：**
- 先将模型下载到本地，例如：
  ```bash
  mkdir -p /data/models
  git lfs install
  git clone https://huggingface.co/BAAI/bge-multilingual-gemma2 /data/models/bge-multilingual-gemma2
  ```
- 运行脚本前设置环境变量指向本地目录：
  ```bash
  export BGE_MODEL_PATH="/data/models/bge-multilingual-gemma2"
  ```
- 若环境变量存在且目录有效，`generate_embeddings.py` 会直接从本地加载，避免重复下载。

### 步骤 3: 质量检查

```bash
python quality_check.py
```

**检查项：**
- ✅ 重复节点检测
- ✅ 孤立节点检测（没有关系的节点）
- ✅ 关系完整性（关系中的节点是否存在）
- ✅ Embedding 覆盖率

**输出：**
- `quality_report.json` - 详细的质量检查报告

### 步骤 4: 统计验证

```bash
python statistics.py
```

**统计项：**
- 📊 各类型节点数量
- 📊 关系类型分布
- 📊 论文统计（年份、类别等）
- 📊 节点连接度分析
- 🔍 结构验证

**输出：**
- `statistics_report.json` - 详细的统计报告

## 📤 导入到 Neo4j

### 方法 1: 使用 Cypher 脚本（推荐）

1. **上传 CSV 文件到 Neo4j**

   如果使用 Neo4j Cloud 或本地 Neo4j：
   - 将 `csv/` 目录下的所有 CSV 文件上传到 Neo4j 的 `import` 目录
   - 或通过 Neo4j Browser 上传

2. **执行 Cypher 脚本**

   在 Neo4j Browser 中执行：
   ```cypher
   :source cypher_scripts/import_nodes_and_relations.cypher
   ```

   或使用 cypher-shell：
   ```bash
   cypher-shell -u neo4j -p <password> -f cypher_scripts/import_nodes_and_relations.cypher
   ```

### 方法 2: 使用 Python 脚本（Neo4j Cloud）

```bash
# 设置环境变量
export NEO4J_URI="bolt://your-neo4j-instance.databases.neo4j.io:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-password"

# 或直接传递参数
python cypher_scripts/import_to_cloud.py \
    "bolt://your-neo4j-instance.databases.neo4j.io:7687" \
    neo4j \
    your-password
```

**功能：**
- 自动创建约束和索引
- 批量导入节点和关系
- 支持 Neo4j Cloud 和本地实例

## 🔧 配置说明

### Neo4j 连接配置

编辑 `cypher_scripts/import_to_cloud.py` 或使用环境变量：

```bash
export NEO4J_URI="bolt://localhost:7687"  # 或你的 Neo4j Cloud URI
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="your-password"
```

### Embedding 模型配置

默认使用 `BAAI/bge-multilingual-gemma2`，如需更换模型，编辑 `generate_embeddings.py`：

```python
model = FlagModel('BAAI/bge-multilingual-gemma2', use_fp16=True)
```

## 📊 节点类型

| 节点类型 | 说明 | 主要属性 |
|---------|------|---------|
| Paper | 论文 | paper_id, title, doi, year, category, authors, embedding |
| Task | 任务 | id, name, type, embedding |
| ImagingModality | 成像模态 | id, name, type, embedding |
| AnatomicalStructure | 解剖结构 | id, name, type, embedding |
| Method | 方法 | id, name, method_type, type, embedding |
| Dataset | 数据集 | id, name, type, embedding |
| Metric | 指标 | id, name, type, embedding |
| Innovation | 创新点 | id, description, innovation_type, type, embedding |

## 🔗 关系类型

- `ADDRESSES_TASK` - 论文研究任务
- `USES_MODALITY` - 论文使用模态
- `FOCUSES_ON_STRUCTURE` - 论文关注结构
- `PROPOSES_METHOD` - 论文提出方法
- `USES_DATASET` - 论文使用数据集
- `REPORTS_METRIC` - 论文报告指标
- `HAS_INNOVATION` - 论文创新点
- `DESIGNED_FOR_TASK` - 方法设计用于任务
- `APPLIED_TO_MODALITY` - 方法应用于模态
- `APPLIED_TO_STRUCTURE` - 方法应用于结构
- `EVALUATED_ON` - 方法在数据集上评估
- `ACHIEVES_METRIC` - 方法达到指标

## 🐛 故障排除

### 1. Embedding 生成失败

**问题：** `ImportError: No module named 'FlagEmbedding'`

**解决：**
```bash
pip install FlagEmbedding
```

**问题：** 内存不足

**解决：**
- 减小 batch_size（在 `generate_embeddings.py` 中）
- 使用更小的模型
- 使用 GPU

### 2. Neo4j 导入失败

**问题：** `File not found` 错误

**解决：**
- 确保 CSV 文件已上传到 Neo4j 的 `import` 目录
- 检查文件路径是否正确

**问题：** 约束创建失败

**解决：**
- 可能是约束已存在，可以忽略
- 或先删除现有约束：`DROP CONSTRAINT constraint_name`

### 3. 关系导入失败

**问题：** `apoc.create.relationship` 不可用

**解决：**
- 安装 APOC 插件
- 或使用备用方法（脚本中已包含）

## 📈 性能优化

1. **批量导入：** 使用批量导入而不是逐条插入
2. **索引：** 确保在导入前创建索引
3. **Embedding：** 使用 GPU 和 FP16 加速
4. **并行处理：** 可以并行处理不同类型的节点

## 📚 参考资料

- [Neo4j 官方文档](https://neo4j.com/docs/)
- [FlagEmbedding 文档](https://github.com/FlagOpen/FlagEmbedding)
- [Cypher 查询语言](https://neo4j.com/developer/cypher/)

## 📝 许可证

本项目遵循项目主许可证。

