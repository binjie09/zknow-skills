---
name: openclaw-setup
description: OpenClaw 自定义 Provider 配置指南。用于配置 OpenClaw 使用 ZKnow 自定义 Provider 连接 Anthropic API。当用户需要配置 OpenClaw、添加自定义 provider、或设置 OpenClaw 使用 ZKnow API 渠道时使用此技能。
---

# OpenClaw ZKnow Provider 配置指南

## 概述

OpenClaw 是一个开源 AI Agent 平台，支持通过 `models.providers` 添加自定义 Provider。本指南说明如何为 OpenClaw 配置 ZKnow 自定义 Provider，使用 Anthropic API 渠道。

## 触发条件

当用户需要：
- 配置 OpenClaw 使用 ZKnow
- 为 OpenClaw 添加自定义 Provider
- 设置 OpenClaw 连接自定义 Anthropic API 端点
- 提到"配置 openclaw"、"openclaw provider"、"openclaw zknow"

## 环境变量

配置需要以下环境变量：

- `ANTHROPIC_API_KEY`: Anthropic API 密钥
- `ANTHROPIC_BASE_URL`: API 基础 URL

## 配置步骤

### 1. 检查 OpenClaw 是否已安装

**首先询问用户是否已安装 OpenClaw，如果未安装，引导用户前往 [OpenClaw 官方文档](https://docs.openclaw.ai) 安装。**

验证安装：
```bash
openclaw --version
```

### 2. 检查环境变量

运行以下命令检查环境变量是否已设置：
```bash
echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+已设置}"
echo "ANTHROPIC_BASE_URL: ${ANTHROPIC_BASE_URL:-未设置}"
```

- 如果环境变量已设置，直接使用环境变量的值进行配置
- 如果未设置，使用 AskUserQuestion 询问用户的 API Key 和 Base URL

### 3. 创建配置目录

```bash
mkdir -p ~/.openclaw
```

### 4. 创建或更新配置文件

在 `~/.openclaw/openclaw.json` 中配置 ZKnow 自定义 Provider：

```json5
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "zknow/claude-sonnet-4-6"
      }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "zknow": {
        "baseUrl": "<ANTHROPIC_BASE_URL>",
        "apiKey": "<ANTHROPIC_API_KEY>",
        "api": "anthropic-messages",
        "models": [
          { "id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6" },
          { "id": "claude-opus-4-6", "name": "Claude Opus 4.6" },
          { "id": "claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5" }
        ]
      }
    }
  }
}
```

**重要提示**：
- 将 `<ANTHROPIC_BASE_URL>` 替换为实际的环境变量值（如 `http://190.92.219.209:8180`）
- 将 `<ANTHROPIC_API_KEY>` 替换为实际的 API Key
- 默认模型为 `claude-sonnet-4-6`，用户可按需切换为 `claude-opus-4-6` 或 `claude-haiku-4-5-20251001`
- 如果已存在 `openclaw.json`，需要合并配置而不是覆盖

### 5. 配置示例

假设环境变量为：
- `ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx`
- `ANTHROPIC_BASE_URL=http://190.92.219.209:8180`

最终配置文件内容：

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "zknow/claude-sonnet-4-6"
      }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "zknow": {
        "baseUrl": "http://190.92.219.209:8180",
        "apiKey": "sk-ant-xxxxxxxxxxxxxxxxxxxxx",
        "api": "anthropic-messages",
        "models": [
          { "id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6" },
          { "id": "claude-opus-4-6", "name": "Claude Opus 4.6" },
          { "id": "claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5" }
        ]
      }
    }
  }
}
```

### 6. 验证配置

运行以下命令验证 Provider 配置：

```bash
openclaw models list --provider zknow
```

测试连通性：
```bash
openclaw models status --probe
```

## 配置说明

- **agents.defaults.model.primary**: 默认使用的模型，格式为 `provider/model-id`
- **models.mode**: 设置为 `"merge"` 以与内置 Provider 合并
- **models.providers.zknow**: ZKnow 自定义 Provider 配置
  - **baseUrl**: API 端点 URL
  - **apiKey**: API 密钥
  - **api**: 线路协议，使用 `anthropic-messages` 对接 Anthropic API
  - **models**: 可用模型列表，每个模型包含 `id` 和 `name`

## 可用模型

| 模型 ID | 名称 | 说明 |
|---------|------|------|
| `claude-sonnet-4-6` | Claude Sonnet 4.6 | 默认模型，均衡性能与速度 |
| `claude-opus-4-6` | Claude Opus 4.6 | 最强性能 |
| `claude-haiku-4-5-20251001` | Claude Haiku 4.5 | 最快速度 |

切换模型：
```bash
openclaw models set zknow/claude-opus-4-6
```

## 故障排查

### 错误：Provider not found

确认 `openclaw.json` 中的 `models.providers.zknow` 配置正确，且 `mode` 设置为 `"merge"`。

### 错误：Authentication failed

检查 `apiKey` 是否正确，确认 API Key 有效且未过期。

### 错误：Connection refused

确认 `baseUrl` 正确且 API 端点可访问：
```bash
curl -s <ANTHROPIC_BASE_URL>/v1/models -H "x-api-key: <ANTHROPIC_API_KEY>" | head -c 200
```

### 模型不可用

运行 `openclaw models list --provider zknow` 检查模型列表，确认模型 ID 拼写正确。

## 执行流程

1. 使用 Bash 检查 OpenClaw 是否已安装（`openclaw --version`）
2. 使用 Bash 检查环境变量 `ANTHROPIC_API_KEY` 和 `ANTHROPIC_BASE_URL` 是否可用
3. 如果环境变量可用，直接读取值；如果不可用，使用 AskUserQuestion 询问用户
4. 使用 Bash 创建配置目录 `mkdir -p ~/.openclaw`
5. 使用 Bash 检查是否已存在 `~/.openclaw/openclaw.json`
6. 如果文件已存在，使用 Read 读取后用 Edit 合并 ZKnow Provider 配置
7. 如果文件不存在，使用 Write 创建完整配置文件（替换环境变量为实际值）
8. 提供验证命令并协助排查问题
