package storage

import (
	"testing"
	"time"

	"github.com/daip-live/daip-live-opencode-plugin/pkg/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestMemoryStorage(t *testing.T) {
	// Create memory storage instance for tests that need it
	// Each subtest will create its own instance to avoid interference

	t.Run("Debate Operations", func(t *testing.T) {
		// Create memory storage instance
		storage := NewMemoryStorage()

		// Test saving a debate
		session := &models.DebateSession{
			ID:           "test-session-1",
			Topic:        "AI Ethics",
			Status:       models.DebateStatusActive,
			TotalRounds:  3,
			CurrentRound: 1,
			Participants: []models.DebateRole{
				{Name: "proponent", Model: "test-model", SystemPrompt: "Proponent prompt", Color: "blue"},
				{Name: "opponent", Model: "test-model", SystemPrompt: "Opponent prompt", Color: "red"},
				{Name: "moderator", Model: "test-model", SystemPrompt: "Moderator prompt", Color: "green"},
			},
			Summary:     "Initial summary",
			Conclusions: []string{"Conclusion 1", "Conclusion 2"},
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
			Turns: []models.DebateTurn{
				{
					ID:            "turn-1",
					SessionID:     "test-session-1",
					RoundNumber:   1,
					Participant:   "proponent",
					Content:       "Pro argument",
					ContentLength: len("Pro argument"),
					Timestamp:     time.Now(),
				},
			},
		}

		// Save debate session
		err := storage.SaveDebate(session)
		require.NoError(t, err)

		// Get debate session
		retrieved, err := storage.GetDebate("test-session-1")
		require.NoError(t, err)
		require.NotNil(t, retrieved)

		assert.Equal(t, "AI Ethics", retrieved.Topic)
		assert.Equal(t, models.DebateStatusActive, retrieved.Status)
		assert.Equal(t, 3, retrieved.TotalRounds)
		assert.Equal(t, 1, retrieved.CurrentRound)
		assert.Len(t, retrieved.Participants, 3)
		assert.Equal(t, "Initial summary", retrieved.Summary)
		assert.Equal(t, []string{"Conclusion 1", "Conclusion 2"}, retrieved.Conclusions)
		assert.Len(t, retrieved.Turns, 1)
		assert.Equal(t, "Pro argument", retrieved.Turns[0].Content)
	})

	t.Run("Wiki Operations", func(t *testing.T) {
		// Create memory storage instance
		storage := NewMemoryStorage()

		// Test saving a wiki page
		page := &models.WikiPage{
			ID:      "test-wiki-1",
			Title:   "Test Wiki Page",
			Content: "This is a test wiki page content",
			Version: 1,
			Metadata: models.WikiMetadata{
				Authors:      []string{"test-author"},
				Tags:         []string{"test", "wiki"},
				RelatedPages: []string{},
				CustomFields: map[string]string{
					"author": "test-author",
				},
			},
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		}

		// Save wiki page
		err := storage.SaveWiki(page)
		require.NoError(t, err)

		// Get wiki page
		retrieved, err := storage.GetWiki("test-wiki-1")
		require.NoError(t, err)
		require.NotNil(t, retrieved)

		assert.Equal(t, "Test Wiki Page", retrieved.Title)
		assert.Equal(t, "This is a test wiki page content", retrieved.Content)
		assert.Equal(t, 1, retrieved.Version)
		assert.Contains(t, retrieved.Metadata.Authors, "test-author")
		assert.Contains(t, retrieved.Metadata.Tags, "test")
		assert.Contains(t, retrieved.Metadata.Tags, "wiki")
	})

	t.Run("Knowledge Operations", func(t *testing.T) {
		// Create memory storage instance
		storage := NewMemoryStorage()

		// Test saving a knowledge concept
		concept := &models.KnowledgeConcept{
			Name:        "test-concept",
			Description: "A test concept",
			Category:    "test-category",
			Tags:        []string{"test", "concept"},
			SourceType:  "test-source",
			SourceID:    "test-source-id",
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		}

		// Save knowledge concept
		err := storage.SaveKnowledgeConcept(concept)
		require.NoError(t, err)

		// Get knowledge concept
		retrieved, err := storage.GetKnowledgeConcept(concept.ID)
		require.NoError(t, err)
		require.NotNil(t, retrieved)

		assert.Equal(t, "test-concept", retrieved.Name)
		assert.Equal(t, "A test concept", retrieved.Description)
		assert.Equal(t, "test-category", retrieved.Category)
		assert.Contains(t, retrieved.Tags, "test")
		assert.Contains(t, retrieved.Tags, "concept")
	})

	t.Run("List Operations", func(t *testing.T) {
		// Create memory storage instance
		storage := NewMemoryStorage()

		// Test listing debates
		debates, err := storage.ListDebates(10)
		require.NoError(t, err)
		assert.NotEmpty(t, debates)

		// Test listing wikis
		wikis, err := storage.ListWikis()
		require.NoError(t, err)
		assert.NotEmpty(t, wikis)
	})
}