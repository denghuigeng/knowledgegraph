# TMI 科研文献知识图谱项目

## 1. 项目概述

本项目旨在将 TMI（医学影像）领域的科研文献转化为一个结构化的**知识图谱**。该图谱不仅捕捉了论文、任务、方法、模态等实体间的显式关系，还为每个核心实体生成了**向量嵌入（Embeddings）**，以支持高级的语义查询和下游智能应用（如：问答系统、语义检索、推荐系统等）。

本文档是为**下游任务开发者**准备的快速入门指南。

---

## 2. 知识图谱 Schema

了解图谱的结构是进行下游开发的基础。

### 2.1. 节点 (Nodes)

图谱包含以下几类核心节点。所有节点（除 Paper 外）都包含 `id`, `name`, `type` 属性。所有节点都有 `embedding` 属性用于语义计算。

| 节点标签 (`Label`)    | 描述                                     | 核心属性 (`Properties`)                                |
| --------------------- | ---------------------------------------- | ------------------------------------------------------ |
| `Paper`               | 代表一篇科研论文                         | `paper_id`, `title`, `doi`, `year`, `category`, `embedding` |
| `Task`                | 论文/方法所解决的任务（如：图像分割）      | `id`, `name`, `embedding`                              |
| `ImagingModality`     | 成像模态（如：MRI, CT）                  | `id`, `name`, `embedding`                              |
| `AnatomicalStructure` | 解剖结构（如：大脑, 肝脏）               | `id`, `name`, `embedding`                              |
| `Method`              | 论文中提出的具体方法                     | `id`, `name`, `embedding`                              |
| `Dataset`             | 实验中使用的数据集                       | `id`, `name`, `embedding`                              |
| `Metric`              | 评估性能的指标                           | `id`, `name`, `embedding`                              |
| `Innovation`          | 论文的核心创新点                         | `id`, `description`, `embedding`                       |

### 2.2. 关系 (Relationships)

节点之间通过以下关系连接，描述了它们之间的语义关联。

| 关系类型 (`Type`)         | 描述                               | 结构示例                                         |
| ------------------------- | ---------------------------------- | ------------------------------------------------ |
| `ADDRESSES_TASK`          | 论文研究某个任务                   | `(:Paper)-[:ADDRESSES_TASK]->(:Task)`             |
| `USES_MODALITY`           | 论文使用了某种成像模态             | `(:Paper)-[:USES_MODALITY]->(:ImagingModality)`   |
| `FOCUSES_ON_STRUCTURE`    | 论文关注某个解剖结构               | `(:Paper)-[:FOCUSES_ON_STRUCTURE]->(:AnatomicalStructure)` |
| `PROPOSES_METHOD`         | 论文提出了某个方法                 | `(:Paper)-[:PROPOSES_METHOD]->(:Method)`          |
| `DESIGNED_FOR_TASK`       | 方法被设计用于某个任务             | `(:Method)-[:DESIGNED_FOR_TASK]->(:Task)`         |
| `APPLIED_TO_MODALITY`     | 方法应用于某个模态                 | `(:Method)-[:APPLIED_TO_MODALITY]->(:ImagingModality)` |
| ...                       | (及其他关系)                         |                                                  |

---

## 3. 如何连接与查询图谱

你可以使用 Python 和 `neo4j` 驱动包来连接数据库并执行 Cypher 查询。

### 3.1. 安装依赖

```bash
pip install neo4j
```
*(完整的依赖列表见 `neo4j_database/requirements.txt`)*

### 3.2. 设置环境变量

为了安全和方便，请将数据库的连接信息设置为环境变量。

```bash
export NEO4J_URI="<your-neo4j-uri>" # 例如: neo4j+s://xxx.databases.neo4j.io
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="<your-password>"
```

### 3.3. Python 连接示例

下面的代码演示了如何连接到 Neo4j 数据库并执行一个简单的查询。

```python
import os
from neo4j import GraphDatabase

# 从环境变量获取连接信息
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

class Neo4jConnection:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)

    def close(self):
        self.driver.close()

    def run_query(self, query, parameters=None):
        """
        执行一个 Cypher 查询并返回结果。
        """
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

# --- 使用示例 ---
if __name__ == "__main__":
    if not URI or not AUTH[1]:
        print("请确保 NEO4J_URI, NEO4J_USER 和 NEO4J_PASSWORD 环境变量已设置。")
    else:
        conn = Neo4jConnection(URI, AUTH)
        try:
            # 示例：查询图中总共有多少个 Paper 节点
            query = "MATCH (p:Paper) RETURN count(p) AS paper_count"
            result = conn.run_query(query)
            
            if result:
                print(f"查询成功！图中的论文总数是: {result[0]['paper_count']}")
            else:
                print("查询未返回结果。")

        except Exception as e:
            print(f"连接或查询时发生错误: {e}")
        finally:
            conn.close()
            print("数据库连接已关闭。")

```

---

## 4. 下游任务示例：基于 Embedding 的语义检索

所有节点都拥有 `embedding` 属性，可以利用 Neo4j 的向量索引进行语义相似度搜索。

**场景**：找到与某篇指定论文在语义上最相似的其他论文。

**前提**：需要在 Neo4j 中为 `Paper` 节点的 `embedding` 属性创建向量索引。

```cypher
// 在 Neo4j Browser 中执行一次即可
CREATE VECTOR INDEX paper_embeddings IF NOT EXISTS
FOR (p:Paper) ON (p.embedding) 
OPTIONS {indexConfig: {
 `vector.dimensions`: 768,
 `vector.similarity_function`: 'cosine'
}}
```

**查询**：假设我们要寻找与 `paper_id` 为 `paper_1859` 的论文最相似的 5 篇论文。

```python
# (在上面的 Neo4jConnection 类基础上)

target_paper_id = "paper_1859"

# 1. 首先获取目标论文的 embedding
get_embedding_query = """
MATCH (p:Paper {paper_id: $paper_id})
RETURN p.embedding AS embedding
"""
embedding_result = conn.run_query(get_embedding_query, {"paper_id": target_paper_id})

if not embedding_result:
    print(f"找不到 ID 为 {target_paper_id} 的论文")
else:
    target_embedding = embedding_result[0]['embedding']

    # 2. 使用向量索引执行相似度搜索
    similarity_query = """
    CALL db.index.vector.queryNodes('paper_embeddings', 5, $embedding) YIELD node AS similarPaper
    RETURN similarPaper.paper_id, similarPaper.title
    """
    
    similar_papers = conn.run_query(similarity_query, {"embedding": target_embedding})
    
    print(f"与 '{target_paper_id}' 最相似的论文:")
    for paper in similar_papers:
        print(f"  - ID: {paper['similarPaper.paper_id']}, Title: {paper['similarPaper.title']}")

```

这个例子展示了如何利用图谱中的向量嵌入来赋能语义应用，你可以将此方法扩展到**任务、方法**等其他节点，实现更复杂的下游功能。

---

## 5. 附录：如何重建知识图谱

如果需要从头开始重建图谱（例如，在数据源 `standard.json` 更新后），请遵循以下步骤。

1.  **进入工具目录**:
    ```bash
    cd neo4j_database
    ```

2.  **安装依赖**:
    ```bash
    # (如果尚未安装)
    pip install -r requirements.txt
    ```

3.  **运行主脚本**:
    ```bash
    # 这将按顺序执行：JSON转CSV -> 生成Embedding -> 质量检查 -> 统计
    python main.py
    ```

4.  **导入到 Neo4j**:
    - **方法A (推荐)**: 将 `neo4j_database/csv/` 目录下的所有 CSV 文件上传到 Neo4j 数据库的 `import` 文件夹中，然后在 Neo4j Browser 里执行 `cypher_scripts/import_nodes_and_relations.cypher`。
    - **方法B**: 参考 `neo4j_database/README.md` 使用 Python 脚本进行导入。

---

## 6. 目录结构

```
.
├── neo4j_database/         # 知识图谱构建的核心工具目录
│   ├── main.py             # -> 主流程执行脚本
│   ├── json_to_csv.py      # -> 1. JSON转CSV
│   ├── generate_embeddings.py # -> 2. 生成向量嵌入
│   ├── quality_check.py    # -> 3. 质量检查
│   ├── statistics.py       # -> 4. 统计分析
│   ├── csv/                # -> 存放生成的节点和关系CSV文件
│   └── cypher_scripts/     # -> 存放Neo4j导入和测试脚本
│
├── models/                 # 存放 bge-multilingual-gemma2 嵌入模型
├── standard.json           # (原始数据) 清洗后的结构化JSON
├── schema_v1.json          # (参考) 数据Schema定义
├── vocabulary.json         # (参考) 标准化词表
└── README.md               # (本文档) 下游任务开发指南
```
