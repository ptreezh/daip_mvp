#!/usr/bin/env python3
"""个性化体验定制服务

提供个性化的用户体验定制功能
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
<<<<<<< HEAD
from typing import Any, Dict, List
=======
from typing import Any
>>>>>>> feature/core-services-refactor

logger = logging.getLogger(__name__)


class PersonalizationLevel(Enum):
    """个性化级别枚举"""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ExperienceTheme(Enum):
    """体验主题枚举"""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ACADEMIC = "academic"
    CREATIVE = "creative"


@dataclass
class UserProfile:
    """用户档案"""

    user_id: str
    personalization_level: PersonalizationLevel
    experience_theme: ExperienceTheme
    preferences: dict[str, Any]
    interaction_history: list[dict[str, Any]]
    learning_style: str
    expertise_areas: list[str]
    created_at: str
    last_updated: str


@dataclass
class PersonalizationRule:
    """个性化规则"""

    rule_id: str
    name: str
    condition: dict[str, Any]
    action: dict[str, Any]
    priority: int
    is_active: bool


class PersonalizedExperienceService:
    """个性化体验定制服务"""

    def __init__(self):
        """初始化个性化体验定制服务"""
        self.user_profiles = {}  # {user_id: UserProfile}
        self.personalization_rules = []
        self.experience_templates = self._initialize_experience_templates()
        self.customization_options = self._initialize_customization_options()

        logger.info("个性化体验定制服务初始化完成")

    def create_user_profile(
        self,
        user_id: str,
        initial_preferences: dict[str, Any] = None,
        personalization_level: PersonalizationLevel = PersonalizationLevel.BASIC
    ) -> dict[str, Any]:
        """创建用户档案"""
        try:
            # 检查用户是否已存在
            if user_id in self.user_profiles:
                return {"error": "用户档案已存在", "user_id": user_id}

            # 创建默认档案
            user_profile = UserProfile(
                user_id=user_id,
                personalization_level=personalization_level,
                experience_theme=ExperienceTheme.PROFESSIONAL,
                preferences=initial_preferences or {},
                interaction_history=[],
                learning_style="balanced",
                expertise_areas=[],
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )

            # 应用初始个性化设置
            self._apply_initial_personalization(user_profile)

            # 保存档案
            self.user_profiles[user_id] = user_profile

            result = {
                "user_id": user_id,
                "profile_created": True,
                "personalization_level": personalization_level.value,
                "available_customizations": self._get_available_customizations(personalization_level),
                "initial_recommendations": self._generate_initial_recommendations(user_profile)
            }

            logger.info(f"用户档案创建完成: {user_id}")
            return result

        except Exception as e:
            logger.error(f"创建用户档案失败: {e}")
            return {"error": str(e)}

    def customize_experience(
        self,
        user_id: str,
        customization_request: dict[str, Any]
    ) -> dict[str, Any]:
        """定制用户体验"""
        try:
            if user_id not in self.user_profiles:
                return {"error": "用户档案不存在"}

            user_profile = self.user_profiles[user_id]

            # 解析定制请求
            customization_type = customization_request.get("type", "preferences")
            customization_data = customization_request.get("data", {})

            # 应用定制
            if customization_type == "preferences":
                self._update_preferences(user_profile, customization_data)
            elif customization_type == "theme":
                self._update_theme(user_profile, customization_data)
            elif customization_type == "personalization_level":
                self._update_personalization_level(user_profile, customization_data)
            elif customization_type == "learning_style":
                self._update_learning_style(user_profile, customization_data)
            elif customization_type == "expertise_areas":
                self._update_expertise_areas(user_profile, customization_data)

            # 更新时间戳
            user_profile.last_updated = datetime.now().isoformat()

            # 生成个性化配置
            personalized_config = self._generate_personalized_config(user_profile)

            # 记录定制历史
            self._record_customization_history(user_profile, customization_request)

            result = {
                "user_id": user_id,
                "customization_applied": True,
                "personalized_config": personalized_config,
                "updated_preferences": user_profile.preferences,
                "recommendations": self._generate_experience_recommendations(user_profile)
            }

            logger.info(f"用户体验定制完成: {user_id}, 类型: {customization_type}")
            return result

        except Exception as e:
            logger.error(f"定制用户体验失败: {e}")
            return {"error": str(e)}

    def get_personalized_interface(
        self,
        user_id: str,
        interface_type: str = "default"
    ) -> dict[str, Any]:
        """获取个性化界面配置"""
        try:
            if user_id not in self.user_profiles:
                return self._get_default_interface_config(interface_type)

            user_profile = self.user_profiles[user_id]

            # 生成个性化界面配置
            interface_config = {
                "user_id": user_id,
                "interface_type": interface_type,
                "theme": self._get_theme_config(user_profile.experience_theme),
                "layout": self._get_layout_config(user_profile),
                "components": self._get_component_config(user_profile),
                "interactions": self._get_interaction_config(user_profile),
                "content_preferences": self._get_content_preferences(user_profile),
                "accessibility": self._get_accessibility_config(user_profile)
            }

            # 应用个性化规则
            interface_config = self._apply_personalization_rules(interface_config, user_profile)

            logger.info(f"个性化界面配置生成: {user_id}, 类型: {interface_type}")
            return interface_config

        except Exception as e:
            logger.error(f"获取个性化界面失败: {e}")
            return self._get_default_interface_config(interface_type)

    def adapt_to_user_behavior(
        self,
        user_id: str,
        behavior_data: dict[str, Any]
    ) -> dict[str, Any]:
        """根据用户行为自适应调整"""
        try:
            if user_id not in self.user_profiles:
                return {"error": "用户档案不存在"}

            user_profile = self.user_profiles[user_id]

            # 分析用户行为
            behavior_analysis = self._analyze_user_behavior(behavior_data)

            # 更新用户档案
            adaptations = self._generate_adaptations(user_profile, behavior_analysis)

            # 应用适应性调整
            for adaptation in adaptations:
                self._apply_adaptation(user_profile, adaptation)

            # 记录行为历史
            user_profile.interaction_history.append({
                "timestamp": datetime.now().isoformat(),
                "behavior_data": behavior_data,
                "adaptations_applied": adaptations
            })

            # 保持历史记录在合理范围内
            if len(user_profile.interaction_history) > 100:
                user_profile.interaction_history = user_profile.interaction_history[-50:]

            user_profile.last_updated = datetime.now().isoformat()

            result = {
                "user_id": user_id,
                "behavior_analyzed": True,
                "adaptations_applied": adaptations,
                "updated_profile": {
                    "personalization_level": user_profile.personalization_level.value,
                    "experience_theme": user_profile.experience_theme.value,
                    "learning_style": user_profile.learning_style,
                    "expertise_areas": user_profile.expertise_areas
                },
                "adaptation_confidence": behavior_analysis.get("confidence", 0.5)
            }

            logger.info(f"用户行为自适应完成: {user_id}, 应用了{len(adaptations)}个调整")
            return result

        except Exception as e:
            logger.error(f"用户行为自适应失败: {e}")
            return {"error": str(e)}

    def get_experience_analytics(
        self,
        user_id: str,
        analytics_type: str = "comprehensive"
    ) -> dict[str, Any]:
        """获取体验分析"""
        try:
            if user_id not in self.user_profiles:
                return {"error": "用户档案不存在"}

            user_profile = self.user_profiles[user_id]

            # 生成不同类型的分析
            analytics = {}

            if analytics_type in ["comprehensive", "usage"]:
                analytics["usage_patterns"] = self._analyze_usage_patterns(user_profile)

            if analytics_type in ["comprehensive", "preferences"]:
                analytics["preference_evolution"] = self._analyze_preference_evolution(user_profile)

            if analytics_type in ["comprehensive", "effectiveness"]:
                analytics["personalization_effectiveness"] = self._analyze_personalization_effectiveness(user_profile)

            if analytics_type in ["comprehensive", "recommendations"]:
                analytics["improvement_recommendations"] = self._generate_improvement_recommendations(user_profile)

            # 生成总体洞察
            analytics["overall_insights"] = self._generate_overall_insights(user_profile, analytics)

            result = {
                "user_id": user_id,
                "analytics_type": analytics_type,
                "analytics": analytics,
                "profile_maturity": self._calculate_profile_maturity(user_profile),
                "personalization_score": self._calculate_personalization_score(user_profile),
                "generated_at": datetime.now().isoformat()
            }

            logger.info(f"体验分析生成完成: {user_id}, 类型: {analytics_type}")
            return result

        except Exception as e:
            logger.error(f"获取体验分析失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def _initialize_experience_templates(self) -> Dict[str, Any]:
=======
    
    def _initialize_experience_templates(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """初始化体验模板"""
        return {
            "professional": {
                "color_scheme": "blue_gray",
                "layout": "structured",
                "information_density": "high",
                "interaction_style": "formal"
            },
            "casual": {
                "color_scheme": "warm",
                "layout": "flexible",
                "information_density": "medium",
                "interaction_style": "friendly"
            },
            "academic": {
                "color_scheme": "neutral",
                "layout": "detailed",
                "information_density": "very_high",
                "interaction_style": "scholarly"
            },
            "creative": {
                "color_scheme": "vibrant",
                "layout": "dynamic",
                "information_density": "low",
                "interaction_style": "inspiring"
            }
        }
<<<<<<< HEAD

    def _initialize_customization_options(self) -> Dict[str, Any]:
=======
    
    def _initialize_customization_options(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """初始化定制选项"""
        return {
            "themes": list(ExperienceTheme),
            "personalization_levels": list(PersonalizationLevel),
            "learning_styles": ["visual", "auditory", "kinesthetic", "reading", "balanced"],
            "interface_layouts": ["compact", "standard", "spacious", "custom"],
            "content_formats": ["text", "visual", "interactive", "mixed"],
            "notification_preferences": ["immediate", "batched", "minimal", "off"],
            "accessibility_options": ["high_contrast", "large_text", "screen_reader", "keyboard_navigation"]
        }

    def _apply_initial_personalization(self, user_profile: UserProfile):
        """应用初始个性化设置"""
        # 根据个性化级别设置默认偏好
        if user_profile.personalization_level == PersonalizationLevel.BASIC:
            user_profile.preferences.update({
                "interface_complexity": "simple",
                "suggestion_frequency": "low",
                "automation_level": "minimal"
            })
        elif user_profile.personalization_level == PersonalizationLevel.ADVANCED:
            user_profile.preferences.update({
                "interface_complexity": "advanced",
                "suggestion_frequency": "high",
                "automation_level": "extensive"
            })
<<<<<<< HEAD

    def _get_available_customizations(self, personalization_level: PersonalizationLevel) -> List[str]:
=======
    
    def _get_available_customizations(self, personalization_level: PersonalizationLevel) -> list[str]:
>>>>>>> feature/core-services-refactor
        """获取可用的定制选项"""
        base_customizations = ["theme", "layout", "content_format"]

        if personalization_level in [PersonalizationLevel.INTERMEDIATE, PersonalizationLevel.ADVANCED, PersonalizationLevel.EXPERT]:
            base_customizations.extend(["learning_style", "interaction_preferences", "automation_settings"])

        if personalization_level in [PersonalizationLevel.ADVANCED, PersonalizationLevel.EXPERT]:
            base_customizations.extend(["custom_rules", "advanced_filters", "api_integrations"])

        return base_customizations
<<<<<<< HEAD

    def _generate_initial_recommendations(self, user_profile: UserProfile) -> List[str]:
=======
    
    def _generate_initial_recommendations(self, user_profile: UserProfile) -> list[str]:
>>>>>>> feature/core-services-refactor
        """生成初始推荐"""
        recommendations = []

        if user_profile.personalization_level == PersonalizationLevel.BASIC:
            recommendations.extend([
                "建议先熟悉基本功能",
                "可以尝试不同的主题风格",
                "根据使用习惯调整界面布局"
            ])
        else:
            recommendations.extend([
                "探索高级个性化选项",
                "设置自定义规则和过滤器",
                "配置自动化工作流程"
            ])

        return recommendations
<<<<<<< HEAD

    def _update_preferences(self, user_profile: UserProfile, preferences_data: Dict[str, Any]):
        """更新用户偏好"""
        user_profile.preferences.update(preferences_data)

    def _update_theme(self, user_profile: UserProfile, theme_data: Dict[str, Any]):
=======
    
    def _update_preferences(self, user_profile: UserProfile, preferences_data: dict[str, Any]):
        """更新用户偏好"""
        user_profile.preferences.update(preferences_data)
    
    def _update_theme(self, user_profile: UserProfile, theme_data: dict[str, Any]):
>>>>>>> feature/core-services-refactor
        """更新主题"""
        theme_name = theme_data.get("theme")
        if theme_name:
            try:
                user_profile.experience_theme = ExperienceTheme(theme_name)
            except ValueError:
                logger.warning(f"无效的主题名称: {theme_name}")
<<<<<<< HEAD

    def _update_personalization_level(self, user_profile: UserProfile, level_data: Dict[str, Any]):
=======
    
    def _update_personalization_level(self, user_profile: UserProfile, level_data: dict[str, Any]):
>>>>>>> feature/core-services-refactor
        """更新个性化级别"""
        level_name = level_data.get("level")
        if level_name:
            try:
                user_profile.personalization_level = PersonalizationLevel(level_name)
            except ValueError:
                logger.warning(f"无效的个性化级别: {level_name}")
<<<<<<< HEAD

    def _update_learning_style(self, user_profile: UserProfile, style_data: Dict[str, Any]):
=======
    
    def _update_learning_style(self, user_profile: UserProfile, style_data: dict[str, Any]):
>>>>>>> feature/core-services-refactor
        """更新学习风格"""
        learning_style = style_data.get("style")
        if learning_style in self.customization_options["learning_styles"]:
            user_profile.learning_style = learning_style
<<<<<<< HEAD

    def _update_expertise_areas(self, user_profile: UserProfile, expertise_data: Dict[str, Any]):
=======
    
    def _update_expertise_areas(self, user_profile: UserProfile, expertise_data: dict[str, Any]):
>>>>>>> feature/core-services-refactor
        """更新专业领域"""
        expertise_areas = expertise_data.get("areas", [])
        if isinstance(expertise_areas, list):
            user_profile.expertise_areas = expertise_areas
<<<<<<< HEAD

    def _generate_personalized_config(self, user_profile: UserProfile) -> Dict[str, Any]:
=======
    
    def _generate_personalized_config(self, user_profile: UserProfile) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """生成个性化配置"""
        return {
            "user_id": user_profile.user_id,
            "theme": user_profile.experience_theme.value,
            "personalization_level": user_profile.personalization_level.value,
            "learning_style": user_profile.learning_style,
            "preferences": user_profile.preferences,
            "expertise_areas": user_profile.expertise_areas,
            "interface_config": self._get_interface_config_for_profile(user_profile),
            "content_config": self._get_content_config_for_profile(user_profile)
        }
<<<<<<< HEAD

    def _record_customization_history(self, user_profile: UserProfile, customization_request: Dict[str, Any]):
=======
    
    def _record_customization_history(self, user_profile: UserProfile, customization_request: dict[str, Any]):
>>>>>>> feature/core-services-refactor
        """记录定制历史"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "customization_type": customization_request.get("type"),
            "customization_data": customization_request.get("data"),
            "applied": True
        }

        user_profile.interaction_history.append(history_entry)
<<<<<<< HEAD

    def _generate_experience_recommendations(self, user_profile: UserProfile) -> List[str]:
=======
    
    def _generate_experience_recommendations(self, user_profile: UserProfile) -> list[str]:
>>>>>>> feature/core-services-refactor
        """生成体验推荐"""
        recommendations = []

        # 基于使用历史生成推荐
        if len(user_profile.interaction_history) < 5:
            recommendations.append("建议多使用系统以获得更好的个性化体验")

        # 基于个性化级别生成推荐
        if user_profile.personalization_level == PersonalizationLevel.BASIC:
            recommendations.append("考虑升级到中级个性化以获得更多定制选项")

        # 基于专业领域生成推荐
        if not user_profile.expertise_areas:
            recommendations.append("设置您的专业领域以获得更相关的内容")

        return recommendations
<<<<<<< HEAD

    def _get_default_interface_config(self, interface_type: str) -> Dict[str, Any]:
=======
    
    def _get_default_interface_config(self, interface_type: str) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取默认界面配置"""
        return {
            "interface_type": interface_type,
            "theme": "professional",
            "layout": "standard",
            "components": ["header", "main", "sidebar", "footer"],
            "interactions": {"style": "standard"},
            "content_preferences": {"format": "mixed"},
            "accessibility": {"level": "standard"}
        }
<<<<<<< HEAD

    def _get_theme_config(self, experience_theme: ExperienceTheme) -> Dict[str, Any]:
        """获取主题配置"""
        return self.experience_templates.get(experience_theme.value, self.experience_templates["professional"])

    def _get_layout_config(self, user_profile: UserProfile) -> Dict[str, Any]:
=======
    
    def _get_theme_config(self, experience_theme: ExperienceTheme) -> dict[str, Any]:
        """获取主题配置"""
        return self.experience_templates.get(experience_theme.value, self.experience_templates["professional"])
    
    def _get_layout_config(self, user_profile: UserProfile) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取布局配置"""
        layout_preference = user_profile.preferences.get("layout", "standard")

        layout_configs = {
            "compact": {"spacing": "tight", "components": "minimal"},
            "standard": {"spacing": "normal", "components": "standard"},
            "spacious": {"spacing": "loose", "components": "expanded"}
        }

        return layout_configs.get(layout_preference, layout_configs["standard"])
<<<<<<< HEAD

    def _get_component_config(self, user_profile: UserProfile) -> Dict[str, Any]:
=======
    
    def _get_component_config(self, user_profile: UserProfile) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取组件配置"""
        components = ["header", "main", "footer"]

        if user_profile.personalization_level in [PersonalizationLevel.INTERMEDIATE, PersonalizationLevel.ADVANCED, PersonalizationLevel.EXPERT]:
            components.extend(["sidebar", "toolbar", "status_bar"])

        if user_profile.personalization_level in [PersonalizationLevel.ADVANCED, PersonalizationLevel.EXPERT]:
            components.extend(["advanced_panel", "customization_panel"])

        return {"enabled_components": components}
<<<<<<< HEAD

    def _get_interaction_config(self, user_profile: UserProfile) -> Dict[str, Any]:
=======
    
    def _get_interaction_config(self, user_profile: UserProfile) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取交互配置"""
        return {
            "style": user_profile.experience_theme.value,
            "responsiveness": user_profile.preferences.get("responsiveness", "standard"),
            "feedback_level": user_profile.preferences.get("feedback_level", "normal")
        }
<<<<<<< HEAD

    def _get_content_preferences(self, user_profile: UserProfile) -> Dict[str, Any]:
=======
    
    def _get_content_preferences(self, user_profile: UserProfile) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取内容偏好"""
        return {
            "format": user_profile.preferences.get("content_format", "mixed"),
            "density": user_profile.preferences.get("information_density", "medium"),
            "expertise_level": user_profile.personalization_level.value
        }
<<<<<<< HEAD

    def _get_accessibility_config(self, user_profile: UserProfile) -> Dict[str, Any]:
=======
    
    def _get_accessibility_config(self, user_profile: UserProfile) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取无障碍配置"""
        accessibility_prefs = user_profile.preferences.get("accessibility", {})

        return {
            "high_contrast": accessibility_prefs.get("high_contrast", False),
            "large_text": accessibility_prefs.get("large_text", False),
            "screen_reader": accessibility_prefs.get("screen_reader", False),
            "keyboard_navigation": accessibility_prefs.get("keyboard_navigation", True)
        }
<<<<<<< HEAD

    def _apply_personalization_rules(self, interface_config: Dict[str, Any], user_profile: UserProfile) -> Dict[str, Any]:
=======
    
    def _apply_personalization_rules(self, interface_config: dict[str, Any], user_profile: UserProfile) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """应用个性化规则"""
        for rule in self.personalization_rules:
            if rule.is_active and self._evaluate_rule_condition(rule.condition, user_profile):
                interface_config = self._apply_rule_action(interface_config, rule.action)

        return interface_config
<<<<<<< HEAD

    def _evaluate_rule_condition(self, condition: Dict[str, Any], user_profile: UserProfile) -> bool:
        """评估规则条件"""
        # 简化的条件评估实现
        return True  # 默认所有规则都适用

    def _apply_rule_action(self, interface_config: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
=======
    
    def _evaluate_rule_condition(self, condition: dict[str, Any], user_profile: UserProfile) -> bool:
        """评估规则条件"""
        # 简化的条件评估实现
        return True  # 默认所有规则都适用
    
    def _apply_rule_action(self, interface_config: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """应用规则动作"""
        # 简化的动作应用实现
        interface_config.update(action)
        return interface_config
<<<<<<< HEAD

    def _analyze_user_behavior(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
=======
    
    def _analyze_user_behavior(self, behavior_data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析用户行为"""
        return {
            "interaction_frequency": behavior_data.get("interaction_count", 0),
            "feature_usage": behavior_data.get("features_used", []),
            "time_spent": behavior_data.get("session_duration", 0),
            "error_rate": behavior_data.get("error_count", 0) / max(behavior_data.get("interaction_count", 1), 1),
            "confidence": 0.7  # 简化的置信度计算
        }
<<<<<<< HEAD

    def _generate_adaptations(self, user_profile: UserProfile, behavior_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
=======
    
    def _generate_adaptations(self, user_profile: UserProfile, behavior_analysis: dict[str, Any]) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """生成适应性调整"""
        adaptations = []

        # 基于交互频率调整
        if behavior_analysis["interaction_frequency"] > 50:
            adaptations.append({
                "type": "personalization_level",
                "action": "upgrade",
                "reason": "高频使用用户"
            })

        # 基于错误率调整
        if behavior_analysis["error_rate"] > 0.1:
            adaptations.append({
                "type": "interface_complexity",
                "action": "simplify",
                "reason": "降低错误率"
            })

        return adaptations
<<<<<<< HEAD

    def _apply_adaptation(self, user_profile: UserProfile, adaptation: Dict[str, Any]):
=======
    
    def _apply_adaptation(self, user_profile: UserProfile, adaptation: dict[str, Any]):
>>>>>>> feature/core-services-refactor
        """应用适应性调整"""
        adaptation_type = adaptation["type"]
        action = adaptation["action"]

        if adaptation_type == "personalization_level" and action == "upgrade":
            current_levels = list(PersonalizationLevel)
            current_index = current_levels.index(user_profile.personalization_level)
            if current_index < len(current_levels) - 1:
                user_profile.personalization_level = current_levels[current_index + 1]

        elif adaptation_type == "interface_complexity" and action == "simplify":
            user_profile.preferences["interface_complexity"] = "simple"
<<<<<<< HEAD

    def _analyze_usage_patterns(self, user_profile: UserProfile) -> Dict[str, Any]:
=======
    
    def _analyze_usage_patterns(self, user_profile: UserProfile) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析使用模式"""
        if not user_profile.interaction_history:
            return {"pattern": "insufficient_data"}

        # 简化的使用模式分析
        total_interactions = len(user_profile.interaction_history)
        recent_interactions = [h for h in user_profile.interaction_history[-10:]]

        return {
            "total_interactions": total_interactions,
            "recent_activity": len(recent_interactions),
            "activity_trend": "increasing" if len(recent_interactions) > 5 else "stable",
            "most_used_features": ["customization", "personalization"]  # 简化实现
        }
<<<<<<< HEAD

    def _analyze_preference_evolution(self, user_profile: UserProfile) -> Dict[str, Any]:
=======
    
    def _analyze_preference_evolution(self, user_profile: UserProfile) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析偏好演化"""
        return {
            "preference_stability": "stable",  # 简化实现
            "major_changes": [],
            "evolution_trend": "consistent"
        }
<<<<<<< HEAD

    def _analyze_personalization_effectiveness(self, user_profile: UserProfile) -> Dict[str, Any]:
=======
    
    def _analyze_personalization_effectiveness(self, user_profile: UserProfile) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析个性化效果"""
        return {
            "effectiveness_score": 0.8,  # 简化实现
            "user_satisfaction": "high",
            "adaptation_success_rate": 0.9
        }
<<<<<<< HEAD

    def _generate_improvement_recommendations(self, user_profile: UserProfile) -> List[str]:
=======
    
    def _generate_improvement_recommendations(self, user_profile: UserProfile) -> list[str]:
>>>>>>> feature/core-services-refactor
        """生成改进推荐"""
        recommendations = []

        if user_profile.personalization_level == PersonalizationLevel.BASIC:
            recommendations.append("考虑探索更高级的个性化功能")

        if not user_profile.expertise_areas:
            recommendations.append("设置专业领域以获得更精准的个性化")

        if len(user_profile.interaction_history) < 10:
            recommendations.append("增加使用频率以改善个性化效果")

        return recommendations
<<<<<<< HEAD

    def _generate_overall_insights(self, user_profile: UserProfile, analytics: Dict[str, Any]) -> List[str]:
=======
    
    def _generate_overall_insights(self, user_profile: UserProfile, analytics: dict[str, Any]) -> list[str]:
>>>>>>> feature/core-services-refactor
        """生成总体洞察"""
        insights = []

        # 基于使用模式的洞察
        usage_patterns = analytics.get("usage_patterns", {})
        if usage_patterns.get("activity_trend") == "increasing":
            insights.append("用户活跃度呈上升趋势，个性化效果良好")

        # 基于个性化效果的洞察
        effectiveness = analytics.get("personalization_effectiveness", {})
        if effectiveness.get("effectiveness_score", 0) > 0.8:
            insights.append("个性化系统运行良好，用户满意度较高")

        return insights

    def _calculate_profile_maturity(self, user_profile: UserProfile) -> str:
        """计算档案成熟度"""
        factors = [
            len(user_profile.interaction_history) > 20,
            len(user_profile.preferences) > 5,
            len(user_profile.expertise_areas) > 0,
            user_profile.personalization_level != PersonalizationLevel.BASIC
        ]

        maturity_score = sum(factors) / len(factors)

        if maturity_score >= 0.8:
            return "mature"
        elif maturity_score >= 0.6:
            return "developing"
        else:
            return "new"

    def _calculate_personalization_score(self, user_profile: UserProfile) -> float:
        """计算个性化分数"""
        # 简化的个性化分数计算
        base_score = 0.5

        # 基于个性化级别
        level_bonus = {
            PersonalizationLevel.BASIC: 0.0,
            PersonalizationLevel.INTERMEDIATE: 0.1,
            PersonalizationLevel.ADVANCED: 0.2,
            PersonalizationLevel.EXPERT: 0.3
        }.get(user_profile.personalization_level, 0.0)

        # 基于偏好设置数量
        preference_bonus = min(0.2, len(user_profile.preferences) * 0.02)

        # 基于交互历史
        history_bonus = min(0.2, len(user_profile.interaction_history) * 0.01)

        return min(1.0, base_score + level_bonus + preference_bonus + history_bonus)
<<<<<<< HEAD

    def _get_interface_config_for_profile(self, user_profile: UserProfile) -> Dict[str, Any]:
=======
    
    def _get_interface_config_for_profile(self, user_profile: UserProfile) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """为档案获取界面配置"""
        return {
            "layout": user_profile.preferences.get("layout", "standard"),
            "theme": user_profile.experience_theme.value,
            "complexity": user_profile.preferences.get("interface_complexity", "standard")
        }
<<<<<<< HEAD

    def _get_content_config_for_profile(self, user_profile: UserProfile) -> Dict[str, Any]:
=======
    
    def _get_content_config_for_profile(self, user_profile: UserProfile) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """为档案获取内容配置"""
        return {
            "format": user_profile.preferences.get("content_format", "mixed"),
            "expertise_level": user_profile.personalization_level.value,
            "areas_of_interest": user_profile.expertise_areas
        }
