// 测试修复后的共识技能
const fs = require('fs');
const path = require('path');

// 读取并执行文件内容
const filePath = path.join(__dirname, 'sisyphus-debatewiki-plugin', 'skills', 'consensus-skill-fixed.js');
const fileContent = fs.readFileSync(filePath, 'utf8');

// 创建一个虚拟环境来测试函数
const vm = require('vm');
const sandbox = {
  module: { exports: {} },
  exports: {},
  console: console,
  process: process,
  require: require,
  __filename: filePath,
  __dirname: path.dirname(filePath)
};

// 执行代码
vm.runInNewContext(fileContent, sandbox);

// 现在可以访问导出的函数
const { calculateVotingConsensus } = sandbox.module.exports;

console.log('🔍 测试修复后的共识技能...');

const testMessages = [
  { agent_name: 'pro', content: 'vote: yes' },
  { agent_name: 'con', content: 'vote: no' },
  { agent_name: 'mod', content: 'vote: yes' }
];

const result = calculateVotingConsensus(testMessages, 0.6);
console.log('✅ 测试结果:');
console.log(JSON.stringify(result, null, 2));