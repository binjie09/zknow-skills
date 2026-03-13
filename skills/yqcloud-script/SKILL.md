---
name: yqcloud-script
description: YQCloud / 燕千云 JS 脚本编写指南。用于编写、改写和审查业务规则、字段脚本、过滤脚本、值集联动脚本、动作脚本和列表联动脚本；适用于需要使用 $GetValue、$SetValue、$GetCurrentTime、$GetCurrentPersonId、$GetBusinessObject、$SearchBusinessObject、$Print、$Invoke 等平台 API，根据当前表单值、业务对象和当前用户生成返回值或回写字段的场景。
---

# YQCloud JS 脚本编写

先判断脚本所在位置，再按对应契约写代码。

## 先识别脚本契约

- 字段脚本、OR 字段脚本、过滤脚本、值集联动脚本、序号脚本：必须 `return`。
- 普通字段返回标量值；引用字段返回对象；列表过滤通常返回逗号拼接字符串。
- 业务规则、动作脚本：优先使用 `$SetValue(key, value)` 回写当前单据；仅在当前引擎明确要求时再 `return`。
- 列表预筛选先确认是不是 SQL/MyBatis 数据源逻辑。复杂查询写在后端 SQL，JS 只负责把页面值透传出去。

## 只用当前环境能跑的 API

- 通用函数：`$GetValue`、`$SetValue`、`$GetCurrentTime`、`$GetCurrentPerson`、`$GetCurrentPersonId`。
- 后端限定函数：`$Print`、`$Invoke`、`$GetBusinessObject`、`$SearchBusinessObject`、`$RestExchange`、`$InvokeInterface`。
- 案例里出现了 `$GetCurrentAttribute`，但它不在你提供的 API 清单里。只有在当前项目已有同类脚本明确使用它时再复用；默认优先 `$GetValue`。

## 固定编写顺序

1. 先取当前值：`$GetValue`、`$GetCurrentPersonId`、`$GetCurrentTime`。
2. 再查关联对象：`$GetBusinessObject`、`$SearchBusinessObject`。
3. 最后输出结果：字段脚本 `return`，业务规则脚本 `$SetValue`。
4. 访问数组首项、子字段、引用字段前先判空，避免直接写 `result[0].id`。

## 保持平台兼容

- 运行时兼容性未知时，优先使用 `var`、`function`、`for`。
- 不默认使用箭头函数、可选链、解构、`let/const` 等较新的语法。
- 调试日志只在后端环境使用 `$Print`。
- 取当前时间优先 `$GetCurrentTime()`；只有明确需要前端本地时间时才用 `new Date()`。

## 按归纳出的规则生成脚本

- 同单据字段回写：用 `$SetValue`。
- 派生字段计算：直接 `return`。
- 关联对象取显示值：用 `field_id:name` 形式取子字段。
- 当前用户自动带出：先查 `IAM_USER`，再按字段类型返回标量或对象。
- 值集/列表过滤：`$SearchBusinessObject` 结果转成 ID 字符串，不要直接对数组取 `['id']`。
- 标题、序号、联动过滤：先取当前页面值，再查已有单据数量或关联对象字段。
- 复杂筛选场景：先确认是否应写后台 SQL，而不是把全部逻辑塞进 JS。

## 输出要求

- 直接给出可粘贴的完整脚本。
- 在脚本前说明脚本类型和返回契约。
- 使用了未在 API 清单中明确说明的能力时，先说明它来自现有项目脚本约定。
- 需要 API 细节、模板和常见坑时，读取 [references/guide.md](references/guide.md)。
