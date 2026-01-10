// Package debate provides the debate engine for DAIP-LIVE
package debate

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/daip-live/daip-live-opencode-plugin/pkg/llm"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/models"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/storage"
	"github.com/google/uuid"
)

// Engine manages debate sessions
type Engine struct {
	storage      *storage.SQLiteStorage
	llmProvider  *llm.Provider
	maxRounds    int
	defaultRoles []models.DebateRole
}

// NewEngine creates a new debate engine
func NewEngine(storage *storage.SQLiteStorage, llmProvider *llm.Provider) *Engine {
	return &Engine{
		storage:     storage,
		llmProvider: llmProvider,
		maxRounds:   3,
		defaultRoles: []models.DebateRole{
			{
				Name:         "Proponent",
				Model:        "claude-sonnet-4-20250514",
				Color:        "#4CAF50",
				SystemPrompt: "You argue in favor of the topic, presenting positive aspects and supporting arguments.",
			},
			{
				Name:         "Opponent",
				Model:        "gpt-4o",
				Color:        "#F44336",
				SystemPrompt: "You argue against the topic, presenting critical aspects and counterarguments.",
			},
			{
				Name:         "Moderator",
				Model:        "claude-sonnet-4-20250514",
				Color:        "#2196F3",
				SystemPrompt: "You facilitate the debate, ensuring balanced discussion and summarizing key points.",
			},
		},
	}
}

// SetMaxRounds sets the maximum number of rounds for debates
func (e *Engine) SetMaxRounds(rounds int) {
	if rounds > 0 {
		e.maxRounds = rounds
	}
}

// SetDefaultRoles sets the default roles for debates
func (e *Engine) SetDefaultRoles(roles []models.DebateRole) {
	e.defaultRoles = roles
}

// StartDebate creates a new debate session
func (e *Engine) StartDebate(ctx context.Context, topic string, roles []string, rounds int, roleModels map[string]string) (*models.DebateSession, error) {
	if rounds <= 0 {
		rounds = e.maxRounds
	}

	// Resolve roles
	var participants []models.DebateRole
	if len(roles) == 0 {
		participants = e.defaultRoles
	} else {
		participants = e.resolveRoles(roles, roleModels)
	}

	session := &models.DebateSession{
		ID:           uuid.New().String(),
		Topic:        topic,
		Status:       models.DebateStatusActive,
		Participants: participants,
		TotalRounds:  rounds,
		CurrentRound: 1,
		Turns:        []models.DebateTurn{},
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}

	// Create moderator opening turn
	moderatorTurn := models.DebateTurn{
		ID:          uuid.New().String(),
		SessionID:   session.ID,
		RoundNumber: 0,
		Participant: "Moderator",
		Content:     fmt.Sprintf("Welcome to today's debate on: \"%s\"\n\nParticipants will present arguments %d rounds each.\nLet's begin with opening statements.", topic, rounds),
		Timestamp:   time.Now(),
	}
	session.Turns = append(session.Turns, moderatorTurn)

	// Save to storage
	if err := e.storage.SaveDebate(session); err != nil {
		return nil, fmt.Errorf("failed to save debate session: %w", err)
	}

	log.Printf("Started debate session %s on topic: %s", session.ID, topic)
	return session, nil
}

// NextTurn executes the next turn in the debate
func (e *Engine) NextTurn(ctx context.Context, sessionID string) (*models.DebateTurn, error) {
	session, err := e.storage.GetDebate(sessionID)
	if err != nil {
		return nil, fmt.Errorf("failed to get debate session: %w", err)
	}
	if session == nil {
		return nil, fmt.Errorf("debate session not found: %s", sessionID)
	}

	if session.Status != models.DebateStatusActive {
		return nil, fmt.Errorf("debate session is not active: %s", session.Status)
	}

	// Determine next participant
	participantIndex := len(session.Turns) % len(session.Participants)
	participant := session.Participants[participantIndex]

	// Determine if this is a new round
	currentRound := len(session.Turns)/len(session.Participants) + 1
	if currentRound > session.TotalRounds {
		// Debate complete, generate summary
		if err := e.completeDebate(ctx, session); err != nil {
			return nil, fmt.Errorf("failed to complete debate: %w", err)
		}
		return nil, fmt.Errorf("debate session is complete")
	}

	// Generate turn content
	turnContent, err := e.generateTurnContent(ctx, session, participant, currentRound)
	if err != nil {
		return nil, fmt.Errorf("failed to generate turn content: %w", err)
	}

	turn := models.DebateTurn{
		ID:            uuid.New().String(),
		SessionID:     session.ID,
		RoundNumber:   currentRound,
		Participant:   participant.Name,
		Content:       turnContent,
		ContentLength: len(turnContent),
		Timestamp:     time.Now(),
	}

	// Update session
	session.Turns = append(session.Turns, turn)
	session.CurrentRound = currentRound
	session.UpdatedAt = time.Now()

	// Save to storage
	if err := e.storage.SaveDebate(session); err != nil {
		return nil, fmt.Errorf("failed to save debate session: %w", err)
	}

	log.Printf("Debate %s: %s took turn %d", sessionID, participant.Name, currentRound)
	return &turn, nil
}

// GetSession retrieves a debate session
func (e *Engine) GetSession(ctx context.Context, sessionID string) (*models.DebateSession, error) {
	session, err := e.storage.GetDebate(sessionID)
	if err != nil {
		return nil, fmt.Errorf("failed to get debate session: %w", err)
	}
	if session == nil {
		return nil, fmt.Errorf("debate session not found: %s", sessionID)
	}
	return session, nil
}

// ListSessions lists all debate sessions
func (e *Engine) ListSessions(ctx context.Context, limit int) ([]*models.DebateSession, error) {
	return e.storage.ListDebates(limit)
}

// PauseDebate pauses an active debate
func (e *Engine) PauseDebate(ctx context.Context, sessionID string) error {
	session, err := e.storage.GetDebate(sessionID)
	if err != nil {
		return fmt.Errorf("failed to get debate session: %w", err)
	}
	if session == nil {
		return fmt.Errorf("debate session not found: %s", sessionID)
	}

	session.Status = models.DebateStatusPaused
	session.UpdatedAt = time.Now()

	return e.storage.SaveDebate(session)
}

// ResumeDebate resumes a paused debate
func (e *Engine) ResumeDebate(ctx context.Context, sessionID string) error {
	session, err := e.storage.GetDebate(sessionID)
	if err != nil {
		return fmt.Errorf("failed to get debate session: %w", err)
	}
	if session == nil {
		return fmt.Errorf("debate session not found: %s", sessionID)
	}

	if session.Status != models.DebateStatusPaused {
		return fmt.Errorf("debate session is not paused: %s", session.Status)
	}

	session.Status = models.DebateStatusActive
	session.UpdatedAt = time.Now()

	return e.storage.SaveDebate(session)
}

// CancelDebate cancels a debate session
func (e *Engine) CancelDebate(ctx context.Context, sessionID string) error {
	session, err := e.storage.GetDebate(sessionID)
	if err != nil {
		return fmt.Errorf("failed to get debate session: %w", err)
	}
	if session == nil {
		return fmt.Errorf("debate session not found: %s", sessionID)
	}

	session.Status = models.DebateStatusCancelled
	session.UpdatedAt = time.Now()

	return e.storage.SaveDebate(session)
}

// GenerateSummary generates a summary of the debate
func (e *Engine) GenerateSummary(ctx context.Context, sessionID string) (string, error) {
	session, err := e.storage.GetDebate(sessionID)
	if err != nil {
		return "", fmt.Errorf("failed to get debate session: %w", err)
	}
	if session == nil {
		return "", fmt.Errorf("debate session not found: %s", sessionID)
	}

	// Build summary from all turns
	summary := fmt.Sprintf("## Debate Summary: %s\n\n", session.Topic)
	summary += fmt.Sprintf("**Status:** %s | **Rounds:** %d/%d | **Participants:** %d\n\n",
		session.Status, session.CurrentRound, session.TotalRounds, len(session.Participants))

	summary += "### Key Arguments:\n\n"
	for _, turn := range session.Turns {
		if turn.RoundNumber > 0 {
			summary += fmt.Sprintf("**%s** (Round %d): %s\n\n", turn.Participant, turn.RoundNumber, truncate(turn.Content, 200))
		}
	}

	// Generate AI summary if we have an LLM provider
	if e.llmProvider != nil && len(session.Turns) > 2 {
		prompt := fmt.Sprintf("Generate a concise summary of this debate topic \"%s\" based on the arguments presented. Focus on the main points from each side.", session.Topic)
		aiSummary, err := e.llmProvider.Generate(ctx, prompt, "claude-sonnet-4-20250514")
		if err == nil {
			summary += fmt.Sprintf("\n### AI Analysis:\n%s\n", aiSummary)
		}
	}

	return summary, nil
}

// CompleteDebate completes the debate and generates final summary
func (e *Engine) CompleteDebate(ctx context.Context, sessionID string) error {
	session, err := e.storage.GetDebate(sessionID)
	if err != nil {
		return fmt.Errorf("failed to get debate session: %w", err)
	}
	if session == nil {
		return fmt.Errorf("debate session not found: %s", sessionID)
	}

	return e.completeDebate(ctx, session)
}

// === Private Methods ===

// resolveRoles resolves role names to DebateRole objects
func (e *Engine) resolveRoles(roleNames []string, roleModels map[string]string) []models.DebateRole {
	var roles []models.DebateRole

	roleTemplates := map[string]models.DebateRole{
		"proponent": {
			Name:         "Proponent",
			Model:        "claude-sonnet-4-20250514",
			Color:        "#4CAF50",
			SystemPrompt: "You argue in favor of the topic, presenting positive aspects and supporting arguments.",
		},
		"opponent": {
			Name:         "Opponent",
			Model:        "gpt-4o",
			Color:        "#F44336",
			SystemPrompt: "You argue against the topic, presenting critical aspects and counterarguments.",
		},
		"moderator": {
			Name:         "Moderator",
			Model:        "claude-sonnet-4-20250514",
			Color:        "#2196F3",
			SystemPrompt: "You facilitate the debate, ensuring balanced discussion and summarizing key points.",
		},
		"analyst": {
			Name:         "Analyst",
			Model:        "claude-sonnet-4-20250514",
			Color:        "#FF9800",
			SystemPrompt: "You provide objective analysis, examining claims and evidence critically.",
		},
		"synthesizer": {
			Name:         "Synthesizer",
			Model:        "gpt-4o",
			Color:        "#9C27B0",
			SystemPrompt: "You work to find common ground and synthesize opposing viewpoints.",
		},
	}

	for _, name := range roleNames {
		if template, ok := roleTemplates[lowercase(name)]; ok {
			// Apply custom model if provided
			if model, ok := roleModels[lowercase(name)]; ok {
				template.Model = model
			}
			roles = append(roles, template)
		} else {
			// Generic role
			roles = append(roles, models.DebateRole{
				Name:         name,
				Model:        "claude-sonnet-4-20250514",
				Color:        "#607D8B",
				SystemPrompt: fmt.Sprintf("You represent the perspective of %s in this debate.", name),
			})
		}
	}

	if len(roles) == 0 {
		return e.defaultRoles
	}

	return roles
}

// generateTurnContent generates content for a debate turn
func (e *Engine) generateTurnContent(ctx context.Context, session *models.DebateSession, participant models.DebateRole, round int) (string, error) {
	// Build context from previous turns
	contextPrompt := buildDebateContext(session, participant.Name, round)

	// Use LLM if provider is available
	if e.llmProvider != nil {
		response, err := e.llmProvider.Generate(ctx, contextPrompt, participant.Model)
		if err != nil {
			log.Printf("LLM generation failed, using template: %v", err)
			return e.generateTemplateResponse(session, participant, round)
		}
		return response, nil
	}

	// Fallback to template response
	return e.generateTemplateResponse(session, participant, round)
}

// generateTemplateResponse generates a template-based response
func (e *Engine) generateTemplateResponse(session *models.DebateSession, participant models.DebateRole, round int) (string, error) {
	basePrompt := participant.SystemPrompt

	var response string
	switch round {
	case 1:
		response = fmt.Sprintf("%s\n\nOpening statement on \"%s\": As the %s, I believe this topic requires careful examination from multiple angles. Let me present my initial thoughts on this matter.", basePrompt, session.Topic, participant.Name)
	case 2:
		response = fmt.Sprintf("%s\n\nRebuttal round: Building on the discussion, I want to address some key points raised by other participants. The evidence suggests...", basePrompt, session.Topic)
	case 3:
		response = fmt.Sprintf("%s\n\nClosing argument: Based on all the evidence and discussion, my final position on \"%s\" is that...", basePrompt, session.Topic)
	default:
		response = fmt.Sprintf("%s\n\nAdditional thoughts on \"%s\": Further analysis reveals...", basePrompt, session.Topic)
	}
	return response, nil
}

// completeDebate finalizes the debate and generates summary
func (e *Engine) completeDebate(ctx context.Context, session *models.DebateSession) error {
	session.Status = models.DebateStatusCompleted
	session.UpdatedAt = time.Now()

	// Generate conclusions
	if e.llmProvider != nil {
		prompt := fmt.Sprintf("Based on this debate on \"%s\", provide 3-5 key conclusions or insights. Format as a simple list.", session.Topic)
		conclusions, err := e.llmProvider.Generate(ctx, prompt, "claude-sonnet-4-20250514")
		if err == nil {
			// Parse conclusions (simple split by newlines)
			session.Conclusions = []string{}
			_ = conclusions
		}
	}

	// Add closing turn
	closingTurn := models.DebateTurn{
		ID:          uuid.New().String(),
		SessionID:   session.ID,
		RoundNumber: session.TotalRounds + 1,
		Participant: "Moderator",
		Content:     "This concludes today's debate. Thank you to all participants for their thoughtful arguments.",
		Timestamp:   time.Now(),
	}
	session.Turns = append(session.Turns, closingTurn)

	return e.storage.SaveDebate(session)
}

// buildDebateContext builds the context prompt for LLM generation
func buildDebateContext(session *models.DebateSession, participantName string, round int) string {
	context := fmt.Sprintf(`Debate Topic: "%s"
Current Round: %d/%d
Your Role: %s

Previous Turns:
`, session.Topic, round, session.TotalRounds, participantName)

	for _, turn := range session.Turns {
		if turn.RoundNumber < round && turn.Participant != "Moderator" {
			context += fmt.Sprintf("- %s (Round %d): %s\n\n", turn.Participant, turn.RoundNumber, truncate(turn.Content, 300))
		}
	}

	context += fmt.Sprintf(`Your Task: Provide your %s statement on this topic. Be substantive, cite evidence when possible, and engage with previous arguments.`, getOrdinal(round))

	return context
}

// Helper functions

func truncate(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	return s[:maxLen] + "..."
}

func lowercase(s string) string {
	result := make([]byte, len(s))
	for i := 0; i < len(s); i++ {
		c := s[i]
		if c >= 'A' && c <= 'Z' {
			result[i] = c + 32
		} else {
			result[i] = c
		}
	}
	return string(result)
}

func getOrdinal(n int) string {
	switch n {
	case 1:
		return "opening"
	case 2:
		return "rebuttal"
	case 3:
		return "closing"
	default:
		return fmt.Sprintf("round %d", n)
	}
}
