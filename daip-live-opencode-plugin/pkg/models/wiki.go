// Package models defines the data structures for DAIP-LIVE
package models

import (
	"encoding/json"
	"time"
)

// WikiPage represents a wiki page
type WikiPage struct {
	ID        string        `json:"id" db:"id"`
	Title     string        `json:"title" db:"title"`
	Content   string        `json:"content" db:"content"`
	Version   int           `json:"version" db:"version"`
	Sections  []WikiSection `json:"sections"`
	Metadata  WikiMetadata  `json:"metadata" db:"metadata"`
	Versions  []WikiVersion `json:"versions"`
	CreatedAt time.Time     `json:"created_at" db:"created_at"`
	UpdatedAt time.Time     `json:"updated_at" db:"updated_at"`
}

// WikiSection represents a section in a wiki page
type WikiSection struct {
	ID       string `json:"id" db:"id"`
	Title    string `json:"title" db:"title"`
	Content  string `json:"content" db:"content"`
	Level    int    `json:"level" db:"level"`
	Order    int    `json:"order" db:"order"`
	ParentID string `json:"parent_id" db:"parent_id"`
}

// WikiVersion represents a version of a wiki page
type WikiVersion struct {
	ID        string    `json:"id" db:"id"`
	Version   int       `json:"version" db:"version"`
	Content   string    `json:"content" db:"content"`
	Author    string    `json:"author" db:"author"`
	Timestamp time.Time `json:"timestamp" db:"timestamp"`
	Changes   string    `json:"changes" db:"changes"`
}

// WikiMetadata represents metadata for a wiki page
type WikiMetadata struct {
	Authors      []string          `json:"authors"`
	Tags         []string          `json:"tags"`
	RelatedPages []string          `json:"related_pages"`
	CustomFields map[string]string `json:"custom_fields"`
}

// ToJSON converts the page to JSON bytes
func (w *WikiPage) ToJSON() ([]byte, error) {
	return json.MarshalIndent(w, "", "  ")
}
