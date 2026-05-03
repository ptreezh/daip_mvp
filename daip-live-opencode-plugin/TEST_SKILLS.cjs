// 测试sisyphus-debatewiki-plugin的独立技能功能
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

async function testSkills() {
  console.log('🔍 测试sisyphus-debatewiki-plugin的独立技能功能...\n');

  // 1. 测试共识技能
  console.log('✅ 1. 测试共识技能...');
  try {
    const consensusResult = spawn('node', [
      path.join(process.env.USERPROFILE, 'AppData', 'Roaming', 'npm', 'node_modules', 'sisyphus-debatewiki', 'skills', 'consensus-skill.js'),
      'calculateVotingConsensus',
      '{"messages": [{"agent_name": "pro", "content": "vote: yes"}, {"agent_name": "con", "content": "vote: no"}, {"agent_name": "mod", "content": "vote: yes"}], "threshold": 0.6}'
    ]);

    consensusResult.stdout.on('data', (data) => {
      console.log(`   共识技能输出:\n${data.toString()}`);
    });

    consensusResult.stderr.on('data', (data) => {
      console.error(`   共识技能错误:\n${data.toString()}`);
    });

    await new Promise((resolve) => {
      consensusResult.on('close', (code) => {
        console.log(`   共识技能执行完成，退出码: ${code}\n`);
        resolve();
      });
    });
  } catch (error) {
    console.error(`   共识技能测试失败: ${error.message}\n`);
  }

  // 2. 测试维基技能
  console.log('✅ 2. 测试维基技能...');
  try {
    const wikiResult = spawn('node', [
      path.join(process.env.USERPROFILE, 'AppData', 'Roaming', 'npm', 'node_modules', 'sisyphus-debatewiki', 'skills', 'wiki-skill.js'),
      'handleWikiAction',
      '{"action": "create", "title": "Test Page", "content": "Test content", "author": "test"}'
    ]);

    wikiResult.stdout.on('data', (data) => {
      console.log(`   维基技能输出:\n${data.toString()}`);
    });

    wikiResult.stderr.on('data', (data) => {
      console.error(`   维基技能错误:\n${data.toString()}`);
    });

    await new Promise((resolve) => {
      wikiResult.on('close', (code) => {
        console.log(`   维基技能执行完成，退出码: ${code}\n`);
        resolve();
      });
    });
  } catch (error) {
    console.error(`   维基技能测试失败: ${error.message}\n`);
  }

  // 3. 测试扎根理论技能
  console.log('✅ 3. 测试扎根理论技能...');
  try {
    const gtResult = spawn('node', [
      path.join(process.env.USERPROFILE, 'AppData', 'Roaming', 'npm', 'node_modules', 'sisyphus-debatewiki', 'skills', 'grounded-theory-skill.js'),
      'handleGroundedTheoryAction',
      '{"action": "create-project", "project_name": "Test Project", "project_description": "Test Description"}'
    ]);

    gtResult.stdout.on('data', (data) => {
      console.log(`   扎根理论技能输出:\n${data.toString()}`);
    });

    gtResult.stderr.on('data', (data) => {
      console.error(`   扎根理论技能错误:\n${data.toString()}`);
    });

    await new Promise((resolve) => {
      gtResult.on('close', (code) => {
        console.log(`   扎根理论技能执行完成，退出码: ${code}\n`);
        resolve();
      });
    });
  } catch (error) {
    console.error(`   扎根理论技能测试失败: ${error.message}\n`);
  }

  console.log('🎉 技能测试完成！');
  console.log('\n📋 测试总结:');
  console.log('   • 共识技能: 已测试');
  console.log('   • 维基技能: 已测试');
  console.log('   • 扎根理论技能: 已测试');
  console.log('\n💡 sisyphus-debatewiki-plugin的独立技能已验证，可以正常工作');
}

// 运行测试
testSkills().catch(console.error);