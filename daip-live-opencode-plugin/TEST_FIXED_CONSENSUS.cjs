// 测试脚本 - 使用临时修复的共识技能
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

async function testFixedConsensusSkill() {
  console.log('🔍 测试修复后的共识技能...\n');

  // 创建临时修复文件
  const tempFilePath = path.join(__dirname, 'TEMP_CONSENSUS_SKILL_FIXED.js');
  const fixedCode = `
// Fixed version of consensus skill without duplicate function declarations
// This is a temporary fix to test the functionality

function extractVotes(messages, sessionId = null) {
  const votes = {};
  
  for (const message of messages || []) {
    const agentName = message.agent_name || 'unknown';
    const content = message.content || '';
    
    // 查找投票模式
    if (content.toLowerCase().includes('vote:')) {
      if (content.toLowerCase().includes('yes') || 
          content.toLowerCase().includes('agree') || 
          content.toLowerCase().includes('support')) {
        votes[agentName] = true;
      } else if (content.toLowerCase().includes('no') || 
                 content.toLowerCase().includes('disagree') || 
                 content.toLowerCase().includes('oppose')) {
        votes[agentName] = false;
      }
    }
  }
  
  return votes;
}

function calculateVotingConsensus(messages, threshold = 0.7, sessionId = null) {
  const votes = extractVotes(messages, sessionId);
  
  if (Object.keys(votes).length === 0) {
    return {
      achieved: false,
      agreement_ratio: 0.0,
      summary: "No votes found in messages",
      votes: {},
      session_id: sessionId
    };
  }
  
  const yesVotes = Object.values(votes).filter(vote => vote).length;
  const totalVotes = Object.keys(votes).length;
  
  const agreementRatio = totalVotes > 0 ? yesVotes / totalVotes : 0;
  const achieved = agreementRatio >= threshold;
  
  let summary = \`Voting Consensus (threshold: \${(threshold*100).toFixed(0)}%)\n\`;
  summary += \`- Total votes: \${totalVotes}\n\`;
  summary += \`- Yes votes: \${yesVotes}\n\`;
  summary += \`- Agreement: \${(agreementRatio*100).toFixed(1)}%\n\`;
  summary += \`- Result: \${achieved ? 'ACHIEVED' : 'NOT ACHIEVED'}\n\`;
  
  if (sessionId) {
    summary += \`- Session ID: \${sessionId}\n\`;
  }
  
  if (Object.keys(votes).length > 0) {
    summary += \`\\nVotes:\\n\`;
    const yesVoters = Object.entries(votes)
      .filter(([_, vote]) => vote)
      .map(([agent, _]) => agent);
    const noVoters = Object.entries(votes)
      .filter(([_, vote]) => !vote)
      .map(([agent, _]) => agent);
    summary += \`- Yes (\${yesVoters.length}): \${yesVoters.length > 0 ? yesVoters.join(', ') : 'None'}\\n\`;
    summary += \`- No (\${noVoters.length}): \${noVoters.length > 0 ? noVoters.join(', ') : 'None'}\\n\`;
  }
  
  return {
    achieved,
    agreement_ratio: agreementRatio,
    summary,
    votes,
    session_id: sessionId
  };
}

// CLI入口点
if (typeof require !== 'undefined' && require.main === module) {
  if (process.argv.length < 3) {
    console.log("Usage: node consensus-skill.js <function_name> [json_input]");
    console.log("");
    console.log("Available functions:");
    console.log("  calculateVotingConsensus - Calculate voting consensus");
    process.exit(1);
  }
  
  const functionName = process.argv[2];
  let inputData = {};
  
  try {
    if (process.argv[3]) {
      inputData = JSON.parse(process.argv[3]);
    } else {
      const inputStr = require('fs').readFileSync(0, 'utf-8');
      inputData = JSON.parse(inputStr);
    }
  } catch (e) {
    console.error("Error parsing input:", e.message);
    process.exit(1);
  }
  
  let result;
  
  switch (functionName) {
    case "calculateVotingConsensus":
      result = calculateVotingConsensus(
        inputData.messages || [],
        inputData.threshold || 0.7,
        inputData.session_id || null
      );
      break;
    default:
      result = { 
        error: \`Unknown function: \${functionName}\`,
        available_functions: ["calculateVotingConsensus"]
      };
  }
  
  console.log(JSON.stringify(result, null, 2));
}

// 导出函数以符合agentskills.io标准
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    calculateVotingConsensus,
    extractVotes
  };
}
  `;
  
  fs.writeFileSync(tempFilePath, fixedCode);
  console.log('✅ 创建临时修复文件');

  // 测试修复后的技能
  console.log('\n✅ 运行共识技能测试...');
  const testProcess = spawn('node', [
    tempFilePath,
    'calculateVotingConsensus',
    '{"messages": [{"agent_name": "pro", "content": "vote: yes"}, {"agent_name": "con", "content": "vote: no"}, {"agent_name": "mod", "content": "vote: yes"}], "threshold": 0.6}'
  ]);

  testProcess.stdout.on('data', (data) => {
    console.log(`   输出:\n${data.toString()}`);
  });

  testProcess.stderr.on('data', (data) => {
    console.error(`   错误:\n${data.toString()}`);
  });

  await new Promise((resolve) => {
    testProcess.on('close', (code) => {
      console.log(`\n✅ 共识技能测试完成，退出码: ${code}`);
      resolve();
    });
  });

  // 删除临时文件
  fs.unlinkSync(tempFilePath);
  console.log('\n🗑️  删除临时修复文件');

  console.log('\n🎉 测试完成！');
}

// 运行测试
testFixedConsensusSkill().catch(console.error);