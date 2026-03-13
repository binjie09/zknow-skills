---
name: yqcloud-knowledge
description: 燕千云知识库查询工具。从 YQCloud 知识库中检索相关知识片段。当用户需要查询燕千云知识库、搜索内部文档、查找产品使用说明、或提到"知识库"、"查一下"、"燕千云文档"时使用此技能。依赖 yqcloud-login-auth 提供的 token。
user-invocable: true
---

# YQCloud 知识库查询

## 概述

从燕千云知识库中检索相关知识片段，返回与问题最匹配的文档内容。基于语义搜索，支持自然语言提问。

## 依赖

- **yqcloud-login-auth**: 需要先完成 OAuth 登录，token 存储在 `~/.yqcloud_tmp/token.json`

## 触发条件

当用户需要：
- 查询燕千云知识库内容
- 搜索内部文档或产品说明
- 提到"知识库"、"查一下"、"燕千云文档"、"帮我查"
- 需要燕千云产品的使用方法、配置说明等

## API 信息

- 端点: `https://api.yqcloud.com/ai/v1/228549383619211264/aigc_knowledge/chunks`
- 方法: GET
- 参数:
  - `question`: 查询问题（URL 编码）
  - `top`: 返回结果数量（默认 5）
- Headers:
  - `Authorization: bearer <access_token>`
  - `x-tenant-id: 228549383619211264`

## 执行步骤

### 1. 检查 Token

```bash
cat ~/.yqcloud_tmp/token.json 2>/dev/null
```

如果 token 不存在，提示用户先运行 `yqcloud-login-auth` 进行登录认证。

### 2. 查询知识库

使用脚本查询：

```bash
python3 <skill_path>/scripts/query_knowledge.py "你的问题"
```

或手动 curl：

```bash
ACCESS_TOKEN=$(python3 -c 'import json; print(json.load(open("'$HOME'/.yqcloud_tmp/token.json"))["access_token"])')
curl -s --location "https://api.yqcloud.com/ai/v1/228549383619211264/aigc_knowledge/chunks?top=5&question=$(python3 -c 'import urllib.parse; print(urllib.parse.quote("你的问题"))')" \
  --header "Authorization: bearer $ACCESS_TOKEN" \
  --header "x-tenant-id: 228549383619211264"
```

### 3. 解读结果

脚本会格式化输出检索到的知识片段，包含：
- 片段内容
- 来源文档
- 相关度评分

## 执行流程（给 Agent 参考）

1. 使用 Bash 检查 `~/.yqcloud_tmp/token.json` 是否存在
2. 如果不存在，告知用户需要先登录（触发 yqcloud-login-auth skill）
3. 使用 Bash 运行 `python3 <skill_path>/scripts/query_knowledge.py "<用户问题>"`
4. 解读返回的知识片段，整理后回答用户问题
5. 如果返回 401，说明 token 过期，提示用户重新认证
