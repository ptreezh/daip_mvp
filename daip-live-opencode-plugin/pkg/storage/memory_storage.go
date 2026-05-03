// Package storage 提供内存中的存储实现，用于测试
package storage

import (
	"fmt"
	"sync"

	"github.com/daip-live/daip-live-opencode-plugin/pkg/interfaces"
	"github.com/daip-live/daip-live-opencode-plugin/pkg/models"
)

// MemoryStorage 提供内存中的存储实现
type MemoryStorage struct {
	mutex                sync.RWMutex
	debates             map[string]*models.DebateSession
	wikis               map[string]*models.WikiPage
	knowledgeConcepts   map[string]*models.KnowledgeConcept
	knowledgeRelations  map[string]*models.KnowledgeRelation
}

// NewMemoryStorage 创建新的内存存储实例
func NewMemoryStorage() *MemoryStorage {
	return &MemoryStorage{
		debates:            make(map[string]*models.DebateSession),
		wikis:              make(map[string]*models.WikiPage),
		knowledgeConcepts:  make(map[string]*models.KnowledgeConcept),
		knowledgeRelations: make(map[string]*models.KnowledgeRelation),
	}
}

// SaveDebate 保存辩论会话
func (ms *MemoryStorage) SaveDebate(session *models.DebateSession) error {
	ms.mutex.Lock()
	defer ms.mutex.Unlock()

	ms.debates[session.ID] = session
	return nil
}

// GetDebate 获取辩论会话
func (ms *MemoryStorage) GetDebate(sessionID string) (*models.DebateSession, error) {
	ms.mutex.RLock()
	defer ms.mutex.RUnlock()

	session, exists := ms.debates[sessionID]
	if !exists {
		return nil, nil // 符合接口约定，返回nil表示未找到
	}

	return session, nil
}

// ListDebates 列出辩论会话
func (ms *MemoryStorage) ListDebates(limit int) ([]*models.DebateSession, error) {
	ms.mutex.RLock()
	defer ms.mutex.RUnlock()

	var sessions []*models.DebateSession
	for _, session := range ms.debates {
		sessions = append(sessions, session)
	}

	// 如果指定了限制，则截取结果
	if limit > 0 && len(sessions) > limit {
		sessions = sessions[:limit]
	}

	return sessions, nil
}

// SaveWiki 保存维基页面
func (ms *MemoryStorage) SaveWiki(page *models.WikiPage) error {
	ms.mutex.Lock()
	defer ms.mutex.Unlock()

	ms.wikis[page.ID] = page
	return nil
}

// GetWiki 获取维基页面
func (ms *MemoryStorage) GetWiki(pageID string) (*models.WikiPage, error) {
	ms.mutex.RLock()
	defer ms.mutex.RUnlock()

	page, exists := ms.wikis[pageID]
	if !exists {
		return nil, nil // 符合接口约定，返回nil表示未找到
	}

	return page, nil
}

// ListWikis 列出维基页面
func (ms *MemoryStorage) ListWikis() ([]*models.WikiPage, error) {
	ms.mutex.RLock()
	defer ms.mutex.RUnlock()

	var pages []*models.WikiPage
	for _, page := range ms.wikis {
		pages = append(pages, page)
	}

	return pages, nil
}

// SaveWikiVersion 保存维基版本
func (ms *MemoryStorage) SaveWikiVersion(pageID string, version *models.WikiVersion) error {
	ms.mutex.Lock()
	defer ms.mutex.Unlock()

	page, exists := ms.wikis[pageID]
	if !exists {
		return fmt.Errorf("wiki page not found: %s", pageID)
	}

	// 更新页面内容
	page.Content = version.Content
	page.Version = version.Version

	return nil
}

// SaveKnowledgeConcept 保存知识概念
func (ms *MemoryStorage) SaveKnowledgeConcept(concept *models.KnowledgeConcept) error {
	ms.mutex.Lock()
	defer ms.mutex.Unlock()

	if concept.ID == "" {
		// 生成一个简单的ID（在实际实现中，这可能使用UUID）
		concept.ID = fmt.Sprintf("concept-%d", len(ms.knowledgeConcepts)+1)
	}

	ms.knowledgeConcepts[concept.ID] = concept
	return nil
}

// GetKnowledgeConcept 获取知识概念
func (ms *MemoryStorage) GetKnowledgeConcept(conceptID string) (*models.KnowledgeConcept, error) {
	ms.mutex.RLock()
	defer ms.mutex.RUnlock()

	concept, exists := ms.knowledgeConcepts[conceptID]
	if !exists {
		return nil, nil // 符合接口约定，返回nil表示未找到
	}

	return concept, nil
}

// SaveKnowledgeRelation 保存知识关系
func (ms *MemoryStorage) SaveKnowledgeRelation(relation *models.KnowledgeRelation) error {
	ms.mutex.Lock()
	defer ms.mutex.Unlock()

	if relation.ID == "" {
		// 生成一个简单的ID（在实际实现中，这可能使用UUID）
		relation.ID = fmt.Sprintf("relation-%d", len(ms.knowledgeRelations)+1)
	}

	ms.knowledgeRelations[relation.ID] = relation
	return nil
}

// SearchKnowledgeConcepts 搜索知识概念
func (ms *MemoryStorage) SearchKnowledgeConcepts(query string, limit int) ([]*models.KnowledgeConcept, error) {
	ms.mutex.RLock()
	defer ms.mutex.RUnlock()

	var results []*models.KnowledgeConcept
	queryLower := toLower(query)

	for _, concept := range ms.knowledgeConcepts {
		if contains(toLower(concept.Name), queryLower) || 
		   contains(toLower(concept.Description), queryLower) {
			results = append(results, concept)
		}
	}

	// 如果指定了限制，则截取结果
	if limit > 0 && len(results) > limit {
		results = results[:limit]
	}

	return results, nil
}

// Close 关闭存储连接
func (ms *MemoryStorage) Close() error {
	// 内存存储不需要关闭操作
	return nil
}

// 辅助函数
func toLower(s string) string {
	// 简单的转小写实现（仅支持ASCII）
	result := make([]byte, len(s))
	for i := 0; i < len(s); i++ {
		c := s[i]
		if c >= 'A' && c <= 'Z' {
			c = c - 'A' + 'a'
		}
		result[i] = c
	}
	return string(result)
}

func contains(s, substr string) bool {
	sLen := len(s)
	subLen := len(substr)
	if subLen == 0 {
		return true
	}
	if subLen > sLen {
		return false
	}
	for i := 0; i <= sLen-subLen; i++ {
		match := true
		for j := 0; j < subLen; j++ {
			if s[i+j] != substr[j] {
				match = false
				break
			}
		}
		if match {
			return true
		}
	}
	return false
}