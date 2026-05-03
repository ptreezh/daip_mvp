// 简单测试修复后的共识技能
const fs = require('fs');

// 读取文件内容
const content = fs.readFileSync('../sisyphus-debatewiki-plugin/skills/consensus-skill-fixed.js', 'utf8');

// 检查是否包含函数定义
if (content.includes('function calculateVotingConsensus')) {
  console.log('✅ 函数 calculateVotingConsensus 已定义');
} else {
  console.log('❌ 函数 calculateVotingConsensus 未定义');
}

if (content.includes('module.exports')) {
  console.log('✅ module.exports 已定义');
} else {
  console.log('❌ module.exports 未定义');
}

console.log('\n📋 文件内容检查完成');
console.log('   文件大小:', content.length, '字符');
console.log('   行数:', content.split('\n').length);