// Neo4j 导入脚本
// 使用方法: 在 Neo4j Browser 或 cypher-shell 中执行此脚本
// 或者使用: cypher-shell -u neo4j -p password -f import_nodes_and_relations.cypher

// ============================================
// 1. 清理数据库（可选，谨慎使用）
// ============================================
// MATCH (n) DETACH DELETE n;

// ============================================
// 2. 创建索引和约束
// ============================================

// Paper 节点约束和索引
CREATE CONSTRAINT paper_id IF NOT EXISTS FOR (p:Paper) REQUIRE p.id IS UNIQUE;
CREATE INDEX paper_title IF NOT EXISTS FOR (p:Paper) ON (p.title);

// Task 节点约束和索引
CREATE CONSTRAINT task_id IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE;
CREATE INDEX task_name IF NOT EXISTS FOR (t:Task) ON (t.name);

// ImagingModality 节点约束和索引
CREATE CONSTRAINT modality_id IF NOT EXISTS FOR (m:ImagingModality) REQUIRE m.id IS UNIQUE;
CREATE INDEX modality_name IF NOT EXISTS FOR (m:ImagingModality) ON (m.name);

// AnatomicalStructure 节点约束和索引
CREATE CONSTRAINT structure_id IF NOT EXISTS FOR (s:AnatomicalStructure) REQUIRE s.id IS UNIQUE;
CREATE INDEX structure_name IF NOT EXISTS FOR (s:AnatomicalStructure) ON (s.name);

// Method 节点约束和索引
CREATE CONSTRAINT method_id IF NOT EXISTS FOR (m:Method) REQUIRE m.id IS UNIQUE;
CREATE INDEX method_name IF NOT EXISTS FOR (m:Method) ON (m.name);

// Dataset 节点约束和索引
CREATE CONSTRAINT dataset_id IF NOT EXISTS FOR (d:Dataset) REQUIRE d.id IS UNIQUE;
CREATE INDEX dataset_name IF NOT EXISTS FOR (d:Dataset) ON (d.name);

// Metric 节点约束和索引
CREATE CONSTRAINT metric_id IF NOT EXISTS FOR (m:Metric) REQUIRE m.id IS UNIQUE;
CREATE INDEX metric_name IF NOT EXISTS FOR (m:Metric) ON (m.name);

// Innovation 节点约束和索引
CREATE CONSTRAINT innovation_id IF NOT EXISTS FOR (i:Innovation) REQUIRE i.id IS UNIQUE;
CREATE INDEX innovation_description IF NOT EXISTS FOR (i:Innovation) ON (i.description);

// ============================================
// 3. 导入节点
// ============================================

// 导入 Paper 节点
LOAD CSV WITH HEADERS FROM 'file:///nodes_Paper.csv' AS row
CREATE (p:Paper {
    id: row.id,
    paper_id: row.paper_id,
    title: row.title,
    doi: row.doi,
    year: CASE WHEN row.year <> '' THEN toInteger(row.year) ELSE null END,
    category: row.category,
    authors: row.authors,
    embedding: CASE WHEN row.embedding <> '' THEN [x IN split(row.embedding, ',') | toFloat(x)] ELSE [] END
});

// 导入 Task 节点
LOAD CSV WITH HEADERS FROM 'file:///nodes_Task.csv' AS row
CREATE (t:Task {
    id: row.id,
    name: row.name,
    type: row.type,
    embedding: CASE WHEN row.embedding <> '' THEN [x IN split(row.embedding, ',') | toFloat(x)] ELSE [] END
});

// 导入 ImagingModality 节点
LOAD CSV WITH HEADERS FROM 'file:///nodes_ImagingModality.csv' AS row
CREATE (m:ImagingModality {
    id: row.id,
    name: row.name,
    type: row.type,
    embedding: CASE WHEN row.embedding <> '' THEN [x IN split(row.embedding, ',') | toFloat(x)] ELSE [] END
});

// 导入 AnatomicalStructure 节点
LOAD CSV WITH HEADERS FROM 'file:///nodes_AnatomicalStructure.csv' AS row
CREATE (s:AnatomicalStructure {
    id: row.id,
    name: row.name,
    type: row.type,
    embedding: CASE WHEN row.embedding <> '' THEN [x IN split(row.embedding, ',') | toFloat(x)] ELSE [] END
});

// 导入 Method 节点
LOAD CSV WITH HEADERS FROM 'file:///nodes_Method.csv' AS row
CREATE (m:Method {
    id: row.id,
    name: row.name,
    method_type: row.method_type,
    type: row.type,
    embedding: CASE WHEN row.embedding <> '' THEN [x IN split(row.embedding, ',') | toFloat(x)] ELSE [] END
});

// 导入 Dataset 节点
LOAD CSV WITH HEADERS FROM 'file:///nodes_Dataset.csv' AS row
CREATE (d:Dataset {
    id: row.id,
    name: row.name,
    type: row.type,
    embedding: CASE WHEN row.embedding <> '' THEN [x IN split(row.embedding, ',') | toFloat(x)] ELSE [] END
});

// 导入 Metric 节点
LOAD CSV WITH HEADERS FROM 'file:///nodes_Metric.csv' AS row
CREATE (m:Metric {
    id: row.id,
    name: row.name,
    type: row.type,
    embedding: CASE WHEN row.embedding <> '' THEN [x IN split(row.embedding, ',') | toFloat(x)] ELSE [] END
});

// 导入 Innovation 节点
LOAD CSV WITH HEADERS FROM 'file:///nodes_Innovation.csv' AS row
CREATE (i:Innovation {
    id: row.id,
    description: row.description,
    innovation_type: row.innovation_type,
    type: row.type,
    embedding: CASE WHEN row.embedding <> '' THEN [x IN split(row.embedding, ',') | toFloat(x)] ELSE [] END
});

// ============================================
// 4. 导入关系
// ============================================

// 方法 1: 使用 APOC 插件（推荐，如果已安装）
// LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
// MATCH (from {id: row.from_id})
// MATCH (to {id: row.to_id})
// CALL apoc.create.relationship(from, row.type, {
//     value: CASE WHEN row.value <> '' THEN toFloat(row.value) ELSE null END,
//     note: row.note
// }, to) YIELD rel
// RETURN count(rel) AS relationships_created;

// 方法 2: 为每种关系类型单独导入（推荐，无需 APOC）
// ADDRESSES_TASK
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
WHERE row.type = 'ADDRESSES_TASK'
MATCH (from {id: row.from_id})
MATCH (to {id: row.to_id})
MERGE (from)-[r:ADDRESSES_TASK]->(to)
SET r.value = CASE WHEN row.value <> '' THEN toFloat(row.value) ELSE null END,
    r.note = row.note;

// USES_MODALITY
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
WHERE row.type = 'USES_MODALITY'
MATCH (from {id: row.from_id})
MATCH (to {id: row.to_id})
MERGE (from)-[r:USES_MODALITY]->(to)
SET r.value = CASE WHEN row.value <> '' THEN toFloat(row.value) ELSE null END,
    r.note = row.note;

// FOCUSES_ON_STRUCTURE
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
WHERE row.type = 'FOCUSES_ON_STRUCTURE'
MATCH (from {id: row.from_id})
MATCH (to {id: row.to_id})
MERGE (from)-[r:FOCUSES_ON_STRUCTURE]->(to)
SET r.value = CASE WHEN row.value <> '' THEN toFloat(row.value) ELSE null END,
    r.note = row.note;

// PROPOSES_METHOD
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
WHERE row.type = 'PROPOSES_METHOD'
MATCH (from {id: row.from_id})
MATCH (to {id: row.to_id})
MERGE (from)-[r:PROPOSES_METHOD]->(to)
SET r.value = CASE WHEN row.value <> '' THEN toFloat(row.value) ELSE null END,
    r.note = row.note;

// USES_DATASET
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
WHERE row.type = 'USES_DATASET'
MATCH (from {id: row.from_id})
MATCH (to {id: row.to_id})
MERGE (from)-[r:USES_DATASET]->(to)
SET r.value = CASE WHEN row.value <> '' THEN toFloat(row.value) ELSE null END,
    r.note = row.note;

// REPORTS_METRIC
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
WHERE row.type = 'REPORTS_METRIC'
MATCH (from {id: row.from_id})
MATCH (to {id: row.to_id})
MERGE (from)-[r:REPORTS_METRIC]->(to)
SET r.value = CASE WHEN row.value <> '' THEN toFloat(row.value) ELSE null END,
    r.note = row.note;

// HAS_INNOVATION
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
WHERE row.type = 'HAS_INNOVATION'
MATCH (from {id: row.from_id})
MATCH (to {id: row.to_id})
MERGE (from)-[r:HAS_INNOVATION]->(to)
SET r.value = CASE WHEN row.value <> '' THEN toFloat(row.value) ELSE null END,
    r.note = row.note;

// DESIGNED_FOR_TASK
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
WHERE row.type = 'DESIGNED_FOR_TASK'
MATCH (from {id: row.from_id})
MATCH (to {id: row.to_id})
MERGE (from)-[r:DESIGNED_FOR_TASK]->(to)
SET r.value = CASE WHEN row.value <> '' THEN toFloat(row.value) ELSE null END,
    r.note = row.note;

// APPLIED_TO_MODALITY
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
WHERE row.type = 'APPLIED_TO_MODALITY'
MATCH (from {id: row.from_id})
MATCH (to {id: row.to_id})
MERGE (from)-[r:APPLIED_TO_MODALITY]->(to)
SET r.value = CASE WHEN row.value <> '' THEN toFloat(row.value) ELSE null END,
    r.note = row.note;

// APPLIED_TO_STRUCTURE
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
WHERE row.type = 'APPLIED_TO_STRUCTURE'
MATCH (from {id: row.from_id})
MATCH (to {id: row.to_id})
MERGE (from)-[r:APPLIED_TO_STRUCTURE]->(to)
SET r.value = CASE WHEN row.value <> '' THEN toFloat(row.value) ELSE null END,
    r.note = row.note;

// EVALUATED_ON
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
WHERE row.type = 'EVALUATED_ON'
MATCH (from {id: row.from_id})
MATCH (to {id: row.to_id})
MERGE (from)-[r:EVALUATED_ON]->(to)
SET r.value = CASE WHEN row.value <> '' THEN toFloat(row.value) ELSE null END,
    r.note = row.note;

// ACHIEVES_METRIC
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
WHERE row.type = 'ACHIEVES_METRIC'
MATCH (from {id: row.from_id})
MATCH (to {id: row.to_id})
MERGE (from)-[r:ACHIEVES_METRIC]->(to)
SET r.value = CASE WHEN row.value <> '' THEN toFloat(row.value) ELSE null END,
    r.note = row.note;

// ============================================
// 5. 创建关系索引（可选，提升查询性能）
// ============================================
// CREATE INDEX rel_type IF NOT EXISTS FOR ()-[r:ADDRESSES_TASK]-() ON (r.type);
// CREATE INDEX rel_type IF NOT EXISTS FOR ()-[r:USES_MODALITY]-() ON (r.type);
// ... 其他关系类型

// ============================================
// 6. 验证导入结果
// ============================================
MATCH (n)
RETURN labels(n)[0] AS nodeType, count(n) AS count
ORDER BY nodeType;

MATCH ()-[r]->()
RETURN type(r) AS relationshipType, count(r) AS count
ORDER BY relationshipType;

