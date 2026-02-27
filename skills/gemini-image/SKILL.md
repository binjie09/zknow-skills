---
name: gemini-image
description: 使用 Gemini 图像生成 API 生成或修改图片。支持自定义 API Key 和 Base URL。
user-invocable: true
---

# Gemini 图像生成 Skill

当用户调用此 skill 时，按以下流程执行：

## 1. 获取配置

按优先级读取配置：
1. 用户在命令中直接提供的参数
2. 环境变量 `GEMINI_API_KEY` 和 `GEMINI_BASE_URL`
3. 若均未提供，使用 AskUserQuestion 工具询问用户

默认值：
- `base_url`: `https://generativelanguage.googleapis.com/v1beta`
- `model`: `gemini-2.0-flash-preview-image-generation`

## 2. 解析用户意图

从用户输入中提取：
- `prompt`: 图像描述或修改指令（必填）
- `image_path`: 本地图片路径（可选，用于图片修改场景）
- `api_key`: API Key（可选，覆盖环境变量）
- `base_url`: 自定义 Base URL（可选）
- `model`: 模型名称（可选，默认 `gemini-2.0-flash-preview-image-generation`）

## 3. 构造请求

### 纯文本生成图片

```bash
curl --location '{base_url}/models/{model}:generateContent' \
  --header 'x-goog-api-key: {api_key}' \
  --header 'Content-Type: application/json' \
  --data '{
    "contents": [{
      "parts": [
        {"text": "{prompt}"}
      ]
    }],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"]
    }
  }'
```

### 图片修改（提供了 image_path）

先将图片转为 base64，再构造请求：

```bash
# 转换图片为 base64
BASE64_IMAGE=$(base64 -w 0 "{image_path}")
MIME_TYPE=$(file --mime-type -b "{image_path}")

curl --location '{base_url}/models/{model}:generateContent' \
  --header 'x-goog-api-key: {api_key}' \
  --header 'Content-Type: application/json' \
  --data '{
    "contents": [{
      "parts": [
        {"text": "{prompt}"},
        {
          "inline_data": {
            "mime_type": "'"$MIME_TYPE"'",
            "data": "'"$BASE64_IMAGE"'"
          }
        }
      ]
    }],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"]
    }
  }'
```

## 4. 处理响应

API 返回的图片数据在 `candidates[0].content.parts` 中，类型为 `inlineData`：

```json
{
  "candidates": [{
    "content": {
      "parts": [
        {"text": "..."},
        {
          "inlineData": {
            "mimeType": "image/png",
            "data": "<base64-encoded-image>"
          }
        }
      ]
    }
  }]
}
```

提取 base64 数据并保存为文件：

```bash
# 从响应中提取并保存图片
echo "{base64_data}" | base64 -d > output_image.png
```

输出文件命名规则：`gemini_output_{timestamp}.png`

## 5. 执行步骤

1. 使用 Bash 工具执行 curl 命令
2. 解析 JSON 响应，提取图片 base64 数据
3. 将图片保存到当前目录
4. 告知用户保存路径

## 注意事项

- API Key 敏感，不要在输出中明文显示完整 key（只显示前4位+****）
- 若请求失败，显示错误信息并给出排查建议
- 支持的图片格式：PNG、JPEG、WEBP、GIF
- 模型名称示例：`gemini-2.0-flash-preview-image-generation`、`gemini-3.1-flash-image-preview`
