// Package storage provides SQLite storage for DAIP-LIVE
package storage

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/daip-live/daip-live-opencode-plugin/pkg/models"
	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
)

// SQLiteStorage provides SQLite-based storage
type SQLiteStorage struct {
	db   *sql.DB
	path string
}

// NewSQLiteStorage creates a new SQLite storage instance
func NewSQLiteStorage(storagePath string) (*SQLiteStorage, error) {
	// Create directory if it doesn't exist
	if err := os.MkdirAll(storagePath, 0755); err != nil {
		return nil, fmt.Errorf("failed to create storage directory: %w", err)
	}

	dbPath := filepath.Join(storagePath, "daip-live.db")
	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	store := &SQLiteStorage{
		db:   db,
		path: storagePath,
	}

	if err := store.initSchema(); err != nil {
		return nil, fmt.Errorf("failed to initialize schema: %w", err)
	}

	return store, nil
}

// Close closes the database connection
func (s *SQLiteStorage) Close() error {
	return s.db.Close()
}

// initSchema creates the database tables
func (s *SQLiteStorage) initSchema() error {
	queries := []string{
		// Debates table
		`CREATE TABLE IF NOT EXISTS debates (
			id TEXT PRIMARY KEY,
			topic TEXT NOT NULL,
			status TEXT DEFAULT 'active',
			total_rounds INTEGER DEFAULT 3,
			current_round INTEGER DEFAULT 0,
			participants TEXT,
			summary TEXT,
			conclusions TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,
		// Debate turns table
		`CREATE TABLE IF NOT EXISTS debate_turns (
			id TEXT PRIMARY KEY,
			session_id TEXT NOT NULL,
			round_number INTEGER NOT NULL,
			participant TEXT NOT NULL,
			content TEXT NOT NULL,
			content_length INTEGER,
			timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (session_id) REFERENCES debates(id)
		)`,
		// Wikis table
		`CREATE TABLE IF NOT EXISTS wikis (
			id TEXT PRIMARY KEY,
			title TEXT NOT NULL,
			content TEXT,
			version INTEGER DEFAULT 1,
			metadata TEXT,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,
		// Wiki versions table
		`CREATE TABLE IF NOT EXISTS wiki_versions (
			id TEXT PRIMARY KEY,
			wiki_id TEXT NOT NULL,
			version INTEGER NOT NULL,
			content TEXT NOT NULL,
			author TEXT,
			changes TEXT,
			timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (wiki_id) REFERENCES wikis(id)
		)`,
		// Knowledge concepts table
		`CREATE TABLE IF NOT EXISTS knowledge_concepts (
			id TEXT PRIMARY KEY,
			name TEXT NOT NULL,
			description TEXT,
			category TEXT,
			tags TEXT,
			count INTEGER DEFAULT 1,
			source_type TEXT,
			source_id TEXT,
			embedding BLOB,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,
		// Knowledge relations table
		`CREATE TABLE IF NOT EXISTS knowledge_relations (
			id TEXT PRIMARY KEY,
			source_id TEXT NOT NULL,
			target_id TEXT NOT NULL,
			relation_type TEXT,
			weight REAL DEFAULT 1.0,
			source_type TEXT,
			source_id_ref TEXT,
			FOREIGN KEY (source_id) REFERENCES knowledge_concepts(id),
			FOREIGN KEY (target_id) REFERENCES knowledge_concepts(id)
		)`,
		// Create indexes
		`CREATE INDEX IF NOT EXISTS idx_debate_turns_session ON debate_turns(session_id)`,
		`CREATE INDEX IF NOT EXISTS idx_wiki_versions_wiki ON wiki_versions(wiki_id)`,
		`CREATE INDEX IF NOT EXISTS idx_knowledge_name ON knowledge_concepts(name)`,
	}

	for _, query := range queries {
		if _, err := s.db.Exec(query); err != nil {
			return fmt.Errorf("failed to execute schema query: %w", err)
		}
	}

	return nil
}

// === Debate Operations ===

// SaveDebate saves a debate session
func (s *SQLiteStorage) SaveDebate(session *models.DebateSession) error {
	tx, err := s.db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()

	participantsJSON, _ := json.Marshal(session.Participants)
	conclusionsJSON, _ := json.Marshal(session.Conclusions)

	// Upsert debate
	query := `INSERT OR REPLACE INTO debates 
		(id, topic, status, total_rounds, current_round, participants, summary, conclusions, created_at, updated_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	now := time.Now()
	if session.CreatedAt.IsZero() {
		session.CreatedAt = now
	}
	session.UpdatedAt = now

	_, err = tx.Exec(query,
		session.ID, session.Topic, session.Status, session.TotalRounds, session.CurrentRound,
		string(participantsJSON), session.Summary, string(conclusionsJSON),
		session.CreatedAt, session.UpdatedAt)
	if err != nil {
		return err
	}

	// Delete existing turns
	if _, err := tx.Exec("DELETE FROM debate_turns WHERE session_id = ?", session.ID); err != nil {
		return err
	}

	// Insert turns
	for _, turn := range session.Turns {
		if _, err := tx.Exec(`INSERT INTO debate_turns 
			(id, session_id, round_number, participant, content, content_length, timestamp)
			VALUES (?, ?, ?, ?, ?, ?, ?)`,
			turn.ID, turn.SessionID, turn.RoundNumber, turn.Participant,
			turn.Content, turn.ContentLength, turn.Timestamp); err != nil {
			return err
		}
	}

	return tx.Commit()
}

// GetDebate retrieves a debate session by ID
func (s *SQLiteStorage) GetDebate(sessionID string) (*models.DebateSession, error) {
	var session models.DebateSession
	var participantsJSON, conclusionsJSON string

	err := s.db.QueryRow(`SELECT id, topic, status, total_rounds, current_round, 
		participants, summary, conclusions, created_at, updated_at
		FROM debates WHERE id = ?`, sessionID).Scan(
		&session.ID, &session.Topic, &session.Status, &session.TotalRounds, &session.CurrentRound,
		&participantsJSON, &session.Summary, &conclusionsJSON,
		&session.CreatedAt, &session.UpdatedAt)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}

	json.Unmarshal([]byte(participantsJSON), &session.Participants)
	json.Unmarshal([]byte(conclusionsJSON), &session.Conclusions)

	// Get turns
	rows, err := s.db.Query(`SELECT id, session_id, round_number, participant, content, 
		content_length, timestamp FROM debate_turns WHERE session_id = ? ORDER BY round_number, timestamp`,
		sessionID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var turn models.DebateTurn
		if err := rows.Scan(&turn.ID, &turn.SessionID, &turn.RoundNumber, &turn.Participant,
			&turn.Content, &turn.ContentLength, &turn.Timestamp); err != nil {
			return nil, err
		}
		session.Turns = append(session.Turns, turn)
	}

	return &session, nil
}

// ListDebates lists all debates with optional limit
func (s *SQLiteStorage) ListDebates(limit int) ([]*models.DebateSession, error) {
	query := `SELECT id, topic, status, total_rounds, current_round, 
		participants, summary, conclusions, created_at, updated_at
		FROM debates ORDER BY created_at DESC`

	if limit > 0 {
		query += fmt.Sprintf(" LIMIT %d", limit)
	}

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var sessions []*models.DebateSession
	for rows.Next() {
		var session models.DebateSession
		var participantsJSON, conclusionsJSON string

		if err := rows.Scan(&session.ID, &session.Topic, &session.Status, &session.TotalRounds, &session.CurrentRound,
			&participantsJSON, &session.Summary, &conclusionsJSON,
			&session.CreatedAt, &session.UpdatedAt); err != nil {
			return nil, err
		}

		json.Unmarshal([]byte(participantsJSON), &session.Participants)
		json.Unmarshal([]byte(conclusionsJSON), &session.Conclusions)
		sessions = append(sessions, &session)
	}

	return sessions, nil
}

// === Wiki Operations ===

// SaveWiki saves a wiki page
func (s *SQLiteStorage) SaveWiki(page *models.WikiPage) error {
	metadataJSON, _ := json.Marshal(page.Metadata)

	now := time.Now()
	if page.CreatedAt.IsZero() {
		page.CreatedAt = now
	}
	page.UpdatedAt = now

	query := `INSERT OR REPLACE INTO wikis 
		(id, title, content, version, metadata, created_at, updated_at)
		VALUES (?, ?, ?, ?, ?, ?, ?)`

	_, err := s.db.Exec(query,
		page.ID, page.Title, page.Content, page.Version, string(metadataJSON),
		page.CreatedAt, page.UpdatedAt)
	return err
}

// GetWiki retrieves a wiki page by ID
func (s *SQLiteStorage) GetWiki(pageID string) (*models.WikiPage, error) {
	var page models.WikiPage
	var metadataJSON string

	err := s.db.QueryRow(`SELECT id, title, content, version, metadata, created_at, updated_at
		FROM wikis WHERE id = ?`, pageID).Scan(
		&page.ID, &page.Title, &page.Content, &page.Version, &metadataJSON,
		&page.CreatedAt, &page.UpdatedAt)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}

	json.Unmarshal([]byte(metadataJSON), &page.Metadata)
	return &page, nil
}

// ListWikis lists all wiki pages
func (s *SQLiteStorage) ListWikis() ([]*models.WikiPage, error) {
	rows, err := s.db.Query(`SELECT id, title, content, version, metadata, created_at, updated_at
		FROM wikis ORDER BY updated_at DESC`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var pages []*models.WikiPage
	for rows.Next() {
		var page models.WikiPage
		var metadataJSON string

		if err := rows.Scan(&page.ID, &page.Title, &page.Content, &page.Version, &metadataJSON,
			&page.CreatedAt, &page.UpdatedAt); err != nil {
			return nil, err
		}

		json.Unmarshal([]byte(metadataJSON), &page.Metadata)
		pages = append(pages, &page)
	}

	return pages, nil
}

// SaveWikiVersion saves a wiki version
func (s *SQLiteStorage) SaveWikiVersion(pageID string, version *models.WikiVersion) error {
	query := `INSERT INTO wiki_versions 
		(id, wiki_id, version, content, author, changes, timestamp)
		VALUES (?, ?, ?, ?, ?, ?, ?)`

	_, err := s.db.Exec(query,
		version.ID, pageID, version.Version, version.Content,
		version.Author, version.Changes, version.Timestamp)
	return err
}

// === Knowledge Operations ===

// SaveKnowledgeConcept saves a knowledge concept
func (s *SQLiteStorage) SaveKnowledgeConcept(concept *models.KnowledgeConcept) error {
	tagsJSON, _ := json.Marshal(concept.Tags)

	query := `INSERT OR REPLACE INTO knowledge_concepts 
		(id, name, description, category, tags, count, source_type, source_id, created_at, updated_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	now := time.Now()
	if concept.ID == "" {
		concept.ID = generateID()
	}
	if concept.CreatedAt.IsZero() {
		concept.CreatedAt = now
	}
	concept.UpdatedAt = now

	_, err := s.db.Exec(query,
		concept.ID, concept.Name, concept.Description, concept.Category, string(tagsJSON),
		concept.Count, concept.SourceType, concept.SourceID,
		concept.CreatedAt, concept.UpdatedAt)
	return err
}

// GetKnowledgeConcept retrieves a knowledge concept by ID
func (s *SQLiteStorage) GetKnowledgeConcept(conceptID string) (*models.KnowledgeConcept, error) {
	var concept models.KnowledgeConcept
	var tagsJSON string

	err := s.db.QueryRow(`SELECT id, name, description, category, tags, count, source_type, source_id, created_at, updated_at
		FROM knowledge_concepts WHERE id = ?`, conceptID).Scan(
		&concept.ID, &concept.Name, &concept.Description, &concept.Category, &tagsJSON,
		&concept.Count, &concept.SourceType, &concept.SourceID,
		&concept.CreatedAt, &concept.UpdatedAt)

	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}

	json.Unmarshal([]byte(tagsJSON), &concept.Tags)
	return &concept, nil
}

// SaveKnowledgeRelation saves a knowledge relation
func (s *SQLiteStorage) SaveKnowledgeRelation(relation *models.KnowledgeRelation) error {
	query := `INSERT OR REPLACE INTO knowledge_relations 
		(id, source_id, target_id, relation_type, weight, source_type, source_id_ref)
		VALUES (?, ?, ?, ?, ?, ?, ?)`

	if relation.ID == "" {
		relation.ID = generateID()
	}

	_, err := s.db.Exec(query,
		relation.ID, relation.SourceID, relation.TargetID, relation.RelationType,
		relation.Weight, relation.SourceType, relation.SourceID)
	return err
}

// SearchKnowledgeConcepts searches knowledge concepts by name or description
func (s *SQLiteStorage) SearchKnowledgeConcepts(query string, limit int) ([]*models.KnowledgeConcept, error) {
	searchQuery := `%` + query + `%`
	sql := `SELECT id, name, description, category, tags, count, source_type, source_id, created_at, updated_at
		FROM knowledge_concepts WHERE name LIKE ? OR description LIKE ? ORDER BY count DESC`

	if limit > 0 {
		sql += fmt.Sprintf(" LIMIT %d", limit)
	}

	rows, err := s.db.Query(sql, searchQuery, searchQuery)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var concepts []*models.KnowledgeConcept
	for rows.Next() {
		var concept models.KnowledgeConcept
		var tagsJSON string

		if err := rows.Scan(&concept.ID, &concept.Name, &concept.Description, &concept.Category, &tagsJSON,
			&concept.Count, &concept.SourceType, &concept.SourceID,
			&concept.CreatedAt, &concept.UpdatedAt); err != nil {
			return nil, err
		}

		json.Unmarshal([]byte(tagsJSON), &concept.Tags)
		concepts = append(concepts, &concept)
	}

	return concepts, nil
}

// generateID generates a new UUID
func generateID() string {
	return uuid.New().String()
}
