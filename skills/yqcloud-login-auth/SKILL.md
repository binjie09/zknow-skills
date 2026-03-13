---
name: yqcloud-login-auth
description: 燕千云 OAuth 登录认证工具。启动临时本地服务器完成 OAuth 认证流程，获取 access_token 并存储到 ~/.yqcloud_tmp/token.json。当用户需要登录燕千云、获取认证 token、或其他 skill 需要 YQCloud token 时使用此技能。
user-invocable: true
---

# YQCloud OAuth 登录认证

## 概述

通过 OAuth 隐式授权流程（Implicit Grant）登录燕千云平台，获取 access_token。启动临时本地 HTTP 服务器作为回调地址，用户在浏览器中完成登录后，token 自动保存到 `~/.yqcloud_tmp/token.json`。

## 触发条件

当用户需要：
- 登录燕千云 / YQCloud
- 获取 YQCloud access_token
- 提到"燕千云认证"、"yqcloud 登录"、"yqcloud token"
- 其他 skill 依赖 YQCloud token 且 token 不存在或已过期

## 认证流程

```
用户触发 → 启动本地服务器(端口49658) → 打开浏览器 → 用户登录
→ OAuth 回调携带 token → 前端提取并发送到服务器 → 存储 token → 服务器关闭
```

## Token 存储

- 目录: `~/.yqcloud_tmp/`
- 文件: `~/.yqcloud_tmp/token.json`
- 格式:
```json
{
  "access_token": "d39a5a21-0e6d-4958-8f58-974b07e5d8c5",
  "token_type": "bearer",
  "state": "",
  "expires_in": "315359994",
  "refresh_token": "b00bb352-cdbe-44d1-986a-06fdc0edb2fe",
  "scope": "default"
}
```

## 执行步骤

### 1. 检查现有 Token

先检查是否已有有效 token：

```bash
cat ~/.yqcloud_tmp/token.json 2>/dev/null
```

如果 token 已存在，询问用户是否需要重新认证。

### 2. 执行认证

运行 OAuth 认证服务器脚本：

```bash
python3 "$(dirname "$0")/../skills/yqcloud-login-auth/scripts/oauth_server.py"
```

**脚本行为：**
1. 在 `localhost:49658` 启动临时 HTTP 服务器
2. 自动打开浏览器访问 OAuth 授权页面
3. 用户在浏览器中登录燕千云
4. OAuth 回调将 token 通过 URL hash fragment 传回
5. 前端 JavaScript 提取 token 并 POST 到服务器
6. 服务器将 token 存储到 `~/.yqcloud_tmp/token.json`
7. 页面显示"认证成功"，服务器自动关闭

### 3. 验证 Token

认证完成后验证 token 是否可用：

```bash
ACCESS_TOKEN=$(python3 -c 'import json; print(json.load(open("'$HOME'/.yqcloud_tmp/token.json"))["access_token"])')
curl -s -w "\nHTTP_STATUS: %{http_code}" \
  --header "accept: application/json" \
  --header "accept-language: zh-CN,zh;q=0.9,zh-TW;q=0.8" \
  --header "authorization: bearer $ACCESS_TOKEN" \
  --header "content-type: application/json" \
  --header "origin: https://support.yqcloud.com" \
  --header "referer: https://support.yqcloud.com/" \
  --header "x-tenant-id: 228549383619211264" \
  "https://api.yqcloud.com/iam/yqc/users/self"
```

返回 HTTP `200` 且包含用户信息表示 token 有效。

## 在其他脚本中使用 Token

读取已保存的 token：

```bash
ACCESS_TOKEN=$(python3 -c 'import json; print(json.load(open("'$HOME'/.yqcloud_tmp/token.json"))["access_token"])')
```

```python
import json
from pathlib import Path

token_file = Path.home() / ".yqcloud_tmp" / "token.json"
token_data = json.loads(token_file.read_text())
access_token = token_data["access_token"]
```

## 故障排查

### 端口被占用

如果 49658 端口被占用：
```bash
lsof -i :49658
kill -9 <PID>
```
然后重新运行认证脚本。

### 浏览器未自动打开

手动在浏览器中访问：
```
https://support.yqcloud.com/oauth/oauth/authorize?response_type=token&client_id=support&state=&redirect_uri=http%3A%2F%2Flocalhost%3A49658
```

### Token 文件不存在

确认认证流程是否完成。如果浏览器页面未显示"认证成功"，可能是：
- 网络问题导致 OAuth 授权页面无法加载
- 用户取消了登录
- 回调服务器已提前关闭（Ctrl+C）

## 执行流程（给 Agent 参考）

1. 使用 Bash 检查 `~/.yqcloud_tmp/token.json` 是否存在
2. 如果存在，使用 Read 读取并展示 token 概要（mask 敏感信息），使用 AskUserQuestion 询问是否重新认证
3. 如果需要认证，使用 Bash 运行 `python3 <skill_path>/scripts/oauth_server.py`（注意：此命令会阻塞直到认证完成或用户中断）
4. 认证完成后，使用 Read 读取 `~/.yqcloud_tmp/token.json` 确认 token 已保存
5. 向用户报告认证结果
