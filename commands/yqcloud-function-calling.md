# YQCloud 自定义 Function Calling 格式说明

本 skill 描述了一套自定义的 function calling 格式，用于 ITSM（IT服务管理）场景下的工单操作。

## 格式结构说明

每个函数定义包含两层结构：
- 外层：标准的函数描述（name、description、parameters）
- 内层 `function` 字段：执行配置（type、url、headers 等）

### 函数类型（function.type）

| 类型 | 说明 |
|------|------|
| `manual` | 手动处理，由前端/系统自行实现逻辑，不发起 HTTP 请求 |
| `call_url` | 自动发起 HTTP 请求到指定 URL |

### 通用字段

- `stopAfterFunctionCall`：调用函数后是否停止 AI 继续生成（true=停止，false=继续）
- `intl`：国际化配置，包含 `zh_CN` 和 `en_US`，每个语言有 `typingMessage`（等待提示语）和可选的 `resultTips`（结果提示语）
- `requestParser`：JavaScript 代码字符串，用于在发送 HTTP 请求前转换请求体，`data` 为 AI 函数调用参数的 **JSON 字符串**（需 `JSON.parse(data)` 解析），返回值作为实际请求体发送
- `responseParser`：JavaScript 代码字符串，用于处理 HTTP 响应数据，`data` 为响应体对象，可使用 `_`（lodash）

### 变量占位符

URL 和 headers 中支持以下变量：
- `${STATIC#yqcloud_url}`：YQCloud 服务基础地址
- `${tenantId}`：当前租户 ID
- `${yqAccessToken}`：当前用户访问令牌

---

## 函数列表

### 1. createTicket — 创建工单

- **类型**：`manual`（前端自行处理，不发 HTTP 请求）
- **stopAfterFunctionCall**：`true`（调用后 AI 停止生成）
- **描述**：创建工单，需传入尽可能多的参数
- **参数**：`additionalProperties: true`，接受任意字段，无固定 schema
- **等待提示**：zh_CN "单据生成中..." / en_US "Ticket is generating..."
- **调用时机**：已获取表单 Schema 并从用户处收集完所有字段后调用

---

### 2. getCreateTicketParamJsonSchema — 获取工单参数 Schema

- **类型**：`call_url`，GET 请求
- **URL**：`${STATIC#yqcloud_url}/ai/v1/${tenantId}/itsmScene/getServiceItemSchema`
- **stopAfterFunctionCall**：`false`（调用后 AI 继续处理返回结果）
- **描述**：获取指定服务项创建工单所需的参数 JSON Schema
- **必填参数**：`id`（string，服务项 ID，来自 getAllServiceItem 结果）
- **等待提示**：zh_CN "正在获取提单所需信息..." / en_US "Obtaining information required for the ticket..."
- **调用时机**：确定服务项后立即调用，根据返回的 Schema 向用户逐一收集字段

---

### 3. getAllServiceItem — 获取全部服务项

- **类型**：`call_url`，GET 请求
- **URL**：`${STATIC#yqcloud_url}/itsm/v1/${tenantId}/service_items/catalog/page/all?serviceCatalogFlag=true&page=0&size=9999`
- **描述**：查出全部服务项列表，用户提出需求后应立即调用
- **参数**：无必填参数
- **等待提示**：zh_CN "正在获取全部服务项信息..." / en_US "Searching service item..."
- **结果提示**：zh_CN "根据您的问题，为您推荐了服务项"
- **responseParser**：过滤 `type === 'SERVICE' || type === 'RECORD'` 的项，只保留 `id`、`name`、`shortDescription`、`description` 字段，返回 `{ allServiceItemList: [...] }`
- **调用时机**：用户提出任何工单相关需求后第一步调用

---

### 4. requestUserSelectServiceItem — 请求用户选择服务项

- **类型**：`call_url`，POST 请求
- **URL**：`/transparent`（透传接口）
- **stopAfterFunctionCall**：`true`（调用后 AI 停止，等待用户在前端操作）
- **描述**：当 AI 无法确定使用哪个服务项时，让用户手动选择
- **必填参数**：`serviceItemList`（array，数据来自 getAllServiceItem，**最多传 1 个**最可能匹配的服务项）
- **等待提示**：zh_CN "正在为你推荐服务项..." / en_US "Recommending services for you..."
- **responseParser**：`return data?.serviceItemList ? data : {result: 'no data'}`
- **调用时机**：已有全部服务项列表、用户已提出需求，但 AI 仍无法确定具体服务项时调用

---

## 典型调用流程

```
用户提出工单需求
       ↓
调用 getAllServiceItem（获取全部服务项列表）
       ↓
AI 分析用户需求，匹配服务项
       ├─ 能确定服务项
       │      ↓
       │  调用 getCreateTicketParamJsonSchema（传入服务项 id，获取表单 Schema）
       │      ↓
       │  AI 根据 Schema 向用户逐一收集必填字段
       │      ↓
       │  调用 createTicket（传入所有收集到的字段，创建工单）
       │
       └─ 无法确定服务项
              ↓
          调用 requestUserSelectServiceItem（传入最多 1 个候选服务项）
              ↓
          用户在前端选择确认后，重新进入流程
```

## 注意事项

1. `getAllServiceItem` 的 `required` 字段定义为 `["param"]` 是原始数据中的笔误，实际无必填参数，直接调用即可
2. `requestUserSelectServiceItem` 的 `serviceItemList` 最多传 **1 个**服务项，不是传全部候选列表
3. `createTicket` 是 `manual` 类型，AI 只负责组装参数并调用，实际创建逻辑由前端实现
4. `stopAfterFunctionCall: true` 的函数调用后 AI 不会继续输出，需等待前端/用户的下一步操作

---

## Parser 使用示例

### requestParser — 转换请求体

适用于 POST 请求需要将 AI 参数映射为特定请求体格式的场景。`data` 是 AI 函数调用参数的 **JSON 字符串**，需先 `JSON.parse`。

```json
{
  "function": {
    "type": "call_url",
    "name": "getLocalAnswer",
    "url": "${STATIC#yqcloud_url}/externalsync/v1/${tenantId}/xudc/get/ai/answer/stream2",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer ${yqAccessToken}",
      "x-tenant-id": "${tenantId}"
    },
    "requestParser": "return {\"content\": JSON.parse(data).question, \"loginName\": \"${loginName}\"}"
  },
  "name": "getLocalAnswer",
  "description": "获取本地知识库答案",
  "parameters": {
    "type": "object",
    "properties": {
      "question": {
        "type": "string",
        "description": "根据上下文总结的用户提出的问题，必须要总结出一个问题"
      }
    }
  }
}
```

说明：AI 调用时传入 `{ question: "..." }`，`requestParser` 将其转换为接口实际需要的 `{ content: "...", loginName: "..." }` 格式再发送。

---

### responseParser — 处理响应数据

适用于需要对接口返回值做过滤、字段映射、格式转换的场景。`data` 为响应体对象，可直接操作。

```json
{
  "function": {
    "type": "call_url",
    "name": "searchKnowledgeForCommon",
    "url": "${STATIC#yqcloud_url}/intelligent/v1/${tenantId}/qa/predict/range",
    "method": "GET",
    "headers": {
      "Authorization": "Bearer ${yqAccessToken}",
      "x-tenant-id": "${tenantId}"
    },
    "responseParser": "data.qnaAnswerList = data.qnaAnswerList?.filter(item => item.score * 1 >= 0.85).map(item => ({ id: item.id, question: item.question, score: item.score, answer: item.answer })); return data;"
  },
  "name": "searchKnowledgeForCommon",
  "description": "查找公共知识库，qnaAnswerList 中 score >= 0.85 的记录必须原样返回 answer 不得修改",
  "parameters": {
    "type": "object",
    "properties": {
      "question": {
        "type": "string",
        "description": "查找的问题描述，必填"
      }
    },
    "required": ["question"]
  }
}
```

说明：`responseParser` 对 `qnaAnswerList` 按 score 过滤并精简字段，再将处理后的 `data` 返回给 AI 继续推理。

