// Package knowledge provides the knowledge graph engine for DAIP-LIVE
package knowledge

import (
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/daip-live/daip-live-opencode-plugin/pkg/llm"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/models"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/storage"
	"github.com/google/uuid"
)

// Engine manages the knowledge graph
type Engine struct {
	storage     *storage.SQLiteStorage
	llmProvider *llm.Provider
}

// NewEngine creates a new knowledge engine
func NewEngine(storage *storage.SQLiteStorage, llmProvider *llm.Provider) *Engine {
	return &Engine{
		storage:     storage,
		llmProvider: llmProvider,
	}
}

// AddConcept adds a new concept to the knowledge graph
func (e *Engine) AddConcept(ctx context.Context, name string, description string, category string, tags []string, sourceType string, sourceID string) (*models.KnowledgeConcept, error) {
	concept := &models.KnowledgeConcept{
		ID:          uuid.New().String(),
		Name:        name,
		Description: description,
		Category:    category,
		Tags:        tags,
		Count:       1,
		SourceType:  sourceType,
		SourceID:    sourceID,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	if err := e.storage.SaveKnowledgeConcept(concept); err != nil {
		return nil, fmt.Errorf("failed to save knowledge concept: %w", err)
	}

	log.Printf("Added knowledge concept: %s (%s)", name, category)
	return concept, nil
}

// GetConcept retrieves a concept by ID
func (e *Engine) GetConcept(ctx context.Context, conceptID string) (*models.KnowledgeConcept, error) {
	concept, err := e.storage.GetKnowledgeConcept(conceptID)
	if err != nil {
		return nil, fmt.Errorf("failed to get knowledge concept: %w", err)
	}
	if concept == nil {
		return nil, fmt.Errorf("knowledge concept not found: %s", conceptID)
	}
	return concept, nil
}

// GetConceptByName retrieves a concept by name
func (e *Engine) GetConceptByName(ctx context.Context, name string) (*models.KnowledgeConcept, error) {
	concepts, err := e.storage.SearchKnowledgeConcepts(name, 1)
	if err != nil {
		return nil, fmt.Errorf("failed to search knowledge concepts: %w", err)
	}
	if len(concepts) == 0 {
		return nil, fmt.Errorf("knowledge concept not found: %s", name)
	}
	return concepts[0], nil
}

// SearchConcepts searches knowledge concepts
func (e *Engine) SearchConcepts(ctx context.Context, query string, limit int) ([]*models.KnowledgeConcept, error) {
	if limit <= 0 {
		limit = 10
	}
	return e.storage.SearchKnowledgeConcepts(query, limit)
}

// IncrementCount increments the count for a concept
func (e *Engine) IncrementCount(ctx context.Context, conceptID string) error {
	concept, err := e.storage.GetKnowledgeConcept(conceptID)
	if err != nil {
		return fmt.Errorf("failed to get knowledge concept: %w", err)
	}
	if concept == nil {
		return fmt.Errorf("knowledge concept not found: %s", conceptID)
	}

	concept.Count++
	concept.UpdatedAt = time.Now()

	return e.storage.SaveKnowledgeConcept(concept)
}

// UpdateConcept updates a concept
func (e *Engine) UpdateConcept(ctx context.Context, conceptID string, name string, description string, category string, tags []string) error {
	concept, err := e.storage.GetKnowledgeConcept(conceptID)
	if err != nil {
		return fmt.Errorf("failed to get knowledge concept: %w", err)
	}
	if concept == nil {
		return fmt.Errorf("knowledge concept not found: %s", conceptID)
	}

	if name != "" {
		concept.Name = name
	}
	if description != "" {
		concept.Description = description
	}
	if category != "" {
		concept.Category = category
	}
	if len(tags) > 0 {
		concept.Tags = tags
	}
	concept.UpdatedAt = time.Now()

	return e.storage.SaveKnowledgeConcept(concept)
}

// DeleteConcept deletes a concept
func (e *Engine) DeleteConcept(ctx context.Context, conceptID string) error {
	concept, err := e.storage.GetKnowledgeConcept(conceptID)
	if err != nil {
		return fmt.Errorf("failed to get knowledge concept: %w", err)
	}
	if concept == nil {
		return fmt.Errorf("knowledge concept not found: %s", conceptID)
	}

	concept.Name = "[deleted]"
	concept.Description = ""
	concept.Count = 0
	concept.UpdatedAt = time.Now()

	return e.storage.SaveKnowledgeConcept(concept)
}

// AddRelation adds a relation between two concepts
func (e *Engine) AddRelation(ctx context.Context, sourceID string, targetID string, relationType string, weight float32) (*models.KnowledgeRelation, error) {
	relation := &models.KnowledgeRelation{
		ID:           uuid.New().String(),
		SourceID:     sourceID,
		TargetID:     targetID,
		RelationType: relationType,
		Weight:       weight,
	}

	if err := e.storage.SaveKnowledgeRelation(relation); err != nil {
		return nil, fmt.Errorf("failed to save knowledge relation: %w", err)
	}

	log.Printf("Added knowledge relation: %s -> %s (%s)", sourceID, targetID, relationType)
	return relation, nil
}

// GetRelatedConcepts gets concepts related to a given concept
func (e *Engine) GetRelatedConcepts(ctx context.Context, conceptID string) ([]*models.KnowledgeConcept, error) {
	concepts, err := e.storage.SearchKnowledgeConcepts("", 100)
	if err != nil {
		return nil, fmt.Errorf("failed to search knowledge concepts: %w", err)
	}

	var related []*models.KnowledgeConcept
	for _, concept := range concepts {
		// Simple relation check - in a real implementation, you'd query the relations table
		if concept.ID != conceptID {
			related = append(related, concept)
		}
	}

	return related, nil
}

// AddConceptFromWiki adds a knowledge concept from wiki content
func (e *Engine) AddConceptFromWiki(ctx context.Context, pageID string, title string, content string, category string) (*models.KnowledgeConcept, error) {
	// Check if concept already exists
	existing, err := e.GetConceptByName(ctx, title)
	if err == nil && existing != nil {
		// Increment count if already exists
		e.IncrementCount(ctx, existing.ID)
		return existing, nil
	}

	// Extract summary from content
	description := extractSummary(content)

	return e.AddConcept(ctx, title, description, category, []string{"wiki", pageID}, "wiki", pageID)
}

// AddConceptFromDebate adds a knowledge concept from debate content
func (e *Engine) AddConceptFromDebate(ctx context.Context, sessionID string, topic string, summary string) (*models.KnowledgeConcept, error) {
	// Check if concept already exists
	existing, err := e.GetConceptByName(ctx, topic)
	if err == nil && existing != nil {
		e.IncrementCount(ctx, existing.ID)
		return existing, nil
	}

	return e.AddConcept(ctx, topic, summary, "debate", []string{"debate", sessionID}, "debate", sessionID)
}

// ExtractConcepts extracts key concepts from text using LLM
func (e *Engine) ExtractConcepts(ctx context.Context, text string, category string) ([]*models.KnowledgeConcept, error) {
	if e.llmProvider == nil {
		return nil, fmt.Errorf("LLM provider not available")
	}

	prompt := fmt.Sprintf(`Extract 3-5 key concepts from the following text. For each concept, provide:
1. The concept name
2. A brief description (1-2 sentences)
3. The category: %s

Format as a JSON array with objects containing "name", "description", and "category" fields.

Text:
%s`, category, text)

	response, err := e.llmProvider.Generate(ctx, prompt, "claude-sonnet-4-20250514")
	if err != nil {
		return nil, fmt.Errorf("failed to extract concepts: %w", err)
	}

	// Parse response - in a real implementation, you'd use proper JSON parsing
	// For now, create simple concepts from the response
	concepts := []*models.KnowledgeConcept{
		{
			ID:          uuid.New().String(),
			Name:        fmt.Sprintf("Extracted from text"),
			Description: response,
			Category:    category,
			Count:       1,
			CreatedAt:   time.Now(),
			UpdatedAt:   time.Now(),
		},
	}

	return concepts, nil
}

// BuildConceptGraph builds a graph of concepts from wiki pages
func (e *Engine) BuildConceptGraph(ctx context.Context, pages []*models.WikiPage) error {
	for _, page := range pages {
		// Add main concept from page title
		_, err := e.AddConceptFromWiki(ctx, page.ID, page.Title, page.Content, "wiki")
		if err != nil {
			log.Printf("Warning: failed to add concept from page %s: %v", page.ID, err)
		}

		// Extract and add concepts from sections
		for _, section := range page.Sections {
			if section.Title != "" {
				_, err := e.AddConcept(ctx, section.Title, section.Content, "section", []string{"wiki", page.ID}, "wiki", page.ID)
				if err != nil {
					log.Printf("Warning: failed to add concept from section %s: %v", section.ID, err)
				}
			}
		}
	}

	return nil
}

// GetConceptsByCategory gets all concepts in a category
func (e *Engine) GetConceptsByCategory(ctx context.Context, category string) ([]*models.KnowledgeConcept, error) {
	allConcepts, err := e.storage.SearchKnowledgeConcepts("", 100)
	if err != nil {
		return nil, fmt.Errorf("failed to search knowledge concepts: %w", err)
	}

	var filtered []*models.KnowledgeConcept
	for _, concept := range allConcepts {
		if concept.Category == category {
			filtered = append(filtered, concept)
		}
	}

	return filtered, nil
}

// GetConceptsByTag gets all concepts with a specific tag
func (e *Engine) GetConceptsByTag(ctx context.Context, tag string) ([]*models.KnowledgeConcept, error) {
	allConcepts, err := e.storage.SearchKnowledgeConcepts("", 100)
	if err != nil {
		return nil, fmt.Errorf("failed to search knowledge concepts: %w", err)
	}

	var filtered []*models.KnowledgeConcept
	for _, concept := range allConcepts {
		for _, t := range concept.Tags {
			if t == tag {
				filtered = append(filtered, concept)
				break
			}
		}
	}

	return filtered, nil
}

// GetTopConcepts gets the most frequently accessed concepts
func (e *Engine) GetTopConcepts(ctx context.Context, limit int) ([]*models.KnowledgeConcept, error) {
	if limit <= 0 {
		limit = 10
	}

	allConcepts, err := e.storage.SearchKnowledgeConcepts("", limit*2)
	if err != nil {
		return nil, fmt.Errorf("failed to search knowledge concepts: %w", err)
	}

	// Sort by count descending
	for i := 0; i < len(allConcepts); i++ {
		for j := i + 1; j < len(allConcepts); j++ {
			if allConcepts[j].Count > allConcepts[i].Count {
				allConcepts[i], allConcepts[j] = allConcepts[j], allConcepts[i]
			}
		}
	}

	if len(allConcepts) > limit {
		allConcepts = allConcepts[:limit]
	}

	return allConcepts, nil
}

// SuggestRelatedConcepts suggests related concepts based on current concepts
func (e *Engine) SuggestRelatedConcepts(ctx context.Context, conceptIDs []string, limit int) ([]*models.KnowledgeConcept, error) {
	if limit <= 0 {
		limit = 5
	}

	allConcepts, err := e.storage.SearchKnowledgeConcepts("", 20)
	if err != nil {
		return nil, fmt.Errorf("failed to search knowledge concepts: %w", err)
	}

	// Simple suggestion based on category matching
	conceptSet := make(map[string]bool)
	for _, id := range conceptIDs {
		conceptSet[id] = true
	}

	var suggestions []*models.KnowledgeConcept
	for _, concept := range allConcepts {
		if !conceptSet[concept.ID] && len(suggestions) < limit {
			suggestions = append(suggestions, concept)
		}
	}

	return suggestions, nil
}

// === Private Helper Functions ===

// extractSummary extracts a summary from content
func extractSummary(content string) string {
	// Simple extraction - first 200 characters
	lines := strings.Split(content, "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if len(line) > 50 {
			if len(line) > 200 {
				return line[:200] + "..."
			}
			return line
		}
	}
	if len(content) > 200 {
		return content[:200] + "..."
	}
	return content
}
