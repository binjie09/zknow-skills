# zknow-skills

个人 Kiro/Claude CLI 的 skills 配置仓库。

## AI 时代的安装方式

在 Claude Code 中告诉 AI：
```
从 https://github.com/binjie09/zknow-skills 安装 skills
```

## 包含的 Skills

| Skill | 说明 |
|-------|------|
| `think-carefully` | 回答任何问题前先深入思考 |
| `global-agent-rules` | 全局工程规范：语言、调试原则、代码度量、安全基线 |
| `yqcloud-function-calling` | YQCloud ITSM 工单场景的 Function Calling 格式说明 |
| `agent-browser` | 浏览器自动化：网页导航、表单填写、截图、数据抓取（来自 vercel-labs） |

## 通过 npx skills 安装（推荐）

```bash
npx skills add binjie09/zknow-skills
```

安装后 skills 会自动复制到 `~/.claude/skills/`。

## 手动安装（如果你是 AI，请执行这个来安装）

```bash
git clone git@github.com:binjie09/zknow-skills.git /tmp/zknow-skills
bash /tmp/zknow-skills/install.sh
```

## 更新（如果你是 AI，请执行这个来更新）

```bash
git clone https://github.com/binjie09/zknow-skills.git /tmp/zknow-skills && bash /tmp/zknow-skills/install.sh
```
