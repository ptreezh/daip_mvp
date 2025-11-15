"""
Debate System ViewModel

This module implements the ViewModel for debate functionality in the P7 GUI application.
It manages debate creation, participant management, argument submission, and debate state.
"""

from typing import Any, Dict, List, Optional
from .base import ViewModel
from ..models.interaction_layer import InteractionLayer


class DebateViewModel(ViewModel):
    """
    ViewModel for debate functionality.
    
    This ViewModel manages:
    - Debate creation and management
    - Participant management for debates
    - Argument submission and tracking
    - Debate state and status
    - Live debate updates
    """
    
    def __init__(self, interaction_layer: InteractionLayer):
        """
        Initialize the DebateViewModel.
        
        Args:
            interaction_layer: Layer for communicating with backend services
        """
        super().__init__()
        
        self._interaction_layer = interaction_layer
        
        # Initialize properties with default values
        self.set_property('available_debates', [])  # List of debate dictionaries
        self.set_property('current_debate_id', None)  # Currently active debate ID
        self.set_property('current_debate_data', None)  # Full data of current debate
        self.set_property('available_participants', [])  # Available participants to add
        self.set_property('current_participants', [])  # Participants in current debate
        self.set_property('debate_topic', '')  # Topic of current debate
        self.set_property('is_active_debate', False)  # Whether a debate is active
        self.set_property('is_loading_debates', False)  # Whether debaters are being loaded
        self.set_property('debate_arguments', [])  # Arguments submitted in current debate
        self.set_property('debate_round', 0)  # Current round in the debate
        self.set_property('debate_status', 'inactive')  # Status of the debate
        self.set_property('selected_participant', None)  # Currently selected participant
        self.set_property('argument_input', '')  # Current argument input text
        self.set_property('votes', {})  # Tracking votes in the debate
        
        # Register debate-specific commands
        self._register_commands()
    
    def _register_commands(self):
        """Register all commands that this ViewModel supports."""
        # Debate management commands
        self.register_command('start_debate', self._start_debate_command)
        self.register_command('join_debate', self._join_debate_command)
        self.register_command('leave_debate', self._leave_debate_command)
        self.register_command('end_debate', self._end_debate_command)
        self.register_command('load_debates', self._load_debates_command)
        self.register_command('refresh_debates', self._refresh_debates_command)
        
        # Participant management commands
        self.register_command('add_participant', self._add_participant_command)
        self.register_command('remove_participant', self._remove_participant_command)
        self.register_command('select_participant', self._select_participant_command)
        
        # Argument submission commands
        self.register_command('submit_argument', self._submit_argument_command)
        self.register_command('clear_argument_input', self._clear_argument_input_command)
        
        # Vote management commands
        self.register_command('cast_vote', self._cast_vote_command)
        self.register_command('reset_votes', self._reset_votes_command)
    
    def _start_debate_command(self, topic: str) -> str:
        """
        Command to initiate debate creation.
        
        Args:
            topic: Topic for the debate
            
        Returns:
            Status message
        """
        # This is a synchronous command that signals async work should begin
        self.set_property('is_loading_debates', True)
        self.set_property('debate_topic', topic)
        return f"Starting debate on topic: {topic}"
    
    def _join_debate_command(self, debate_id: str, user_id: str) -> str:
        """
        Command to join an existing debate.
        
        Args:
            debate_id: ID of the debate to join
            user_id: ID of the user joining
            
        Returns:
            Status message
        """
        self.set_property('current_debate_id', debate_id)
        return f"Joining debate {debate_id}"
    
    def _leave_debate_command(self) -> str:
        """
        Command to leave the current debate.
        
        Returns:
            Status message
        """
        current_debate_id = self.get_property('current_debate_id')
        if not current_debate_id:
            return "No active debate to leave"
        
        # Update state
        self.set_property('current_debate_id', None)
        self.set_property('current_participants', [])
        self.set_property('is_active_debate', False)
        self.set_property('debate_status', 'inactive')
        
        return f"Left debate: {current_debate_id}"
    
    def _end_debate_command(self) -> str:
        """
        Command to end the current debate.
        
        Returns:
            Status message
        """
        current_debate_id = self.get_property('current_debate_id')
        if not current_debate_id:
            return "No active debate to end"
        
        # In a real implementation, this would call the backend to end the debate
        # For now, just update the local state
        self.set_property('is_active_debate', False)
        self.set_property('debate_status', 'completed')
        
        # Remove from current participants
        self.set_property('current_participants', [])
        
        return f"Ended debate: {current_debate_id}"
    
    def _load_debates_command(self) -> str:
        """
        Command to initiate debate loading.
        
        Returns:
            Status message
        """
        self.set_property('is_loading_debates', True)
        return "Loading debates initiated"
    
    def _refresh_debates_command(self) -> str:
        """
        Command to refresh the debates list.
        
        Returns:
            Status message
        """
        self.set_property('is_loading_debates', True)
        return "Refreshing debates list"
    
    def _add_participant_command(self, participant_id: str, name: str) -> str:
        """
        Command to add a participant to the current debate.
        
        Args:
            participant_id: ID of the participant to add
            name: Name of the participant
            
        Returns:
            Status message
        """
        current_participants = self.get_property('current_participants', [])
        participant = {
            'id': participant_id,
            'name': name,
            'joined_at': self._get_current_timestamp(),
            'role': 'debater'
        }
        
        current_participants.append(participant)
        self.set_property('current_participants', current_participants)
        
        return f"Added participant: {name}"
    
    def _remove_participant_command(self, participant_id: str) -> str:
        """
        Command to remove a participant from the current debate.
        
        Args:
            participant_id: ID of the participant to remove
            
        Returns:
            Status message
        """
        current_participants = self.get_property('current_participants', [])
        updated_participants = [p for p in current_participants if p['id'] != participant_id]
        self.set_property('current_participants', updated_participants)
        
        return f"Removed participant: {participant_id}"
    
    def _select_participant_command(self, participant_id: str) -> str:
        """
        Command to select a participant.
        
        Args:
            participant_id: ID of the participant to select
            
        Returns:
            Status message
        """
        current_participants = self.get_property('current_participants', [])
        selected_participant = next((p for p in current_participants if p['id'] == participant_id), None)
        
        if selected_participant:
            self.set_property('selected_participant', selected_participant)
            return f"Selected participant: {selected_participant['name']}"
        else:
            return f"Participant with ID {participant_id} not found"
    
    def _submit_argument_command(self) -> str:
        """
        Command to submit an argument to the current debate.
        
        Returns:
            Status message
        """
        argument_text = self.get_property('argument_input', '').strip()
        if not argument_text:
            return "No argument to submit"
        
        selected_participant = self.get_property('selected_participant')
        if not selected_participant:
            return "No participant selected to make argument"
        
        # Create argument object
        argument = {
            'id': f'arg_{len(self.get_property("debate_arguments", [])) + 1}',
            'content': argument_text,
            'participant_id': selected_participant['id'],
            'participant_name': selected_participant['name'],
            'timestamp': self._get_current_timestamp(),
            'round': self.get_property('debate_round', 0),
            'type': 'argument'  # Could be 'argument', 'counter', 'rebuttal'
        }
        
        # Add to arguments list
        current_arguments = self.get_property('debate_arguments', [])
        current_arguments.append(argument)
        self.set_property('debate_arguments', current_arguments)
        
        # Clear input and advance round
        self.set_property('argument_input', '')
        self.set_property('debate_round', self.get_property('debate_round', 0) + 1)
        
        return f"Submitted argument: {argument_text[:30]}..."
    
    def _clear_argument_input_command(self) -> str:
        """
        Command to clear the argument input field.
        
        Returns:
            Status message
        """
        self.set_property('argument_input', '')
        return "Cleared argument input"
    
    def _cast_vote_command(self, option: str, voter_id: str) -> str:
        """
        Command to cast a vote in the debate.
        
        Args:
            option: Vote option
            voter_id: ID of the voter
            
        Returns:
            Status message
        """
        votes = self.get_property('votes', {})
        votes[voter_id] = option
        self.set_property('votes', votes)
        
        return f"Casted vote: {option}"
    
    def _reset_votes_command(self) -> str:
        """
        Command to reset all votes in the debate.
        
        Returns:
            Status message
        """
        self.set_property('votes', {})
        return "Reset all votes"
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp as an ISO string.
        
        Returns:
            Current timestamp in ISO format
        """
        return "2025-11-08T00:00:00Z"  # Placeholder
    
    # Public methods for debate functionality
    async def start_debate(self, topic: str) -> Dict[str, Any]:
        """
        Start a new debate with the specified topic.
        
        Args:
            topic: Topic for the new debate
            
        Returns:
            Created debate data
        """
        try:
            self.set_property('is_loading_debates', True)
            
            # In a real implementation, this would call the interaction layer
            # to create a new debate in the backend
            new_debate = {
                'id': f'debate_{len(self.get_property("available_debates", [])) + 1}',
                'topic': topic,
                'status': 'active',
                'created_at': self._get_current_timestamp(),
                'participants': [],
                'arguments': [],
                'moderator': None,
                'rules': ['take_turns', 'respect_opponents', 'follow_topic']
            }
            
            # Update local state
            available_debates = self.get_property('available_debates', [])
            available_debates.append(new_debate)
            self.set_property('available_debates', available_debates)
            self.set_property('current_debate_id', new_debate['id'])
            self.set_property('current_debate_data', new_debate)
            self.set_property('debate_topic', topic)
            self.set_property('is_active_debate', True)
            self.set_property('debate_status', 'active')
            
            return new_debate
        finally:
            self.set_property('is_loading_debates', False)
    
    async def join_debate(self, debate_id: str, user_id: str) -> Dict[str, Any]:
        """
        Join an existing debate.
        
        Args:
            debate_id: ID of the debate to join
            user_id: ID of the user joining
            
        Returns:
            Join status and updated debate data
        """
        try:
            self.set_property('is_loading_debates', True)
            
            # Find the debate
            available_debates = self.get_property('available_debates', [])
            target_debate = None
            debate_idx = -1
            
            for i, debate in enumerate(available_debates):
                if debate['id'] == debate_id:
                    target_debate = debate
                    debate_idx = i
                    break
            
            if not target_debate:
                raise ValueError(f"Debate with ID {debate_id} not found")
            
            # Add user as participant
            participant = {
                'id': user_id,
                'joined_at': self._get_current_timestamp(),
                'role': 'debater',
                'ready_status': 'ready'
            }
            
            if participant not in target_debate.get('participants', []):
                participants = target_debate.get('participants', [])
                participants.append(participant)
                target_debate['participants'] = participants
                available_debates[debate_idx] = target_debate
            
            # Update local state
            self.set_property('available_debates', available_debates)
            self.set_property('current_debate_id', debate_id)
            self.set_property('current_debate_data', target_debate)
            self.set_property('is_active_debate', True)
            self.set_property('debate_status', 'active')
            
            return {
                'success': True,
                'debate': target_debate,
                'message': f'Joined debate {debate_id} as user {user_id}'
            }
        finally:
            self.set_property('is_loading_debates', False)
    
    def add_participant(self, participant_id: str, name: str, role: str = 'debater') -> str:
        """
        Add a participant to the current debate.
        
        Args:
            participant_id: ID of the participant to add
            name: Name of the participant
            role: Role of the participant (debater, moderator, observer, etc.)
            
        Returns:
            Confirmation message
        """
        current_participants = self.get_property('current_participants', [])
        
        # Check if participant already exists
        if any(p['id'] == participant_id for p in current_participants):
            return f"Participant {name} already in debate"
        
        participant = {
            'id': participant_id,
            'name': name,
            'role': role,
            'joined_at': self._get_current_timestamp(),
            'status': 'active'
        }
        
        current_participants.append(participant)
        self.set_property('current_participants', current_participants)
        
        # If this is the current debate, also update the debate data
        current_debate = self.get_property('current_debate_data')
        if current_debate:
            debate_participants = current_debate.get('participants', [])
            debate_participants.append(participant)
            self.set_property('current_debate_data', current_debate)
            
            # Update the available debates list
            available_debates = self.get_property('available_debates', [])
            for i, debate in enumerate(available_debates):
                if debate['id'] == self.get_property('current_debate_id'):
                    available_debates[i] = current_debate
                    break
            self.set_property('available_debates', available_debates)
        
        return f"Added participant: {name} ({role})"
    
    def remove_participant(self, participant_id: str) -> str:
        """
        Remove a participant from the current debate.
        
        Args:
            participant_id: ID of the participant to remove
            
        Returns:
            Confirmation message
        """
        current_participants = self.get_property('current_participants', [])
        participant_idx = -1
        
        for i, participant in enumerate(current_participants):
            if participant['id'] == participant_id:
                participant_idx = i
                break
        
        if participant_idx == -1:
            return f"No participant with ID {participant_id} found in current debate"
        
        removed_participant = current_participants.pop(participant_idx)
        self.set_property('current_participants', current_participants)
        
        # If this is the current debate, also update the debate data
        current_debate = self.get_property('current_debate_data')
        if current_debate:
            debate_participants = current_debate.get('participants', [])
            debate_participants = [p for p in debate_participants if p['id'] != participant_id]
            current_debate['participants'] = debate_participants
            self.set_property('current_debate_data', current_debate)
            
            # Update the available debates list
            available_debates = self.get_property('available_debates', [])
            for i, debate in enumerate(available_debates):
                if debate['id'] == self.get_property('current_debate_id'):
                    available_debates[i] = current_debate
                    break
            self.set_property('available_debates', available_debates)
        
        return f"Removed participant: {removed_participant['name']}"
    
    def submit_argument(self, content: str, participant_id: str = None) -> str:
        """
        Submit an argument to the current debate.
        
        Args:
            content: Content of the argument
            participant_id: ID of the participant making the argument (optional)
            
        Returns:
            Confirmation message
        """
        if not content.strip():
            return "Cannot submit empty argument"
        
        # Determine participant
        arg_participant_id = participant_id or self.get_property('selected_participant', {}).get('id')
        if not arg_participant_id:
            return "No participant selected for argument"
        
        current_participants = self.get_property('current_participants', [])
        arg_participant = next((p for p in current_participants if p['id'] == arg_participant_id), None)
        if not arg_participant:
            return f"Participant with ID {arg_participant_id} not found"
        
        # Create argument object
        argument = {
            'id': f'arg_{len(self.get_property("debate_arguments", [])) + 1}',
            'content': content.strip(),
            'participant_id': arg_participant_id,
            'participant_name': arg_participant.get('name', 'Unknown'),
            'timestamp': self._get_current_timestamp(),
            'round': self.get_property('debate_round', 0),
            'type': 'argument'
        }
        
        # Add to arguments list
        current_arguments = self.get_property('debate_arguments', [])
        current_arguments.append(argument)
        self.set_property('debate_arguments', current_arguments)
        
        # Advance round counter
        self.set_property('debate_round', self.get_property('debate_round', 0) + 1)
        
        # If this is the current debate, also update the debate data
        current_debate = self.get_property('current_debate_data')
        if current_debate:
            debate_arguments = current_debate.get('arguments', [])
            debate_arguments.append(argument)
            current_debate['arguments'] = debate_arguments
            self.set_property('current_debate_data', current_debate)
            
            # Update the available debates list
            available_debates = self.get_property('available_debates', [])
            for i, debate in enumerate(available_debates):
                if debate['id'] == self.get_property('current_debate_id'):
                    available_debates[i] = current_debate
                    break
            self.set_property('available_debates', available_debates)
        
        return f"Submitted argument: {content[:30]}..."
    
    def get_debates_list(self) -> List[Dict[str, Any]]:
        """Get the list of available debates."""
        return self.get_property('available_debates', [])
    
    def get_active_debate_id(self) -> Optional[str]:
        """Get the ID of the current debate."""
        return self.get_property('current_debate_id')
    
    def get_active_debate_data(self) -> Optional[Dict[str, Any]]:
        """Get the data of the current debate."""
        return self.get_property('current_debate_data')
    
    def get_current_participants(self) -> List[Dict[str, Any]]:
        """Get the list of participants in the current debate."""
        return self.get_property('current_participants', [])
    
    def get_debate_arguments(self) -> List[Dict[str, Any]]:
        """Get the list of arguments in the current debate."""
        return self.get_property('debate_arguments', [])
    
    def is_debate_active(self) -> bool:
        """Check if there is an active debate."""
        return self.get_property('is_active_debate', False)
    
    def get_debate_status(self) -> str:
        """Get the status of the current debate."""
        return self.get_property('debate_status', 'inactive')
    
    def get_debate_topic(self) -> str:
        """Get the topic of the current debate."""
        return self.get_property('debate_topic', '')
    
    def is_loading_debates(self) -> bool:
        """Check if debates are being loaded."""
        return self.get_property('is_loading_debates', False)
    
    def get_available_participants(self) -> List[Dict[str, Any]]:
        """Get the list of available participants."""
        return self.get_property('available_participants', [])
    
    def clear_current_debate(self):
        """Clear the current debate data."""
        self.set_property('current_debate_id', None)
        self.set_property('current_debate_data', None)
        self.set_property('current_participants', [])
        self.set_property('is_active_debate', False)
        self.set_property('debate_status', 'inactive')
        self.set_property('debate_arguments', [])
        self.set_property('debate_round', 0)
        self.set_property('votes', {})
        self.set_property('selected_participant', None)