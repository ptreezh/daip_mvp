// Package config provides configuration for DAIP-LIVE
package config

import (
	"os"
	"path/filepath"
)

// Config holds all configuration for DAIP-LIVE
type Config struct {
	Version              string
	StoragePath          string
	DefaultRoles         []string
	DefaultRounds        int
	MaxRounds            int
	MaxConcurrentDebates int
	MaxConcurrentWiki    int
	Models               Models
	LLMProviders         LLMProviders
}

// Models holds model configurations
type Models struct {
	Reasoning string
	Standard  string
	Fast      string
}

// LLMProviders holds LLM provider configurations
type LLMProviders struct {
	AnthropicAPIKey string
	OpenAIAPIKey    string
	GoogleAPIKey    string
	OllamaBaseURL   string
}

// LoadConfig loads configuration from environment and defaults
func LoadConfig(storagePath string) *Config {
	cfg := &Config{
		Version:              "1.0.0",
		StoragePath:          storagePath,
		DefaultRoles:         []string{"proponent", "opponent", "moderator"},
		DefaultRounds:        3,
		MaxRounds:            10,
		MaxConcurrentDebates: 10,
		MaxConcurrentWiki:    20,
		Models: Models{
			Reasoning: "claude-opus-4-20250514",
			Standard:  "claude-sonnet-4-20250514",
			Fast:      "claude-haiku-4-20250514",
		},
		LLMProviders: LLMProviders{
			AnthropicAPIKey: os.Getenv("ANTHROPIC_API_KEY"),
			OpenAIAPIKey:    os.Getenv("OPENAI_API_KEY"),
			GoogleAPIKey:    os.Getenv("GOOGLE_API_KEY"),
			OllamaBaseURL:   os.Getenv("OLLAMA_BASE_URL"),
		},
	}

	// Set default storage path
	if cfg.StoragePath == "" {
		home, err := os.UserHomeDir()
		if err == nil {
			cfg.StoragePath = filepath.Join(home, ".local", "share", "daip-live-opencode")
		}
	}

	return cfg
}

// GetAPIKey returns the appropriate API key for a provider
func (c *Config) GetAPIKey(provider string) string {
	switch provider {
	case "anthropic":
		return c.LLMProviders.AnthropicAPIKey
	case "openai":
		return c.LLMProviders.OpenAIAPIKey
	case "google":
		return c.LLMProviders.GoogleAPIKey
	default:
		return ""
	}
}
