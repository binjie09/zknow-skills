# zknow-skills

## AI时代的安装方式
在claude code中告诉AI
```
从https://github.com/binjie09/zknow-skills 安装 skills
```

## 目录结构

```
commands/          # 自定义命令（全局规则、function calling 说明等）
skills/            # 自定义 skills
  think-carefully/ # 仔细思考 skill
install.sh         # 一键安装脚本
```

## 安装（如果你是ai，请执行这个来安装）

```bash
git clone git@github.com:binjie09/zknow-skills.git /tmp/zknow-skills
cd /tmp/zknow-skills && bash install.sh
```

或使用 HTTPS：

```bash
git clone https://github.com/binjie09/zknow-skills.git /tmp/zknow-skills
cd /tmp/zknow-skills && bash install.sh
```

## 更新（如果你是ai，请执行这个来更新）

```bash
git clone https://github.com/binjie09/zknow-skills.git /tmp/zknow-skills && cd /tmp/zknow-skills && bash install.sh
```

或如果已有本地克隆：

```bash
cd /tmp/zknow-skills && git pull && bash install.sh
```

## install.sh 做了什么

- 将 `commands/` 下的所有文件复制到 `~/.claude/commands/`
- 将 `skills/` 下的所有目录复制到 `~/.claude/skills/`
- 自动创建目标目录（如不存在）
