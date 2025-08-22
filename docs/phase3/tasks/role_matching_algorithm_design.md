# 角色专业领域匹配算法设计

## 设计目标
实现一个智能的角色与任务匹配算法，能够根据任务内容自动选择最合适的专业角色参与Wiki协作和辩论。

## 设计原则
1. **准确性**：匹配算法应能准确识别任务内容与角色专业领域的相关性
2. **效率**：算法应具有良好的性能，能够快速完成匹配
3. **可扩展**：算法应易于扩展以支持新的专业领域和角色
4. **灵活性**：算法应能处理模糊和多义的任务描述

## 算法设计

### 1. 关键词提取
从任务描述中提取关键词，用于匹配角色专业领域。

### 2. 领域匹配
将提取的关键词与角色的专业领域进行匹配，计算匹配度。

### 3. 角色排序
根据匹配度对角色进行排序，选择最匹配的角色。

### 4. 多角色选择
根据任务复杂度选择多个角色参与。

## 算法实现

### 数据结构
```python
class RoleDomainMatcher:
    def __init__(self):
        # 角色专业领域映射
        self.role_domains = {
            "生物信息学研究员": ["生物信息学", "基因组学", "蛋白质组学", "生物数据"],
            "基因组学数据分析师": ["基因组学", "DNA序列", "基因表达", "变异检测"],
            # ... 其他角色领域映射
        }
        
        # 领域同义词映射
        self.domain_synonyms = {
            "生物信息学": ["计算生物学", "生物数据科学"],
            "基因组学": ["基因学", "DNA分析"],
            # ... 其他同义词映射
        }
```

### 匹配算法
```python
def match_roles_to_task(self, task_description: str, max_roles: int = 3) -> List[str]:
    """
    根据任务描述匹配最合适的角色
    
    Args:
        task_description: 任务描述
        max_roles: 最大返回角色数
        
    Returns:
        匹配的角色ID列表
    """
    # 1. 提取关键词
    keywords = self.extract_keywords(task_description)
    
    # 2. 计算角色匹配度
    role_scores = {}
    for role_id, domains in self.role_domains.items():
        score = self.calculate_match_score(keywords, domains)
        role_scores[role_id] = score
    
    # 3. 按匹配度排序并选择前N个角色
    sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
    selected_roles = [role_id for role_id, score in sorted_roles if score > 0][:max_roles]
    
    return selected_roles
```

### 关键词提取
```python
def extract_keywords(self, text: str) -> List[str]:
    """
    从文本中提取关键词
    
    Args:
        text: 输入文本
        
    Returns:
        关键词列表
    """
    # 移除停用词
    stop_words = {"的", "和", "与", "及", "以及", "或者", "还是", "但是", "然而", "因此", "所以", "为了", "关于", "对于", "通过", "基于", "利用", "采用"}
    
    # 分词并过滤
    words = [word.strip() for word in text.replace("，", " ").replace(",", " ").split() if word.strip()]
    keywords = [word for word in words if word not in stop_words and len(word) > 1]
    
    # 扩展同义词
    extended_keywords = set(keywords)
    for keyword in keywords:
        if keyword in self.domain_synonyms:
            extended_keywords.update(self.domain_synonyms[keyword])
    
    return list(extended_keywords)
```

### 匹配度计算
```python
def calculate_match_score(self, keywords: List[str], domains: List[str]) -> float:
    """
    计算关键词与领域列表的匹配度
    
    Args:
        keywords: 关键词列表
        domains: 领域列表
        
    Returns:
        匹配度分数 (0-1)
    """
    if not keywords or not domains:
        return 0.0
    
    # 计算关键词在领域中的出现次数
    match_count = 0
    for keyword in keywords:
        for domain in domains:
            if keyword in domain or domain in keyword:
                match_count += 1
                break
    
    # 计算匹配度分数
    score = match_count / len(keywords)
    return score
```