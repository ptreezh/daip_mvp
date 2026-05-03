"""Example integration of intelligent role management in TUI"""

import asyncio
from typing import List, Optional

from daip_live.p4_role_manager_tools.intelligent_role_manager import IntelligentRoleManager
from daip_live.p4_role_manager_tools.role_model_config import EnhancedRole


class IntelligentRoleIntegration:
    """Integration class to connect intelligent role management with TUI"""

    def __init__(self, model_provider=None):
        self.role_manager = IntelligentRoleManager(model_provider=model_provider)

    async def get_relevant_roles_for_topic(self, topic: str, num_roles: int = 2) -> List[EnhancedRole]:
        """
        Get relevant roles for a topic using intelligent selection.

        Args:
            topic: The debate topic
            num_roles: Number of roles to return

        Returns:
            List of relevant EnhancedRole objects
        """
        # First try to load existing roles
        available_roles = []
        import os
        from pathlib import Path

        # Use the same robust path resolution as the IntelligentRoleManager
        roles_path = Path(self.role_manager._resolve_roles_path("roles"))
        if roles_path.exists():
            for file_path in roles_path.glob("*.yaml"):
                role = self.role_manager.load_role_from_file(file_path.stem)
                if role:
                    available_roles.append(role)

        if available_roles:
            # Use intelligent selection to pick the best roles
            selected_roles = self.role_manager.auto_select_roles(
                topic, available_roles, num_roles=num_roles
            )
            return selected_roles
        else:
            # If no existing roles, create new ones based on the topic
            created_roles = []

            positions = ["supporting", "opposing", "neutral"][:num_roles]
            for i, position in enumerate(positions):
                role = self.role_manager.create_role_from_topic(
                    topic=topic,
                    role_position=position
                )

                # Update model based on availability
                updated_role = await self.role_manager.update_role_models(role)

                # Save to file for future reuse
                self.role_manager.save_role_to_file(updated_role)

                created_roles.append(updated_role)

            return created_roles

    async def create_custom_role_for_topic(self, 
                                         topic: str, 
                                         role_name: str, 
                                         position: str = "supporting",
                                         custom_persona: Optional[str] = None) -> Optional[EnhancedRole]:
        """
        Create a specific custom role for a topic.
        
        Args:
            topic: The debate topic
            role_name: Name for the new role
            position: Position in the debate ('supporting', 'opposing', 'neutral', 'moderator')
            custom_persona: Custom persona text (optional)
            
        Returns:
            Created EnhancedRole object or None if failed
        """
        if custom_persona:
            # Create role with custom persona
            role = EnhancedRole(
                name=role_name,
                persona=custom_persona,
                tools=[],
                model_configs=[
                    self.role_manager._generate_model_config_for_topic(
                        self.role_manager.analyze_topic(topic)
                    )
                ]
            )
        else:
            # Create role based on topic and position
            role = self.role_manager.create_role_from_topic(
                topic=topic,
                role_position=position,
                custom_persona=None
            )
            # Update the name to the specified custom name
            role.name = role_name
        
        # Update models based on availability
        updated_role = await self.role_manager.update_role_models(role)
        
        # Save to file
        success = self.role_manager.save_role_to_file(updated_role)
        
        if success:
            return updated_role
        else:
            return None

    async def analyze_topic_and_provide_recommendations(self, topic: str) -> dict:
        """
        Analyze a topic and provide recommendations for debate setup.

        Args:
            topic: The debate topic

        Returns:
            Dictionary with analysis and recommendations
        """
        analysis = self.role_manager.analyze_topic(topic)

        # Get suggested roles
        available_roles = []
        import os
        from pathlib import Path

        # Use the same robust path resolution as the IntelligentRoleManager
        roles_path = Path(self.role_manager._resolve_roles_path("roles"))
        if roles_path.exists():
            for file_path in roles_path.glob("*.yaml"):
                role = self.role_manager.load_role_from_file(file_path.stem)
                if role:
                    available_roles.append(role)

        if available_roles:
            suggested_roles = self.role_manager.suggest_roles_for_topic(
                topic, available_roles, num_suggestions=3
            )
        else:
            # Create example roles if none exist
            suggested_roles = []
            positions = ["supporting", "opposing", "neutral"]
            for position in positions:
                role = self.role_manager.create_role_from_topic(
                    topic=topic,
                    role_position=position
                )
                suggested_roles.append(role)

        recommendations = {
            'topic_analysis': analysis,
            'suggested_roles': suggested_roles,
            'debate_type': analysis['debate_type'],
            'complexity_score': analysis['complexity_score'],
            'suggested_positions': ['supporting', 'opposing'] if len(suggested_roles) >= 2 else ['supporting']
        }

        return recommendations


# Example usage
async def example_usage():
    """Example of how to use the intelligent role integration"""
    
    # Initialize the integration
    integration = IntelligentRoleIntegration()
    
    # Example 1: Get relevant roles for a topic
    print("Example 1: Getting relevant roles for 'AI in healthcare'")
    roles = await integration.get_relevant_roles_for_topic("AI in healthcare", num_roles=2)
    for role in roles:
        print(f"  - {role.name}: {role.persona[:80]}...")
    
    print("\nExample 2: Creating a custom role")
    custom_role = await integration.create_custom_role_for_topic(
        topic="Climate change policies",
        role_name="ClimateScientist",
        position="supporting",
        custom_persona="You are a climate scientist with deep expertise in environmental science and climate modeling."
    )
    if custom_role:
        print(f"  Created: {custom_role.name}")
    
    print("\nExample 3: Analyzing topic and getting recommendations")
    recommendations = await integration.analyze_topic_and_provide_recommendations("The ethics of genetic engineering")
    print(f"  Debate type: {recommendations['debate_type']}")
    print(f"  Complexity: {recommendations['complexity_score']:.2f}")
    print(f"  Suggested roles: {[r.name for r in recommendations['suggested_roles']]}")
    
    print("\nAll examples completed successfully!")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_usage())