"""Intelligent role selection system for debate topics."""

import re
from dataclasses import dataclass

from daip_live.core.models import Role


@dataclass
class TopicAnalysis:
    """Analysis result of a debate topic."""

    topic: str
    domains: list[str]
    keywords: list[str]
    complexity_score: float
    debate_type: str  # "technical", "ethical", "social", "political", "economic"


@dataclass
class RoleSuggestion:
    """Suggested role with relevance score."""

    role: Role
    role_features: dict[str, any]  # Extracted features for conflict calculation
    relevance_score: float
    reasoning: str
    conflict_potential: float  # How likely this role is to create interesting debate


class IntelligentRoleSelector:
    """Intelligently selects roles for debate topics based on relevance and debate dynamics."""  # noqa: E501

    def __init__(self):
        # Domain keyword mappings
        self.domain_keywords = {
            "technology": [
                "ai",
                "software",
                "hardware",
                "internet",
                "digital",
                "computer",
                "algorithm",
                "automation",
            ],
            "ethics": [
                "moral",
                "ethical",
                "right",
                "wrong",
                "should",
                "ought",
                "justice",
                "fair",
                "implications",
            ],
            "politics": [
                "government",
                "policy",
                "law",
                "regulation",
                "election",
                "democracy",
                "reform",
            ],
            "economics": [
                "money",
                "market",
                "economy",
                "business",
                "cost",
                "profit",
                "trade",
                "economic",
                "financial",
                "automation",
            ],
            "science": [
                "research",
                "study",
                "experiment",
                "evidence",
                "data",
                "scientific",
                "genetic",
                "engineering",
            ],
            "social": [
                "society",
                "culture",
                "community",
                "people",
                "relationship",
                "social",
                "reform",
            ],
            "environment": [
                "climate",
                "environment",
                "nature",
                "pollution",
                "sustainability",
                "green",
            ],
            "health": [
                "medical",
                "health",
                "disease",
                "treatment",
                "patient",
                "doctor",
                "medicine",
            ],
            "education": [
                "school",
                "learning",
                "teach",
                "student",
                "education",
                "knowledge",
            ],
            "philosophy": [
                "meaning",
                "existence",
                "consciousness",
                "reality",
                "truth",
                "wisdom",
            ],
        }

        # Debate type patterns
        self.debate_type_patterns = {
            "technical": [
                "how",
                "implement",
                "technical",
                "feasible",
                "architecture",
                "system",
            ],
            "ethical": ["should", "moral", "right", "wrong", "ethical", "just", "fair"],
            "social": [
                "society",
                "community",
                "cultural",
                "social",
                "people",
                "relationship",
            ],
            "political": [
                "government",
                "policy",
                "law",
                "regulation",
                "political",
                "democratic",
            ],
            "economic": [
                "economic",
                "financial",
                "cost",
                "benefit",
                "market",
                "business",
            ],
        }

        # Personality traits that create good debate dynamics
        self.complementary_traits = {
            "analytical": ["creative", "emotional", "intuitive"],
            "creative": ["analytical", "practical", "logical"],
            "conservative": ["progressive", "radical", "innovative"],
            "progressive": ["conservative", "traditional", "cautious"],
            "optimistic": ["pessimistic", "realistic", "skeptical"],
            "pessimistic": ["optimistic", "hopeful", "idealistic"],
        }

    def analyze_topic(self, topic: str) -> TopicAnalysis:
        """Analyze a debate topic to extract domains, keywords, and type."""
        # Convert to lowercase for processing
        topic_lower = topic.lower()

        # Extract domains
        domains = []
        for domain, keywords in self.domain_keywords.items():
            if any(keyword in topic_lower for keyword in keywords):
                domains.append(domain)

        # Extract keywords from topic
        words = re.findall(r"\b\w+\b", topic_lower)
        keywords = [word for word in words if len(word) > 3]

        # Determine debate type
        debate_type = "general"
        for dtype, patterns in self.debate_type_patterns.items():
            if any(pattern in topic_lower for pattern in patterns):
                debate_type = dtype
                break

        # Calculate complexity score (simple heuristic)
        complexity_score = min(len(keywords) / 10.0, 1.0)
        if any(
            word in topic_lower
            for word in ["regulation", "policy", "implementation", "governance"]
        ):
            complexity_score += 0.2

        return TopicAnalysis(
            topic=topic,
            domains=domains,
            keywords=keywords,
            complexity_score=min(complexity_score, 1.0),
            debate_type=debate_type,
        )

    def extract_role_features(self, role: Role) -> dict[str, any]:
        """Extract features from a role for matching."""
        features = {
            "name": role.name,
            "persona_lower": role.persona.lower(),
            "expertise_domains": [],
            "personality_traits": [],
            "keywords": [],
        }

        # Extract expertise domains from persona
        for domain, keywords in self.domain_keywords.items():
            if any(keyword in features["persona_lower"] for keyword in keywords):
                features["expertise_domains"].append(domain)

        # Extract personality traits
        persona_text = features["persona_lower"]
        if "analytical" in persona_text or "logical" in persona_text:
            features["personality_traits"].append("analytical")
        if "creative" in persona_text or "innovative" in persona_text:
            features["personality_traits"].append("creative")
        if "conservative" in persona_text or "traditional" in persona_text:
            features["personality_traits"].append("conservative")
        if "progressive" in persona_text or "forward" in persona_text:
            features["personality_traits"].append("progressive")
        if "optimistic" in persona_text or "positive" in persona_text:
            features["personality_traits"].append("optimistic")
        if "pessimistic" in persona_text or "skeptical" in persona_text:
            features["personality_traits"].append("pessimistic")

        # Extract keywords from persona
        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in features["persona_lower"]:
                    features["keywords"].append(keyword)

        return features

    def calculate_relevance_score(
        self, topic_analysis: TopicAnalysis, role_features: dict[str, any]
    ) -> float:
        """Calculate how relevant a role is to the topic."""
        score = 0.0

        # Domain matching (40% weight)
        topic_domains = set(topic_analysis.domains)
        role_domains = set(role_features.get("expertise_domains", []))
        if topic_domains and role_domains:
            domain_overlap = len(topic_domains.intersection(role_domains))
            score += (domain_overlap / len(topic_domains)) * 0.4

        # Keyword matching (30% weight)
        topic_keywords = set(topic_analysis.keywords)
        role_keywords = set(role_features.get("keywords", []))
        if topic_keywords and role_keywords:
            keyword_overlap = len(topic_keywords.intersection(role_keywords))
            score += (keyword_overlap / len(topic_keywords)) * 0.3

        # Debate type matching (20% weight)
        topic_type = topic_analysis.debate_type
        personality_traits = role_features.get("personality_traits", [])
        if topic_type == "technical" and "analytical" in personality_traits:
            score += 0.2
        elif topic_type == "ethical" and any(
            trait in personality_traits
            for trait in ["analytical", "conservative", "progressive"]
        ):
            score += 0.2
        elif topic_type == "social" and any(
            trait in personality_traits for trait in ["optimistic", "pessimistic"]
        ):
            score += 0.2
        elif topic_type == "political" and any(
            trait in personality_traits for trait in ["conservative", "progressive"]
        ):
            score += 0.2
        elif topic_type == "economic" and "analytical" in personality_traits:
            score += 0.2

        # Persona relevance (10% weight)
        persona_relevance = self._calculate_persona_relevance(
            topic_analysis, role_features
        )
        score += persona_relevance * 0.1

        return min(score, 1.0)

    def _calculate_persona_relevance(
        self, topic_analysis: TopicAnalysis, role_features: dict[str, any]
    ) -> float:
        """Calculate persona relevance based on semantic similarity."""
        # Simple keyword-based semantic matching
        topic_text = " ".join(topic_analysis.keywords + topic_analysis.domains)
        persona_text = role_features.get("persona_lower", "")

        # Count matching words
        topic_words = set(topic_text.split())
        persona_words = set(persona_text.split())
        overlap = len(topic_words.intersection(persona_words))

        return overlap / max(len(topic_words), 1)

    def calculate_conflict_potential(
        self, role1_features: dict[str, any], role2_features: dict[str, any]
    ) -> float:
        """Calculate how much conflict potential exists between two roles."""
        conflict_score = 0.0

        # Personality trait conflicts
        traits1 = set(role1_features.get("personality_traits", []))
        traits2 = set(role2_features.get("personality_traits", []))

        for trait in traits1:
            if trait in self.complementary_traits:
                conflicting_traits = set(self.complementary_traits[trait])
                if conflicting_traits.intersection(traits2):
                    conflict_score += 0.3

        # Domain expertise differences (some difference is good for debate)
        domains1 = set(role1_features.get("expertise_domains", []))
        domains2 = set(role2_features.get("expertise_domains", []))
        if domains1 and domains2:
            domain_similarity = len(domains1.intersection(domains2)) / len(
                domains1.union(domains2)
            )
            conflict_score += (1.0 - domain_similarity) * 0.4

        return min(conflict_score, 1.0)

    def suggest_roles(
        self, topic: str, available_roles: list[Role], num_suggestions: int = 3
    ) -> list[RoleSuggestion]:
        """Suggest roles for a debate topic."""
        topic_analysis = self.analyze_topic(topic)
        role_features_list = [
            (role, self.extract_role_features(role)) for role in available_roles
        ]

        # Calculate relevance scores for all roles
        suggestions = []
        for role, features in role_features_list:
            relevance_score = self.calculate_relevance_score(topic_analysis, features)

            # Generate reasoning
            reasoning = self._generate_reasoning(
                topic_analysis, features, relevance_score
            )

            suggestion = RoleSuggestion(
                role=role,
                role_features=features,
                relevance_score=relevance_score,
                reasoning=reasoning,
                conflict_potential=0.0,  # Will be calculated later
            )
            suggestions.append(suggestion)

        # Sort by relevance score
        suggestions.sort(key=lambda x: x.relevance_score, reverse=True)

        # Take top suggestions
        top_suggestions = suggestions[:num_suggestions]

        # Calculate conflict potential for the selected roles
        for i, suggestion in enumerate(top_suggestions):
            other_features = [
                s.role_features for s in top_suggestions if s != suggestion
            ]
            if other_features:
                max_conflict = max(
                    self.calculate_conflict_potential(
                        suggestion.role_features, other_role
                    )
                    for other_role in other_features
                )
                suggestion.conflict_potential = max_conflict

        return top_suggestions

    def _generate_reasoning(
        self, topic_analysis: TopicAnalysis, role_features: dict[str, any], score: float
    ) -> str:
        """Generate human-readable reasoning for role suggestion."""
        reasons = []

        # Domain expertise
        common_domains = set(topic_analysis.domains).intersection(
            set(role_features.get("expertise_domains", []))
        )
        if common_domains:
            reasons.append(f"expertise in {', '.join(common_domains)}")

        # Personality traits
        if topic_analysis.debate_type != "general":
            relevant_traits = []
            personality_traits = role_features.get("personality_traits", [])
            if (
                topic_analysis.debate_type == "technical"
                and "analytical" in personality_traits
            ):
                relevant_traits.append("analytical thinking")
            elif (
                topic_analysis.debate_type == "ethical"
                and "analytical" in personality_traits
            ):
                relevant_traits.append("ethical reasoning")

            if relevant_traits:
                reasons.append(f"{', '.join(relevant_traits)}")

        # Keyword relevance
        if role_features.get("keywords", []):
            reasons.append("relevant knowledge base")

        if not reasons:
            reasons.append("general debating capability")

        return f"Strong {', '.join(reasons)}"

    def auto_select_roles(
        self, topic: str, available_roles: list[Role], num_roles: int = 2
    ) -> list[Role]:
        """Automatically select the best roles for a debate."""
        suggestions = self.suggest_roles(topic, available_roles, num_roles * 2)

        # Select roles with good balance of relevance and conflict potential
        selected_roles = []
        remaining_suggestions = suggestions.copy()

        while len(selected_roles) < num_roles and remaining_suggestions:
            # Start with the most relevant role
            if not selected_roles:
                selected_roles.append(remaining_suggestions[0].role)
                remaining_suggestions.pop(0)
            else:
                # Find role with highest conflict potential that's still relevant
                best_conflict_idx = -1
                best_conflict_score = 0

                for i, suggestion in enumerate(remaining_suggestions):
                    if suggestion.relevance_score > 0.3:  # Minimum relevance threshold
                        conflict_score = suggestion.conflict_potential
                        if conflict_score > best_conflict_score:
                            best_conflict_score = conflict_score
                            best_conflict_idx = i

                if best_conflict_idx >= 0:
                    selected_roles.append(remaining_suggestions[best_conflict_idx].role)
                    remaining_suggestions.pop(best_conflict_idx)
                else:
                    # No more good conflict candidates, pick by relevance
                    selected_roles.append(remaining_suggestions[0].role)
                    remaining_suggestions.pop(0)

        return selected_roles
