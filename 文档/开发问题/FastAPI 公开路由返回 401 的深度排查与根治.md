
---

## Skill：FastAPI 公开路由返回 401 的深度排查与根治

### 一、适用场景
- FastAPI 项目中某些接口明确未添加认证依赖，但仍返回 `401 Unauthorized` 且响应头包含 `WWW-Authenticate: Bearer`。
- 调整路由顺序、添加 `dependencies=[]` 均无效。
- 日志显示请求已到达服务，但返回 401。

### 二、问题现象速查
| 现象 | 指向原因 |
|------|----------|
| 带 token 的需认证接口正常（200），公开接口反而 401 | 路由匹配错误（静态路由被动态路由拦截） |
| curl 测试同样返回 401，响应体 `{"detail":"Not authenticated"}` | 请求命中了某个携带 `OAuth2PasswordBearer` 依赖的路由 |
| 路由函数内部添加的 `print` 语句未输出 | 请求未进入目标函数，被上游拦截 |
| `/docs` 中该路由显示“需认证”小锁图标 | 路由定义存在认证依赖或被全局依赖污染 |

### 三、核心排查步骤（按优先级执行）

#### 1. 确认路由是否真正被注册
```bash
curl http://localhost:8000/openapi.json | grep -o '"路径前缀/你的路由"[^,]*'
```
- **无输出**：路由未注册，检查文件缩进、装饰器语法、Router 挂载。
- **有输出**：查看 `openapi.json` 中该路由的 `security` 字段，判断是否被注入了认证依赖。

#### 2. 隔离测试：编写极简测试路由
在疑似路由文件中添加：
```python
@router.get("/你的路由")
async def test_route():
    print(">>> 路由被调用")
    return {"status": "ok"}
```
- **仍返回 401**：问题在路由匹配层或全局中间件。
- **返回 200**：原业务逻辑中存在异常被全局异常处理器转为 401（如数据库连接失败触发 `AuthenticationError`）。

#### 3. 检查动态路由拦截（最常见）
若路由路径结构为：
- 静态：`/tag-categories`
- 动态：`/{bookmark_id}`

且 `/tag-categories` 定义在 `/{bookmark_id}` **之后**，则字符串 `tag-categories` 会被当作 `bookmark_id` 参数传入，触发动态路由的认证依赖。

**验证方法**：在动态路由依赖的认证函数中打印 `bookmark_id` 值，观察是否为 `"tag-categories"`。

**永久修复**：为动态路由添加类型约束：
```python
@router.get("/{bookmark_id:int}")   # 仅匹配纯数字
```

#### 4. 排查全局依赖污染
检查 `APIRouter` 实例化及 `include_router` 时是否传入全局 `dependencies`：
```python
# ❌ 错误：所有子路由均需认证
api_router = APIRouter(dependencies=[Depends(get_current_user)])

# ❌ 错误：包含时附加依赖
api_router.include_router(bookmarks.router, dependencies=[Depends(get_current_user)])
```

**修复**：
- 对公开路由显式覆盖 `dependencies=[]`（临时）。
- 将需认证路由与公开路由拆分为不同 Router（长期）。

#### 5. 检查全局中间件和异常处理器
- 搜索 `@app.middleware("http")`，查看是否在请求早期阶段校验 token。
- 搜索 `@app.exception_handler`，确认是否有异常被错误映射为 401。

**典型错误映射**：
```python
@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request, exc):
    return JSONResponse(status_code=401, content={"detail": "Database error"})
```

### 四、本次问题根因回顾（书签项目案例）

| 阶段 | 发现 | 结论 |
|------|------|------|
| 初始现象 | `/tag-categories` 公开接口 401，需认证接口正常 | 路由匹配问题高度可疑 |
| 路由顺序调整 | 将静态路由提前，无效 | 可能存在更深层拦截 |
| 添加 `dependencies=[]` | 无效 | 路由函数本身未被调用 |
| 极简测试路由 | 仍 401，但日志无输出 | 请求被完全拦截在路由层之外 |
| 检查 `bookmarks.py` 缩进 | 发现部分代码缩进异常，但修正后问题依旧 | 排除缩进干扰 |
| 强制覆盖路由（main.py 中挂载） | 仍 401 | 说明问题不在路由注册层级 |
| 最终尝试：curl + 动态路由类型约束 | 添加 `:int` 后，测试路由 `print` 首次输出，但返回 500 | **动态路由拦截确认**，且响应验证失败 |
| 修复业务逻辑 | 恢复 `response_model` 与正确返回数据 | 200 成功，问题彻底解决 |

**根本原因**：`/tag-categories` 被 `/{bookmark_id}` 动态路由拦截，触发了 `get_current_active_user` 认证依赖，而该路由又因临时测试代码返回了 `None` 导致响应验证失败。

### 五、标准修复方案（针对动态路由拦截）

#### 方案 A：添加类型约束（推荐，一劳永逸）
为所有可能产生歧义的动态路由参数添加类型限定：

```python
# 修改前
@router.get("/{bookmark_id}")
@router.put("/{bookmark_id}")
@router.delete("/{bookmark_id}")

# 修改后
@router.get("/{bookmark_id:int}")
@router.put("/{bookmark_id:int}")
@router.delete("/{bookmark_id:int}")
```

#### 方案 B：更换静态路由路径（备选）
若无法修改动态路由，可将静态路由改为不会被误匹配的路径：
- `/tag-categories` → `/categories/tags`

#### 方案 C：路由顺序 + 类型约束双重保障
1. 所有静态路由置于动态路由之前。
2. 所有动态路由参数添加类型约束。

### 六、长效预防机制

| 检查项 | 频率 | 工具/方法 |
|--------|------|-----------|
| 路由定义顺序 | 每次新增路由时 | 人工 Review，静态优先 |
| 动态路由类型约束 | 每次新增动态路由时 | 强制使用 `:int` / `:uuid` 等约束 |
| 公开接口认证依赖审计 | 每周或发布前 | 检查 `/docs` 中接口的小锁图标 |
| 异常处理器响应码审计 | 每次新增异常处理时 | 确保数据库异常不返回 401/403 |
| 自动化测试 | CI 集成 | 编写测试用例：未登录访问公开接口断言 200 |

### 七、调试利器清单

| 工具/命令 | 用途 |
|-----------|------|
| `curl -v http://localhost:8000/路由` | 绕过前端，查看原始响应 |
| `http://localhost:8000/docs` | 可视化查看路由安全锁及依赖 |
| `http://localhost:8000/openapi.json` | 精确查看路由元数据 |
| 路由函数内 `print` | 判断函数是否被执行 |
| 全局中间件 `print(request.scope.get('route'))` | 查看请求匹配的实际路由对象 |
| `grep -r "exception_handler" back/` | 查找异常到 401 的映射 |

### 八、常见误区总结

| 误区 | 正确认知 |
|------|----------|
| “我没加 `Depends(get_current_user)` 就一定是公开接口” | 全局依赖、父路由依赖、动态路由拦截都可能注入认证 |
| “把静态路由放在前面就行了” | 若动态路由无类型约束，字符串仍可能被匹配 |
| “添加 `dependencies=[]` 就一定能覆盖” | 仅覆盖 Router 级依赖，无法覆盖动态路由拦截 |
| “401 一定是认证问题” | 也可能是异常处理器将其他错误映射为 401 |

---

**文档版本**：1.0  
**最后更新**：2026-04-16  
**关联项目**：FastAPI + Vue 3 书签管理器

如果需要我将此内容保存为独立的 Markdown 文件或进一步精简为检查清单格式，请告诉我。