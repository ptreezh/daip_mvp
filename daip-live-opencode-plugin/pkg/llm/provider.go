// Package llm provides LLM provider support for DAIP-LIVE
package llm

import (
	"context"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/sashabaranov/go-openai"
)

// Provider manages LLM interactions
type Provider struct {
	clients map[string]*openai.Client
	config  Config
}

// Config holds LLM configuration
type Config struct {
	AnthropicAPIKey string
	OpenAIAPIKey    string
	GoogleAPIKey    string
	DefaultModel    string
	MaxTokens       int
	Timeout         time.Duration
}

// NewProvider creates a new LLM provider
func NewProvider(config Config) *Provider {
	provider := &Provider{
		clients: make(map[string]*openai.Client),
		config:  config,
	}

	// Initialize clients if API keys are available
	if config.AnthropicAPIKey != "" {
		provider.clients["anthropic"] = openai.NewClient(config.AnthropicAPIKey)
	}

	if config.OpenAIAPIKey != "" {
		provider.clients["openai"] = openai.NewClient(config.OpenAIAPIKey)
	}

	if config.GoogleAPIKey != "" {
		provider.clients["google"] = openai.NewClient(config.GoogleAPIKey)
	}

	return provider
}

// NewProviderFromEnv creates a new LLM provider from environment variables
func NewProviderFromEnv() *Provider {
	config := Config{
		AnthropicAPIKey: os.Getenv("ANTHROPIC_API_KEY"),
		OpenAIAPIKey:    os.Getenv("OPENAI_API_KEY"),
		GoogleAPIKey:    os.Getenv("GOOGLE_API_KEY"),
		DefaultModel:    "claude-sonnet-4-20250514",
		MaxTokens:       4096,
		Timeout:         60 * time.Second,
	}
	return NewProvider(config)
}

// Generate generates a response from the LLM
func (p *Provider) Generate(ctx context.Context, prompt string, model string) (string, error) {
	// Resolve model to provider
	provider, modelName := p.resolveModel(model)

	client, ok := p.clients[provider]
	if !ok {
		// Return a template response if no client is available
		log.Printf("No LLM client available for provider: %s", provider)
		return p.generateTemplateResponse(prompt), nil
	}

	// Build request based on provider
	switch provider {
	case "anthropic":
		return p.generateAnthropic(ctx, client, prompt, modelName)
	case "openai":
		return p.generateOpenAI(ctx, client, prompt, modelName)
	case "google":
		return p.generateGoogle(ctx, client, prompt, modelName)
	default:
		return p.generateOpenAI(ctx, client, prompt, modelName)
	}
}

// generateAnthropic generates a response using Anthropic Claude
func (p *Provider) generateAnthropic(ctx context.Context, client *openai.Client, prompt string, model string) (string, error) {
	// Note: Using OpenAI client format for Claude via OpenAI compatibility
	// In production, you'd use the official Anthropic SDK
	req := openai.ChatCompletionRequest{
		Model: model,
		Messages: []openai.ChatCompletionMessage{
			{
				Role:    openai.ChatMessageRoleUser,
				Content: prompt,
			},
		},
		MaxTokens: p.config.MaxTokens,
	}

	resp, err := client.CreateChatCompletion(ctx, req)
	if err != nil {
		log.Printf("Anthropic API error: %v", err)
		return p.generateTemplateResponse(prompt), nil
	}

	if len(resp.Choices) > 0 {
		return resp.Choices[0].Message.Content, nil
	}

	return "", fmt.Errorf("no response from Anthropic")
}

// generateOpenAI generates a response using OpenAI
func (p *Provider) generateOpenAI(ctx context.Context, client *openai.Client, prompt string, model string) (string, error) {
	req := openai.ChatCompletionRequest{
		Model: model,
		Messages: []openai.ChatCompletionMessage{
			{
				Role:    openai.ChatMessageRoleUser,
				Content: prompt,
			},
		},
		MaxTokens: p.config.MaxTokens,
	}

	resp, err := client.CreateChatCompletion(ctx, req)
	if err != nil {
		log.Printf("OpenAI API error: %v", err)
		return p.generateTemplateResponse(prompt), nil
	}

	if len(resp.Choices) > 0 {
		return resp.Choices[0].Message.Content, nil
	}

	return "", fmt.Errorf("no response from OpenAI")
}

// generateGoogle generates a response using Google AI
func (p *Provider) generateGoogle(ctx context.Context, client *openai.Client, prompt string, model string) (string, error) {
	// Note: Using OpenAI client format for Google via OpenAI compatibility
	req := openai.ChatCompletionRequest{
		Model: model,
		Messages: []openai.ChatCompletionMessage{
			{
				Role:    openai.ChatMessageRoleUser,
				Content: prompt,
			},
		},
		MaxTokens: p.config.MaxTokens,
	}

	resp, err := client.CreateChatCompletion(ctx, req)
	if err != nil {
		log.Printf("Google API error: %v", err)
		return p.generateTemplateResponse(prompt), nil
	}

	if len(resp.Choices) > 0 {
		return resp.Choices[0].Message.Content, nil
	}

	return "", fmt.Errorf("no response from Google")
}

// GenerateWithSystem generates a response with system prompt
func (p *Provider) GenerateWithSystem(ctx context.Context, systemPrompt string, userPrompt string, model string) (string, error) {
	provider, modelName := p.resolveModel(model)

	client, ok := p.clients[provider]
	if !ok {
		return p.generateTemplateResponse(userPrompt), nil
	}

	req := openai.ChatCompletionRequest{
		Model: modelName,
		Messages: []openai.ChatCompletionMessage{
			{
				Role:    openai.ChatMessageRoleSystem,
				Content: systemPrompt,
			},
			{
				Role:    openai.ChatMessageRoleUser,
				Content: userPrompt,
			},
		},
		MaxTokens: p.config.MaxTokens,
	}

	resp, err := client.CreateChatCompletion(ctx, req)
	if err != nil {
		log.Printf("LLM API error: %v", err)
		return p.generateTemplateResponse(userPrompt), nil
	}

	if len(resp.Choices) > 0 {
		return resp.Choices[0].Message.Content, nil
	}

	return "", fmt.Errorf("no response from LLM")
}

// StreamGenerate generates a response with streaming
func (p *Provider) StreamGenerate(ctx context.Context, prompt string, model string) (<-chan string, error) {
	provider, modelName := p.resolveModel(model)

	client, ok := p.clients[provider]
	if !ok {
		ch := make(chan string, 1)
		ch <- p.generateTemplateResponse(prompt)
		close(ch)
		return ch, nil
	}

	req := openai.ChatCompletionRequest{
		Model: modelName,
		Messages: []openai.ChatCompletionMessage{
			{
				Role:    openai.ChatMessageRoleUser,
				Content: prompt,
			},
		},
		MaxTokens: p.config.MaxTokens,
		Stream:    true,
	}

	stream, err := client.CreateChatCompletionStream(ctx, req)
	if err != nil {
		log.Printf("LLM stream error: %v", err)
		ch := make(chan string, 1)
		ch <- p.generateTemplateResponse(prompt)
		close(ch)
		return ch, nil
	}

	ch := make(chan string)
	go func() {
		defer close(ch)
		defer stream.Close()

		for {
			resp, err := stream.Recv()
			if err != nil {
				break
			}

			if len(resp.Choices) > 0 {
				content := resp.Choices[0].Delta.Content
				if content != "" {
					ch <- content
				}
			}
		}
	}()

	return ch, nil
}

// IsAvailable checks if an LLM provider is available
func (p *Provider) IsAvailable(model string) bool {
	provider, _ := p.resolveModel(model)
	_, ok := p.clients[provider]
	return ok
}

// ListModels lists available models
func (p *Provider) ListModels() []string {
	models := []string{
		"claude-sonnet-4-20250514",
		"claude-opus-4-20250514",
		"gpt-4o",
		"gpt-4o-mini",
		"gpt-4-turbo",
	}
	return models
}

// === Private Methods ===

// resolveModel resolves a model name to provider and actual model
func (p *Provider) resolveModel(model string) (string, string) {
	if model == "" {
		model = p.config.DefaultModel
	}

	// Model name mappings
	mappings := map[string][2]string{
		"claude-sonnet-4-20250514": {"anthropic", "claude-sonnet-4-20250514"},
		"claude-opus-4-20250514":   {"anthropic", "claude-opus-4-20250514"},
		"claude-haiku-4-20250514":  {"anthropic", "claude-haiku-4-20250514"},
		"gpt-4o":                   {"openai", "gpt-4o"},
		"gpt-4o-mini":              {"openai", "gpt-4o-mini"},
		"gpt-4-turbo":              {"openai", "gpt-4-turbo"},
		"gpt-4":                    {"openai", "gpt-4"},
		"gemini-pro":               {"google", "gemini-pro"},
	}

	if mapping, ok := mappings[model]; ok {
		return mapping[0], mapping[1]
	}

	// Fallback: try to determine provider from model name
	if strings.Contains(model, "claude") {
		return "anthropic", model
	} else if strings.Contains(model, "gpt") || strings.Contains(model, "openai") {
		return "openai", model
	} else if strings.Contains(model, "gemini") {
		return "google", model
	}

	return "openai", model
}

// generateTemplateResponse generates a template-based response when LLM is unavailable
func (p *Provider) generateTemplateResponse(prompt string) string {
	// Extract key topics from prompt
	topic := extractTopic(prompt)

	return fmt.Sprintf(`[AI Response - Template]

Based on your query about "%s", here's a structured response:

## Key Points
- The topic requires careful consideration of multiple perspectives
- Evidence-based analysis is crucial for understanding
- Different models may provide varying insights

## Recommendations
1. Consider multiple sources of information
2. Evaluate arguments critically
3. Synthesize findings from different viewpoints

## Next Steps
- Explore related concepts in the knowledge base
- Start a debate to get multi-perspective analysis
- Create a wiki page to document findings

---
*Note: This is a template response. Configure an LLM API key for full AI capabilities.*`, topic)
}

// extractTopic extracts the main topic from a prompt
func extractTopic(prompt string) string {
	// Simple extraction - look for quoted text or key phrases
	if idx := strings.Index(prompt, "\""); idx != -1 {
		if endIdx := strings.Index(prompt[idx+1:], "\""); endIdx != -1 {
			return prompt[idx+1 : idx+1+endIdx]
		}
	}

	// Fallback: first 50 characters
	if len(prompt) > 50 {
		return prompt[:50] + "..."
	}
	return prompt
}
