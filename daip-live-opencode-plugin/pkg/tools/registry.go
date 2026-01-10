// Package tools provides OpenCode tool integration for DAIP-LIVE
package tools

import (
	"context"
	"encoding/json"
	"fmt"
	"log"

	"github.com/daip-live/daip-live-opencode-plugin/pkg/debate"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/knowledge"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/llm"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/storage"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/wiki"
)

// Registry manages DAIP-LIVE tools for OpenCode
type Registry struct {
	debateEngine    *debate.Engine
	wikiEngine      *wiki.Engine
	knowledgeEngine *knowledge.Engine
	llmProvider     *llm.Provider
}

// NewRegistry creates a new tool registry
func NewRegistry(storage *storage.SQLiteStorage, llmProvider *llm.Provider) *Registry {
	return &Registry{
		debateEngine:    debate.NewEngine(storage, llmProvider),
		wikiEngine:      wiki.NewEngine(storage, llmProvider),
		knowledgeEngine: knowledge.NewEngine(storage, llmProvider),
		llmProvider:     llmProvider,
	}
}

// Tool represents a tool that can be registered with OpenCode
type Tool struct {
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Parameters  map[string]interface{} `json:"parameters"`
}

// GetDebateTools returns the debate tools
func (r *Registry) GetDebateTools() []Tool {
	return []Tool{
		{
			Name:        "daip_debate_start",
			Description: "Start a new multi-model debate session on a topic",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"topic": map[string]interface{}{
						"type":        "string",
						"description": "The debate topic or question",
					},
					"roles": map[string]interface{}{
						"type":        "array",
						"description": "List of role names (e.g., [\"proponent\", \"opponent\"])",
						"items":       map[string]interface{}{"type": "string"},
					},
					"rounds": map[string]interface{}{
						"type":        "integer",
						"description": "Number of debate rounds (default: 3)",
					},
				},
				"required": []string{"topic"},
			},
		},
		{
			Name:        "daip_debate_turn",
			Description: "Execute the next turn in an active debate",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"session_id": map[string]interface{}{
						"type":        "string",
						"description": "The debate session ID",
					},
				},
				"required": []string{"session_id"},
			},
		},
		{
			Name:        "daip_debate_summary",
			Description: "Get a summary of a debate session",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"session_id": map[string]interface{}{
						"type":        "string",
						"description": "The debate session ID",
					},
				},
				"required": []string{"session_id"},
			},
		},
		{
			Name:        "daip_debate_list",
			Description: "List all debate sessions",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"limit": map[string]interface{}{
						"type":        "integer",
						"description": "Maximum number of sessions to return",
					},
				},
			},
		},
	}
}

// GetWikiTools returns the wiki tools
func (r *Registry) GetWikiTools() []Tool {
	return []Tool{
		{
			Name:        "daip_wiki_create",
			Description: "Create a new wiki page",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"title": map[string]interface{}{
						"type":        "string",
						"description": "The wiki page title",
					},
					"content": map[string]interface{}{
						"type":        "string",
						"description": "The initial content (markdown format)",
					},
					"author": map[string]interface{}{
						"type":        "string",
						"description": "The author name",
					},
					"tags": map[string]interface{}{
						"type":        "array",
						"description": "Tags for the page",
						"items":       map[string]interface{}{"type": "string"},
					},
				},
				"required": []string{"title", "content"},
			},
		},
		{
			Name:        "daip_wiki_get",
			Description: "Get a wiki page by ID",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"page_id": map[string]interface{}{
						"type":        "string",
						"description": "The wiki page ID",
					},
				},
				"required": []string{"page_id"},
			},
		},
		{
			Name:        "daip_wiki_update",
			Description: "Update a wiki page",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"page_id": map[string]interface{}{
						"type":        "string",
						"description": "The wiki page ID",
					},
					"content": map[string]interface{}{
						"type":        "string",
						"description": "The new content",
					},
					"author": map[string]interface{}{
						"type":        "string",
						"description": "The author name",
					},
					"changes": map[string]interface{}{
						"type":        "string",
						"description": "Description of changes",
					},
				},
				"required": []string{"page_id", "content"},
			},
		},
		{
			Name:        "daip_wiki_list",
			Description: "List all wiki pages",
			Parameters:  map[string]interface{}{},
		},
		{
			Name:        "daip_wiki_search",
			Description: "Search wiki pages",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"query": map[string]interface{}{
						"type":        "string",
						"description": "Search query",
					},
					"limit": map[string]interface{}{
						"type":        "integer",
						"description": "Maximum results",
					},
				},
				"required": []string{"query"},
			},
		},
	}
}

// GetKnowledgeTools returns the knowledge tools
func (r *Registry) GetKnowledgeTools() []Tool {
	return []Tool{
		{
			Name:        "daip_knowledge_add",
			Description: "Add a knowledge concept",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"name": map[string]interface{}{
						"type":        "string",
						"description": "Concept name",
					},
					"description": map[string]interface{}{
						"type":        "string",
						"description": "Concept description",
					},
					"category": map[string]interface{}{
						"type":        "string",
						"description": "Concept category",
					},
					"tags": map[string]interface{}{
						"type":        "array",
						"description": "Concept tags",
						"items":       map[string]interface{}{"type": "string"},
					},
				},
				"required": []string{"name"},
			},
		},
		{
			Name:        "daip_knowledge_search",
			Description: "Search knowledge concepts",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"query": map[string]interface{}{
						"type":        "string",
						"description": "Search query",
					},
					"limit": map[string]interface{}{
						"type":        "integer",
						"description": "Maximum results",
					},
				},
				"required": []string{"query"},
			},
		},
		{
			Name:        "daip_knowledge_top",
			Description: "Get top accessed knowledge concepts",
			Parameters: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"limit": map[string]interface{}{
						"type":        "integer",
						"description": "Maximum results",
					},
				},
			},
		},
	}
}

// GetAllTools returns all DAIP-LIVE tools
func (r *Registry) GetAllTools() []Tool {
	tools := append(r.GetDebateTools(), r.GetWikiTools()...)
	tools = append(tools, r.GetKnowledgeTools()...)
	return tools
}

// ExecuteDebateTool executes a debate tool
func (r *Registry) ExecuteDebateTool(ctx context.Context, name string, args json.RawMessage) (interface{}, error) {
	switch name {
	case "daip_debate_start":
		return r.executeDebateStart(ctx, args)
	case "daip_debate_turn":
		return r.executeDebateTurn(ctx, args)
	case "daip_debate_summary":
		return r.executeDebateSummary(ctx, args)
	case "daip_debate_list":
		return r.executeDebateList(ctx, args)
	default:
		return nil, fmt.Errorf("unknown debate tool: %s", name)
	}
}

// ExecuteWikiTool executes a wiki tool
func (r *Registry) ExecuteWikiTool(ctx context.Context, name string, args json.RawMessage) (interface{}, error) {
	switch name {
	case "daip_wiki_create":
		return r.executeWikiCreate(ctx, args)
	case "daip_wiki_get":
		return r.executeWikiGet(ctx, args)
	case "daip_wiki_update":
		return r.executeWikiUpdate(ctx, args)
	case "daip_wiki_list":
		return r.executeWikiList(ctx, args)
	case "daip_wiki_search":
		return r.executeWikiSearch(ctx, args)
	default:
		return nil, fmt.Errorf("unknown wiki tool: %s", name)
	}
}

// ExecuteKnowledgeTool executes a knowledge tool
func (r *Registry) ExecuteKnowledgeTool(ctx context.Context, name string, args json.RawMessage) (interface{}, error) {
	switch name {
	case "daip_knowledge_add":
		return r.executeKnowledgeAdd(ctx, args)
	case "daip_knowledge_search":
		return r.executeKnowledgeSearch(ctx, args)
	case "daip_knowledge_top":
		return r.executeKnowledgeTop(ctx, args)
	default:
		return nil, fmt.Errorf("unknown knowledge tool: %s", name)
	}
}

// === Private Debate Tool Methods ===

func (r *Registry) executeDebateStart(ctx context.Context, args json.RawMessage) (interface{}, error) {
	var params struct {
		Topic  string   `json:"topic"`
		Roles  []string `json:"roles"`
		Rounds int      `json:"rounds"`
	}
	if err := json.Unmarshal(args, &params); err != nil {
		return nil, fmt.Errorf("failed to parse arguments: %w", err)
	}

	session, err := r.debateEngine.StartDebate(ctx, params.Topic, params.Roles, params.Rounds, nil)
	if err != nil {
		return nil, err
	}

	return map[string]interface{}{
		"session_id":   session.ID,
		"topic":        session.Topic,
		"status":       session.Status,
		"participants": session.Participants,
		"total_rounds": session.TotalRounds,
	}, nil
}

func (r *Registry) executeDebateTurn(ctx context.Context, args json.RawMessage) (interface{}, error) {
	var params struct {
		SessionID string `json:"session_id"`
	}
	if err := json.Unmarshal(args, &params); err != nil {
		return nil, fmt.Errorf("failed to parse arguments: %w", err)
	}

	turn, err := r.debateEngine.NextTurn(ctx, params.SessionID)
	if err != nil {
		return nil, err
	}

	return map[string]interface{}{
		"turn_id":      turn.ID,
		"session_id":   turn.SessionID,
		"round_number": turn.RoundNumber,
		"participant":  turn.Participant,
		"content":      turn.Content,
	}, nil
}

func (r *Registry) executeDebateSummary(ctx context.Context, args json.RawMessage) (interface{}, error) {
	var params struct {
		SessionID string `json:"session_id"`
	}
	if err := json.Unmarshal(args, &params); err != nil {
		return nil, fmt.Errorf("failed to parse arguments: %w", err)
	}

	summary, err := r.debateEngine.GenerateSummary(ctx, params.SessionID)
	if err != nil {
		return nil, err
	}

	return map[string]interface{}{
		"session_id": params.SessionID,
		"summary":    summary,
	}, nil
}

func (r *Registry) executeDebateList(ctx context.Context, args json.RawMessage) (interface{}, error) {
	var params struct {
		Limit int `json:"limit"`
	}
	if err := json.Unmarshal(args, &params); err != nil {
		params.Limit = 10
	}

	sessions, err := r.debateEngine.ListSessions(ctx, params.Limit)
	if err != nil {
		return nil, err
	}

	result := make([]map[string]interface{}, len(sessions))
	for i, session := range sessions {
		result[i] = map[string]interface{}{
			"session_id":    session.ID,
			"topic":         session.Topic,
			"status":        session.Status,
			"total_rounds":  session.TotalRounds,
			"current_round": session.CurrentRound,
		}
	}

	return map[string]interface{}{
		"sessions": result,
	}, nil
}

// === Private Wiki Tool Methods ===

func (r *Registry) executeWikiCreate(ctx context.Context, args json.RawMessage) (interface{}, error) {
	var params struct {
		Title   string   `json:"title"`
		Content string   `json:"content"`
		Author  string   `json:"author"`
		Tags    []string `json:"tags"`
	}
	if err := json.Unmarshal(args, &params); err != nil {
		return nil, fmt.Errorf("failed to parse arguments: %w", err)
	}

	if params.Author == "" {
		params.Author = "OpenCode"
	}

	page, err := r.wikiEngine.CreatePage(ctx, params.Title, params.Content, params.Author, params.Tags)
	if err != nil {
		return nil, err
	}

	return map[string]interface{}{
		"page_id": page.ID,
		"title":   page.Title,
		"version": page.Version,
		"authors": page.Metadata.Authors,
	}, nil
}

func (r *Registry) executeWikiGet(ctx context.Context, args json.RawMessage) (interface{}, error) {
	var params struct {
		PageID string `json:"page_id"`
	}
	if err := json.Unmarshal(args, &params); err != nil {
		return nil, fmt.Errorf("failed to parse arguments: %w", err)
	}

	page, err := r.wikiEngine.GetPage(ctx, params.PageID)
	if err != nil {
		return nil, err
	}

	return map[string]interface{}{
		"page_id":    page.ID,
		"title":      page.Title,
		"content":    page.Content,
		"version":    page.Version,
		"sections":   page.Sections,
		"tags":       page.Metadata.Tags,
		"authors":    page.Metadata.Authors,
		"created_at": page.CreatedAt,
		"updated_at": page.UpdatedAt,
	}, nil
}

func (r *Registry) executeWikiUpdate(ctx context.Context, args json.RawMessage) (interface{}, error) {
	var params struct {
		PageID  string `json:"page_id"`
		Content string `json:"content"`
		Author  string `json:"author"`
		Changes string `json:"changes"`
	}
	if err := json.Unmarshal(args, &params); err != nil {
		return nil, fmt.Errorf("failed to parse arguments: %w", err)
	}

	if params.Author == "" {
		params.Author = "OpenCode"
	}
	if params.Changes == "" {
		params.Changes = "Updated via OpenCode"
	}

	page, err := r.wikiEngine.UpdatePage(ctx, params.PageID, params.Content, params.Author, params.Changes)
	if err != nil {
		return nil, err
	}

	return map[string]interface{}{
		"page_id": page.ID,
		"title":   page.Title,
		"version": page.Version,
		"updated": true,
	}, nil
}

func (r *Registry) executeWikiList(ctx context.Context, args json.RawMessage) (interface{}, error) {
	pages, err := r.wikiEngine.ListPages(ctx)
	if err != nil {
		return nil, err
	}

	result := make([]map[string]interface{}, len(pages))
	for i, page := range pages {
		result[i] = map[string]interface{}{
			"page_id": page.ID,
			"title":   page.Title,
			"version": page.Version,
			"tags":    page.Metadata.Tags,
			"authors": page.Metadata.Authors,
		}
	}

	return map[string]interface{}{
		"pages": result,
	}, nil
}

func (r *Registry) executeWikiSearch(ctx context.Context, args json.RawMessage) (interface{}, error) {
	var params struct {
		Query string `json:"query"`
		Limit int    `json:"limit"`
	}
	if err := json.Unmarshal(args, &params); err != nil {
		return nil, fmt.Errorf("failed to parse arguments: %w", err)
	}

	pages, err := r.wikiEngine.SearchPages(ctx, params.Query, params.Limit)
	if err != nil {
		return nil, err
	}

	result := make([]map[string]interface{}, len(pages))
	for i, page := range pages {
		result[i] = map[string]interface{}{
			"page_id": page.ID,
			"title":   page.Title,
			"version": page.Version,
		}
	}

	return map[string]interface{}{
		"pages": result,
	}, nil
}

// === Private Knowledge Tool Methods ===

func (r *Registry) executeKnowledgeAdd(ctx context.Context, args json.RawMessage) (interface{}, error) {
	var params struct {
		Name        string   `json:"name"`
		Description string   `json:"description"`
		Category    string   `json:"category"`
		Tags        []string `json:"tags"`
	}
	if err := json.Unmarshal(args, &params); err != nil {
		return nil, fmt.Errorf("failed to parse arguments: %w", err)
	}

	concept, err := r.knowledgeEngine.AddConcept(ctx, params.Name, params.Description, params.Category, params.Tags, "manual", "")
	if err != nil {
		return nil, err
	}

	return map[string]interface{}{
		"concept_id": concept.ID,
		"name":       concept.Name,
		"category":   concept.Category,
	}, nil
}

func (r *Registry) executeKnowledgeSearch(ctx context.Context, args json.RawMessage) (interface{}, error) {
	var params struct {
		Query string `json:"query"`
		Limit int    `json:"limit"`
	}
	if err := json.Unmarshal(args, &params); err != nil {
		return nil, fmt.Errorf("failed to parse arguments: %w", err)
	}

	concepts, err := r.knowledgeEngine.SearchConcepts(ctx, params.Query, params.Limit)
	if err != nil {
		return nil, err
	}

	result := make([]map[string]interface{}, len(concepts))
	for i, concept := range concepts {
		result[i] = map[string]interface{}{
			"concept_id":  concept.ID,
			"name":        concept.Name,
			"description": concept.Description,
			"category":    concept.Category,
			"count":       concept.Count,
		}
	}

	return map[string]interface{}{
		"concepts": result,
	}, nil
}

func (r *Registry) executeKnowledgeTop(ctx context.Context, args json.RawMessage) (interface{}, error) {
	var params struct {
		Limit int `json:"limit"`
	}
	if err := json.Unmarshal(args, &params); err != nil {
		params.Limit = 10
	}

	concepts, err := r.knowledgeEngine.GetTopConcepts(ctx, params.Limit)
	if err != nil {
		return nil, err
	}

	result := make([]map[string]interface{}, len(concepts))
	for i, concept := range concepts {
		result[i] = map[string]interface{}{
			"concept_id": concept.ID,
			"name":       concept.Name,
			"count":      concept.Count,
			"category":   concept.Category,
		}
	}

	return map[string]interface{}{
		"concepts": result,
	}, nil
}

// === Utility Methods ===

// PrintTools prints all available tools in a formatted way
func (r *Registry) PrintTools() {
	tools := r.GetAllTools()
	log.Printf("=== DAIP-LIVE Tools (%d total) ===\n", len(tools))

	for _, tool := range tools {
		log.Printf("\n## %s\n%s", tool.Name, tool.Description)
	}
}
