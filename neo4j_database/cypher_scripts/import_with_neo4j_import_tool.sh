#!/bin/bash
# Neo4j 批量导入脚本（使用 neo4j-admin import 工具）
# 适用于 Neo4j 4.x/5.x
# 使用方法: ./import_with_neo4j_import_tool.sh

# 配置 Neo4j 路径（根据实际安装路径修改）
NEO4J_HOME="${NEO4J_HOME:-/var/lib/neo4j}"
NEO4J_DB_DIR="${NEO4J_DB_DIR:-$NEO4J_HOME/data/databases/neo4j}"
NEO4J_IMPORT_DIR="${NEO4J_IMPORT_DIR:-$NEO4J_HOME/import}"

# CSV 文件目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV_DIR="$SCRIPT_DIR/../csv"

echo "=========================================="
echo "Neo4j 批量导入工具"
echo "=========================================="
echo "CSV 目录: $CSV_DIR"
echo "Neo4j 导入目录: $NEO4J_IMPORT_DIR"
echo ""

# 检查 CSV 文件是否存在
if [ ! -d "$CSV_DIR" ]; then
    echo "❌ 错误: CSV 目录不存在: $CSV_DIR"
    exit 1
fi

# 复制 CSV 文件到 Neo4j import 目录
echo "📋 复制 CSV 文件到 Neo4j import 目录..."
mkdir -p "$NEO4J_IMPORT_DIR"
cp "$CSV_DIR"/*.csv "$NEO4J_IMPORT_DIR/"

echo "✅ CSV 文件已复制"
echo ""
echo "📝 请按照以下步骤操作:"
echo "1. 停止 Neo4j 服务"
echo "2. 在 Neo4j Browser 或 cypher-shell 中执行:"
echo "   :source $SCRIPT_DIR/import_nodes_and_relations.cypher"
echo ""
echo "或者使用 cypher-shell:"
echo "   cypher-shell -u neo4j -p <password> -f $SCRIPT_DIR/import_nodes_and_relations.cypher"
echo ""
echo "注意: 如果使用 Neo4j Cloud，请通过 Web UI 上传 CSV 文件并使用 LOAD CSV 命令"

