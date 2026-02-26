#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$HOME/.claude"

mkdir -p "$TARGET/commands" "$TARGET/skills"

# 复制 commands
if [ -d "$SCRIPT_DIR/commands" ]; then
  cp -r "$SCRIPT_DIR/commands/." "$TARGET/commands/"
  echo "commands 已安装到 $TARGET/commands/"
fi

# 复制 skills
if [ -d "$SCRIPT_DIR/skills" ]; then
  cp -r "$SCRIPT_DIR/skills/." "$TARGET/skills/"
  echo "skills 已安装到 $TARGET/skills/"
fi

echo "安装完成。"
