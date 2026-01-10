// Package models defines the data structures for DAIP-LIVE
package models

import (
	"encoding/json"
	"time"
)

// DebateSession represents a debate session
type DebateSession struct {
	ID           string       `json:"id" db:"id"`
	Topic        string       `json:"topic" db:"topic"`
	Status       DebateStatus `json:"status" db:"status"`
	Participants []DebateRole `json:"participants"`
	TotalRounds  int          `json:"total_rounds" db:"total_rounds"`
	CurrentRound int          `json:"current_round" db:"current_round"`
	Turns        []DebateTurn `json:"turns"`
	Summary      string       `json:"summary" db:"summary"`
	Conclusions  []string     `json:"conclusions"`
	CreatedAt    time.Time    `json:"created_at" db:"created_at"`
	UpdatedAt    time.Time    `json:"updated_at" db:"updated_at"`
}

// DebateStatus represents the status of a debate session
type DebateStatus string

const (
	DebateStatusActive    DebateStatus = "active"
	DebateStatusCompleted DebateStatus = "completed"
	DebateStatusPaused    DebateStatus = "paused"
	DebateStatusCancelled DebateStatus = "cancelled"
)

// DebateRole represents a participant in a debate
type DebateRole struct {
	Name         string `json:"name"`
	Model        string `json:"model"`
	SystemPrompt string `json:"system_prompt"`
	Color        string `json:"color"`
}

// DebateTurn represents a single turn in a debate
type DebateTurn struct {
	ID            string    `json:"id" db:"id"`
	SessionID     string    `json:"session_id" db:"session_id"`
	RoundNumber   int       `json:"round_number" db:"round_number"`
	Participant   string    `json:"participant" db:"participant"`
	Content       string    `json:"content" db:"content"`
	ContentLength int       `json:"content_length"`
	Timestamp     time.Time `json:"timestamp" db:"timestamp"`
}

// DebateConfig represents configuration for a debate
type DebateConfig struct {
	MaxRounds   int               `json:"max_rounds"`
	Roles       []string          `json:"roles"`
	Models      map[string]string `json:"models"`
	AutoSummary bool              `json:"auto_summary"`
}

// ToJSON converts the session to JSON bytes
func (s *DebateSession) ToJSON() ([]byte, error) {
	return json.MarshalIndent(s, "", "  ")
}
