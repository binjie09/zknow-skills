#!/usr/bin/env python3
"""
YQCloud 知识库查询工具。

从燕千云知识库检索与问题相关的知识片段。
依赖 ~/.yqcloud_tmp/token.json 中的 access_token。
"""

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://api.yqcloud.com/ai/v1/228549383619211264/aigc_knowledge/chunks"
TENANT_ID = "228549383619211264"
TOKEN_FILE = Path.home() / ".yqcloud_tmp" / "token.json"


def load_token():
    """读取本地存储的 access_token。"""
    if not TOKEN_FILE.exists():
        print("[ERROR] Token 文件不存在: ~/.yqcloud_tmp/token.json")
        print("[INFO]  请先运行 yqcloud-login-auth 进行登录认证")
        sys.exit(1)

    data = json.loads(TOKEN_FILE.read_text())
    token = data.get("access_token")
    if not token:
        print("[ERROR] Token 文件中没有 access_token")
        sys.exit(1)
    return token


def query(question, top=5):
    """查询知识库，返回相关知识片段。"""
    token = load_token()

    params = urllib.parse.urlencode({"question": question, "top": top})
    url = f"{API_BASE}?{params}"

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"bearer {token}",
            "x-tenant-id": TENANT_ID,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status == 200:
                return json.loads(resp.read())
            else:
                body = resp.read().decode("utf-8", errors="replace")
                print(f"[ERROR] API 返回 {resp.status}: {body}")
                sys.exit(1)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("[ERROR] Token 已过期或无效 (401)")
            print("[INFO]  请重新运行 yqcloud-login-auth 进行登录认证")
            sys.exit(1)
        body = e.read().decode("utf-8", errors="replace")
        print(f"[ERROR] API 返回 {e.code}: {body}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
        sys.exit(1)


def format_output(result, question):
    """格式化输出查询结果。"""
    print(f"查询: {question}")
    print("=" * 60)

    if isinstance(result, list):
        chunks = result
    elif isinstance(result, dict):
        chunks = result.get("content") or result.get("chunks") or result.get("data") or []
        if isinstance(chunks, dict):
            chunks = chunks.get("content") or chunks.get("chunks") or [chunks]
    else:
        chunks = []

    if not chunks:
        print("未找到相关知识片段。")
        print("\n原始响应:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- 片段 {i} ---")

        # 尝试多种字段名
        content = (
            chunk.get("content")
            or chunk.get("text")
            or chunk.get("chunk_content")
            or chunk.get("answer")
            or ""
        )
        source = (
            chunk.get("source")
            or chunk.get("document_name")
            or chunk.get("file_name")
            or chunk.get("title")
            or chunk.get("knowledgeName")
            or ""
        )
        score = chunk.get("score") or chunk.get("similarity") or chunk.get("relevance")

        if source:
            print(f"来源: {source}")
        if score is not None:
            print(f"相关度: {score}")
        print(f"内容:\n{content}")

    print("\n" + "=" * 60)
    print(f"共返回 {len(chunks)} 个知识片段")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 query_knowledge.py <问题> [返回数量]")
        print("示例: python3 query_knowledge.py 'Teams应用对接配置' 5")
        sys.exit(1)

    question = sys.argv[1]
    top = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    result = query(question, top)
    format_output(result, question)


if __name__ == "__main__":
    main()
