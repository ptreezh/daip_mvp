# OpenCode测试脚本 - sisyphus-debatewiki-plugin全面测试

# 测试目标：验证sisyphus-debatewiki-plugin的所有功能是否正常工作

# 测试环境准备
echo "🔍 准备测试环境..."
echo "✅ 检查OpenCode版本"
opencode --version

echo "✅ 检查当前配置"
opencode debug config | grep -i "sisyphus-debatewiki\|plugin" || echo "sisyphus-debatewiki not in config (expected)"

# 1. 论坛引擎测试
echo ""
echo "🧪 开始论坛引擎测试..."

echo "   A1. 自由辩论流程测试"
echo '   启动自由辩论: /start-free-debate topic="AI伦理" participants="proponent,opponent,moderator"'
echo "   [此测试需要在OpenCode会话中手动执行]"

echo "   A2. 对抗辩论流程测试"
echo '   启动对抗辩论: /start-adversarial-debate topic="AI对就业的影响" rounds=6'
echo "   [此测试需要在OpenCode会话中手动执行]"

echo "   A3. 小组讨论流程测试"
echo '   启动小组讨论: /start-group-discussion topic="AI安全策略" participants="insight,media,query,moderator"'
echo "   [此测试需要在OpenCode会话中手动执行]"

# 2. 共识算法测试
echo ""
echo "🧪 开始共识算法测试..."

echo "   B1. 投票共识算法测试"
echo '   计算投票共识: /consensus-voting threshold=0.7'
echo "   [此测试需要在OpenCode会话中手动执行]"

echo "   B2. 审议共识算法测试"
echo '   计算审议共识: /consensus-deliberation max_rounds=10 convergence_threshold=0.85'
echo "   [此测试需要在OpenCode会话中手动执行]"

echo "   B3. 加权共识算法测试"
echo '   计算加权共识: /consensus-weighted threshold=0.65 weights="insight:0.8,media:0.6,query:0.7"'
echo "   [此测试需要在OpenCode会话中手动执行]"

# 3. 维基协作测试
echo ""
echo "🧪 开始维基协作测试..."

echo "   C1. 页面创建功能测试"
echo '   创建维基页面: /wiki-create title="AI伦理原则" content="# AI伦理原则\n\n## 概述\n这是AI伦理原则的维基页面..."'
echo "   [此测试需要在OpenCode会话中手动执行]"

echo "   C2. 页面更新功能测试"
echo '   更新维基页面: /wiki-update page_id="wiki-123" content="## 新增章节..."'  
echo "   [此测试需要在OpenCode会话中手动执行]"

echo "   C3. 版本控制功能测试"
echo '   检查版本历史: /wiki-versioning action=list page_id="wiki-123"'
echo "   [此测试需要在OpenCode会话中手动执行]"

# 4. 扎根理论引擎测试
echo ""
echo "🧪 开始扎根理论引擎测试..."

echo "   D1. 开放编码功能测试"
echo '   创建扎根理论项目: /gt-create-project project_name="AI对就业影响研究" project_description="研究AI对不同类型工作岗位的影响"'
echo "   [此测试需要在OpenCode会话中手动执行]"

echo "   D2. 主轴编码功能测试"
echo '   执行主轴编码: /gt-axial-coding category="就业影响" subcategory="岗位替代" codes=["code1","code2"] conditions="AI技术发展" actions="岗位替代" consequences="就业结构调整"'
echo "   [此测试需要在OpenCode会话中手动执行]"

echo "   D3. 饱和度检验功能测试"
echo '   检验理论饱和度: /gt-saturation-test project_id="gt-123" new_content="新的访谈数据..."'
echo "   [此测试需要在OpenCode会话中手动执行]"

# 5. 独立技能测试
echo ""
echo "🧪 开始独立技能测试..."

echo "   测试共识技能"
node node_modules/sisyphus-debatewiki/skills/consensus-skill.js calculateVotingConsensus '{"messages": [{"agent_name": "pro", "content": "vote: yes"}, {"agent_name": "con", "content": "vote: no"}, {"agent_name": "mod", "content": "vote: yes"}], "threshold": 0.6}'

echo "   测试维基技能"
node node_modules/sisyphus-debatewiki/skills/wiki-skill.js handleWikiAction '{"action": "create", "title": "Test Page", "content": "Test content", "author": "test"}'

echo "   测试扎根理论技能"
node node_modules/sisyphus-debatewiki/skills/grounded-theory-skill.js handleGroundedTheoryAction '{"action": "create-project", "project_name": "Test Project", "project_description": "Test Description"}'

echo ""
echo "📋 测试计划执行完毕"
echo "   请在OpenCode会话中手动执行标记为'[此测试需要在OpenCode会话中手动执行]'的测试用例"
echo "   独立技能测试已自动执行"