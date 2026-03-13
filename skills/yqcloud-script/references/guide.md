# YQCloud JS 脚本规则手册

## 目录

- 执行模型
- API 速查
- 从案例归纳出的硬规则
- 常用模板
- 调试与避坑

## 执行模型

先判断这段脚本运行在哪一类位置：

| 类型 | 典型用途 | 输出方式 |
|---|---|---|
| 字段脚本 | 自动带出标题、当前用户、日期、关联字段 | `return` |
| OR 字段脚本 | 回显或派生某个字段值 | `return` |
| 过滤脚本 | 过滤产品、问题单、列表数据 | `return` |
| 值集联动脚本 | 父子值集联动、按编码反查值集项 | `return` |
| 业务规则脚本 | 创建后回写、状态更新、字段同步 | `$SetValue` |
| 动作脚本 | 取消、认领、关闭等按钮动作 | `$SetValue`，必要时 `return` |
| 列表预筛选 | 页面输入驱动列表查询参数 | 通常 `return` 当前页面值 |

经验规则：

- 字段脚本和过滤脚本必须能独立返回结果，不要依赖隐式副作用。
- 业务规则脚本优先改当前单据字段，不要把字段脚本中的 `return` 逻辑原样搬过来。
- 列表联动经常是“JS 返回一个参数值，后台 SQL 根据这个参数过滤”，两者职责不要混。

## API 速查

| API | 范围 | 用途 | 备注 |
|---|---|---|---|
| `$GetValue(key)` | 前后端 | 取当前表单字段或请求参数值 | 可以取到页面已选择但尚未提交的值 |
| `$SetValue(key, value)` | 前后端 | 给当前业务对象字段赋值 | 你给的文档示例漏了第二个参数，实际按案例都应传 `value` |
| `$GetCurrentTime()` | 前后端 | 取平台当前时间 | 优先用它而不是本地 `new Date()` |
| `$GetCurrentPerson()` | 前后端 | 取当前用户对象 | 缺少具体结构示例，优先使用更稳定的 ID 查询模式 |
| `$GetCurrentPersonId()` | 前后端 | 取当前用户 ID | 最常用于查询 `IAM_USER` |
| `$Print(...args)` | 后端 | 打印调试日志 | UI 侧不要假设它可用 |
| `$GetBusinessObject(boc, key, fields)` | 后端 | 按主键查单条业务对象 | 支持 `field_id:name` 取子字段 |
| `$SearchBusinessObject(boc, params, fields)` | 后端 | 按条件查多条业务对象 | 返回数组 |
| `$Invoke(service, component, key)` | 后端 | 调用平台后端服务 | 参数细节以项目已有服务定义为准 |
| `$RestExchange(url, method, headers, body)` | 后端 | 发起 HTTP 请求 | 只在必须调用外部接口时使用 |
| `$InvokeInterface(...)` | 后端 | 调平台接口 | 你给的材料没有完整签名，先查项目已有用法 |

补充判断：

- 案例里出现了 `$GetCurrentAttribute('id')`。它说明某些项目环境可能还暴露了“读取当前记录属性”的方法。
- 新写脚本时默认优先 `$GetValue`。只有明确需要读取已落库属性且项目已有同类写法时，再跟随现有约定使用 `$GetCurrentAttribute`。

## 从案例归纳出的硬规则

### 1. 先判空，再取 `[0]`

你给的很多案例直接写了 `result[0].id`。新脚本不要照抄，必须先判空：

```javascript
var rows = $SearchBusinessObject('PROBLEM', { t_incident: incidentId }, ['id']);
if (!rows || !rows.length) {
  return;
}
return rows[0].id;
```

### 2. `$SearchBusinessObject` 返回数组，不是对象

案例里有一段把查询结果直接写成 `...['id']`，这不成立。正确写法是先拿数组，再循环或取首项：

```javascript
var rows = $SearchBusinessObject('FD_LOOKUP_VALUE', {
  type_code: 'UAES_TSLX',
  parent_id: 0
}, ['id']);
var ids = [];
for (var i = 0; i < rows.length; i++) {
  ids.push(rows[i].id);
}
return ids.join(',');
```

### 3. 引用字段返回对象，普通字段返回值

像“申请人”“所属公司”“所属部门”这种引用字段，不要只返回 ID：

```javascript
var user = $GetBusinessObject('IAM_USER', $GetCurrentPersonId(), ['id', 'real_name']);
if (!user || !user.id) {
  return;
}
return {
  id: user.id,
  real_name: user.real_name
};
```

如果只是邮件、电话、序号、标题，直接返回字符串或数字即可。

### 4. 同步当前单据字段时，优先用 `$SetValue`

业务规则或动作脚本中，若目的是把查到的结果回写到当前单据：

```javascript
var incidentId = $GetValue('id');
if (!incidentId) {
  return;
}
var problems = $SearchBusinessObject('PROBLEM', {
  t_incident: incidentId
}, ['id']);
if (!problems || !problems.length) {
  return;
}
$SetValue('problem_id', problems[0].id);
```

### 5. 关联对象显示值优先用 `field_id:name`

子字段查询是平台高频模式：

```javascript
var incident = $GetBusinessObject('incident', incidentId, [
  'id',
  'problem_id:name',
  'name'
]);
return incident['problem_id:name'];
```

生成标题、带出优先级、取公司名称时都可以复用这套模式。

### 6. 当前页面值优先用 `$GetValue`

联动过滤时，取值不一定来自数据库，往往就是页面刚选中的值：

```javascript
var ph1 = $GetValue('t_ph1');
return ph1;
```

这条规则尤其适用于“根据表单输入值，对两个列表进行联动筛选”。

### 7. 平台时间和本地时间分开处理

- 需要和平台时区一致、用于业务字段时：优先 `$GetCurrentTime()`。
- 只是前端简单拼接日期字符串时：可以用 `new Date()`。
- 需要减天数或格式化时，先写小函数再返回结果，不要把格式化逻辑散落在主流程里。

### 8. 配置映射优先抽成字典

像“SCC 位置分单”这种规则，本质是“页面值 -> 人员 ID”的静态映射。优先把配置和通用逻辑分开：

```javascript
var code = 'select_gdnrouax';
var personDepartmentMap = {
  '227478968817750016': ['CP_RLZY', 'CP_AQ'],
  '227478968809361408': ['CP_ZZ', 'CP_ZL']
};
```

这样只改配置，不改算法。

### 9. 复杂预筛选优先落到 SQL，不要强塞进 JS

你给的“测试项维护预筛选”案例本质是列表 SQL。它说明：

- JS 负责返回页面字段值，比如 `t_ph1`、`material`。
- 真正的多表关联、`NOT EXISTS`、模糊查询应放在后台 SQL 或数据集查询里。
- 当用户说“写个过滤脚本”时，先确认他要的是页面字段脚本还是列表数据源 SQL。

## 常用模板

### 模板 1：根据关联对象带出普通字段

```javascript
var cpId = $GetValue('t_cp');
if (!cpId) {
  return;
}
var cp = $GetBusinessObject('UAES_CP', cpId, ['t_ph1']);
if (!cp) {
  return;
}
return cp['t_ph1'];
```

### 模板 2：自动带出当前用户引用字段

```javascript
var user = $GetBusinessObject('IAM_USER', $GetCurrentPersonId(), ['id', 'real_name']);
if (!user || !user.id) {
  return;
}
return {
  id: user.id,
  real_name: user.real_name
};
```

### 模板 3：根据当前记录回写关联单据

```javascript
var incidentId = $GetValue('id');
if (!incidentId) {
  return;
}
var problems = $SearchBusinessObject('PROBLEM', {
  t_incident: incidentId
}, ['id']);
if (!problems || !problems.length) {
  return;
}
$SetValue('problem_id', problems[0].id);
```

如果当前环境已经统一用 `$GetCurrentAttribute('id')` 取主键，就跟随项目现有写法。

### 模板 4：值集联动返回单个 ID

```javascript
var rows = $SearchBusinessObject('FD_LOOKUP_VALUE', {
  lookup_type_code: 'UAES_TSLX',
  code: $GetValue('t_tslx')
}, ['id']);
if (!rows || !rows.length) {
  return;
}
return rows[0].id;
```

### 模板 5：值集过滤返回逗号拼接 ID

```javascript
var rows = $SearchBusinessObject('FD_LOOKUP_VALUE', {
  type_code: 'UAES_TSLX',
  parent_id: 0
}, ['id']);
var ids = [];
for (var i = 0; i < rows.length; i++) {
  ids.push(rows[i].id);
}
return ids.join(',');
```

### 模板 6：标题或序号生成

```javascript
var rwxxId = $GetValue('t_vak');
if (!rwxxId) {
  return;
}
var rwxx = $GetBusinessObject('UAES_RWXX', rwxxId, [
  't_vak',
  't_txlx_ba:t_name',
  't_priority:name'
]);
if (!rwxx) {
  return;
}
var incidents = $SearchBusinessObject('INCIDENT', { t_vak: rwxxId }, ['id']);
var seq = incidents ? incidents.length + 1 : 1;
return rwxx['t_vak'] + '_' + seq + '_' + rwxx['t_txlx_ba:t_name'] + '_' + rwxx['t_priority:name'];
```

### 模板 7：日期减 N 天

```javascript
function subDate(dateTime, days) {
  var prev = new Date(new Date(dateTime).getTime() - days * 24 * 3600 * 1000);
  var month = prev.getMonth() + 1;
  var day = prev.getDate();
  var hour = prev.getHours();
  var minute = prev.getMinutes();
  if (month < 10) {
    month = '0' + month;
  }
  if (day < 10) {
    day = '0' + day;
  }
  if (hour < 10) {
    hour = '0' + hour;
  }
  if (minute < 10) {
    minute = '0' + minute;
  }
  return prev.getFullYear() + '-' + month + '-' + day + ' ' + hour + ':' + minute;
}

return subDate($GetCurrentTime(), 30);
```

## 调试与避坑

- 后端脚本调试优先用 `$Print('key = ', value)`。
- 打印关键节点：输入值、查询结果长度、最终输出值。
- 表名和字段编码跟随平台配置，大小写不要想当然统一。
- 取公司、部门、用户组等组织数据时，先查 `IAM_USER`，再顺着 `company_id`、`department_id`、`user_group_id` 查关联表。
- 调用 `$Invoke`、`$RestExchange`、`$InvokeInterface` 前，先搜项目里的现有调用，复用同样的参数顺序和返回解析。
- 不要在脚本里写死不确定的对象结构；引用字段返回什么键名，以目标字段现有脚本或接口返回为准。
- 不要为了“先跑起来”省掉空值判断。平台脚本最常见的问题就是查无数据后直接访问属性。
