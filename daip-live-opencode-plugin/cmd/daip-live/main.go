// Package daip-live provides DAIP-LIVE functionality for OpenCode
// including multi-model debate, wiki collaboration, and knowledge synthesis.
package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"github.com/daip-live/daip-live-opencode-plugin/pkg/config"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/debate"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/knowledge"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/llm"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/models"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/storage"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/tools"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/wiki"
)

// Version is the plugin version
const Version = "1.0.0"

var (
	debug       = flag.Bool("debug", false, "Enable debug mode")
	configPath  = flag.String("config", "", "Config file path")
	storagePath = flag.String("storage", "", "Storage directory path")
)

func main() {
	flag.Parse()

	// Load configuration
	cfg := config.LoadConfig(*storagePath)

	fmt.Println("DAIP-LIVE OpenCode Plugin CLI")
	fmt.Println("==============================")
	fmt.Println()
	fmt.Println("Version:", Version)
	fmt.Println("Storage:", cfg.StoragePath)
	fmt.Println()

	// Initialize storage
	store, err := storage.NewSQLiteStorage(cfg.StoragePath)
	if err != nil {
		fmt.Printf("Failed to initialize storage: %v\n", err)
		os.Exit(1)
	}
	defer store.Close()

	// Initialize LLM provider
	llmProvider := llm.NewProvider(llm.Config{
		AnthropicAPIKey: cfg.LLMProviders.AnthropicAPIKey,
		OpenAIAPIKey:    cfg.LLMProviders.OpenAIAPIKey,
		GoogleAPIKey:    cfg.LLMProviders.GoogleAPIKey,
		DefaultModel:    cfg.Models.Standard,
	})

	// Initialize engines
	debateEngine := debate.NewEngine(store, llmProvider)
	debateEngine.SetMaxRounds(cfg.MaxRounds)

	// Initialize tool registry
	toolRegistry := tools.NewRegistry(store, llmProvider)

	fmt.Println("Available tools:")
	for _, tool := range toolRegistry.GetAllTools() {
		fmt.Printf("  - %s: %s\n", tool.Name, tool.Description)
	}
	fmt.Println()
	fmt.Println("This plugin is designed to be run from within OpenCode.")
	fmt.Println("Configure it in your .opencode/opencode.json:")
	fmt.Println()
	fmt.Println(`{
  "plugin": ["daip-live"]
}`)
	fmt.Println()
}

// DAIPLive is the main plugin struct that OpenCode will use
type DAIPLive struct {
	debateEngine    *debate.Engine
	wikiEngine      *wiki.Engine
	knowledgeEngine *knowledge.Engine
	config          *config.Config
}

// NewDAIPLive creates a new DAIPLive plugin instance
func NewDAIPLive(cfg *config.Config) *DAIPLive {
	// Initialize storage
	store, err := storage.NewSQLiteStorage(cfg.StoragePath)
	if err != nil {
		fmt.Printf("Failed to initialize storage: %v\n", err)
		return nil
	}

	// Initialize LLM provider
	llmProvider := llm.NewProvider(llm.Config{
		AnthropicAPIKey: cfg.LLMProviders.AnthropicAPIKey,
		OpenAIAPIKey:    cfg.LLMProviders.OpenAIAPIKey,
		GoogleAPIKey:    cfg.LLMProviders.GoogleAPIKey,
		DefaultModel:    cfg.Models.Standard,
	})

	return &DAIPLive{
		debateEngine:    debate.NewEngine(store, llmProvider),
		wikiEngine:      wiki.NewEngine(store, llmProvider),
		knowledgeEngine: knowledge.NewEngine(store, llmProvider),
		config:          cfg,
	}
}

// StartDebate starts a new debate session
func (d *DAIPLive) StartDebate(ctx context.Context, topic string, roles []string, rounds int) (*models.DebateSession, error) {
	if rounds <= 0 {
		rounds = d.config.DefaultRounds
	}
	return d.debateEngine.StartDebate(ctx, topic, roles, rounds, nil)
}

// GetDebate gets a debate session by ID
func (d *DAIPLive) GetDebate(ctx context.Context, sessionID string) (*models.DebateSession, error) {
	return d.debateEngine.GetSession(ctx, sessionID)
}

// ListDebates lists all debate sessions
func (d *DAIPLive) ListDebates(ctx context.Context, limit int) ([]*models.DebateSession, error) {
	return d.debateEngine.ListSessions(ctx, limit)
}

// CreateWiki creates a new wiki page
func (d *DAIPLive) CreateWiki(ctx context.Context, title, content, author string, tags []string) (*models.WikiPage, error) {
	if author == "" {
		author = "OpenCode"
	}
	return d.wikiEngine.CreatePage(ctx, title, content, author, tags)
}

// GetWiki gets a wiki page by ID
func (d *DAIPLive) GetWiki(ctx context.Context, pageID string) (*models.WikiPage, error) {
	return d.wikiEngine.GetPage(ctx, pageID)
}

// ListWikis lists all wiki pages
func (d *DAIPLive) ListWikis(ctx context.Context) ([]*models.WikiPage, error) {
	return d.wikiEngine.ListPages(ctx)
}

// SearchWikis searches wiki pages
func (d *DAIPLive) SearchWikis(ctx context.Context, query string, limit int) ([]*models.WikiPage, error) {
	return d.wikiEngine.SearchPages(ctx, query, limit)
}

// AddKnowledge adds a knowledge concept
func (d *DAIPLive) AddKnowledge(ctx context.Context, name, description, category string, tags []string) (*models.KnowledgeConcept, error) {
	return d.knowledgeEngine.AddConcept(ctx, name, description, category, tags, "manual", "")
}

// SearchKnowledge searches the knowledge graph
func (d *DAIPLive) SearchKnowledge(ctx context.Context, query string, limit int) ([]*models.KnowledgeConcept, error) {
	return d.knowledgeEngine.SearchConcepts(ctx, query, limit)
}

// GetTopKnowledge gets the most accessed knowledge concepts
func (d *DAIPLive) GetTopKnowledge(ctx context.Context, limit int) ([]*models.KnowledgeConcept, error) {
	return d.knowledgeEngine.GetTopConcepts(ctx, limit)
}

// ExportResult is the JSON output structure for tool responses
type ExportResult struct {
	Success   bool            `json:"success"`
	Message   string          `json:"message"`
	SessionID string          `json:"session_id,omitempty"`
	Content   json.RawMessage `json:"content,omitempty"`
}

// ToJSON exports the result as JSON bytes
func (e *ExportResult) ToJSON() ([]byte, error) {
	return json.Marshal(e)
}
