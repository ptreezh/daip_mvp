// Package storageadapter provides adapter implementations for different storage backends
package storageadapter

import (
	"github.com/daip-live/daip-live-opencode-plugin/pkg/interfaces"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/storage"
)

// StorageAdapterFactory provides factory methods to create storage adapters
type StorageAdapterFactory struct{}

// NewSQLiteStorageAdapter creates a new SQLite storage adapter
func (f *StorageAdapterFactory) NewSQLiteStorageAdapter(storagePath string) (interfaces.Storage, error) {
	sqliteStorage, err := storage.NewSQLiteStorage(storagePath)
	if err != nil {
		return nil, err
	}
	return sqliteStorage, nil
}

// NewMemoryStorageAdapter creates a new memory storage adapter for testing
func (f *StorageAdapterFactory) NewMemoryStorageAdapter() interfaces.Storage {
	return storage.NewMemoryStorage()
}