import csv
import os
import random
import string
import time
from typing import Any

import requests
import tiktoken

# 导入adaptive提示词模块
try:
    from adaptive_prompts import ADAPTIVE_SYSTEM_PROMPTS, get_adaptive_messages

    ADAPTIVE_AVAILABLE = True
    print("✅ Adaptive prompts module loaded successfully")
except ImportError:
    ADAPTIVE_AVAILABLE = False
    print("⚠️ Adaptive prompts module not found, using standard prompts")

# === Qiniu DeepSeek (OpenAI兼容) API 配置 ===
QINIU_API_URL = "https://api.qnaigc.com/v1/chat/completions"
QINIU_API_KEY = (
    "sk-85a07f1fd99e9ebb760104e7257a8678c0f0e018fd1a22019e4506323b6db0af"  # 请替换为你的实际密钥
)
QINIU_GROUP = "DeepSeek"  # 分组名称（如有需要）

# --- CONFIGURATION ---
# 请根据您的本地Ollama服务进行配置
OLLAMA_API_URL = "http://localhost:11434/api/chat"
# 需要进行评测的模型列表
MODELS_TO_TEST = [
    "deepseek-v3-qiniu",  # 优先测试七牛云 DeepSeek 外部API模型
    "qwen3:4b",
    "gemma3:latest"
    #  'atlas/intersync-gemma-7b-instruct-function-calling:latest', # 如果您有这个模型
    #  'mistral-nemo:latest',
    #  'cogito:latest',
    #  'yi:6b',
    #  'deepseek-coder:6.7b-instruct',
    #  'qwen:7b-chat'
    # 'exaone-deep:7.8b'
]
MAX_CONTEXT_TOKENS = 8192  # 假设所有模型的上下文窗口为8k
NUM_TEST_CASES = 5  # 增加为5轮测试
# 增加任务复杂度，生成6万字以上的对话
TOTAL_TURNS_PER_CASE = 2000  # 每轮平均约30字，2000轮约6万字
API_TIMEOUT = 3000  # API调用超时时间（秒），对于大模型推理，可能需要设置长一点

# 使用tiktoken进行精确的token计算
try:
    TOKENIZER = tiktoken.get_encoding("cl100k_base")
except Exception:
    TOKENIZER = tiktoken.encoding_for_model("gpt-4")  # 备用方案

# --- 1. DATA GENERATION (IMPROVED) ---


def generate_god_view_script() -> dict[str, Any]:
    """动态生成一个独立的'狼人杀'案件剧本。
    返回包含凶手、动机、强线索和弱线索(干扰项)的字典
    增加干扰项比例，并引入多重推理（伪动机、伪强线索）
    """
    roles = list(string.ascii_uppercase)[:13]  # A-M
    killer = random.choice(roles)
    # 随机选一个伪嫌疑人
    fake_suspect = random.choice([r for r in roles if r != killer])
    motives = {
        "lumberjack": {
            "motive_desc": "因木材利润纠纷而行凶",
            "strong_clues": [
                f"案发现场发现了稀有的松木碎屑，只有伐木工 {killer} 会接触这种木材",
                f"{killer} 的斧头最近被异常仔细地打磨和清洗过",
                f"有村民听到 {killer} 在案发前晚对受害者咆哮说'这是你最后一次交货'",
            ],
            "red_herrings": [
                "当晚有人听到了奇怪的野兽嚎叫声",
                "一个常在河边散步的村民看到一个模糊的黑影跳入水中",
                "受害者最近似乎中了一笔小彩票，但很快就花光了",
            ],
        },
        "baker": {
            "motive_desc": "因商业竞争而下毒",
            "strong_clues": [
                "法医在受害者的茶杯中检测到微量杏仁味毒素",
                f"面包师 {killer} 最近从黑市购买了一批被称为'特殊发酵粉'的化学品",
                f"在受害者的垃圾桶里发现了一张被撕碎的、写有 {killer} 字迹的配方纸条",
            ],
            "red_herrings": [
                "受害者的窗户被发现是开着的",
                f"另一位村民 {random.choice([r for r in roles if r != killer])} 前几天也和受害者发生过激烈争吵",
                "案发现场附近的一棵树上挂着一块深色布料",
            ],
        },
    }
    motive_key = random.choice(list(motives.keys()))
    script = motives[motive_key]
    # 增加干扰项比例：将red_herrings数量翻倍
    weak_clues = script["red_herrings"] * 2
    # 引入多重推理：生成伪动机和伪强线索
    fake_motive = f"{fake_suspect} 因为与受害者有经济纠纷，近期行为异常。"
    fake_strong_clues = [
        f"有人看到 {fake_suspect} 深夜出现在案发现场附近，神色慌张",
        f"{fake_suspect} 的衣服上发现了疑似受害者的血迹",
        f"有匿名信指控 {fake_suspect} 曾威胁受害者",
    ]
    # 将伪强线索混入all_clues
    all_clues = script["strong_clues"] + weak_clues + fake_strong_clues
    random.shuffle(all_clues)
    return {
        "true_killer": killer,
        "motive": script["motive_desc"],
        "strong_clues": script["strong_clues"],
        "weak_clues": weak_clues,
        "fake_motive": fake_motive,
        "fake_strong_clues": fake_strong_clues,
        "all_clues": all_clues,
    }


def generate_dialogue(script: dict[str, Any], total_turns: int) -> str:
    """根据剧本，生成包含大量噪音和关键线索的对话文本。
    """
    dialogue_lines = []
    roles = list(string.ascii_uppercase)[:13]
    clues_to_inject = script["all_clues"].copy()
    random.shuffle(clues_to_inject)

    injection_points = sorted(
        random.sample(range(50, total_turns - 50), len(clues_to_inject))
    )

    common_templates = [
        "最近村里气氛很怪。",
        "我会注意身边的动静。",
        "我觉得大家应该团结起来。",
        "说实话，我有点害怕，昨晚根本没敢出门。",
        "大家都别乱猜了，咱们还是把知道的都说出来吧。",
        "唉，这种事怎么会发生在我们村啊……",
        "我觉得线索太零碎了。",
        "要不我们轮流说说昨晚都干了啥？",
    ]

    clue_idx = 0
    for i in range(total_turns):
        speaker = random.choice(roles)
        if clue_idx < len(injection_points) and i == injection_points[clue_idx]:
            clue = clues_to_inject[clue_idx]
            line = f"{speaker}：我好像发现了点什么…… {clue}。不过也可能是我多心了。"
            clue_idx += 1
        else:
            line = f"{speaker}：{random.choice(common_templates)}"
        dialogue_lines.append(line)

    return "\n".join(dialogue_lines)


# --- 2. PROMPT ENGINEERING ---


def get_prompt(prompt_type: str, context: dict[str, str] = {}, model: str = "") -> str:
    # 优化系统提示词：强化侦探角色和破案目标，强调因果关系和排除法
    optimized_system_prompt = (
        "你是一名经验丰富的侦探，你的任务是破解这起谋杀案，找出真凶，并用证据支持你的结论。"
        "请建立清晰的因果关系（哪个证据指向哪个嫌疑人，以及为什么），"
        "并详细说明为什么排除其他嫌疑人，如何识别和排除伪造线索。"
    )
    # 针对atlas/intersync-gemma模型的英文缩写格式（最高效）
    if "atlas/intersync-gemma" in model:
        if prompt_type == "intermediate":
            if (
                context.get("summary_so_far", "").strip()
                and context.get("summary_so_far", "").strip() != "None"
            ):
                summary = context["summary_so_far"][:60]
                new_content = context["new_dialogue_chunk"][:50]
                return f"E:{summary} N:{new_content} U:"
            else:
                content = context["new_dialogue_chunk"][:70]
                return f"S:{content}"
        elif prompt_type == "final":
            facts = context.get("summary_so_far", "")[:150]
            return f"E:{facts} K?"
    # 标准提示词（其他模型）
    if prompt_type == "intermediate":
        if (
            context.get("summary_so_far", "").strip()
            and context.get("summary_so_far", "").strip() != "None"
        ):
            return f"""System: {optimized_system_prompt}\n\nPrevious summary: {context['summary_so_far']}\n\nNew dialogue segment: {context['new_dialogue_chunk']}\n\n请用简明、逻辑缜密的语言更新摘要，突出因果链条（哪个证据指向哪个嫌疑人，以及为什么），并说明如何排除其他嫌疑人和伪造线索："""
        else:
            return f"""System: {optimized_system_prompt}\n\n请总结本段对话，突出关键证据、因果关系（哪个证据指向哪个嫌疑人，以及为什么），并说明如何排除其他嫌疑人和伪造线索：\n\n{context['new_dialogue_chunk']}\n\n摘要（简明、逻辑缜密）："""
    elif prompt_type == "final":
        return f"""System: {optimized_system_prompt}\n\n请基于所有已收集的证据和信息，分析并确定谁是真正的凶手。\n\n完整证据摘要: {context.get('summary_so_far', '')}\n\n请给出你的最终推理和结论，必须建立清晰的因果关系（哪个证据指向哪个嫌疑人，以及为什么），并详细说明为什么排除其他嫌疑人，以及如何识别和排除伪造线索："""
    return ""


# --- 3. EXECUTION & EVALUATION ---


def call_ollama(
    model: str,
    prompt: str,
    use_adaptive: bool = True,
    test_context: str = "detective_reasoning",
    max_retries: int = 10,
) -> str:
    """Calls the Ollama API and returns the content of the response.
    支持adaptive提示词功能和零响应重试机制，针对atlas模型进行特殊优化

    Args:
    ----
        model: 模型名称
        prompt: 用户提示词
        use_adaptive: 是否使用adaptive提示词
        test_context: 测试上下文，用于选择合适的adaptive提示词
        max_retries: 最大重试次数
    """
    print(f"    - Calling model: {model}...")

    # 针对atlas/intersync-gemma模型的特殊处理
    if "atlas/intersync-gemma" in model:
        # 使用精简系统提示词（不超过80字符）
        system_prompt = (
            "Detective. Analyze murder case. Summarize key evidence concisely."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        print(
            f"    🎯 Using optimized prompt for atlas model (total: {len(system_prompt + prompt)} chars)"
        )
    else:
        # 标准模型的adaptive提示词处理
        if use_adaptive and ADAPTIVE_AVAILABLE:
            try:
                # 为TestLLM创建一个虚拟的测试脚本名，基于测试上下文
                test_script_name = f"test_pillar_{test_context}.py"

                # 检查是否有针对该模型的adaptive提示词
                if (
                    model in ADAPTIVE_SYSTEM_PROMPTS
                    and test_script_name in ADAPTIVE_SYSTEM_PROMPTS[model]
                ):
                    system_prompt = ADAPTIVE_SYSTEM_PROMPTS[model][test_script_name]
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ]
                    print(f"    📝 Using adaptive system prompt for {model}")
                else:
                    # 如果没有特定的adaptive提示词，使用通用的detective reasoning提示词
                    if model in ADAPTIVE_SYSTEM_PROMPTS:
                        # 使用该模型的任意一个adaptive提示词作为基础
                        available_prompts = list(ADAPTIVE_SYSTEM_PROMPTS[model].keys())
                        if available_prompts:
                            # 修改为适合detective reasoning的提示词
                            detective_prompt = "You are an expert detective and logical reasoning engine. Your task is to analyze evidence, identify patterns, and draw logical conclusions from the provided information. Focus on clear, step-by-step reasoning."
                            messages = [
                                {"role": "system", "content": detective_prompt},
                                {"role": "user", "content": prompt},
                            ]
                            print(
                                f"    📝 Using adapted detective reasoning prompt for {model}"
                            )
                        else:
                            messages = [{"role": "user", "content": prompt}]
                    else:
                        messages = [{"role": "user", "content": prompt}]
            except Exception as e:
                print(f"    ⚠️ Adaptive prompts failed, using standard: {e}")
                messages = [{"role": "user", "content": prompt}]
        else:
            # 使用标准消息格式
            messages = [{"role": "user", "content": prompt}]

    # 零响应重试机制
    for attempt in range(max_retries):
        # 针对atlas模型的强化参数优化（确保零响应）
        if "atlas/intersync-gemma" in model:
            # 渐进式参数调整策略
            if attempt <= 2:
                # 前3次尝试：标准参数
                temp = 0.6 + (attempt * 0.2)
                top_p = 0.95
                top_k = 60
            elif attempt <= 5:
                # 第4-6次：提高随机性
                temp = 0.9 + (attempt * 0.1)
                top_p = 0.98
                top_k = 80
            else:
                # 第7-10次：最大随机性
                temp = 1.2 + (attempt * 0.1)
                top_p = 1.0
                top_k = 100

            options = {
                "temperature": min(temp, 2.0),  # 限制最大温度
                "top_p": top_p,
                "top_k": top_k,
                "repeat_penalty": max(1.0, 1.05 - (attempt * 0.01)),  # 逐步降低重复惩罚
                "timeout": 40,
                "num_ctx": max(1024, 2048 - (attempt * 100)),  # 逐步减少上下文
                "num_predict": 100 + (attempt * 10),  # 逐步增加输出长度
                "seed": -1,  # 随机种子
                "mirostat": 2 if attempt > 3 else 0,  # 后期启用mirostat
                "mirostat_tau": 5.0 if attempt > 3 else 5.0,
            }
        else:
            options = {
                "temperature": 0.1 + (attempt * 0.1),  # 逐步增加温度
                "top_p": 0.9,
                "timeout": 30,
            }

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": options,
        }

        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=API_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "")

            if content and content.strip():
                # 成功获得非空响应
                if attempt > 0:
                    print(f"    ✅ Success on retry {attempt + 1}: {len(content)} chars")
                else:
                    print(f"    ✅ Success: {len(content)} chars")
                return content
            else:
                # 零响应，需要重试
                print(f"    ⚠️ Zero response on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    print("    🔄 Retrying with adjusted parameters...")
                    time.sleep(2)  # 等待2秒后重试
                    continue
                else:
                    print("    ❌ All retries failed - returning empty response")
                    return ""

        except requests.exceptions.Timeout:
            print(f"    ⏰ Timeout on attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                print("    🔄 Retrying after timeout...")
                time.sleep(3)  # 超时后等待更长时间
                continue
            else:
                return f"[API Error: Timeout after {max_retries} attempts]"

        except requests.exceptions.RequestException as e:
            print(f"    ❌ Request error on attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                print("    🔄 Retrying after error...")
                time.sleep(2)
                continue
            else:
                return f"[API Error: {e} after {max_retries} attempts]"

    return f"[API Error: All {max_retries} attempts failed]"


def call_qiniu_deepseek(prompt: str, max_retries: int = 5) -> str:
    """调用七牛云 DeepSeek (OpenAI兼容) API，返回响应内容。
    """
    headers = {
        "Authorization": f"Bearer {QINIU_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-v3",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.7,
        # "group": QINIU_GROUP  # 如API支持分组参数可加上
    }
    for attempt in range(max_retries):
        try:
            response = requests.post(
                QINIU_API_URL, headers=headers, json=payload, timeout=60
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            if content and content.strip():
                print(f"    ✅ Qiniu DeepSeek success: {len(content)} chars")
                return content
        except Exception as e:
            print(f"    ❌ Qiniu DeepSeek API error: {e}")
            time.sleep(2)
    return "[API Error: Qiniu DeepSeek API failed]"


def save_detailed_test_data(
    case_num: int,
    model: str,
    script: dict[str, Any],
    dialogue: str,
    prompts_and_responses: list,
    final_reasoning: str,
):
    """保存每次测试的详细数据，包括剧本全文、分段对话、提示词和响应
    """
    # 创建测试案例专用文件夹
    safe_model_name = model.replace("/", "_").replace(":", "_")
    case_folder = f"case_{case_num}_{safe_model_name}"
    if not os.path.exists(case_folder):
        os.makedirs(case_folder)

    # 1. 保存完整剧本信息
    script_content = f"""=== 案例 {case_num} 完整剧本 ===
测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
测试模型: {model}

--- 案件基本信息 ---
真正凶手: {script['true_killer']}
作案动机: {script['motive']}

--- 关键证据 (强线索) ---
{chr(10).join(f"{i+1}. {clue}" for i, clue in enumerate(script['strong_clues']))}

--- 干扰信息 (弱线索) ---
{chr(10).join(f"{i+1}. {clue}" for i, clue in enumerate(script['weak_clues']))}

--- 伪动机 ---
{script['fake_motive']}

--- 伪强线索 ---
{chr(10).join(f"{i+1}. {clue}" for i, clue in enumerate(script['fake_strong_clues']))}

--- 所有线索混合 ---
{chr(10).join(f"{i+1}. {clue}" for i, clue in enumerate(script['all_clues']))}
"""

    with open(os.path.join(case_folder, "01_script.txt"), "w", encoding="utf-8") as f:
        f.write(script_content)

    # 2. 保存完整对话文本（分段保存）
    dialogue_lines = dialogue.split("\n")
    lines_per_segment = 500  # 每段500行对话

    for i in range(0, len(dialogue_lines), lines_per_segment):
        segment_lines = dialogue_lines[i : i + lines_per_segment]
        segment_num = i // lines_per_segment + 1
        segment_content = f"""=== 对话段落 {segment_num} ===
行数范围: {i+1} - {min(i+lines_per_segment, len(dialogue_lines))}
总行数: {len(dialogue_lines)}

{chr(10).join(segment_lines)}
"""
        with open(
            os.path.join(case_folder, f"02_dialogue_segment_{segment_num:02d}.txt"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(segment_content)

    # 3. 保存所有提示词和响应
    prompts_content = f"""=== 案例 {case_num} 所有提示词和响应 ===
测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
测试模型: {model}
总交互次数: {len(prompts_and_responses)}

"""

    for i, interaction in enumerate(prompts_and_responses, 1):
        prompts_content += f"""
--- 交互 {i} ---
类型: {interaction['type']}
Token范围: {interaction.get('token_range', 'N/A')}

【提示词】
{interaction['prompt']}

【模型响应】
{interaction['response']}

{'='*50}
"""

    with open(
        os.path.join(case_folder, "03_prompts_and_responses.txt"), "w", encoding="utf-8"
    ) as f:
        f.write(prompts_content)

    # 4. 保存最终推理
    final_content = f"""=== 案例 {case_num} 最终推理 ===
测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
测试模型: {model}

--- 最终推理结果 ---
{final_reasoning}

--- 正确答案对照 ---
正确凶手: {script['true_killer']}
作案动机: {script['motive']}

--- 评判要点 ---
1. 是否正确识别凶手 {script['true_killer']}
2. 是否有效利用关键证据
3. 是否被干扰信息误导
4. 推理逻辑是否清晰
5. 是否识别并排除伪线索
"""

    with open(
        os.path.join(case_folder, "04_final_reasoning.txt"), "w", encoding="utf-8"
    ) as f:
        f.write(final_content)

    # 5. 创建测试摘要
    summary_content = f"""=== 案例 {case_num} 测试摘要 ===
测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
测试模型: {model}

--- 文件说明 ---
01_script.txt - 完整案件剧本和线索信息
02_dialogue_segment_XX.txt - 分段对话内容
03_prompts_and_responses.txt - 所有提示词和模型响应
04_final_reasoning.txt - 最终推理结果和评判标准

--- 快速对比 ---
正确答案: {script['true_killer']}
模型是否提及正确凶手: {'是' if script['true_killer'] in final_reasoning else '否'}
响应长度: {len(final_reasoning)} 字符
响应状态: {'正常' if final_reasoning and '[API Error:' not in final_reasoning else '异常'}

--- 人工评判提示 ---
请查看 04_final_reasoning.txt 中的最终推理，
对比正确答案 {script['true_killer']}，
评估模型的推理质量和准确性。
"""

    with open(os.path.join(case_folder, "00_README.txt"), "w", encoding="utf-8") as f:
        f.write(summary_content)

    print(f"    ✅ 详细测试数据已保存到文件夹: {case_folder}")
    return case_folder


def save_case_analysis(
    case_num: int, model: str, script: dict[str, Any], final_reasoning: str
):
    """保存案例分析报告，包含正确答案和评判标准（保持向后兼容）
    """
    # 检查模型响应质量
    if not final_reasoning or final_reasoning.strip() == "":
        reasoning_status = "❌ 模型未提供分析 (可能是零响应问题)"
        reasoning_content = "无响应内容"
    elif "[API Error:" in final_reasoning:
        reasoning_status = "❌ API调用错误"
        reasoning_content = final_reasoning
    else:
        reasoning_status = "✅ 模型提供了分析"
        reasoning_content = final_reasoning

    analysis_report = f"""
=== 案例 {case_num} 分析报告 ===
模型: {model}
时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
状态: {reasoning_status}

--- 模型原始分析 ---
{reasoning_content}

--- 正确答案与评判标准 ---
✅ 正确凶手: {script['true_killer']}
✅ 作案动机: {script['motive']}

✅ 关键证据 (强线索):
{chr(10).join(f"  • {clue}" for clue in script['strong_clues'])}

⚠️ 干扰信息 (弱线索):
{chr(10).join(f"  • {clue}" for clue in script['weak_clues'])}

❗ 伪动机:
  • {script['fake_motive']}
❗ 伪强线索:
{chr(10).join(f"  • {clue}" for clue in script['fake_strong_clues'])}

📋 评判标准:
1. 凶手识别 (是否正确指出 {script['true_killer']})
2. 证据使用 (是否有效利用关键证据)
3. 逻辑推理 (推理链是否清晰连贯)
4. 干扰排除 (是否被弱线索或伪线索误导)
5. 多重推理 (是否能识别并排除伪动机/伪强线索)

--- 推理要点 ---
正确的推理应该:
• 重点关注强线索，它们直接指向真凶
• 识别并排除干扰信息和伪线索
• 建立清晰的因果关系链
• 得出明确的结论
• 能识别伪动机和伪强线索的误导

--- 手动评判指南 ---
请根据以上标准对模型分析进行评分 (1-5分):
□ 凶手识别: ___/5 (是否正确识别出 {script['true_killer']})
□ 证据使用: ___/5 (是否有效使用强线索)
□ 逻辑推理: ___/5 (推理是否清晰连贯)
□ 干扰排除: ___/5 (是否避免被弱线索或伪线索误导)
□ 多重推理: ___/5 (是否能识别伪动机/伪强线索)
□ 总体评分: ___/5

===============================
"""

    # 保存到文件，若重名则自动编号
    base_filename = (
        f"case_{case_num}_{model.replace('/', '_').replace(':', '_')}_analysis.txt"
    )
    filename = base_filename
    file_index = 1
    while os.path.exists(filename):
        name_part, ext = os.path.splitext(base_filename)
        filename = f"{name_part}_{file_index}{ext}"
        file_index += 1
    with open(filename, "w", encoding="utf-8") as f:
        f.write(analysis_report)

    print(f"    ✅ 分析报告已保存: {filename}")
    return analysis_report


def run_test_pipeline():
    """主测试流程函数 - 只使用4000 tokens分段方案，记录原始分析报告，保存详细测试数据
    """
    results_filepath = "model_analysis_reports.csv"
    all_results = []

    chunk_size = 4000  # 只用4000 tokens分段
    strategy_name = f"Balanced-{chunk_size}tokens"
    breakpoints = [chunk_size]
    for i in range(NUM_TEST_CASES):
        print(f"\n--- Running Test Case {i+1}/{NUM_TEST_CASES} ---")
        script = generate_god_view_script()
        dialogue = generate_dialogue(script, TOTAL_TURNS_PER_CASE)
        dialogue_tokens = TOKENIZER.encode(dialogue)
        print(
            f"  - Case generated. Killer: {script['true_killer']}. Total tokens: {len(dialogue_tokens)}"
        )
        for model in MODELS_TO_TEST:
            print(f"\n  Testing Model: {model}, Strategy: {strategy_name}")
            last_summary = ""
            start_idx = 0
            segment_count = 0
            prompts_and_responses = []  # 记录所有提示词和响应

            while start_idx < len(dialogue_tokens):
                end_idx = min(start_idx + chunk_size, len(dialogue_tokens))
                chunk_text = TOKENIZER.decode(dialogue_tokens[start_idx:end_idx])
                segment_count += 1
                print(
                    f"    - Segment {segment_count}: Processing tokens {start_idx} to {end_idx} ({end_idx - start_idx} tokens)"
                )
                prompt = get_prompt(
                    "intermediate",
                    {"summary_so_far": last_summary, "new_dialogue_chunk": chunk_text},
                    model,
                )

                if model == "deepseek-v3-qiniu":
                    intermediate_summary = call_qiniu_deepseek(prompt)
                else:
                    intermediate_summary = call_ollama(
                        model,
                        prompt,
                        use_adaptive=False,
                        test_context="summary_analysis",
                    )

                # 记录提示词和响应
                prompts_and_responses.append(
                    {
                        "type": f"intermediate_segment_{segment_count}",
                        "token_range": f"{start_idx}-{end_idx}",
                        "prompt": prompt,
                        "response": intermediate_summary,
                    }
                )

                if not intermediate_summary or intermediate_summary.strip() == "":
                    print("    🔄 Zero response, trying fallback prompt...")
                    if "atlas/intersync-gemma" in model:
                        if last_summary.strip():
                            fallback_prompt = f"Update:{last_summary[:30]}"
                        else:
                            fallback_prompt = f"Sum:{chunk_text[:40]}"
                        intermediate_summary = call_ollama(
                            model,
                            fallback_prompt,
                            use_adaptive=False,
                            test_context="summary_analysis",
                        )
                        print(
                            f"    🆘 Fallback prompt result: {len(intermediate_summary) if intermediate_summary else 0} chars"
                        )

                        # 记录fallback提示词和响应
                        prompts_and_responses.append(
                            {
                                "type": f"fallback_segment_{segment_count}",
                                "token_range": f"{start_idx}-{end_idx}",
                                "prompt": fallback_prompt,
                                "response": intermediate_summary,
                            }
                        )

                if "[API Error:" in intermediate_summary:
                    print("    - Halting strategy due to API error.")
                    last_summary = intermediate_summary
                    break
                if not intermediate_summary or intermediate_summary.strip() == "":
                    print("    🆘 Using default summary to continue...")
                    if last_summary.strip():
                        intermediate_summary = last_summary[:100] + " [continued]"
                    else:
                        intermediate_summary = (
                            "Evidence found, investigation continues."
                        )
                if "atlas/intersync-gemma" in model and intermediate_summary:
                    if len(intermediate_summary) > 150:
                        intermediate_summary = intermediate_summary[:147] + "..."
                        print("    📏 Truncated summary to 150 chars for atlas model")
                last_summary = intermediate_summary
                start_idx = end_idx
                time.sleep(2)

            if "[API Error:" in last_summary:
                final_reasoning = last_summary
            else:
                print("    - Generating final reasoning...")
                final_prompt = get_prompt(
                    "final", {"summary_so_far": last_summary}, model
                )
                if model == "deepseek-v3-qiniu":
                    final_reasoning = call_qiniu_deepseek(final_prompt)
                else:
                    final_reasoning = call_ollama(
                        model,
                        final_prompt,
                        use_adaptive=False,
                        test_context="final_reasoning",
                    )

                # 记录最终推理提示词和响应
                prompts_and_responses.append(
                    {
                        "type": "final_reasoning",
                        "token_range": "final",
                        "prompt": final_prompt,
                        "response": final_reasoning,
                    }
                )

                if not final_reasoning or final_reasoning.strip() == "":
                    print("    🔄 Final reasoning zero response, trying fallback...")
                    if "atlas/intersync-gemma" in model:
                        fallback_final = f"Who killed? {last_summary[:50]}"
                        final_reasoning = call_ollama(
                            model,
                            fallback_final,
                            use_adaptive=False,
                            test_context="final_reasoning",
                        )
                        print(
                            f"    🆘 Fallback final reasoning: {len(final_reasoning) if final_reasoning else 0} chars"
                        )

                        # 记录fallback最终推理
                        prompts_and_responses.append(
                            {
                                "type": "fallback_final_reasoning",
                                "token_range": "final",
                                "prompt": fallback_final,
                                "response": final_reasoning,
                            }
                        )

                if not final_reasoning or final_reasoning.strip() == "":
                    print("    🆘 Using default final reasoning...")
                    final_reasoning = f"Based on the evidence: {last_summary[:100]}, further investigation needed to determine the killer."

            # 保存详细测试数据（新功能）
            print("    - Saving detailed test data...")
            save_detailed_test_data(
                i + 1, model, script, dialogue, prompts_and_responses, final_reasoning
            )

            # 保存传统分析报告（保持向后兼容）
            if "[API Error:" not in final_reasoning:
                print("    - Saving analysis report with correct answers...")
                save_case_analysis(i + 1, model, script, final_reasoning)

            if not final_reasoning or final_reasoning.strip() == "":
                response_status = "zero_response"
            elif "[API Error:" in final_reasoning:
                response_status = "api_error"
            else:
                response_status = "success"
            result = {
                "test_case": i + 1,
                "model": model,
                "strategy": strategy_name,
                "true_killer": script["true_killer"],
                "motive": script["motive"],
                "strong_clues": "; ".join(script["strong_clues"]),
                "weak_clues": "; ".join(script["weak_clues"]),
                "final_reasoning": final_reasoning,
                "response_status": response_status,
                "reasoning_length": len(final_reasoning) if final_reasoning else 0,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            all_results.append(result)
            if all_results:
                with open(results_filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
                    writer.writeheader()
                    writer.writerows(all_results)
    print(f"\n--- Test Suite Complete. Full report saved to {results_filepath} ---")


# ====== 最小化外部API连通性测试 ======
if __name__ == "__main__":
    if not os.path.exists("recursive_summary_results"):
        os.makedirs("recursive_summary_results")
    os.chdir("recursive_summary_results")

    run_test_pipeline()

    print("\n--- 测试完成 ---")
    print("所有测试数据已保存到当前目录")
    print("")
    print("📊 汇总报告:")
    print("  • CSV汇总报告: model_analysis_reports.csv")
    print("  • 传统分析报告: case_X_MODEL_analysis.txt")
    print("")
    print("📁 详细测试数据 (每个案例一个文件夹):")
    print("  • case_X_MODEL/ - 包含完整测试数据")
    print("    ├── 00_README.txt - 测试摘要和快速对比")
    print("    ├── 01_script.txt - 完整案件剧本和线索")
    print("    ├── 02_dialogue_segment_XX.txt - 分段对话内容")
    print("    ├── 03_prompts_and_responses.txt - 所有提示词和响应")
    print("    └── 04_final_reasoning.txt - 最终推理和评判标准")
    print("")
    print("🔍 人工对比测试:")
    print("  • 查看各文件夹中的 03_prompts_and_responses.txt")
    print("  • 复制提示词到网页AI服务进行对比测试")
    print("  • 参考 04_final_reasoning.txt 中的正确答案")
    print("  • 使用 00_README.txt 快速了解测试结果")

# ====== 最小化外部API连通性测试（如需单独测试请取消注释） ======
# if __name__ == "__main__":
#     print("\n--- Qiniu DeepSeek API 最小化连通性测试 ---")
#     test_prompt = "请用一句话介绍七牛云的AI推理能力。"
#     result = call_qiniu_deepseek(test_prompt)
#     print("API返回：", result)

import io
import sys


# 修改标准输出编码为UTF-8
# 函数说明：初始化系统标准输出流，设置编码为UTF-8以支持Unicode字符
def init_console_encoding():
    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )


# 调用初始化函数
init_console_encoding()

# 测试Unicode字符输出
print("✓ Adaptive prompts module loaded successfully")
