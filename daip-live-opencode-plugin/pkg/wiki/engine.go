// Package wiki provides the wiki engine for DAIP-LIVE
package wiki

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

// Engine manages wiki pages and collaboration
type Engine struct {
	storage     *storage.SQLiteStorage
	llmProvider *llm.Provider
}

// NewEngine creates a new wiki engine
func NewEngine(storage *storage.SQLiteStorage, llmProvider *llm.Provider) *Engine {
	return &Engine{
		storage:     storage,
		llmProvider: llmProvider,
	}
}

// CreatePage creates a new wiki page
func (e *Engine) CreatePage(ctx context.Context, title string, content string, author string, tags []string) (*models.WikiPage, error) {
	page := &models.WikiPage{
		ID:       uuid.New().String(),
		Title:    title,
		Content:  content,
		Version:  1,
		Sections: []models.WikiSection{},
		Metadata: models.WikiMetadata{
			Authors:      []string{author},
			Tags:         tags,
			RelatedPages: []string{},
			CustomFields: make(map[string]string),
		},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	// Parse sections from content
	page.Sections = e.parseSections(content)

	// Save to storage
	if err := e.storage.SaveWiki(page); err != nil {
		return nil, fmt.Errorf("failed to save wiki page: %w", err)
	}

	// Save initial version
	version := &models.WikiVersion{
		Version:   1,
		Content:   content,
		Author:    author,
		Timestamp: time.Now(),
		Changes:   "Initial version",
	}
	if err := e.storage.SaveWikiVersion(page.ID, version); err != nil {
		log.Printf("Warning: failed to save wiki version: %v", err)
	}

	log.Printf("Created wiki page %s: %s", page.ID, title)
	return page, nil
}

// GetPage retrieves a wiki page by ID
func (e *Engine) GetPage(ctx context.Context, pageID string) (*models.WikiPage, error) {
	page, err := e.storage.GetWiki(pageID)
	if err != nil {
		return nil, fmt.Errorf("failed to get wiki page: %w", err)
	}
	if page == nil {
		return nil, fmt.Errorf("wiki page not found: %s", pageID)
	}

	// Parse sections
	page.Sections = e.parseSections(page.Content)

	return page, nil
}

// GetPageByTitle retrieves a wiki page by title
func (e *Engine) GetPageByTitle(ctx context.Context, title string) (*models.WikiPage, error) {
	pages, err := e.storage.ListWikis()
	if err != nil {
		return nil, fmt.Errorf("failed to list wiki pages: %w", err)
	}

	for _, page := range pages {
		if page.Title == title {
			page.Sections = e.parseSections(page.Content)
			return page, nil
		}
	}

	return nil, fmt.Errorf("wiki page not found: %s", title)
}

// ListPages lists all wiki pages
func (e *Engine) ListPages(ctx context.Context) ([]*models.WikiPage, error) {
	pages, err := e.storage.ListWikis()
	if err != nil {
		return nil, fmt.Errorf("failed to list wiki pages: %w", err)
	}

	// Parse sections for each page
	for _, page := range pages {
		page.Sections = e.parseSections(page.Content)
	}

	return pages, nil
}

// UpdatePage updates an existing wiki page
func (e *Engine) UpdatePage(ctx context.Context, pageID string, content string, author string, changes string) (*models.WikiPage, error) {
	page, err := e.storage.GetWiki(pageID)
	if err != nil {
		return nil, fmt.Errorf("failed to get wiki page: %w", err)
	}
	if page == nil {
		return nil, fmt.Errorf("wiki page not found: %s", pageID)
	}

	// Save old version
	oldVersion := &models.WikiVersion{
		Version:   page.Version,
		Content:   page.Content,
		Author:    page.Metadata.Authors[len(page.Metadata.Authors)-1],
		Timestamp: page.UpdatedAt,
		Changes:   changes,
	}
	if err := e.storage.SaveWikiVersion(page.ID, oldVersion); err != nil {
		log.Printf("Warning: failed to save wiki version: %v", err)
	}

	// Update page
	page.Content = content
	page.Version++
	page.Sections = e.parseSections(content)
	page.UpdatedAt = time.Now()

	// Update authors
	page.Metadata.Authors = append(page.Metadata.Authors, author)

	// Save to storage
	if err := e.storage.SaveWiki(page); err != nil {
		return nil, fmt.Errorf("failed to save wiki page: %w", err)
	}

	// Save new version
	newVersion := &models.WikiVersion{
		Version:   page.Version,
		Content:   content,
		Author:    author,
		Timestamp: time.Now(),
		Changes:   changes,
	}
	if err := e.storage.SaveWikiVersion(page.ID, newVersion); err != nil {
		log.Printf("Warning: failed to save wiki version: %v", err)
	}

	log.Printf("Updated wiki page %s to version %d", pageID, page.Version)
	return page, nil
}

// UpdatePageTitle updates the title of a wiki page
func (e *Engine) UpdatePageTitle(ctx context.Context, pageID string, newTitle string) error {
	page, err := e.storage.GetWiki(pageID)
	if err != nil {
		return fmt.Errorf("failed to get wiki page: %w", err)
	}
	if page == nil {
		return fmt.Errorf("wiki page not found: %s", pageID)
	}

	page.Title = newTitle
	page.UpdatedAt = time.Now()

	return e.storage.SaveWiki(page)
}

// DeletePage deletes a wiki page
func (e *Engine) DeletePage(ctx context.Context, pageID string) error {
	page, err := e.storage.GetWiki(pageID)
	if err != nil {
		return fmt.Errorf("failed to get wiki page: %w", err)
	}
	if page == nil {
		return fmt.Errorf("wiki page not found: %s", pageID)
	}

	// For now, we just set content to empty as a soft delete
	page.Content = ""
	page.UpdatedAt = time.Now()

	return e.storage.SaveWiki(page)
}

// AddTag adds a tag to a wiki page
func (e *Engine) AddTag(ctx context.Context, pageID string, tag string) error {
	page, err := e.storage.GetWiki(pageID)
	if err != nil {
		return fmt.Errorf("failed to get wiki page: %w", err)
	}
	if page == nil {
		return fmt.Errorf("wiki page not found: %s", pageID)
	}

	// Add tag if not exists
	for _, t := range page.Metadata.Tags {
		if t == tag {
			return nil // Tag already exists
		}
	}
	page.Metadata.Tags = append(page.Metadata.Tags, tag)
	page.UpdatedAt = time.Now()

	return e.storage.SaveWiki(page)
}

// RemoveTag removes a tag from a wiki page
func (e *Engine) RemoveTag(ctx context.Context, pageID string, tag string) error {
	page, err := e.storage.GetWiki(pageID)
	if err != nil {
		return fmt.Errorf("failed to get wiki page: %w", err)
	}
	if page == nil {
		return fmt.Errorf("wiki page not found: %s", pageID)
	}

	// Remove tag
	newTags := []string{}
	for _, t := range page.Metadata.Tags {
		if t != tag {
			newTags = append(newTags, t)
		}
	}
	page.Metadata.Tags = newTags
	page.UpdatedAt = time.Now()

	return e.storage.SaveWiki(page)
}

// LinkPages creates a link between two wiki pages
func (e *Engine) LinkPages(ctx context.Context, pageID1 string, pageID2 string) error {
	page1, err := e.storage.GetWiki(pageID1)
	if err != nil {
		return fmt.Errorf("failed to get wiki page: %w", err)
	}
	if page1 == nil {
		return fmt.Errorf("wiki page not found: %s", pageID1)
	}

	page2, err := e.storage.GetWiki(pageID2)
	if err != nil {
		return fmt.Errorf("failed to get wiki page: %w", err)
	}
	if page2 == nil {
		return fmt.Errorf("wiki page not found: %s", pageID2)
	}

	// Add link if not exists
	for _, p := range page1.Metadata.RelatedPages {
		if p == pageID2 {
			return nil // Link already exists
		}
	}
	page1.Metadata.RelatedPages = append(page1.Metadata.RelatedPages, pageID2)
	page2.Metadata.RelatedPages = append(page2.Metadata.RelatedPages, pageID1)
	page1.UpdatedAt = time.Now()
	page2.UpdatedAt = time.Now()

	if err := e.storage.SaveWiki(page1); err != nil {
		return err
	}
	return e.storage.SaveWiki(page2)
}

// SearchPages searches wiki pages by query
func (e *Engine) SearchPages(ctx context.Context, query string, limit int) ([]*models.WikiPage, error) {
	allPages, err := e.storage.ListWikis()
	if err != nil {
		return nil, fmt.Errorf("failed to list wiki pages: %w", err)
	}

	// Simple text search
	query = strings.ToLower(query)
	var results []*models.WikiPage
	for _, page := range allPages {
		if strings.Contains(strings.ToLower(page.Title), query) ||
			strings.Contains(strings.ToLower(page.Content), query) {
			page.Sections = e.parseSections(page.Content)
			results = append(results, page)
			if limit > 0 && len(results) >= limit {
				break
			}
		}
	}

	return results, nil
}

// GetPagesByTag retrieves wiki pages with a specific tag
func (e *Engine) GetPagesByTag(ctx context.Context, tag string) ([]*models.WikiPage, error) {
	allPages, err := e.storage.ListWikis()
	if err != nil {
		return nil, fmt.Errorf("failed to list wiki pages: %w", err)
	}

	var results []*models.WikiPage
	for _, page := range allPages {
		for _, t := range page.Metadata.Tags {
			if t == tag {
				page.Sections = e.parseSections(page.Content)
				results = append(results, page)
				break
			}
		}
	}

	return results, nil
}

// GenerateContent generates wiki content using LLM
func (e *Engine) GenerateContent(ctx context.Context, topic string, style string) (string, error) {
	if e.llmProvider == nil {
		return "", fmt.Errorf("LLM provider not available")
	}

	prompt := fmt.Sprintf(`Write a comprehensive wiki article about: "%s"

Style: %s

Requirements:
- Use markdown format
- Include multiple sections with headers
- Provide detailed explanations
- Use balanced, informative tone`, topic, style)

	return e.llmProvider.Generate(ctx, prompt, "claude-sonnet-4-20250514")
}

// ExpandContent expands a section of wiki content using LLM
func (e *Engine) ExpandContent(ctx context.Context, content string, instruction string) (string, error) {
	if e.llmProvider == nil {
		return "", fmt.Errorf("LLM provider not available")
	}

	prompt := fmt.Sprintf(`Expand or improve the following content:

Original content:
%s

Instruction: %s

Provide the improved content in markdown format:`, content, instruction)

	return e.llmProvider.Generate(ctx, prompt, "claude-sonnet-4-20250514")
}

// SummarizeContent summarizes wiki content using LLM
func (e *Engine) SummarizeContent(ctx context.Context, content string, maxLength int) (string, error) {
	if e.llmProvider == nil {
		return "", fmt.Errorf("LLM provider not available")
	}

	prompt := fmt.Sprintf(`Summarize the following content to approximately %d characters:

%s

Provide a concise summary:`, maxLength, content)

	return e.llmProvider.Generate(ctx, prompt, "claude-sonnet-4-20250514")
}

// GetVersionHistory retrieves the version history of a wiki page
func (e *Engine) GetVersionHistory(ctx context.Context, pageID string) ([]*models.WikiVersion, error) {
	page, err := e.storage.GetWiki(pageID)
	if err != nil {
		return nil, fmt.Errorf("failed to get wiki page: %w", err)
	}
	if page == nil {
		return nil, fmt.Errorf("wiki page not found: %s", pageID)
	}

	// For now, return the current page as the latest version
	versions := []*models.WikiVersion{
		{
			Version:   page.Version,
			Content:   page.Content,
			Author:    page.Metadata.Authors[len(page.Metadata.Authors)-1],
			Timestamp: page.UpdatedAt,
			Changes:   "Current version",
		},
	}

	return versions, nil
}

// === Private Methods ===

// parseSections parses wiki content into sections
func (e *Engine) parseSections(content string) []models.WikiSection {
	sections := []models.WikiSection{}
	lines := strings.Split(content, "\n")
	var currentSection *models.WikiSection
	sectionCounter := 0

	for _, line := range lines {
		// Check for headers
		if strings.HasPrefix(line, "#") {
			// Save previous section
			if currentSection != nil {
				sections = append(sections, *currentSection)
			}

			// Parse header
			level := 0
			for strings.HasPrefix(line, "#") {
				level++
				line = line[1:]
			}
			line = strings.TrimSpace(line)

			sectionCounter++
			currentSection = &models.WikiSection{
				ID:       fmt.Sprintf("section-%d", sectionCounter),
				Title:    line,
				Content:  "",
				Level:    level,
				Order:    sectionCounter,
				ParentID: "",
			}
		} else if currentSection != nil {
			currentSection.Content += line + "\n"
		}
	}

	// Save last section
	if currentSection != nil {
		sections = append(sections, *currentSection)
	}

	return sections
}
