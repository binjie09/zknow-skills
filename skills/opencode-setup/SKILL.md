---
name: opencode-setup
description: OpenCode 安装和配置指南。用于安装 OpenCode 并配置使用自定义 Anthropic API 渠道（ZKnow）。当用户需要安装或配置 OpenCode 连接到自定义 API 端点时使用此技能。
---

# OpenCode 安装和配置指南

## 概述

OpenCode 是一个强大的 AI 编码助手，支持配置自定义 API 渠道。本指南说明如何安装 OpenCode 并配置使用 ZKnow 的 Anthropic API 渠道。

## 安装 OpenCode

**首先询问用户是否已安装 OpenCode，如果未安装，提供以下安装方式：**

### 安装方式

选择以下任一方式安装：

**方式 1：使用安装脚本（推荐）**
```bash
curl -fsSL https://opencode.ai/install | bash
```

**方式 2：使用 npm**
```bash
npm i -g opencode-ai
```

**方式 3：使用 Homebrew（macOS）**
```bash
brew install anomalyco/tap/opencode
```

安装完成后，验证安装：
```bash
opencode --version
```

## 环境变量

配置需要以下环境变量：

- `ANTHROPIC_API_KEY`: Anthropic API 密钥
- `ANTHROPIC_BASE_URL`: API 基础 URL

## 配置步骤

### 1. 创建配置目录

```bash
mkdir -p ~/.config/opencode
```

### 2. 创建配置文件

在 `~/.config/opencode/opencode.json` 中创建配置：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "zknow/claude-opus-4-6",
  "provider": {
    "zknow": {
      "npm": "@ai-sdk/anthropic",
      "name": "ZKnow",
      "options": {
        "baseURL": "${ANTHROPIC_BASE_URL}/v1",
        "apiKey": "${ANTHROPIC_API_KEY}"
      },
      "models": {
        "claude-opus-4-6": {
          "name": "claude-opus-4-6"
        }
      }
    }
  }
}
```

**重要提示**：
- `baseURL` 必须以 `/v1` 结尾
- 将 `${ANTHROPIC_BASE_URL}` 和 `${ANTHROPIC_API_KEY}` 替换为实际的环境变量值

### 3. 配置示例

假设环境变量为：
- `ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx`
- `ANTHROPIC_BASE_URL=http://your-api-endpoint.com:8180`

配置文件内容：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "zknow/claude-opus-4-6",
  "provider": {
    "zknow": {
      "npm": "@ai-sdk/anthropic",
      "name": "ZKnow",
      "options": {
        "baseURL": "http://your-api-endpoint.com:8180/v1",
        "apiKey": "sk-ant-xxxxxxxxxxxxxxxxxxxxx"
      },
      "models": {
        "claude-opus-4-6": {
          "name": "claude-opus-4-6"
        }
      }
    }
  }
}
```

### 4. 验证配置

运行 OpenCode 验证配置是否正确：

```bash
opencode
```

如果配置正确，OpenCode 将启动并显示 "Build claude-opus-4-6 ZKnow"。

## 配置说明

- **model**: 指定使用的模型，格式为 `provider/model-name`
- **provider.zknow**: 自定义 provider 配置
  - **npm**: 使用的 AI SDK 包（`@ai-sdk/anthropic`）
  - **name**: Provider 显示名称
  - **options.baseURL**: API 端点 URL（必须以 `/v1` 结尾）
  - **options.apiKey**: API 密钥
  - **models**: 可用模型列表

## 故障排查

### 错误：Anthropic API key is missing

确保在配置文件的 `options` 中包含了 `apiKey` 字段。

### 错误：Unrecognized keys

检查配置文件格式是否正确，确保使用 `provider` 结构而不是直接使用 `apiKey` 和 `baseURL`。

### 连接失败

确认 `baseURL` 以 `/v1` 结尾，并且 API 端点可访问。

## 参考资料

- [OpenCode 官方文档](https://opencode.ai)
- [OpenCode 配置 Schema](https://opencode.ai/config.json)
