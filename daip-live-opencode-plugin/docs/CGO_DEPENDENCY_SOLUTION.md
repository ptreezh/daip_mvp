# 解决CGO依赖问题的方案

## 问题背景

OpenCode插件系统原本使用SQLite数据库，依赖于`github.com/mattn/go-sqlite3`包，该包需要CGO支持。这导致在某些环境中无法运行Go单元测试。

## 解决方案

我们采用了以下解决方案来消除对CGO的依赖：

### 1. 使用纯Go SQLite实现

项目使用了 `github.com/glebarez/go-sqlite`，这是一个纯Go的SQLite实现，不需要CGO。该包使用纯Go编写的SQLite绑定，避免了对C库的依赖。

### 2. 内存存储实现

为了解决测试环境中的CGO问题，我们创建了内存存储实现（MemoryStorage），用于：

- 单元测试：避免依赖外部数据库
- 集成测试：提供快速、隔离的测试环境
- CI/CD环境：无需配置数据库环境

### 3. 存储适配器模式

实现了存储接口抽象，允许在不同存储后端之间切换：

```go
// interfaces/storage.go
type Storage interface {
    // Debate Operations
    SaveDebate(session *models.DebateSession) error
    GetDebate(sessionID string) (*models.DebateSession, error)
    ListDebates(limit int) ([]*models.DebateSession, error)
    
    // Wiki Operations
    SaveWiki(page *models.WikiPage) error
    GetWiki(pageID string) (*models.WikiPage, error)
    ListWikis() ([]*models.WikiPage, error)
    SaveWikiVersion(pageID string, version *models.WikiVersion) error
    
    // Knowledge Operations
    SaveKnowledgeConcept(concept *models.KnowledgeConcept) error
    GetKnowledgeConcept(conceptID string) (*models.KnowledgeConcept, error)
    SaveKnowledgeRelation(relation *models.KnowledgeRelation) error
    SearchKnowledgeConcepts(query string, limit int) ([]*models.KnowledgeConcept, error)
    
    // 关闭连接
    Close() error
}
```

### 4. 测试策略

- **单元测试**：使用内存存储实现，无需CGO
- **集成测试**：在支持CGO的环境中使用SQLite存储
- **端到端测试**：使用内存存储实现

## 优势

1. **跨平台兼容性**：无需配置CGO环境
2. **简化部署**：更容易在各种环境中部署
3. **快速测试**：内存存储提供更快的测试执行速度
4. **灵活性**：可以根据环境选择合适的存储后端

## 验证

所有Go测试现在都可以在CGO禁用的环境中运行：

```bash
SET CGO_ENABLED=0
go test ./pkg/...
```

测试结果：
- ✅ 所有存储相关测试通过
- ✅ 论坛功能测试通过
- ✅ 维基功能测试通过
- ✅ 知识图谱功能测试通过

## 生产环境考虑

在生产环境中，系统将继续使用SQLite存储（通过纯Go实现），以确保数据持久化和性能。内存存储仅用于测试环境。