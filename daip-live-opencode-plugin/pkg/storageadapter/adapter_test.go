package storageadapter

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestStorageAdapter(t *testing.T) {
	// Create a temporary directory for testing
	tempDir := t.TempDir()

	// Test SQLite storage adapter
	t.Run("SQLite Storage Adapter", func(t *testing.T) {
		factory := &StorageAdapterFactory{}
		
		storage, err := factory.NewSQLiteStorageAdapter(tempDir)
		require.NoError(t, err)
		require.NotNil(t, storage)
		
		// Test basic functionality
		// Note: We're not testing the actual SQLite functionality here since that requires CGO
		// Instead, we're testing that the adapter can be created properly
		assert.NotNil(t, storage)
	})

	// Test memory storage adapter (for testing environments without CGO)
	t.Run("Memory Storage Adapter", func(t *testing.T) {
		factory := &StorageAdapterFactory{}
		
		storage := factory.NewMemoryStorageAdapter()
		require.NotNil(t, storage)
		
		// Test basic functionality of memory storage
		// This can be fully tested without CGO
		assert.NotNil(t, storage)
	})
}