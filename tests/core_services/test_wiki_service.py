"""@Time    : 2025-07-03 20:27:00
@Author  : DAIP-LIVE Team
@File    : test_wiki_service.py
@Description:
    Unit tests for the WikiService.
"""

import json
import os
import shutil
from pathlib import Path

import pytest
from daip_mvp_project.src.core_services.wiki_service import WikiService


@pytest.fixture
def temp_wiki_dir(tmp_path):
    """Provides a temporary directory for wiki files."""
    wiki_dir = tmp_path / "test_wiki"
    os.makedirs(wiki_dir, exist_ok=True)
    yield str(wiki_dir)
    shutil.rmtree(wiki_dir)  # Clean up after tests


@pytest.fixture
def wiki_service(temp_wiki_dir):
    """Provides a WikiService instance initialized with a temporary directory."""
    return WikiService(wiki_directory=temp_wiki_dir)


def test_create_entry_success(wiki_service, temp_wiki_dir):
    """Tests successful creation of a wiki entry."""
    entry_name = "TestEntry"
    content = "This is a test wiki entry."
    author = "TestAuthor"

    entry = wiki_service.create_entry(entry_name, content, author)
    assert entry is not None
    assert entry.entry_name == entry_name
    assert entry.content == content
    assert entry.version == "v1.0"
    assert entry.author == author

    # Verify directory and files are created
    entry_dir = Path(temp_wiki_dir) / entry_name
    assert entry_dir.is_dir()
    assert (entry_dir / "current.md").is_file()
    assert (entry_dir / "versions" / "v1.0.md").is_file()
    assert (entry_dir / "proposals").is_dir()

    assert (entry_dir / "current.md").read_text(encoding="utf-8") == content


def test_propose_edit_success(wiki_service, temp_wiki_dir):
    """Tests successful creation of an edit proposal."""
    entry_name = "EditableEntry"
    initial_content = "Original content."
    wiki_service.create_entry(entry_name, initial_content, "InitialAuthor")

    changes = {"diff": "line 1 changed", "new_content_snippet": "updated content"}
    author = "Proposer"

    success = wiki_service.propose_edit(entry_name, changes, author)
    assert success is True

    # Verify proposal file is created
    entry_dir = Path(temp_wiki_dir) / entry_name
    proposals_dir = entry_dir / "proposals"

    # Check if any .json file exists in proposals_dir
    proposal_files = list(proposals_dir.glob("proposal_*.json"))
    assert len(proposal_files) == 1

    # Load and verify content of the proposal file
    with open(proposal_files[0], encoding="utf-8") as f:
        proposal_data = json.load(f)

    assert "proposal_id" in proposal_data
    assert proposal_data["entry_name"] == entry_name
    assert proposal_data["author_role"] == author
    assert proposal_data["changes"] == changes
    assert proposal_data["status"] == "proposed"


def test_propose_edit_non_existent_entry(wiki_service):
    """Tests proposing an edit for a non-existent entry."""
    success = wiki_service.propose_edit(
        "NonExistentEntry", {"diff": "some change"}, "Author"
    )
    assert success is False


def test_create_entry_already_exists(wiki_service, temp_wiki_dir):
    """Tests creating an entry that already exists."""
    entry_name = "ExistingEntry"
    content = "Initial content."
    author = "Author1"
    wiki_service.create_entry(entry_name, content, author)

    # Attempt to create again
    new_entry = wiki_service.create_entry(entry_name, "New content.", "Author2")
    assert (
        new_entry is None
    )  # Should return None if creation fails due to existing entry

    # Verify content is still original
    entry_dir = Path(temp_wiki_dir) / entry_name
    assert (entry_dir / "current.md").read_text(encoding="utf-8") == content
