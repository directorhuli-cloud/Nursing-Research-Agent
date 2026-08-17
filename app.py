from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from neo4j import GraphDatabase
import os
from typing import List, Dict
import uvicorn
from datetime import datetime
import time
import json

app = FastAPI(title="Nursing Research Agent")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# 🔑 API 配置
# ==============================
# Coze API 配置
COZE_API_TOKEN = os.getenv("COZE_API_TOKEN", "pat_G0ds4eP3r6L5USmt54VA402lBSG1RrorD4Ddo3wK1Uv8RMKX3sPHxEiwjIahRVok")
COZE_BASE_URL = "https://api.coze.com"
COZE_WORKFLOW_ID = os.getenv("COZE_WORKFLOW_ID", "7599959005917921285")
COZE_BOT_ID = os.getenv("COZE_BOT_ID", "")

# Neo4j 配置
URI = os.getenv("NEO4J_URI", "neo4j+s://b857a56f.databases.neo4j.io")
AUTH = (
    os.getenv("NEO4J_USERNAME", "neo4j"),
    os.getenv("NEO4J_PASSWORD", "bLu-cjcS06QjkLDmFCl1Dn_fdC1uiiCltXPUDgH9D90")
)
DATABASE_NAME = os.getenv("NEO4J_DATABASE", "neo4j")

# ==============================
# 🤖 Coze API 调用
# ==============================
def extract_text_from_json(obj):
    """从Coze API返回的JSON中提取文本内容"""
    if obj and isinstance(obj, dict):
        # Workflow API: data字段可能是JSON字符串，需要解析
        if obj.get('data') and isinstance(obj['data'], str):
            try:
                parsed_data = json.loads(obj['data'])
                if isinstance(parsed_data, dict) and parsed_data.get('output'):
                    output = parsed_data['output']
                    if isinstance(output, str) and output.strip():
                        return output
            except json.JSONDecodeError:
                # 如果data不是JSON，直接返回
                if obj['data'].strip():
                    return obj['data']
        
        # Workflow API: 直接查找output字段
        if obj.get('output') and isinstance(obj['output'], str) and obj['output'].strip():
            return obj['output']
        
        # Workflow API: 查找data.output（如果data已经是对象）
        if obj.get('data') and isinstance(obj['data'], dict) and obj['data'].get('output'):
            output = obj['data']['output']
            if isinstance(output, str) and output.strip():
                return output
        
        # 查找content字段
        if obj.get('content') and isinstance(obj['content'], str) and obj['content'].strip():
            return obj['content']
        
        # 查找messages数组中的内容（合并所有消息）
        if isinstance(obj.get('messages'), list):
            contents = []
            for msg in obj['messages']:
                if isinstance(msg, dict) and msg.get('type') == 'answer' and msg.get('content'):
                    content = msg['content']
                    if isinstance(content, str) and content.strip():
                        contents.append(content)
            if contents:
                return '\n\n'.join(contents)
        
        # 查找data字段（如果是对象）
        if obj.get('data') and isinstance(obj['data'], dict):
            result = extract_text_from_json(obj['data'])
            if result:
                return result
        
        # 查找result字段
        if obj.get('result') and isinstance(obj['result'], str) and obj['result'].strip():
            return obj['result']
        
        # 查找answer字段
        if obj.get('answer') and isinstance(obj['answer'], str) and obj['answer'].strip():
            return obj['answer']
        
        # 递归搜索其他字段，找到最长的文本（确保获取完整内容）
        skip_keys = ['id', 'conversation_id', 'bot_id', 'user_id', 'created_at', 'updated_at', 
                     'status', 'code', 'msg', 'logid', 'request_id', 'trace_id', 'timestamp', 'detail']
        longest_result = ''
        for key, value in obj.items():
            if key in skip_keys:
                continue
            result = extract_text_from_json(value)
            if result and isinstance(result, str) and len(result) > len(longest_result):
                longest_result = result
        
        if longest_result:
            return longest_result
    
    elif isinstance(obj, list):
        # 对于列表，合并所有找到的文本内容
        results = []
        for item in obj:
            result = extract_text_from_json(item)
            if result and isinstance(result, str) and result.strip():
                results.append(result)
        if results:
            return '\n\n'.join(results)
    
    return ''

def call_coze_workflow(message: str) -> str:
    """调用Coze Workflow API"""
    endpoint = f"{COZE_BASE_URL}/v1/workflow/run"
    
    headers = {
        "Authorization": f"Bearer {COZE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "workflow_id": COZE_WORKFLOW_ID,
        "parameters": {
            "input": message
        }
    }
    
    # 如果提供了bot_id，添加到payload中
    if COZE_BOT_ID:
        payload["bot_id"] = COZE_BOT_ID
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=120)  # 增加超时时间到120秒
        response.raise_for_status()
        
        # 检查响应内容长度
        content_length = len(response.content)
        print(f"📦 Coze API 响应大小: {content_length} 字节")
        
        # 解析响应
        result = response.json()
        
        # 🔍 调试：打印 Coze API 原始响应
        print("=" * 80)
        print("🔍 Coze API 原始响应:")
        # 如果响应太大，只打印结构信息
        result_str = json.dumps(result, ensure_ascii=False, indent=2)
        if len(result_str) > 5000:
            print(f"   响应太大 ({len(result_str)} 字符)，只打印结构:")
            print(f"   响应类型: {type(result)}")
            if isinstance(result, dict):
                print(f"   响应键: {list(result.keys())}")
                # 打印每个键的大小
                for key, value in result.items():
                    if isinstance(value, str):
                        print(f"   {key}: {len(value)} 字符")
                    elif isinstance(value, (dict, list)):
                        print(f"   {key}: {type(value).__name__} (大小: {len(str(value))} 字符)")
        else:
            print(result_str)
        print("=" * 80)
        
        # 检查是否有错误
        if isinstance(result, dict) and result.get('code') and result['code'] != 0:
            error_msg = result.get('msg', 'Unknown error')
            raise Exception(f"Coze API Error ({result['code']}): {error_msg}")
        
        # 提取文本内容
        text = extract_text_from_json(result)
        
        # 🔍 调试：打印提取后的文本内容
        print("=" * 80)
        print("📝 提取后的文本内容:")
        print(f"   总长度: {len(text)} 字符")
        if len(text) > 0:
            print(f"   前500字符: {text[:500]}")
            if len(text) > 1000:
                print(f"   ... (中间省略 {len(text) - 1000} 字符) ...")
                print(f"   后500字符: {text[-500:]}")
            elif len(text) > 500:
                print(f"   剩余字符: {text[500:]}")
        print("=" * 80)
        
        if text and text.strip():
            return text.strip()
        else:
            # 如果无法提取文本，返回原始响应的字符串表示
            return json.dumps(result, ensure_ascii=False, indent=2)
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Coze API请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"错误详情: {error_detail}")
            except:
                print(f"错误响应: {e.response.text}")
        raise Exception(f"Coze API请求失败: {str(e)}")
    except Exception as e:
        print(f"❌ Coze API调用异常: {e}")
        raise

# ==============================
# 🧩 Neo4j 知识图谱
# ==============================
driver = GraphDatabase.driver(URI, auth=AUTH)

def execute_query(query_text):
    """执行 Neo4j 查询"""
    from neo4j.exceptions import Neo4jError
    result_str = ""

    def format_relationships(relationships, current_node_name):
        if not relationships or (isinstance(relationships, list) and len(relationships) == 0):
            return []
        formatted = []
        for rel in relationships:
            if isinstance(rel, dict) and rel.get('关联节点名称'):
                direction = rel.get('关系方向', '')
                rel_type = rel.get('关系类型', '')
                node_type = rel.get('关联节点', '')
                node_name = rel.get('关联节点名称', '')
                arrow = "-->" if direction == '出向' else "<--" if direction == '入向' else "--"
                formatted.append(f"{current_node_name} {arrow}[{rel_type}] {node_type}({node_name})")
        return formatted

    try:
        # 生成 Cypher
        cypher_query = natural_language_query(query_text)
        print(f"🔍 生成的Cypher查询: {cypher_query}")
        
        records, summary, keys = driver.execute_query(cypher_query, database_=DATABASE_NAME)
        print(f"📊 查询返回记录数: {len(records) if records else 0}")
        
        if not records:
            return "知识图谱中没有找到相关结果。"

        for i, record in enumerate(records, 1):
            data = record.data()
            node_name = data.get('节点名称', data.get('节点类型', '未知节点'))
            node_type = data.get('节点类型', '')
            result_str += f"{i}. 【{node_name}】({node_type})\n"

            for key, value in data.items():
                if key not in ['节点名称', '节点类型', '出向关系', '入向关系'] and value:
                    if isinstance(value, list):
                        result_str += f"   {key}: {', '.join(map(str, value))}\n"
                    else:
                        result_str += f"   {key}: {value}\n"

            # 添加关系
            all_rels = []
            if '出向关系' in data:
                all_rels.extend(format_relationships(data['出向关系'], node_name))
            if '入向关系' in data:
                all_rels.extend(format_relationships(data['入向关系'], node_name))
            if all_rels:
                result_str += "   【关联关系】\n"
                for rel in all_rels:
                    result_str += f"   • {rel}\n"
            result_str += "\n"

        return result_str

    except Neo4jError as e:
        print(f"❌ Neo4j查询错误: {e}")
        return f"Neo4j 查询错误: {e}"
    except Exception as e:
        print(f"❌ 知识图谱查询异常: {e}")
        return f"知识图谱查询异常: {e}"

def natural_language_query(query_text):
    """使用提取的关键词进行知识图谱查询"""
    query_text = query_text.lower().strip()
    
    # 将关键词分割成列表
    keywords = [kw.strip() for kw in query_text.split(',') if kw.strip()]
    
    # 构建查询条件
    where_conditions = []
    for keyword in keywords:
        keyword = keyword.strip()
        if keyword:
            where_conditions.append(f"toLower(n.name) CONTAINS toLower('{keyword}')")
            where_conditions.append(f"toLower(n.definition) CONTAINS toLower('{keyword}')")
            where_conditions.append(f"toLower(n.description) CONTAINS toLower('{keyword}')")
    
    if not where_conditions:
        return "MATCH (n) RETURN n.name AS 节点名称, labels(n)[0] AS 节点类型 LIMIT 5"
    
    where_clause = " OR ".join(where_conditions)
    
    return f"""
    MATCH (n)
    WHERE {where_clause}
    OPTIONAL MATCH (n)-[r1]->(related1)
    OPTIONAL MATCH (related2)-[r2]->(n)
    RETURN n.name AS 节点名称, 
           labels(n)[0] AS 节点类型, 
           n.definition AS 定义, 
           n.description AS 描述,
           collect(DISTINCT CASE WHEN r1 IS NOT NULL THEN {{关系方向: '出向', 关系类型: type(r1), 关联节点: labels(related1)[0], 关联节点名称: related1.name}} END) AS 出向关系,
           collect(DISTINCT CASE WHEN r2 IS NOT NULL THEN {{关系方向: '入向', 关系类型: type(r2), 关联节点: labels(related2)[0], 关联节点名称: related2.name}} END) AS 入向关系
    LIMIT 10
    """

# ==============================
# FastAPI 路由
# ==============================
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/")
async def read_root():
    """返回前端页面"""
    return FileResponse("index.html")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理聊天请求 - 直接调用Coze API"""
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        user_question = request.message.strip()
        if not user_question:
            raise HTTPException(status_code=400, detail="消息不能为空")
        
        print("=" * 80)
        print(f"📥 [{timestamp}] 收到用户问题:")
        print(f"   问题: {user_question}")
        print("=" * 80)
        
        # 直接调用Coze Workflow
        step_start = time.time()
        response_text = call_coze_workflow(user_question)
        step_time = time.time() - step_start
        
        total_time = time.time() - start_time
        print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Coze API调用完成 (耗时: {step_time:.2f}s)")
        print("=" * 80)
        print(f"📤 [{datetime.now().strftime('%H:%M:%S')}] 返回回复:")
        print(f"   回复长度: {len(response_text)} 字符")
        print(f"   总耗时: {total_time:.2f}s")
        print("=" * 80)
        print()
        
        return ChatResponse(response=response_text)
        
    except Exception as e:
        error_time = datetime.now().strftime("%H:%M:%S")
        total_time = time.time() - start_time
        print("=" * 80)
        print(f"❌ [{error_time}] 发生错误!")
        print(f"   错误信息: {str(e)}")
        print(f"   总耗时: {total_time:.2f}s")
        print("=" * 80)
        print()
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@app.get("/cards")
async def get_cards():
    """从 Neo4j 图谱动态生成知识卡片"""
    try:
        query = """
        MATCH (n)
        WITH DISTINCT labels(n)[0] AS label, collect(DISTINCT n.name) AS nodes
        RETURN label, nodes 
        ORDER BY label
        LIMIT 20
        """
        records, summary, keys = driver.execute_query(query, database_=DATABASE_NAME)
        
        cards = []
        for record in records:
            data = record.data()
            label = data.get("label", "")
            nodes = data.get("nodes", [])
            
            # 过滤空节点名
            nodes = [n for n in nodes if n and n.strip()]
            if not nodes:
                continue
                
            cards.append({
                "label": label,
                "nodes": nodes[:10]  # 限制最多显示10个节点
            })
        
        print(f"📚 生成了 {len(cards)} 个知识卡片类别")
        return cards
        
    except Exception as e:
        print(f"❌ 获取知识卡片失败: {e}")
        return {"error": str(e)}

@app.get("/search")
async def search_knowledge(query: str):
    """在知识图谱中搜索相关知识"""
    try:
        search_query = f"""
        MATCH (n)
        WHERE toLower(n.name) CONTAINS toLower('{query}') 
           OR toLower(n.definition) CONTAINS toLower('{query}')
           OR toLower(n.description) CONTAINS toLower('{query}')
        RETURN n.name AS name, labels(n)[0] AS label, n.definition AS definition
        LIMIT 20
        """
        
        records, summary, keys = driver.execute_query(search_query, database_=DATABASE_NAME)
        
        results = []
        for record in records:
            data = record.data()
            results.append({
                "name": data.get("name", ""),
                "label": data.get("label", ""),
                "definition": data.get("definition", "")
            })
        
        print(f"🔍 搜索 '{query}' 找到 {len(results)} 个结果")
        return results
        
    except Exception as e:
        print(f"❌ 知识图谱搜索失败: {e}")
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "message": "Nursing Research Agent is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
