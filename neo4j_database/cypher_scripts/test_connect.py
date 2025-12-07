from neo4j import GraphDatabase
import sys

# 填入你的信息
URI = "neo4j+s://e96b056a.databases.neo4j.io"
AUTH = ("neo4j", "l_Xozo1gLym66VVmHMXa9WMNmpju9uUsScSXtYy-elc") 

try:
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        print("✅ 连接成功！密码正确，封禁已解除。")
        print("🚀 现在可以去运行你的导入脚本了。")
except Exception as e:
    print("❌ 连接失败！")
    print(e)
    print("\n⚠️ 如果提示 Unauthorized，说明密码还是错的。")
    print("⚠️ 如果提示 RateLimit，说明还需要再多等一会儿。")