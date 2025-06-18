# SystemPromptManager.py
from database import db
from elasticsearch import Elasticsearch
import time
from bson import ObjectId

system_prompts_collection = db["system_prompts"]
es = Elasticsearch("http://localhost:9200")  # 如果有验证，添加 basic_auth 参数

async def save_system_prompt(user_id, agent_id, title, prompt_text):
    document = {
        "user_id": user_id,
        "agent_id": agent_id,
        "title": title,
        "prompt": prompt_text,
        "timestamp": time.time()
    }
    result = await system_prompts_collection.insert_one(document)

    # Elasticsearch 插入
    es.index(index="system_prompts", id=str(result.inserted_id), document={
        "user_id": str(user_id),
        "agent_id": agent_id,
        "title": title,
        "prompt": prompt_text,
        "timestamp": document["timestamp"]
    })

    return {"success": True, "prompt_id": str(result.inserted_id)}

async def search_system_prompts(query, user_id=None, agent_id=None, size=10):
    must_conditions = [
        {
            "multi_match": {
                "query": query,
                "fields": ["title", "prompt"]
            }
        }
    ]

    if user_id:
        must_conditions.append({"term": {"user_id": str(user_id)}})

    if agent_id:
        must_conditions.append({"term": {"agent_id": agent_id}})

    body = {
        "query": {
            "bool": {
                "must": must_conditions
            }
        },
        "size": size
    }

    results = es.search(index="system_prompts", body=body)
    hits = results.get("hits", {}).get("hits", [])
    return [
        {
            "agent_id": hit["_source"]["agent_id"],
            "title": hit["_source"]["title"],
            "prompt": hit["_source"]["prompt"],
            "timestamp": hit["_source"]["timestamp"],
            "id": hit["_id"]
        }
        for hit in hits
    ]
