#!/usr/bin/env python3
"""
DAIP-LIVE 文档协同关系分析器
分析文档之间的依赖关系、协同工作和逻辑对应
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass


@dataclass
class DocumentReference:
    """文档引用信息"""
    source_doc: str
    target_doc: str
    reference_type: str  # 'dependency', 'implementation', 'related', 'extends'
    reference_context: str
    confidence: float


@dataclass
class ModuleDocument:
    """模块文档信息"""
    module_id: str
    module_name: str
    module_type: str  # 'P1'-'P8', 'strategic', 'feature'
    documents: List[str]
    primary_spec: str
    implementation_docs: List[str]
    test_docs: List[str]


class DocumentCollaborationAnalyzer:
    """文档协同关系分析器"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

        # P1-P8 模块定义
        self.p_modules = {
            'P1': {
                'name': 'Data Persistence',
                'path_pattern': 'persistence|database',
                'keywords': ['数据库', '持久化', 'session', 'SQLite', 'database']
            },
            'P2': {
                'name': 'Knowledge Management',
                'path_pattern': 'wiki|knowledge',
                'keywords': ['wiki', '知识', '知识管理', 'collaboration', 'FAISS']
            },
            'P3': {
                'name': 'Model Provider',
                'path_pattern': 'model_provider|llm',
                'keywords': ['模型', 'LLM', 'LiteLLM', 'Ollama', 'OpenAI', 'Claude']
            },
            'P4': {
                'name': 'Role & Tool Management',
                'path_pattern': 'p4_|role|tool',
                'keywords': ['角色', '工具', 'role', 'tool', 'management']
            },
            'P5': {
                'name': 'Agent Engine',
                'path_pattern': 'agent_engine|p5_',
                'keywords': ['agent', '引擎', 'execution', 'intent', 'step']
            },
            'P6': {
                'name': 'Terminal Interface',
                'path_pattern': 'cli|tui|interface',
                'keywords': ['TUI', 'CLI', '界面', 'terminal', 'Textual']
            },
            'P7': {
                'name': 'GUI Interface',
                'path_pattern': 'p7_|gui|streamlit',
                'keywords': ['GUI', 'Web', 'Streamlit', 'interface']
            },
            'P8': {
                'name': 'Debate System',
                'path_pattern': 'p8_|debate',
                'keywords': ['辩论', 'debate', '多模型', 'collaboration', 'multi-agent']
            }
        }

        # 文档引用模式
        self.reference_patterns = [
            # 直接引用
            r'\[([^\]]+)\]\(([^)]+)\.md\)',
            # 相对路径引用
            r'\.\.\/([^)]+)\.md',
            # 模块引用
            r'(P[1-8])[^a-zA-Z]',
            # 参见类引用
            r'(详见|参考|see also|reference)[：:]?\s*([^\n\r\.]+\.md)',
            # 实现引用
            r'(实现|implemented in|implementation)[：:]?\s*([^\n\r\.]+)',
            # 相关文档引用
            r'(相关|related)[：:]?\s*([^\n\r\.]+\.md)'
        ]

    def load_documents(self) -> Dict[str, Dict]:
        """加载所有文档数据"""
        docs_file = self.base_path / "tutor/document_quality_assessment/filtered_documents_sorted_by_date.json"

        if not docs_file.exists():
            print(f"找不到文档数据文件: {docs_file}")
            return {}

        with open(docs_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)

        return {doc['file_path']: doc for doc in documents}

    def classify_document_module(self, doc_path: str, doc_name: str, content: str) -> str:
        """分类文档所属模块"""
        doc_path_lower = doc_path.lower()
        doc_name_lower = doc_name.lower()
        content_lower = content.lower()

        for module_id, module_info in self.p_modules.items():
            # 路径匹配
            if re.search(module_info['path_pattern'], doc_path_lower):
                return module_id

            # 关键词匹配
            keyword_score = sum(1 for keyword in module_info['keywords']
                              if keyword.lower() in content_lower)
            if keyword_score >= 2:
                return module_id

        return 'OTHER'

    def extract_references(self, content: str, source_path: str) -> List[DocumentReference]:
        """从文档内容中提取引用关系"""
        references = []

        for pattern in self.reference_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    groups = match.groups()

                    if len(groups) >= 2:
                        target_name = groups[1].strip()
                        context = match.group(0)

                        # 跳过外部链接
                        if 'http://' in target_name or 'https://' in target_name:
                            continue

                        # 清理文件名
                        target_name = re.sub(r'[#?].*$', '', target_name)  # 移除锚点和参数
                        target_name = target_name.strip()

                        if target_name.endswith('.md'):
                            target_path = self.find_target_document(target_name, source_path)
                            if target_path:
                                ref_type = self.classify_reference_type(context, source_path, target_path)
                                references.append(DocumentReference(
                                    source_doc=source_path,
                                    target_doc=target_path,
                                    reference_type=ref_type,
                                    reference_context=context,
                                    confidence=self.calculate_confidence(context, ref_type)
                                ))

                except Exception as e:
                    continue

        return references

    def find_target_document(self, target_name: str, source_path: str) -> str:
        """查找目标文档的完整路径"""
        # 尝试相对路径
        source_dir = str(Path(source_path).parent)

        # 移除开头的 ./
        if target_name.startswith('./'):
            target_name = target_name[2:]

        # 尝试不同路径组合
        possible_paths = [
            Path(source_dir) / target_name,
            Path(source_dir) / (target_name + '.md'),
            self.base_path / target_name,
            self.base_path / (target_name + '.md'),
            self.base_path / 'docs' / target_name,
            self.base_path / 'docs' / (target_name + '.md'),
            self.base_path / 'docs/specs' / target_name,
            self.base_path / 'docs/specs' / (target_name + '.md'),
        ]

        for path in possible_paths:
            if path.exists():
                return str(path.absolute())

        return ""

    def classify_reference_type(self, context: str, source_path: str, target_path: str) -> str:
        """分类引用类型"""
        context_lower = context.lower()
        source_lower = source_path.lower()
        target_lower = target_path.lower()

        # 实现引用
        if any(word in context_lower for word in ['实现', 'implemented in', 'implementation']):
            return 'implementation'

        # 依赖引用
        if any(word in context_lower for word in ['依赖', 'depends on', 'requirement']):
            return 'dependency'

        # 扩展引用
        if any(word in context_lower for word in ['扩展', 'extends', 'extends on']):
            return 'extends'

        # 相关引用
        return 'related'

    def calculate_confidence(self, context: str, ref_type: str) -> float:
        """计算引用的置信度"""
        confidence = 0.5  # 基础置信度

        # 根据引用类型调整
        type_scores = {
            'implementation': 0.9,
            'dependency': 0.8,
            'extends': 0.7,
            'related': 0.6
        }
        confidence = type_scores.get(ref_type, 0.5)

        # 根据上下文调整
        if '详见' in context or 'see also' in context:
            confidence += 0.1
        if 'http' not in context:  # 内部链接
            confidence += 0.1

        return min(confidence, 1.0)

    def analyze_module_dependencies(self) -> Dict[str, ModuleDocument]:
        """分析模块依赖关系"""
        documents = self.load_documents()
        module_docs = defaultdict(lambda: ModuleDocument(
            module_id='', module_name='', module_type='', documents=[],
            primary_spec='', implementation_docs=[], test_docs=[]
        ))

        # 分类文档到模块
        for doc_path, doc_data in documents.items():
            doc_name = doc_data['file_name']
            doc_type = doc_data.get('document_type', '')

            # 读取文档内容
            content = ""
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                continue

            # 分类模块
            module_id = self.classify_document_module(doc_path, doc_name, content)

            if module_id != 'OTHER':
                module_info = self.p_modules.get(module_id, {})
                module_doc = module_docs[module_id]
                module_doc.module_id = module_id
                module_doc.module_name = module_info.get('name', module_id)
                module_doc.module_type = module_id
                module_doc.documents.append(doc_path)

                # 进一步分类文档类型
                if 'spec' in doc_name.lower() or 'requirement' in doc_name.lower():
                    if not module_doc.primary_spec:
                        module_doc.primary_spec = doc_path
                elif 'test' in doc_name.lower() or 'test_' in doc_path.lower():
                    module_doc.test_docs.append(doc_path)
                elif any(keyword in doc_name.lower() for keyword in ['implementation', 'code', 'develop']):
                    module_doc.implementation_docs.append(doc_path)

        return dict(module_docs)

    def analyze_document_collaboration(self) -> Dict:
        """分析文档协同关系"""
        documents = self.load_documents()
        references = []

        # 提取所有引用关系
        for doc_path, doc_data in documents.items():
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                doc_refs = self.extract_references(content, doc_path)
                references.extend(doc_refs)

            except Exception as e:
                continue

        # 分析协同网络
        collaboration_network = self.build_collaboration_network(references, documents)

        # 分析模块协同
        module_collaboration = self.analyze_module_collaboration(references)

        return {
            'total_references': len(references),
            'collaboration_network': collaboration_network,
            'module_collaboration': module_collaboration,
            'reference_types': self.analyze_reference_types(references),
            'dependency_graph': self.build_dependency_graph(references),
            'collaboration_metrics': self.calculate_collaboration_metrics(references, documents)
        }

    def build_collaboration_network(self, references: List[DocumentReference], documents: Dict) -> Dict:
        """构建协同网络"""
        network = defaultdict(lambda: {'incoming': [], 'outgoing': [], 'collaborators': set()})

        for ref in references:
            source_name = Path(ref.source_doc).name
            target_name = Path(ref.target_doc).name

            network[source_name]['outgoing'].append({
                'target': target_name,
                'type': ref.reference_type,
                'confidence': ref.confidence,
                'context': ref.reference_context
            })

            network[target_name]['incoming'].append({
                'source': source_name,
                'type': ref.reference_type,
                'confidence': ref.confidence,
                'context': ref.reference_context
            })

            # 建立双向协作关系
            network[source_name]['collaborators'].add(target_name)
            network[target_name]['collaborators'].add(source_name)

        # 转换为字典格式
        result = {}
        for doc_name, data in network.items():
            result[doc_name] = {
                'incoming_count': len(data['incoming']),
                'outgoing_count': len(data['outgoing']),
                'total_collaborators': len(data['collaborators']),
                'incoming': data['incoming'],
                'outgoing': data['outgoing'],
                'collaborators': list(data['collaborators'])
            }

        return result

    def analyze_module_collaboration(self, references: List[DocumentReference]) -> Dict:
        """分析模块间协作关系"""
        module_refs = defaultdict(lambda: defaultdict(list))

        for ref in references:
            source_module = self.classify_document_module(ref.source_doc, "", "")
            target_module = self.classify_document_module(ref.target_doc, "", "")

            if source_module != 'OTHER' and target_module != 'OTHER':
                module_refs[source_module][target_module].append(ref)

        # 计算协作强度
        collaboration_matrix = {}
        for source_module, target_modules in module_refs.items():
            collaboration_matrix[source_module] = {}
            for target_module, refs in target_modules.items():
                total_confidence = sum(ref.confidence for ref in refs)
                collaboration_matrix[source_module][target_module] = {
                    'reference_count': len(refs),
                    'total_confidence': total_confidence,
                    'average_confidence': total_confidence / len(refs),
                    'reference_types': list(set(ref.reference_type for ref in refs))
                }

        return collaboration_matrix

    def analyze_reference_types(self, references: List[DocumentReference]) -> Dict:
        """分析引用类型分布"""
        type_counts = Counter(ref.reference_type for ref in references)
        confidence_by_type = defaultdict(list)

        for ref in references:
            confidence_by_type[ref.reference_type].append(ref.confidence)

        result = {}
        for ref_type, count in type_counts.items():
            confidences = confidence_by_type[ref_type]
            result[ref_type] = {
                'count': count,
                'percentage': count / len(references) * 100,
                'average_confidence': sum(confidences) / len(confidences),
                'min_confidence': min(confidences),
                'max_confidence': max(confidences)
            }

        return result

    def build_dependency_graph(self, references: List[DocumentReference]) -> Dict:
        """构建依赖图"""
        dependencies = defaultdict(list)

        for ref in references:
            if ref.reference_type in ['dependency', 'implementation']:
                dependencies[ref.source_doc].append({
                    'depends_on': ref.target_doc,
                    'type': ref.reference_type,
                    'confidence': ref.confidence
                })

        return dict(dependencies)

    def calculate_collaboration_metrics(self, references: List[DocumentReference], documents: Dict) -> Dict:
        """计算协作指标"""
        total_docs = len(documents)
        docs_with_references = len(set(ref.source_doc for ref in references))
        docs_referenced = len(set(ref.target_doc for ref in references))

        # 计算协作密度
        possible_connections = total_docs * (total_docs - 1)
        actual_connections = len(set((ref.source_doc, ref.target_doc) for ref in references))
        collaboration_density = actual_connections / possible_connections if possible_connections > 0 else 0

        return {
            'total_documents': total_docs,
            'documents_with_references': docs_with_references,
            'documents_referenced': docs_referenced,
            'collaboration_density': collaboration_density,
            'average_references_per_doc': len(references) / total_docs if total_docs > 0 else 0
        }

    def generate_teaching_structure(self, collaboration_data: Dict) -> Dict:
        """生成基于协同关系的教学结构"""
        module_deps = self.analyze_module_dependencies()

        teaching_modules = {}

        for module_id, module_doc in module_deps.items():
            teaching_module = {
                'module_id': module_id,
                'module_name': module_doc.module_name,
                'learning_objectives': self.generate_learning_objectives(module_id),
                'core_documents': {
                    'specification': module_doc.primary_spec,
                    'implementation': module_doc.implementation_docs,
                    'tests': module_doc.test_docs
                },
                'prerequisites': self.find_prerequisites(module_id, collaboration_data),
                'learning_sequence': self.generate_learning_sequence(module_id, module_doc),
                'exercises': self.generate_exercises(module_id, module_doc),
                'assessment_criteria': self.generate_assessment_criteria(module_id)
            }

            teaching_modules[module_id] = teaching_module

        # 生成整体学习路径
        learning_path = self.generate_learning_path(teaching_modules, collaboration_data)

        return {
            'teaching_modules': teaching_modules,
            'learning_path': learning_path,
            'collaboration_map': collaboration_data,
            'cross_module_projects': self.generate_cross_module_projects(teaching_modules)
        }

    def generate_learning_objectives(self, module_id: str) -> List[str]:
        """生成学习目标"""
        objectives_map = {
            'P1': [
                '理解数据持久化的设计原理',
                '掌握SQLite数据库的使用',
                '学会会话管理和状态持久化',
                '能够设计高效的数据模型'
            ],
            'P2': [
                '掌握向量搜索和知识管理',
                '理解FAISS索引的原理和应用',
                '学会Wiki系统的设计和实现',
                '能够构建协作知识库'
            ],
            'P3': [
                '理解多模型提供者架构',
                '掌握LiteLLM的使用',
                '学会模型抽象和切换机制',
                '能够集成不同的AI服务'
            ],
            'P4': [
                '理解角色和工具管理系统',
                '掌握动态角色分配机制',
                '学会工具系统的扩展方法',
                '能够设计灵活的权限管理'
            ],
            'P5': [
                '理解Agent引擎的执行机制',
                '掌握意图识别和步骤分解',
                '学会事件驱动的架构设计',
                '能够构建智能执行引擎'
            ],
            'P6': [
                '掌握TUI界面的设计和开发',
                '理解Textual框架的使用',
                '学会命令驱动的交互设计',
                '能够构建现代化的终端应用'
            ],
            'P7': [
                '理解Web界面的集成方法',
                '掌握Streamlit的使用',
                '学会API设计和实现',
                '能够构建图形化用户界面'
            ],
            'P8': [
                '理解多模型辩论系统',
                '掌握角色分配和模型选择',
                '学会协作推理机制',
                '能够构建智能辩论系统'
            ]
        }

        return objectives_map.get(module_id, ['掌握' + self.p_modules[module_id]['name'] + '的核心概念和实现方法'])

    def find_prerequisites(self, module_id: str, collaboration_data: Dict) -> List[str]:
        """找到学习前置条件"""
        # P1是基础，其他模块通常依赖P1
        if module_id == 'P1':
            return []

        prerequisites = ['P1']  # 大多数模块都需要数据持久化基础

        # 特殊依赖关系
        special_deps = {
            'P5': ['P3', 'P4'],  # Agent引擎需要模型提供者和角色管理
            'P8': ['P3', 'P5'],  # 辩论系统需要模型提供者和Agent引擎
            'P7': ['P6'],        # GUI通常在TUI基础上扩展
        }

        return special_deps.get(module_id, prerequisites)

    def generate_learning_sequence(self, module_id: str, module_doc: ModuleDocument) -> List[Dict]:
        """生成学习顺序"""
        sequence = []

        # 1. 理论学习
        if module_doc.primary_spec:
            sequence.append({
                'step': 1,
                'title': '理论学习和规格理解',
                'documents': [module_doc.primary_spec],
                'activities': ['阅读规格文档', '理解设计原理', '分析需求规格']
            })

        # 2. 代码实践
        if module_doc.implementation_docs:
            sequence.append({
                'step': 2,
                'title': '代码实现和实践',
                'documents': module_doc.implementation_docs,
                'activities': ['阅读源代码', '运行示例', '修改功能', '扩展特性']
            })

        # 3. 测试验证
        if module_doc.test_docs:
            sequence.append({
                'step': 3,
                'title': '测试和质量验证',
                'documents': module_doc.test_docs,
                'activities': ['运行测试', '编写测试用例', '性能测试', '质量检查']
            })

        # 4. 综合实践
        sequence.append({
            'step': 4,
            'title': '综合项目和集成',
            'documents': module_doc.documents,
            'activities': ['完成项目实践', '模块集成', '文档编写', '成果展示']
        })

        return sequence

    def generate_exercises(self, module_id: str, module_doc: ModuleDocument) -> List[Dict]:
        """生成练习题目"""
        exercises = []

        # 基础练习
        exercises.append({
            'level': 'beginner',
            'title': f'{module_doc.module_name}基础练习',
            'description': f'理解{module_doc.module_name}的基本概念和使用方法',
            'tasks': [
                '阅读相关文档并总结核心概念',
                '运行基础示例代码',
                '完成简单的修改实验',
                '编写学习笔记和心得'
            ]
        })

        # 进阶练习
        exercises.append({
            'level': 'intermediate',
            'title': f'{module_doc.module_name}进阶实践',
            'description': f'深入理解{module_doc.module_name}的实现原理和扩展方法',
            'tasks': [
                '分析源代码实现',
                '完成功能扩展任务',
                '编写单元测试',
                '优化性能和用户体验'
            ]
        })

        # 高级练习
        exercises.append({
            'level': 'advanced',
            'title': f'{module_doc.module_name}高级应用',
            'description': f'掌握{module_doc.module_name}的高级特性和最佳实践',
            'tasks': [
                '设计新的功能模块',
                '集成第三方服务',
                '编写完整的技术文档',
                '参与开源项目贡献'
            ]
        })

        return exercises

    def generate_assessment_criteria(self, module_id: str) -> Dict:
        """生成评估标准"""
        return {
            'theory_understanding': {
                'weight': 30,
                'criteria': [
                    '能够准确描述模块的核心概念',
                    '理解模块在整个系统中的作用',
                    '掌握模块的设计原理和技术选型',
                    '能够分析模块的优缺点'
                ]
            },
            'practical_skills': {
                'weight': 40,
                'criteria': [
                    '能够独立完成模块的配置和使用',
                    '掌握模块的API和接口调用',
                    '能够进行功能扩展和定制开发',
                    '具备问题排查和调试能力'
                ]
            },
            'integration_ability': {
                'weight': 20,
                'criteria': [
                    '能够将模块与其他系统组件集成',
                    '理解模块间的接口和依赖关系',
                    '能够设计合理的系统集成方案',
                    '具备系统级的思维和架构能力'
                ]
            },
            'documentation_quality': {
                'weight': 10,
                'criteria': [
                    '能够编写清晰的技术文档',
                    '掌握规格文档的编写规范',
                    '能够进行有效的知识分享',
                    '具备良好的表达能力'
                ]
            }
        }

    def generate_learning_path(self, teaching_modules: Dict, collaboration_data: Dict) -> List[Dict]:
        """生成学习路径"""
        path = []

        # 阶段1：基础入门
        path.append({
            'phase': 1,
            'title': '基础入门阶段',
            'duration': '2-3周',
            'modules': ['P1', 'P6'],
            'objectives': '掌握数据持久化和基础界面开发',
            'deliverables': ['完成环境配置', '理解P1-P6架构', '运行基础示例']
        })

        # 阶段2：核心能力
        path.append({
            'phase': 2,
            'title': '核心能力培养',
            'duration': '4-5周',
            'modules': ['P2', 'P3', 'P5'],
            'objectives': '掌握知识管理、模型集成和智能执行',
            'deliverables': ['完成P2-P3学习', '理解Agent引擎', '实现基础AI功能']
        })

        # 阶段3：高级特性
        path.append({
            'phase': 3,
            'title': '高级特性掌握',
            'duration': '3-4周',
            'modules': ['P4', 'P8'],
            'objectives': '掌握角色管理和多模型协作',
            'deliverables': ['完成P4-P8学习', '实现辩论系统', '集成完整功能']
        })

        # 阶段4：系统集成
        path.append({
            'phase': 4,
            'title': '系统集成实践',
            'duration': '2-3周',
            'modules': ['P7'],
            'objectives': '掌握界面集成和系统部署',
            'deliverables': ['完成P7学习', '系统集成测试', '项目部署上线']
        })

        return path

    def generate_cross_module_projects(self, teaching_modules: Dict) -> List[Dict]:
        """生成跨模块项目"""
        projects = []

        # 项目1：基础应用开发
        projects.append({
            'title': '个人助理应用开发',
            'modules': ['P1', 'P3', 'P5', 'P6'],
            'difficulty': 'intermediate',
            'duration': '2-3周',
            'description': '开发一个基于TUI的个人助理应用，集成对话、记忆和任务管理功能',
            'learning_points': [
                '模块间协作机制',
                '数据持久化和会话管理',
                'AI模型集成',
                '用户界面设计'
            ]
        })

        # 项目2：知识管理系统
        projects.append({
            'title': '协作知识管理系统',
            'modules': ['P1', 'P2', 'P3', 'P6', 'P7'],
            'difficulty': 'advanced',
            'duration': '3-4周',
            'description': '开发一个支持多用户的协作知识管理系统，包含Wiki、搜索和版本控制功能',
            'learning_points': [
                '向量搜索和知识管理',
                '多用户协作机制',
                'Web界面集成',
                '权限管理系统'
            ]
        })

        # 项目3：智能辩论平台
        projects.append({
            'title': '多模型智能辩论平台',
            'modules': ['P1', 'P3', 'P4', 'P5', 'P6', 'P8'],
            'difficulty': 'expert',
            'duration': '4-5周',
            'description': '开发一个支持多模型协作的智能辩论平台，集成完整的P1-P8模块',
            'learning_points': [
                '多模型协作机制',
                '角色管理和权限控制',
                '复杂系统集成',
                '性能优化和扩展性'
            ]
        })

        return projects

    def generate_collaboration_report(self, collaboration_data: Dict, teaching_structure: Dict) -> str:
        """生成协同关系分析报告"""
        report = f"""# DAIP-LIVE 文档协同关系分析报告

## 分析概述

本报告分析了DAIP-LIVE项目中271份规范化文档之间的协同关系、依赖联系和逻辑对应，为教学平台的设计提供数据支撑。

## 📊 协同关系统计

### 基础指标
- **总引用数**: {collaboration_data['total_references']}
- **参与协作文档数**: {collaboration_data['collaboration_metrics']['documents_with_references']}
- **被引用文档数**: {collaboration_data['collaboration_metrics']['documents_referenced']}
- **协作密度**: {collaboration_data['collaboration_metrics']['collaboration_density']:.3f}
- **平均引用数**: {collaboration_data['collaboration_metrics']['average_references_per_doc']:.2f}

### 引用类型分布
"""

        # 添加引用类型统计
        for ref_type, stats in collaboration_data['reference_types'].items():
            report += f"- **{ref_type}**: {stats['count']} 次 ({stats['percentage']:.1f}%)，平均置信度 {stats['average_confidence']:.2f}\n"

        # 添加模块协作分析
        report += f"\n## 🏗️ 模块间协作分析\n\n"
        module_collab = collaboration_data['module_collaboration']

        for source_module, targets in module_collab.items():
            if source_module in teaching_structure['teaching_modules']:
                module_info = teaching_structure['teaching_modules'][source_module]
                report += f"### {source_module} - {module_info['module_name']}\n"

                for target_module, collab_data in targets.items():
                    if target_module in teaching_structure['teaching_modules']:
                        target_info = teaching_structure['teaching_modules'][target_module]
                        report += f"- **{target_module} ({target_info['module_name']}**: "
                        report += f"{collab_data['reference_count']} 次引用，"
                        report += f"平均置信度 {collab_data['average_confidence']:.2f}\n"

                report += "\n"

        # 添加教学模块总结
        report += "## 📚 教学模块设计\n\n"
        teaching_modules = teaching_structure['teaching_modules']

        for module_id, module_data in teaching_modules.items():
            report += f"### {module_id}: {module_data['module_name']}\n"
            report += f"- **学习目标**: {', '.join(module_data['learning_objectives'][:3])}\n"
            report += f"- **前置条件**: {', '.join(module_data['prerequisites'])}\n"
            report += f"- **文档数量**: {len(module_data['core_documents']['specification'])} 规格 + "
            report += f"{len(module_data['core_documents']['implementation'])} 实现 + "
            report += f"{len(module_data['core_documents']['tests'])} 测试\n"
            report += f"- **练习数量**: {len(module_data['exercises'])} 个练习\n"
            report += "\n"

        # 添加学习路径
        report += "## 🎯 推荐学习路径\n\n"
        learning_path = teaching_structure['learning_path']

        for phase in learning_path:
            report += f"### 阶段{phase['phase']}: {phase['title']}\n"
            report += f"- **时长**: {phase['duration']}\n"
            report += f"- **涉及模块**: {', '.join(phase['modules'])}\n"
            report += f"- **学习目标**: {phase['objectives']}\n"
            report += f"- **交付成果**: {', '.join(phase['deliverables'])}\n"
            report += "\n"

        # 添加跨模块项目
        report += "## 🔗 跨模块实践项目\n\n"
        cross_projects = teaching_structure['cross_module_projects']

        for i, project in enumerate(cross_projects, 1):
            report += f"### 项目{i}: {project['title']}\n"
            report += f"- **难度**: {project['difficulty']}\n"
            report += f"- **时长**: {project['duration']}\n"
            report += f"- **涉及模块**: {', '.join(project['modules'])}\n"
            report += f"- **项目描述**: {project['description']}\n"
            report += f"- **学习要点**: {', '.join(project['learning_points'][:3])}\n"
            report += "\n"

        # 添加教学建议
        report += "## 💡 教学实施建议\n\n"
        report += "### 核心教学原则\n"
        report += "1. **循序渐进**: 按照P1→P6→P3→P5→P4→P8→P7的顺序进行教学\n"
        report += "2. **理论结合实践**: 每个模块都包含规格文档、实现代码和测试验证\n"
        report += "3. **协同学习**: 鼓励学员进行模块间的协作和集成开发\n"
        report += "4. **项目驱动**: 通过完整的跨模块项目巩固学习成果\n\n"

        report += "### 实施策略\n"
        report += "1. **模块化教学**: 每个P1-P8模块作为独立教学单元\n"
        report += "2. **文档引导**: 以规格文档为学习主线，代码为实践载体\n"
        report += "3. **质量意识**: 强调文档质量与代码质量的同等重要性\n"
        report += "4. **持续改进**: 基于教学反馈不断优化教学内容和方法\n"

        return report


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python document_collaboration_analyzer.py <项目根目录> <输出目录>")
        return

    project_root = sys.argv[1]
    output_dir = sys.argv[2]

    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    analyzer = DocumentCollaborationAnalyzer(project_root)

    print("开始分析文档协同关系...")

    # 分析协同关系
    collaboration_data = analyzer.analyze_document_collaboration()

    # 生成教学结构
    teaching_structure = analyzer.generate_teaching_structure(collaboration_data)

    # 保存分析结果
    collaboration_file = Path(output_dir) / "document_collaboration_analysis.json"
    with open(collaboration_file, 'w', encoding='utf-8') as f:
        json.dump(collaboration_data, f, ensure_ascii=False, indent=2, default=str)

    # 保存教学结构
    teaching_file = Path(output_dir) / "teaching_structure.json"
    with open(teaching_file, 'w', encoding='utf-8') as f:
        json.dump(teaching_structure, f, ensure_ascii=False, indent=2, default=str)

    # 生成协同关系报告
    report = analyzer.generate_collaboration_report(collaboration_data, teaching_structure)
    report_file = Path(output_dir) / "collaboration_analysis_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"文档协同关系分析完成！")
    print(f"- 协同分析数据: {collaboration_file}")
    print(f"- 教学结构数据: {teaching_file}")
    print(f"- 分析报告: {report_file}")


if __name__ == "__main__":
    main()