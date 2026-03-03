# YQCloud AI 配置工具

自动配置 YQCloud 专用的 Claude Code、Codex 和 Gemini CLI 工具。

## 触发条件

当用户需要：
- 配置 YQCloud AI 服务
- 设置 Claude Code/Codex/Gemini CLI 使用 YQCloud 中转
- 初始化 ZKnow AI 开发环境
- 提到"配置 yqcloud ai"、"设置 claude code"、"配置 codex"、"设置 gemini cli"

## 使用说明

**访问地址**: http://190.92.219.209:8180/
使用燕千云 support 租户账号登录后，在控制台创建 API Key。

**支持环境**: test、preprod、stag（请勿用于生产环境）

## 配置步骤

### 1. 获取 API Key

首先询问用户的 API Key：
- 如果用户未提供，引导访问 http://190.92.219.209:8180/ 创建

### 2. 检测 Shell 类型

运行以下命令检测用户使用的 shell：
```bash
echo $SHELL
```

### 3. 配置 Claude Code

创建三个配置文件：

**~/.claude/settings.json**:
```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "<API_KEY>",
    "ANTHROPIC_BASE_URL": "http://190.92.219.209:8180",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": 1
  },
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

**~/.claude/config.json** (VSCode 插件使用):
```json
{
    "primaryApiKey": "zknow"
}
```

**Shell 环境变量** (追加到 ~/.bashrc 或 ~/.zshrc):
```bash
export ANTHROPIC_BASE_URL="http://190.92.219.209:8180"
export ANTHROPIC_AUTH_TOKEN="<API_KEY>"
```

### 4. 配置 Codex

创建两个配置文件：

**~/.codex/config.toml**:
```toml
model_provider = "zknow"
model = "gpt-5.3-codex"
model_reasoning_effort = "high"
disable_response_storage = true

[model_providers.zknow]
name = "zknow"
base_url = "http://190.92.219.209:8180/v1"
wire_api = "responses"
requires_openai_auth = true
```

**~/.codex/auth.json**:
```json
{
  "OPENAI_API_KEY": "<API_KEY>"
}
```

### 5. 配置 Gemini CLI

创建两个配置文件：

**~/.gemini/.env**:
```
GOOGLE_GEMINI_BASE_URL=http://190.92.219.209:8180
GEMINI_API_KEY=<API_KEY>
GEMINI_MODEL=gemini-3.1-pro-preview
```

**~/.gemini/settings.json**:
```json
{
  "ide": {
    "enabled": true
  },
  "security": {
    "auth": {
      "selectedType": "gemini-api-key"
    }
  }
}
```

### 6. 应用配置

提示用户运行以下命令使环境变量生效：
```bash
source ~/.zshrc  # 或 source ~/.bashrc
```

## 验证配置

配置完成后，建议用户测试：
- Claude Code: 运行 `claude`
- Codex: 运行 `codex`
- Gemini CLI: 运行 `gemini`（如遇 401 错误，运行 `/auth` 重新填入 key）

## 注意事项

- 所有配置文件中的 `<API_KEY>` 需替换为用户实际的 API Key
- 确保目录存在（~/.claude、~/.codex、~/.gemini）
- Windows 用户路径为 `C:\Users\<username>\` 对应的目录
- 配置仅适用于非生产环境

## 执行流程

1. 使用 AskUserQuestion 询问用户的 API Key（如未提供）
2. 使用 Bash 检测 shell 类型
3. 使用 Write 工具创建所有配置文件（替换 API Key）
4. 使用 Edit 工具追加环境变量到 shell 配置文件
5. 提示用户 source shell 配置文件
6. 提供验证命令和故障排除建议
