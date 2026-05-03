# OpenCode测试脚本 - sisyphus-debatewiki-plugin全面测试

Write-Host "🔍 准备测试环境..." -ForegroundColor Green

# 检查OpenCode版本
Write-Host "✅ 检查OpenCode版本"
$version = opencode --version
Write-Host "   OpenCode版本: $version" -ForegroundColor Cyan

# 检查当前配置
Write-Host "`n✅ 检查当前配置" -ForegroundColor Green
$config = Get-Content "$env:USERPROFILE\.config\opencode\opencode.json" -Raw | ConvertFrom-Json
Write-Host "   当前插件: $($config.plugin -join ', ')" -ForegroundColor Cyan

# 1. 独立技能测试
Write-Host "`n🧪 开始独立技能测试..." -ForegroundColor Green

Write-Host "   测试共识技能" -ForegroundColor Yellow
try {
  $consensusResult = node "$env:USERPROFILE\node_modules\sisyphus-debatewiki\skills\consensus-skill.js" calculateVotingConsensus '{\"messages\": [{\"agent_name\": \"pro\", \"content\": \"vote: yes\"}, {\"agent_name\": \"con\", \"content\": \"vote: no\"}, {\"agent_name\": \"mod\", \"content\": \"vote: yes\"}], \"threshold\": 0.6}'
  Write-Host "   ✅ 共识技能测试通过" -ForegroundColor Green
} catch {
  Write-Host "   ❌ 共识技能测试失败: $_" -ForegroundColor Red
}

Write-Host "   测试维基技能" -ForegroundColor Yellow
try {
  $wikiResult = node "$env:USERPROFILE\node_modules\sisyphus-debatewiki\skills\wiki-skill.js" handleWikiAction '{\"action\": \"create\", \"title\": \"Test Page\", \"content\": \"Test content\", \"author\": \"test\"}'
  Write-Host "   ✅ 维基技能测试通过" -ForegroundColor Green
} catch {
  Write-Host "   ❌ 维基技能测试失败: $_" -ForegroundColor Red
}

Write-Host "   测试扎根理论技能" -ForegroundColor Yellow
try {
  $gtResult = node "$env:USERPROFILE\node_modules\sisyphus-debatewiki\skills\grounded-theory-skill.js" handleGroundedTheoryAction '{\"action\": \"create-project\", \"project_name\": \"Test Project\", \"project_description\": \"Test Description\"}'
  Write-Host "   ✅ 扎根理论技能测试通过" -ForegroundColor Green
} catch {
  Write-Host "   ❌ 扎根理论技能测试失败: $_" -ForegroundColor Red
}

# 2. 功能模块测试计划
Write-Host "`n📋 功能模块测试计划" -ForegroundColor Green
Write-Host "   以下测试需要在OpenCode会话中手动执行:" -ForegroundColor Cyan

Write-Host "`n   A. 论坛引擎测试"
Write-Host "   - /start-free-debate topic='AI伦理' participants='proponent,opponent,moderator'"
Write-Host "   - /start-adversarial-debate topic='AI对就业的影响' rounds=6"
Write-Host "   - /start-group-discussion topic='AI安全策略' participants='insight,media,query,moderator'"

Write-Host "`n   B. 共识算法测试"
Write-Host "   - /consensus-voting threshold=0.7"
Write-Host "   - /consensus-deliberation max_rounds=10 convergence_threshold=0.85"
Write-Host "   - /consensus-weighted threshold=0.65 weights='insight:0.8,media:0.6,query:0.7'"

Write-Host "`n   C. 维基协作测试"
Write-Host "   - /wiki-create title='AI伦理原则' content='# AI伦理原则...'"
Write-Host "   - /wiki-update page_id='...' content='## 新增章节...'"
Write-Host "   - /wiki-versioning action=list page_id='...'"

Write-Host "`n   D. 扎根理论引擎测试"
Write-Host "   - /gt-create-project project_name='AI对就业影响研究' project_description='研究AI对不同类型工作岗位的影响'"
Write-Host "   - /gt-axial-coding category='就业影响' subcategory='岗位替代' codes=['code1','code2']"
Write-Host "   - /gt-saturation-test project_id='...' new_content='新的访谈数据...'"

Write-Host "`n🎉 测试计划执行完毕" -ForegroundColor Green
Write-Host "   独立技能测试已完成，功能模块测试需要在OpenCode会话中手动执行" -ForegroundColor Cyan