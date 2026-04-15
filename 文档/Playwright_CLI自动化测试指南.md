以下是精简后的 Markdown 文档，保留了所有关键信息，格式清晰，可直接一键复制。

```markdown
# Playwright CLI 自动化测试使用指南

## 环境准备

```powershell
npm install -g @playwright/cli@latest
cd back
uvicorn app.main:app --reload   # 后端运行在 http://localhost:8000
```

## 常见问题与解决方案

### 1. 浏览器闪退
**解决**：加 `--headed` 参数  
```powershell
playwright-cli open --headed http://localhost:8000/docs
```

### 2. PowerShell 中文乱码
**解决**：脚本中使用英文注释  
```powershell
Write-Host "Step 1: Register user" -ForegroundColor Cyan
```

### 3. 中文路径导致文件找不到
**解决**：使用相对路径，或在 PowerShell 配置中设置 UTF-8  
```powershell
cd "C:\...\FastAPI_demo\back"
[System.IO.File]::WriteAllText(".\test.ps1", $content, [System.Text.UTF8Encoding]::new($true))
```

### 4. `playwright-cli` 命令找不到
**解决**：使用 `npx` 或重新安装  
```powershell
npx playwright-cli open --headed http://localhost:8000/docs
```

## 快速开始

### 方式1：手动交互（新手）

```powershell
playwright-cli -s=test open --headed http://localhost:8000/docs
playwright-cli -s=test snapshot
playwright-cli -s=test click "getByRole('button', { name: 'POST /api/v1/auth/register' })"
playwright-cli -s=test click "getByRole('button', { name: 'Try it out' })"
playwright-cli -s=test fill "textarea" '{"username":"test","email":"test@test.com","password":"Test@123"}'
playwright-cli -s=test click "getByRole('button', { name: 'Execute' })"
playwright-cli -s=test screenshot --filename=result.png
playwright-cli -s=test close
```

### 方式2：PowerShell 脚本（熟练后）

创建 `admin_test.ps1`（英文注释），示例片段：

```powershell
playwright-cli close-all
playwright-cli -s=admin-test open --headed http://localhost:8000/docs
Start-Sleep -Seconds 2
# 注册、登录、测试权限、创建标签等步骤...
```

执行：`.\admin_test.ps1`

## 完整测试流程（管理员标签管理）

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 注册用户 `testadmin` | 200 OK |
| 2 | 登录获取 token | 200, 返回 access_token |
| 3 | 配置 Swagger Authorize | 成功 |
| 4 | 普通用户访问 `GET /admin/tags` | **403 Forbidden** |
| 5 | MySQL 执行 `UPDATE users SET role='admin' WHERE email='admin@test.com'` | 成功 |
| 6 | 重新登录获取新 token | 200, token 含 admin 角色 |
| 7 | 创建标签 `{"name":"AI"}` | 200, 返回 id |
| 8 | 获取标签列表 | 200, 包含 usage_count |
| 9 | 更新标签名称 | 200 |
| 10 | 删除未使用标签 | 200 |
| 11 | 删除已使用标签 | **409 Conflict** |

## 常用命令速查

```powershell
# 浏览器控制
playwright-cli -s=mytest open --headed http://localhost:8000/docs
playwright-cli -s=mytest close
playwright-cli close-all
playwright-cli -s=mytest reload

# 交互
playwright-cli -s=mytest snapshot
playwright-cli -s=mytest click "getByRole('button', { name: 'Submit' })"
playwright-cli -s=mytest fill "input[name='username']" "admin"
playwright-cli -s=mytest press Enter

# 截图调试
playwright-cli -s=mytest screenshot --filename=out.png
playwright-cli -s=mytest console
playwright-cli -s=mytest network

# 会话
playwright-cli list
playwright-cli -s=mytest state-save auth.json
playwright-cli -s=mytest state-load auth.json
```

## 最佳实践

1. **始终使用会话名称**：`-s=mysession`
2. **关键操作后等待**：`Start-Sleep -Seconds 2`
3. **优先用 Locator 而非 ref**：`getByRole(...)` 比 `e15` 稳定
4. **脚本中只用英文注释**
5. **每步截图**：便于回溯
6. **脚本开头清理旧会话**：`playwright-cli close-all`
7. **需手动干预时用 `Read-Host` 暂停**

## 附录：常见状态码

| 状态码 | 含义 |
|--------|------|
| 401 | Token 无效/过期 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 冲突（如删除使用中的标签） |
| 422 | 参数校验失败 |

---

**版本**：v1.0 | **日期**：2026-04-15
```

