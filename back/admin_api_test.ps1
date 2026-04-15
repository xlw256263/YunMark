# 在 back 目录下执行这个命令
cd "C:\Users\shumeng\Desktop\求职\2026\FastAPI_demo\back"

# 使用相对路径创建文件
$content = @'
playwright-cli close-all
playwright-cli -s=admin-test open --headed http://localhost:8000/docs
playwright-cli -s=admin-test snapshot
Write-Host "Step 2: Register user" -ForegroundColor Cyan
playwright-cli -s=admin-test click "getByRole('button', { name: 'POST /api/v1/auth/register' })"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Try it out' })"
playwright-cli -s=admin-test fill "textarea" '{
  "username": "testadmin",
  "email": "admin@test.com",
  "password": "Admin@123456"
}'
playwright-cli -s=admin-test click "getByRole('button', { name: 'Execute' })"
Start-Sleep -Seconds 2
playwright-cli -s=admin-test screenshot --filename=01_register.png
Write-Host "Step 3: Login" -ForegroundColor Cyan
playwright-cli -s=admin-test click "getByRole('button', { name: 'POST /api/v1/auth/token' })"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Try it out' })"
playwright-cli -s\admin-test fill "input[name='username']" "admin@test.com"
playwright-cli -s\admin-test fill "input[name='password']" "Admin@123456"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Execute' })"
Start-Sleep -Seconds 2
playwright-cli -s\admin-test screenshot --filename=02_login.png
Write-Host "Please configure Bearer Token manually, then press Enter" -ForegroundColor Yellow
Read-Host "Press Enter to continue"
Write-Host "Step 4: Test permission control" -ForegroundColor Cyan
playwright-cli -s\admin-test click "getByRole('button', { name: 'GET /api/v1/admin/tags' })"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Try it out' })"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Execute' })"
Start-Sleep -Seconds 2
playwright-cli -s\admin-test screenshot --filename=03_normal_user_access.png
Write-Host "If returns 403, permission control works" -ForegroundColor Green
Write-Host "Please execute SQL: UPDATE users SET role = admin WHERE email = admin@test.com;" -ForegroundColor Cyan
Read-Host "After executing SQL, press Enter to continue"
Write-Host "Step 6: Re-login as admin" -ForegroundColor Cyan
playwright-cli -s\admin-test reload
playwright-cli -s\admin-test click "getByRole('button', { name: 'POST /api/v1/auth/token' })"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Try it out' })"
playwright-cli -s\admin-test fill "input[name='username']" "admin@test.com"
playwright-cli -s\admin-test fill "input[name='password']" "Admin@123456"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Execute' })"
Start-Sleep -Seconds 2
playwright-cli -s\admin-test screenshot --filename=04_admin_login.png
Write-Host "Please update Bearer Token with new admin token" -ForegroundColor Yellow
Read-Host "Press Enter to continue"
Write-Host "Step 7: Create tag" -ForegroundColor Cyan
playwright-cli -s\admin-test click "getByRole('button', { name: 'POST /api/v1/admin/tags' })"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Try it out' })"
playwright-cli -s\admin-test fill "textarea" '{"name": "AI"}'
playwright-cli -s\admin-test click "getByRole('button', { name: 'Execute' })"
Start-Sleep -Seconds 2
playwright-cli -s\admin-test screenshot --filename=05_create_tag.png
Write-Host "Step 8: List tags" -ForegroundColor Cyan
playwright-cli -s\admin-test click "getByRole('button', { name: 'GET /api/v1/admin/tags' })"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Try it out' })"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Execute' })"
Start-Sleep -Seconds 2
playwright-cli -s\admin-test screenshot --filename=06_list_tags.png
Write-Host "Step 9: Update tag" -ForegroundColor Cyan
$tagId = Read-Host "Enter tag ID"
playwright-cli -s\admin-test click "getByRole('button', { name: 'PUT /api/v1/admin/tags/{tag_id}' })"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Try it out' })"
playwright-cli -s\admin-test fill "input[placeholder='tag_id']" $tagId
playwright-cli -s\admin-test fill "input[placeholder='tag_name']" "Artificial Intelligence"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Execute' })"
Start-Sleep -Seconds 2
playwright-cli -s\admin-test screenshot --filename=07_update_tag.png
Write-Host "Step 10: Delete unused tag" -ForegroundColor Cyan
playwright-cli -s\admin-test click "getByRole('button', { name: 'POST /api/v1/admin/tags' })"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Try it out' })"
playwright-cli -s\admin-test fill "textarea" '{"name": "TempTag"}'
playwright-cli -s\admin-test click "getByRole('button', { name: 'Execute' })"
Start-Sleep -Seconds 1
$tempTagId = Read-Host "Enter temp tag ID"
playwright-cli -s\admin-test click "getByRole('button', { name: 'DELETE /api/v1/admin/tags/{tag_id}' })"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Try it out' })"
playwright-cli -s\admin-test fill "input[placeholder='tag_id']" $tempTagId
playwright-cli -s\admin-test click "getByRole('button', { name: 'Execute' })"
Start-Sleep -Seconds 2
playwright-cli -s\admin-test screenshot --filename=08_delete_unused_tag.png
Write-Host "Step 11: Try delete used tag (should fail)" -ForegroundColor Cyan
$usedTagId = Read-Host "Enter used tag ID"
playwright-cli -s\admin-test click "getByRole('button', { name: 'DELETE /api/v1/admin/tags/{tag_id}' })"
playwright-cli -s\admin-test click "getByRole('button', { name: 'Try it out' })"
playwright-cli -s\admin-test fill "input[placeholder='tag_id']" $usedTagId
playwright-cli -s\admin-test click "getByRole('button', { name: 'Execute' })"
Start-Sleep -Seconds 2
playwright-cli -s\admin-test screenshot --filename=09_delete_used_tag_error.png
Write-Host "`nAll tests completed!" -ForegroundColor Green
playwright-cli -s=admin-test close
'@

[System.IO.File]::WriteAllText(".\admin_api_test.ps1", $content, [System.Text.UTF8Encoding]::new($true))
Write-Host "File created successfully" -ForegroundColor Green
