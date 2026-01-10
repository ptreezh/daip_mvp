// Package models defines the data structures for DAIP-LIVE
package models

import (
	"encoding/json"
	"time"
)

// KnowledgeGraph represents the knowledge graph
type KnowledgeGraph struct {
	ID        string              `json:"id" db:"id"`
	Concepts  []KnowledgeConcept  `json:"concepts"`
	Relations []KnowledgeRelation `json:"relations"`
	Sources   []string            `json:"sources"`
	Version   int                 `json:"version" db:"version"`
	CreatedAt time.Time           `json:"created_at" db:"created_at"`
	UpdatedAt time.Time           `json:"updated_at" db:"updated_at"`
}

// KnowledgeConcept represents a concept in the knowledge graph
type KnowledgeConcept struct {
	ID          string    `json:"id" db:"id"`
	Name        string    `json:"name" db:"name"`
	Description string    `json:"description" db:"description"`
	Category    string    `json:"category" db:"category"`
	Tags        []string  `json:"tags"`
	Count       int       `json:"count" db:"count"`
	SourceType  string    `json:"source_type" db:"source_type"`
	SourceID    string    `json:"source_id" db:"source_id"`
	Embedding   []float32 `json:"embedding,omitempty"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`
}

// KnowledgeRelation represents a relation between concepts
type KnowledgeRelation struct {
	ID           string  `json:"id" db:"id"`
	SourceID     string  `json:"source_id" db:"source_id"`
	TargetID     string  `json:"target_id" db:"target_id"`
	RelationType string  `json:"relation_type" db:"relation_type"`
	Weight       float32 `json:"weight" db:"weight"`
	SourceType   string  `json:"source_type" db:"source_type"`
	SourceIDRef  string  `json:"source_id_ref" db:"source_id_ref"`
}

// KnowledgeSearchResult represents a search result
type KnowledgeSearchResult struct {
	Concept   KnowledgeConcept `json:"concept"`
	Score     float32          `json:"score"`
	Highlight string           `json:"highlight"`
}

// ToJSON converts the graph to JSON bytes
func (k *KnowledgeGraph) ToJSON() ([]byte, error) {
	return json.MarshalIndent(k, "", "  ")
}
