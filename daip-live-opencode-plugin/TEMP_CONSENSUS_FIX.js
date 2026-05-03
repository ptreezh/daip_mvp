// Fixed version of consensus-skill.js without duplicate function declarations
// This is a temporary fix to test the functionality

// Consensus Calculation Skill with Concurrency Support
// 独立的共识计算技能，支持并发访问和会话隔离，符合agentskills.io标准

/**
 * 从消息中提取投票
 * @param {Array<Object>} messages - 消息列表
 * @param {string} sessionId - 会话ID，用于隔离不同会话的数据
 * @returns {Object} 投票字典，键为代理名称，值为投票(true/false)
 */
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

/**
 * 计算投票共识
 * @param {Array<Object>} messages - 包含投票信息的消息列表
 * @param {number} threshold - 达成共识所需的阈值 (0-1)
 * @param {string} sessionId - 会话ID，用于隔离不同会话的数据
 * @returns {Object} 包含共识结果的对象
 */
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
  
  let summary = `Voting Consensus (threshold: ${(threshold*100).toFixed(0)}%)\n`;
  summary += `- Total votes: ${totalVotes}\n`;
  summary += `- Yes votes: ${yesVotes}\n`;
  summary += `- Agreement: ${(agreementRatio*100).toFixed(1)}%\n`;
  summary += `- Result: ${achieved ? 'ACHIEVED' : 'NOT ACHIEVED'}\n`;
  
  if (sessionId) {
    summary += `- Session ID: ${sessionId}\n`;
  }
  
  if (Object.keys(votes).length > 0) {
    summary += `\nVotes:\n`;
    const yesVoters = Object.entries(votes)
      .filter(([_, vote]) => vote)
      .map(([agent, _]) => agent);
    const noVoters = Object.entries(votes)
      .filter(([_, vote]) => !vote)
      .map(([agent, _]) => agent);
    summary += `- Yes (${yesVoters.length}): ${yesVoters.length > 0 ? yesVoters.join(', ') : 'None'}\n`;
    summary += `- No (${noVoters.length}): ${noVoters.length > 0 ? noVoters.join(', ') : 'None'}\n`;
  }
  
  return {
    achieved,
    agreement_ratio: agreementRatio,
    summary,
    votes,
    session_id: sessionId
  };
}

/**
 * 按轮次对消息进行分组
 * @param {Array<Object>} messages - 消息列表
 * @param {string} sessionId - 会话ID，用于隔离不同会话的数据
 * @returns {Object} 按轮次分组的消息
 */
function groupMessagesByRounds(messages, sessionId = null) {
  const rounds = {};
  
  for (const message of messages || []) {
    const content = message.content || '';
    
    // 查找轮次标记
    const roundMatch = content.match(/round:\s*(\d+)/i);
    
    if (roundMatch) {
      const roundNum = parseInt(roundMatch[1], 10);
      if (!rounds[roundNum]) {
        rounds[roundNum] = [];
      }
      rounds[roundNum].push(message);
    } else {
      // 如果没有明确轮次标记，将所有消息放在第1轮
      if (!rounds[1]) {
        rounds[1] = [];
      }
      rounds[1].push(message);
    }
  }
  
  // 添加会话ID信息
  if (sessionId) {
    for (const roundMessages of Object.values(rounds)) {
      for (const msg of roundMessages) {
        msg.session_id = sessionId;
      }
    }
  }
  
  return rounds;
}

/**
 * 计算审议共识
 * @param {Array<Object>} messages - 消息列表
 * @param {number} maxRounds - 最大审议轮数
 * @param {number} convergenceThreshold - 收敛阈值 (0-1)
 * @param {string} sessionId - 会话ID，用于隔离不同会话的数据
 * @returns {Object} 包含审议共识结果的对象
 */
function calculateDeliberationConsensus(messages, maxRounds = 10, convergenceThreshold = 0.85, sessionId = null) {
  // 按轮次分组消息
  const rounds = groupMessagesByRounds(messages, sessionId);
  
  // 计算每轮的收敛度
  const convergenceHistory = calculateConvergence(rounds, sessionId);
  
  // 确定最终收敛度
  const finalConvergence = convergenceHistory[convergenceHistory.length - 1] || 0;
  const achieved = finalConvergence >= convergenceThreshold;
  
  let summary = `Deliberation Consensus\n`;
  summary += `- Max Rounds: ${maxRounds}\n`;
  summary += `- Convergence Threshold: ${(convergenceThreshold*100).toFixed(0)}%\n`;
  summary += `- Final Convergence: ${(finalConvergence*100).toFixed(1)}%\n`;
  summary += `- Result: ${achieved ? 'ACHIEVED' : 'NOT ACHIEVED'}\n`;
  
  if (sessionId) {
    summary += `- Session ID: ${sessionId}\n`;
  }
  
  summary += `\nRound Progress:\n`;
  const roundNumbers = Object.keys(rounds).sort((a, b) => parseInt(a) - parseInt(b));
  
  for (let i = 0; i < roundNumbers.length; i++) {
    const roundNum = roundNumbers[i];
    const convergenceScore = convergenceHistory[i] || 0;
    summary += `- Round ${roundNum}: ${(convergenceScore*100).toFixed(1)}% convergence\n`;
  }
  
  if (!achieved && Object.keys(rounds).length >= maxRounds) {
    summary += `\nNote: Max rounds reached without convergence.\n`;
  }
  
  return {
    achieved,
    agreement_ratio: finalConvergence,
    summary,
    convergence_history: convergenceHistory,
    rounds_count: Object.keys(rounds).length,
    session_id: sessionId
  };
}

/**
 * 计算轮次间的收敛度
 * @param {Object} rounds - 按轮次分组的消息
 * @param {string} sessionId - 会话ID，用于隔离不同会话的数据
 * @returns {Array<number>} 收敛度历史
 */
function calculateConvergence(rounds, sessionId = null) {
  const convergenceScores = [];
  const roundNumbers = Object.keys(rounds).sort((a, b) => parseInt(a) - parseInt(b));
  
  for (let i = 1; i < roundNumbers.length; i++) {
    const prevRound = rounds[roundNumbers[i-1]];
    const currRound = rounds[roundNumbers[i]];
    
    const similarity = calculateSimilarityBetweenRounds(prevRound, currRound, sessionId);
    convergenceScores.push(similarity);
  }
  
  // 如果只有一轮，收敛度为0
  if (convergenceScores.length === 0) {
    convergenceScores.push(0);
  }
  
  return convergenceScores;
}

/**
 * 计算两轮之间的相似度
 * @param {Array<Object>} roundA - 第一轮消息
 * @param {Array<Object>} roundB - 第二轮消息
 * @param {string} sessionId - 会话ID，用于隔离不同会话的数据
 * @returns {number} 相似度 (0-1)
 */
function calculateSimilarityBetweenRounds(roundA, roundB, sessionId = null) {
  if (!roundA || !roundB || roundA.length === 0 || roundB.length === 0) {
    return 0;
  }
  
  // 提取立场
  const stancesA = extractStances(roundA, sessionId);
  const stancesB = extractStances(roundB, sessionId);
  
  if (Object.keys(stancesA).length === 0 || Object.keys(stancesB).length === 0) {
    return 0;
  }
  
  // 比较立场
  let matches = 0;
  let total = 0;
  
  for (const [agent, stanceA] of Object.entries(stancesA)) {
    if (stancesB[agent] !== undefined) {
      total++;
      if (stanceA === stancesB[agent]) {
        matches++;
      }
    }
  }
  
  return total > 0 ? matches / total : 0;
}

/**
 * 从消息中提取立场
 * @param {Array<Object>} messages - 消息列表
 * @param {string} sessionId - 会话ID，用于隔离不同会话的数据
 * @returns {Object} 立场字典
 */
function extractStances(messages, sessionId = null) {
  const stances = {};
  
  for (const message of messages || []) {
    const agentName = message.agent_name || 'unknown';
    const content = message.content || '';
    
    // 查找立场标记
    const stanceMatch = content.match(/stance:\s*(support|oppose|neutral)/i);
    
    if (stanceMatch) {
      stances[agentName] = stanceMatch[1].toLowerCase();
    }
  }
  
  return stances;
}

/**
 * 计算加权共识
 * @param {Array<Object>} messages - 消息列表
 * @param {Object} weights - 代理权重映射
 * @param {number} threshold - 达成共识所需的阈值 (0-1)
 * @param {string} sessionId - 会话ID，用于隔离不同会话的数据
 * @returns {Object} 包含加权共识结果的对象
 */
function calculateWeightedConsensus(messages, weights = {}, threshold = 0.65, sessionId = null) {
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
  
  // 计算加权同意率
  let weightedYes = 0;
  let totalWeight = 0;
  
  for (const [agent, vote] of Object.entries(votes)) {
    const weight = weights[agent] || 1.0; // 默认权重为1.0
    totalWeight += weight;
    
    if (vote) {
      weightedYes += weight;
    }
  }
  
  const weightedAgreement = totalWeight > 0 ? weightedYes / totalWeight : 0;
  const achieved = weightedAgreement >= threshold;
  
  let summary = `Weighted Consensus (threshold: ${(threshold*100).toFixed(0)}%)\n`;
  summary += `- Total Weight: ${totalWeight.toFixed(2)}\n`;
  summary += `- Weighted Yes: ${weightedYes.toFixed(2)}\n`;
  summary += `- Weighted Agreement: ${(weightedAgreement*100).toFixed(1)}%\n`;
  summary += `- Result: ${achieved ? 'ACHIEVED' : 'NOT ACHIEVED'}\n`;
  
  if (sessionId) {
    summary += `- Session ID: ${sessionId}\n`;
  }
  
  if (Object.keys(votes).length > 0) {
    summary += `\nVotes and Weights:\n`;
    for (const [agent, vote] of Object.entries(votes)) {
      const weight = weights[agent] || 1.0;
      summary += `- ${agent}: ${vote ? 'Yes' : 'No'}, Weight: ${weight}\n`;
    }
  }
  
  return {
    achieved,
    agreement_ratio: weightedAgreement,
    summary,
    votes,
    session_id: sessionId
  };
}

// 导出函数以符合agentskills.io标准
if (typeof module !== 'undefined' && module.exports) {
  // Node.js 环境
  module.exports = {
    calculateVotingConsensus,
    calculateDeliberationConsensus,
    calculateWeightedConsensus,
    extractVotes,
    extractStances,
    groupMessagesByRounds
  };
} else if (typeof window !== 'undefined') {
  // 浏览器环境
  window.ConsensusSkills = {
    calculateVotingConsensus,
    calculateDeliberationConsensus,
    calculateWeightedConsensus,
    extractVotes,
    extractStances,
    groupMessagesByRounds
  };
}

// CLI入口点 - 符合agentskills.io标准
if (typeof require !== 'undefined' && require.main === module) {
  if (process.argv.length < 3) {
    console.log("Usage: node consensus-skill.js <function_name> [json_input]");
    console.log("");
    console.log("Available functions:");
    console.log("  calculateVotingConsensus - Calculate voting consensus");
    console.log("  calculateDeliberationConsensus - Calculate deliberation consensus");
    console.log("  calculateWeightedConsensus - Calculate weighted consensus");
    console.log("  extractVotes - Extract votes from messages");
    console.log("  extractStances - Extract stances from messages");
    console.log("  groupMessagesByRounds - Group messages by rounds");
    process.exit(1);
  }
  
  const functionName = process.argv[2];
  let inputData = {};
  
  try {
    // 从命令行参数或stdin获取输入
    if (process.argv[3]) {
      inputData = JSON.parse(process.argv[3]);
    } else {
      const inputStr = require('fs').readFileSync(0, 'utf-8');
      inputData = JSON.parse(inputStr);
    }
    
    // 如果没有提供action，使用命令行参数中的action
    if (!inputData.action) {
      inputData.action = functionName;
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
    case "calculateDeliberationConsensus":
      result = calculateDeliberationConsensus(
        inputData.messages || [],
        inputData.max_rounds || 10,
        inputData.convergence_threshold || 0.85,
        inputData.session_id || null
      );
      break;
    case "calculateWeightedConsensus":
      result = calculateWeightedConsensus(
        inputData.messages || [],
        inputData.weights || {},
        inputData.threshold || 0.65,
        inputData.session_id || null
      );
      break;
    case "extractVotes":
      result = {
        votes: extractVotes(inputData.messages || [], inputData.session_id || null),
        session_id: inputData.session_id || null
      };
      break;
    case "extractStances":
      result = {
        stances: extractStances(inputData.messages || [], inputData.session_id || null),
        session_id: inputData.session_id || null
      };
      break;
    case "groupMessagesByRounds":
      result = {
        rounds: groupMessagesByRounds(inputData.messages || [], inputData.session_id || null),
        session_id: inputData.session_id || null
      };
      break;
    default:
      result = { 
        error: `Unknown function: ${functionName}`,
        available_functions: [
          "calculateVotingConsensus",
          "calculateDeliberationConsensus", 
          "calculateWeightedConsensus",
          "extractVotes",
          "extractStances",
          "groupMessagesByRounds"
        ]
      };
  }
  
  console.log(JSON.stringify(result, null, 2));
}