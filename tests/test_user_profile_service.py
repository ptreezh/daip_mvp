"""Tests for the UserProfileService and SessionManagementService.

This module contains unit tests for the user profile and session management functionality.
"""

import os
import shutil
import tempfile
import time
import unittest

from src.core_services.session_management_service import SessionManagementService
from src.core_services.user_profile_service import UserProfileService


class TestUserProfileService(unittest.TestCase):
    """Test cases for the UserProfileService."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.profiles_dir = os.path.join(self.test_dir, "profiles")
        self.user_profile_service = UserProfileService(data_dir=self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_create_profile(self):
        """Test creating a user profile."""
        # Create a profile
        profile = self.user_profile_service.create_profile(
            username="testuser",
            metadata={"display_name": "Test User"}
        )

        # Verify profile was created
        self.assertIsNotNone(profile)
        self.assertEqual(profile.username, "testuser")
        self.assertEqual(profile.metadata.get("display_name"), "Test User")

        # Verify profile was saved to disk
        profile_path = os.path.join(self.profiles_dir, f"{profile.user_id}.json")
        self.assertTrue(os.path.exists(profile_path))

    def test_get_profile(self):
        """Test retrieving a user profile."""
        # Create a profile
        profile = self.user_profile_service.create_profile(username="testuser")

        # Get the profile
        retrieved_profile = self.user_profile_service.get_profile(profile.user_id)

        # Verify profile was retrieved
        self.assertIsNotNone(retrieved_profile)
        self.assertEqual(retrieved_profile.user_id, profile.user_id)
        self.assertEqual(retrieved_profile.username, "testuser")

    def test_get_profile_by_username(self):
        """Test retrieving a user profile by username."""
        # Create a profile
        profile = self.user_profile_service.create_profile(username="testuser")

        # Get the profile by username
        retrieved_profile = self.user_profile_service.get_profile_by_username("testuser")

        # Verify profile was retrieved
        self.assertIsNotNone(retrieved_profile)
        self.assertEqual(retrieved_profile.user_id, profile.user_id)
        self.assertEqual(retrieved_profile.username, "testuser")

    def test_update_profile(self):
        """Test updating a user profile."""
        # Create a profile
        profile = self.user_profile_service.create_profile(username="testuser")

        # Update the profile
        updated_profile = self.user_profile_service.update_profile(
            profile.user_id,
            preferences={"theme": "dark"},
            metadata={"display_name": "Updated User"}
        )

        # Verify profile was updated
        self.assertIsNotNone(updated_profile)
        self.assertEqual(updated_profile.preferences.get("theme"), "dark")
        self.assertEqual(updated_profile.metadata.get("display_name"), "Updated User")

        # Verify changes were saved to disk
        retrieved_profile = self.user_profile_service.get_profile(profile.user_id)
        self.assertEqual(retrieved_profile.preferences.get("theme"), "dark")
        self.assertEqual(retrieved_profile.metadata.get("display_name"), "Updated User")

    def test_create_session(self):
        """Test creating a user session."""
        # Create a profile
        profile = self.user_profile_service.create_profile(username="testuser")

        # Create a session
        session = self.user_profile_service.create_session(
            profile.user_id,
            expiry_minutes=60,
            metadata={"ip_address": "127.0.0.1"}
        )

        # Verify session was created
        self.assertIsNotNone(session)
        self.assertEqual(session.user_id, profile.user_id)
        self.assertTrue(session.is_active)
        self.assertEqual(session.metadata.get("ip_address"), "127.0.0.1")

        # Verify session was added to profile
        updated_profile = self.user_profile_service.get_profile(profile.user_id)
        self.assertIn(session.session_id, updated_profile.sessions)

    def test_get_session(self):
        """Test retrieving a user session."""
        # Create a profile and session
        profile = self.user_profile_service.create_profile(username="testuser")
        session = self.user_profile_service.create_session(profile.user_id)

        # Get the session
        retrieved_session = self.user_profile_service.get_session(session.session_id)

        # Verify session was retrieved
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.session_id, session.session_id)
        self.assertEqual(retrieved_session.user_id, profile.user_id)

    def test_end_session(self):
        """Test ending a user session."""
        # Create a profile and session
        profile = self.user_profile_service.create_profile(username="testuser")
        session = self.user_profile_service.create_session(profile.user_id)

        # End the session
        success = self.user_profile_service.end_session(session.session_id)

        # Verify session was ended
        self.assertTrue(success)

        # Verify session is no longer active
        retrieved_session = self.user_profile_service.get_session(session.session_id)
        self.assertIsNone(retrieved_session)

    def test_get_active_sessions_for_user(self):
        """Test retrieving active sessions for a user."""
        # Create a profile and multiple sessions
        profile = self.user_profile_service.create_profile(username="testuser")
        session1 = self.user_profile_service.create_session(profile.user_id)
        session2 = self.user_profile_service.create_session(profile.user_id)

        # End one session
        self.user_profile_service.end_session(session1.session_id)

        # Get active sessions
        active_sessions = self.user_profile_service.get_active_sessions_for_user(profile.user_id)

        # Verify only one session is active
        self.assertEqual(len(active_sessions), 1)
        self.assertEqual(active_sessions[0].session_id, session2.session_id)

    def test_expired_session(self):
        """Test that expired sessions are handled correctly."""
        # Create a profile and session with short expiry
        profile = self.user_profile_service.create_profile(username="testuser")

        # Create session that expires in 1 second
        session = self.user_profile_service.create_session(
            profile.user_id,
            expiry_minutes=1/60  # 1 second
        )

        # Wait for session to expire
        time.sleep(1.1)

        # Try to get the expired session
        retrieved_session = self.user_profile_service.get_session(session.session_id)

        # Verify session is no longer active
        self.assertIsNone(retrieved_session)


class TestSessionManagementService(unittest.TestCase):
    """Test cases for the SessionManagementService."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.auth_dir = os.path.join(self.test_dir, "auth")
        self.profiles_dir = os.path.join(self.test_dir, "profiles")

        # Create services
        self.user_profile_service = UserProfileService(data_dir=self.profiles_dir)
        self.session_management_service = SessionManagementService(
            user_profile_service=self.user_profile_service,
            auth_data_dir=self.auth_dir,
            session_expiry_minutes=60,
            token_secret="test_secret"
        )

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_register_user(self):
        """Test registering a new user."""
        # Register a user
        success, message, profile = self.session_management_service.register_user(
            username="testuser",
            password="password123",
            display_name="Test User"
        )

        # Verify user was registered
        self.assertTrue(success)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.username, "testuser")

    def test_authenticate(self):
        """Test authenticating a user."""
        # Register a user
        self.session_management_service.register_user(
            username="testuser",
            password="password123"
        )

        # Authenticate with correct credentials
        response = self.session_management_service.authenticate(
            username="testuser",
            password="password123"
        )

        # Verify authentication succeeded
        self.assertTrue(response.success)
        self.assertIsNotNone(response.user_id)
        self.assertIsNotNone(response.session_id)

        # Authenticate with incorrect password
        response = self.session_management_service.authenticate(
            username="testuser",
            password="wrongpassword"
        )

        # Verify authentication failed
        self.assertFalse(response.success)
        self.assertIsNone(response.user_id)
        self.assertIsNone(response.session_id)

    def test_validate_session(self):
        """Test validating a session."""
        # Register and authenticate a user
        self.session_management_service.register_user(
            username="testuser",
            password="password123"
        )
        auth_response = self.session_management_service.authenticate(
            username="testuser",
            password="password123"
        )

        # Validate the session
        is_valid, user_id, session = self.session_management_service.validate_session(
            auth_response.session_id
        )

        # Verify session is valid
        self.assertTrue(is_valid)
        self.assertEqual(user_id, auth_response.user_id)
        self.assertIsNotNone(session)

        # Validate an invalid session
        is_valid, user_id, session = self.session_management_service.validate_session(
            "invalid_session_id"
        )

        # Verify session is invalid
        self.assertFalse(is_valid)
        self.assertIsNone(user_id)
        self.assertIsNone(session)

    def test_change_password(self):
        """Test changing a user's password."""
        # Register a user
        success, message, profile = self.session_management_service.register_user(
            username="testuser",
            password="password123"
        )

        # Change password
        success, message = self.session_management_service.change_password(
            user_id=profile.user_id,
            current_password="password123",
            new_password="newpassword456"
        )

        # Verify password was changed
        self.assertTrue(success)

        # Authenticate with new password
        response = self.session_management_service.authenticate(
            username="testuser",
            password="newpassword456"
        )

        # Verify authentication succeeded with new password
        self.assertTrue(response.success)

    def test_generate_and_validate_token(self):
        """Test generating and validating a token."""
        # Register a user
        success, message, profile = self.session_management_service.register_user(
            username="testuser",
            password="password123"
        )

        # Generate a token
        token = self.session_management_service.generate_token(
            user_id=profile.user_id,
            expiry_minutes=60
        )

        # Verify token was generated
        self.assertIsNotNone(token)

        # Validate the token
        is_valid, user_id, payload = self.session_management_service.validate_token(token)

        # Verify token is valid
        self.assertTrue(is_valid)
        self.assertEqual(user_id, profile.user_id)
        self.assertIsNotNone(payload)


if __name__ == "__main__":
    unittest.main()
