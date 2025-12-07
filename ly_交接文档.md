# 📘 **TMI 知识图谱项目 —— 数据情况 & 标准化交接说明**

本文档用于介绍我目前完成的工作：

---

# #️⃣ 1. 我负责的数据部分是什么？

我负责本项目的 **数据层**，目前已达成：

✔ 建立 **统一的 Schema（字段规范）**
✔ 对所有 JSON 进行 **格式标准化 / 质量检查 / 词表校准**

---

# #️⃣ 2. 当前数据的来源是什么？

我已经使用大模型（LLM）编写了一套**结构化信息抽取 Prompt**（如下节）
从 TMI 文献的：

* 标题
* 摘要
* 类别（大模型+人工标注）
* 年份等基础信息

自动抽取成一个结构化 JSON，每个 JSON 对应一篇论文。

示例（已抽取）：

```json
{
    "paper_id": "paper_1859",
    "title": "...",
    "doi": "...",
    "year": 2019,
    "category": "图像重建-PET/SPECT",
    "tasks": ["重建"],
    "imaging_modalities": ["SPECT"],
    "methods": [{"name": "Higher-Order Polynomial Method", "type": "方法"}],
    "metrics": [ ... ],
    "innovations": [ ... ],
    "relations": [ ... ]
}
```

总数据规模：**1960 篇**。

---

# #️⃣ 3. 我使用的 LLM 抽取 Prompt


我对 LLM 的要求是：

* 必须遵循我们定义的 Schema
* 不能编造不存在的信息
* 所有实体字段必须来自词表（task 词表 / 模态词表 / 解剖词表）

该 Prompt 完整地定义了：

### ✔ 我们的实体类型

* **任务**（task）
* **成像模态**（modality）
* 方法（method）
* 数据集（dataset）
* **解剖结构**（structure）
* 指标（metric）
* 创新点（innovation）

### ✔ 我们的关系类型

例如：

* DESIGNED_FOR_TASK
* USES_MODALITY
* ACHIEVES_METRIC
* ……

### ✔ 如何从论文内容提取这些关系

如“方法 X 用于任务 Y → DESIGNED_FOR_TASK”。

### ✔ 如何确保统一命名

所有模态、任务、结构都必须来自**给定词表**，避免产生重复概念。


---

# #️⃣ 4. 当前 JSON 数据的特点（需要团队知道）

根据目前抽取结果，总体情况如下：


* JSON 结构完整统一
* 所有任务、模态、结构已受词表约束
* 每篇论文都包含**关系**（relations），便于图谱构建
* 无编造信息（空的就为空数组）

---

# #️⃣ 5. 接下来的工作


### 🟧 **图谱搭建**

输入：我提供的 **standard_json**
任务：

* 将 JSON → 节点表 CSV / 关系 CSV
* 写 Cypher 脚本导入到 Neo4j
* 图谱质量检查（是否有重复节点）
* 节点统计、结构验证

最终输出：

```
neo4j_database/
cypher_scripts/
csv/
```

---

### 🟩 **下游应用**

输入：Neo4j 图谱
任务：

* 编写核心查询（Cypher Templates）
* 对外提供 REST API（FastAPI）
* 构建 QA / 检索 / 推荐系统
* 做图谱可视化（Bloom/GraphXR）

---

# #️⃣ 6. 总结：我的交付方式？

我最终交付以下内容：

```
1. schema_v1.json     （定义所有实体字段、命名规则）
2. vocabulary.json     （task/modality/method/structure 标准词表）
3. standard_json/      （全部清洗后的 JSON）
```

其中：

* 可直接用 standard_json → 生成图谱
* 后续下游同学用标准命名的实体名称编写查询模板


---
