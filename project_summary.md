# 项目总结：基于科研文献的知识图谱构建与应用

本文档是对当前项目状态的全面总结，旨在帮助团队成员快速了解项目的数据、流程和目标。

---

## 1. 项目概述

本项目的核心目标是**从TMI（医学影像领域）的科研文献中抽取结构化信息，构建一个知识图谱**，并以此为基础支持下游的智能应用，如问答（QA）、内容检索和推荐系统。

项目目前完成了**数据层**的建设和**图谱自动化构建**工具链的开发。

---

## 2. 数据层详解

### 2.1. 数据来源

数据来源于 **1960 篇 TMI 科研论文**。通过一个定制的**大语言模型（LLM）抽取 Prompt**，从每篇论文的标题、摘要、类别等信息中自动抽取出结构化的 JSON 数据。

### 2.2. Schema（数据结构）

为了保证数据的一致性，项目定义了统一的 Schema 和标准词表。

#### 实体（节点）类型

- **Paper**: 论文本身。
- **Task**: 论文研究的任务（如：图像重建、分割）。
- **ImagingModality**: 成像模态（如：MRI, CT, PET）。
- **AnatomicalStructure**: 解剖结构（如：大脑, 肝脏）。
- **Method**: 论文中提出的方法。
- **Dataset**: 使用的数据集。
- **Metric**: 评估指标。
- **Innovation**: 论文的核心创新点。

#### 关系（边）类型

- `ADDRESSES_TASK`: 论文 → 任务
- `USES_MODALITY`: 论文 → 成像模态
- `PROPOSES_METHOD`: 论文 → 方法
- `DESIGNED_FOR_TASK`: 方法 → 任务
- ... 以及其他多种关系。

### 2.3. 交付产物

数据层的工作最终交付了三个核心文件：

- `schema_v1.json`: 定义了所有字段和命名规则。
- `vocabulary.json`: 包含了任务、模态、解剖结构等实体的标准词表，用于校准和统一命名。
- `standard.json`: 经过清洗、格式化和校准后的最终版 JSON 数据，作为知识图谱构建的直接输入。

---

## 3. 知识图谱构建流程

项目提供了一套位于 `neo4j_database/` 目录下的自动化脚本，用于将 `standard.json` 中的数据构建为 Neo4j 图谱。

### 3.1. 核心步骤

完整的构建流程由 `main.py` 脚本统一调度，具体步骤如下：

1.  **JSON 转 CSV (`json_to_csv.py`)**:
    - 读取 `standard.json` 文件。
    - 将数据转换为节点表（`nodes_*.csv`）和关系表（`relations.csv`）。
    - 在此过程中自动对节点进行去重，确保唯一性。

2.  **生成向量嵌入 (`generate_embeddings.py`)**:
    - 使用 **`BAAI/bge-multilingual-gemma2`** 模型为所有节点生成高质量的向量嵌入（Embeddings）。
    - 这些嵌入对于后续的语义检索、问答等下游任务至关重要。
    - 脚本会自动将生成的 `embedding` 列更新到对应的节点 CSV 文件中。

3.  **质量检查 (`quality_check.py`)**:
    - 对生成的 CSV 数据进行质量检查，例如：
      - 检测重复节点。
      - 发现孤立节点（没有连接关系的节点）。
      - 验证关系的完整性。
    - 生成一份 `quality_report.json` 报告。

4.  **统计分析 (`statistics.py`)**:
    - 对图谱的结构和内容进行统计，例如：
      - 各类型节点的数量。
      - 关系类型的分布情况。
      - 节点的连接度分析。
    - 生成一份 `statistics_report.json` 报告。

### 3.2. 如何运行

```bash
# 进入 neo4j_database 目录
cd neo4j_database

# 安装依赖
pip install -r requirements.txt

# 运行完整流程
python main.py
```

### 3.3. 导入 Neo4j

数据处理完成后，`csv/` 目录包含了所有导入所需的文件。可以通过以下方式导入 Neo4j：

- **Cypher 脚本（推荐）**: 将 CSV 文件上传至 Neo4j 的 `import` 目录，然后执行 `cypher_scripts/import_nodes_and_relations.cypher` 脚本。
- **Python 脚本**: 使用 `cypher_scripts/import_to_cloud.py` 连接到 Neo4j 实例（云或本地）并执行导入。

---

## 4. 文件与目录结构解析

- `ly_交接文档.md`: 项目初期的数据层交接文档，详细说明了数据来源和标准化过程。
- `schema_v1.json`: 定义数据结构的权威文件。
- `vocabulary.json`: 标准化命名词汇表。
- `standard.json`: (推测存在) 经过处理后的标准数据，是图谱构建的输入。
- `models/`: 存放用于生成嵌入的 `bge-multilingual-gemma2` 模型。
- `neo4j_database/`: 核心的图谱构建工具目录。
  - `main.py`: 主执行脚本。
  - `json_to_csv.py`: 数据转换脚本。
  - `generate_embeddings.py`: 向量嵌入生成脚本。
  - `quality_check.py` / `statistics.py`: 数据质量与统计脚本。
  - `csv/`: 生成的用于导入 Neo4j 的数据文件。
  - `cypher_scripts/`: Neo4j 导入脚本。
  - `README.md`: `neo4j_database` 工具的详细使用说明。

---

## 5. 后续工作（下游应用）

根据交接文档的规划，在知识图谱构建完成之后，接下来的工作重点是**开发下游应用**，包括：

- **提供 API 服务**: 使用 FastAPI 等框架将图谱查询能力封装成 REST API。
- **开发问答（QA）系统**: 结合图谱和检索技术，回答用户关于科研文献的自然语言问题。
- **图谱可视化**: 使用 Neo4j Bloom 等工具对图谱进行可视化探索。
