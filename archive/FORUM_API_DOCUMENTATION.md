# 📚 Forum API Documentation

**Version**: V0.3.12 Forum Mode  
**Last Updated**: 2025-08-07  

## 📋 Overview

The Forum API provides comprehensive endpoints for managing multi-agent debate sessions, user interventions, and real-time consensus tracking. This documentation covers all Forum mode endpoints implemented in the DAIP-LIVE platform.

## 🔗 Base URL

```
http://localhost:8000/api/forum
```

## 📊 API Endpoints

### 1. Session Management

#### Create Forum Session
```http
POST /api/forum/session
```

**Description**: Create a new Forum session with multi-agent debate capabilities.

**Request Body**:
```json
{
  "topic": "讨论话题",
  "user_id": "default_user",
  "settings": {
    "max_agents": 5,
    "debate_rounds": 3,
    "consensus_threshold": 0.7
  }
}
```

**Response**:
```json
{
  "session_id": "forum_abc123",
  "topic": "讨论话题",
  "status": "active",
  "start_time": "2025-08-07T10:00:00",
  "active_agents": ["technical_expert", "business_analyst", "research_scientist"],
  "message_count": 0,
  "user_intervention_count": 0,
  "consensus_level": 0.0,
  "duration": 0.5
}
```

#### Get Session Context
```http
GET /api/forum/session/{session_id}
```

**Description**: Get detailed context information about a Forum session.

**Response**:
```json
{
  "session_id": "forum_abc123",
  "topic": "讨论话题",
  "status": "active",
  "consensus_level": 0.75,
  "active_agents": ["technical_expert", "business_analyst", "research_scientist"],
  "key_arguments": [
    {
      "content": "技术角度的分析...",
      "sender": "technical_expert",
      "timestamp": "2025-08-07T10:01:00",
      "importance": 0.8
    }
  ],
  "message_count": 15,
  "user_intervention_count": 2,
  "start_time": "2025-08-07T10:00:00",
  "duration": 120.5
}
```

#### Get Session Messages
```http
GET /api/forum/session/{session_id}/messages
```

**Description**: Get message history for a specific session.

**Response**:
```json
{
  "session_id": "forum_abc123",
  "messages": [
    {
      "sender": "technical_expert",
      "content": "从技术角度来看...",
      "timestamp": "2025-08-07T10:01:00",
      "message_type": "agent_response"
    },
    {
      "sender": "user",
      "content": "我需要更详细的解释",
      "timestamp": "2025-08-07T10:02:00",
      "message_type": "user_intervention"
    }
  ],
  "message_count": 15,
  "timestamp": "2025-08-07T10:15:00"
}
```

#### List Active Sessions
```http
GET /api/forum/sessions
```

**Description**: Get all active Forum sessions.

**Response**:
```json
{
  "sessions": [
    {
      "session_id": "forum_abc123",
      "topic": "AI技术发展趋势",
      "status": "active",
      "start_time": "2025-08-07T10:00:00",
      "active_agents": ["technical_expert", "business_analyst"],
      "message_count": 15
    }
  ],
  "count": 1,
  "timestamp": "2025-08-07T10:15:00"
}
```

### 2. User Intervention

#### Handle User Intervention
```http
POST /api/forum/intervention
```

**Description**: Process user intervention in an ongoing Forum session.

**Request Body**:
```json
{
  "session_id": "forum_abc123",
  "message": {
    "content": "我需要更详细的技术解释",
    "timestamp": "2025-08-07T10:02:00"
  },
  "intent": "question"
}
```

**Response**:
```json
{
  "status": "integrated",
  "optimized_input": "关于AI技术发展趋势，我需要更详细的技术解释",
  "session_id": "forum_abc123",
  "timestamp": "2025-08-07T10:02:00"
}
```

#### Optimize User Input
```http
POST /api/forum/session/{session_id}/optimize
```

**Description**: Optimize user input for better collaboration.

**Request Body**:
```json
{
  "input": "解释一下这个技术",
  "intent": "question"
}
```

**Response**:
```json
{
  "original_input": "解释一下这个技术",
  "optimized_input": "关于AI技术发展趋势，能否详细解释一下相关技术细节？",
  "intent": "question",
  "session_id": "forum_abc123",
  "timestamp": "2025-08-07T10:02:00"
}
```

### 3. Session Control

#### Control Session
```http
POST /api/forum/control
```

**Description**: Control session state (pause, resume, end).

**Request Body**:
```json
{
  "session_id": "forum_abc123",
  "action": "pause"
}
```

**Response**:
```json
{
  "status": "success",
  "action": "pause",
  "session_id": "forum_abc123",
  "timestamp": "2025-08-07T10:15:00"
}
```

#### Delete Session
```http
DELETE /api/forum/session/{session_id}
```

**Description**: Delete a Forum session.

**Response**:
```json
{
  "status": "deleted",
  "session_id": "forum_abc123",
  "result": {
    "session_id": "forum_abc123",
    "topic": "AI技术发展趋势",
    "duration": 900.0,
    "total_messages": 45,
    "user_interventions": 8,
    "final_consensus": {
      "consensus_level": 0.82,
      "summary": "高度共识：参与者对AI技术发展趋势有很强的一致性"
    }
  },
  "timestamp": "2025-08-07T10:15:00"
}
```

### 4. Monitoring and Statistics

#### Get Forum Statistics
```http
GET /api/forum/statistics
```

**Description**: Get comprehensive Forum service statistics.

**Response**:
```json
{
  "total_sessions": 25,
  "active_sessions": 3,
  "total_messages": 342,
  "total_interventions": 67,
  "average_consensus": 0.76
}
```

#### Forum Health Check
```http
GET /api/forum/health
```

**Description**: Check Forum service health status.

**Response**:
```json
{
  "status": "healthy",
  "service": "forum",
  "active_sessions": 3,
  "statistics": {
    "total_sessions": 25,
    "active_sessions": 3,
    "total_messages": 342,
    "total_interventions": 67,
    "average_consensus": 0.76
  },
  "timestamp": "2025-08-07T10:15:00"
}
```

## 📋 Data Models

### ForumSessionRequest
```typescript
interface ForumSessionRequest {
  topic: string;
  user_id?: string;
  settings?: Record<string, any>;
}
```

### UserInterventionRequest
```typescript
interface UserInterventionRequest {
  session_id: string;
  message: {
    content: string;
    timestamp?: string;
  };
  intent?: string;
}
```

### SessionControlRequest
```typescript
interface SessionControlRequest {
  session_id: string;
  action: 'pause' | 'resume' | 'end';
}
```

### ForumSessionResponse
```typescript
interface ForumSessionResponse {
  session_id: string;
  topic: string;
  status: string;
  start_time: string;
  active_agents: string[];
  message_count: number;
  user_intervention_count: number;
  consensus_level: number;
  duration: number;
}
```

### SessionContextResponse
```typescript
interface SessionContextResponse {
  session_id: string;
  topic: string;
  status: string;
  consensus_level: number;
  active_agents: string[];
  key_arguments: Array<{
    content: string;
    sender: string;
    timestamp: string;
    importance: number;
  }>;
  message_count: number;
  user_intervention_count: number;
  start_time: string;
  duration: number;
}
```

### ForumStatisticsResponse
```typescript
interface ForumStatisticsResponse {
  total_sessions: number;
  active_sessions: number;
  total_messages: number;
  total_interventions: number;
  average_consensus: number;
}
```

## 🔄 WebSocket Integration

The Forum mode supports real-time communication through WebSocket connections:

### WebSocket Events

#### Session Updates
```json
{
  "event": "session_update",
  "session_id": "forum_abc123",
  "data": {
    "status": "active",
    "consensus_level": 0.75,
    "message_count": 15,
    "timestamp": "2025-08-07T10:15:00"
  }
}
```

#### New Messages
```json
{
  "event": "new_message",
  "session_id": "forum_abc123",
  "message": {
    "sender": "technical_expert",
    "content": "从技术角度来看...",
    "timestamp": "2025-08-07T10:15:00",
    "message_type": "agent_response"
  }
}
```

#### Consensus Updates
```json
{
  "event": "consensus_update",
  "session_id": "forum_abc123",
  "data": {
    "consensus_level": 0.78,
    "key_arguments": [...],
    "timestamp": "2025-08-07T10:15:00"
  }
}
```

## ⚡ Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "FORUM_SERVICE_ERROR",
    "message": "Session not found",
    "timestamp": "2025-08-07T10:15:00",
    "status_code": 404
  }
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | VALIDATION_ERROR | Invalid request parameters |
| 404 | SESSION_NOT_FOUND | Forum session not found |
| 400 | FORUM_SERVICE_ERROR | Forum service specific error |
| 500 | INTERNAL_ERROR | Internal server error |

## 🎯 Usage Examples

### Basic Forum Session
```javascript
// Create a new Forum session
const session = await fetch('/api/forum/session', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    topic: 'AI技术发展趋势',
    user_id: 'user123'
  })
});

// Handle user intervention
const intervention = await fetch('/api/forum/intervention', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: 'forum_abc123',
    message: {
      content: '我需要更详细的技术解释'
    },
    intent: 'question'
  })
});

// Get session context
const context = await fetch('/api/forum/session/forum_abc123');
```

### Real-time Updates
```javascript
// WebSocket connection for real-time updates
const ws = new WebSocket('ws://localhost:8000/ws/forum/forum_abc123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.event) {
    case 'session_update':
      console.log('Session updated:', data.data);
      break;
    case 'new_message':
      console.log('New message:', data.message);
      break;
    case 'consensus_update':
      console.log('Consensus updated:', data.data);
      break;
  }
};
```

## 🔧 Configuration

### Session Settings
```json
{
  "max_agents": 5,
  "debate_rounds": 3,
  "consensus_threshold": 0.7,
  "intervention_optimization": true,
  "real_time_updates": true
}
```

### Agent Selection
The system automatically selects agents based on the topic, but you can also specify preferred agents:

```json
{
  "topic": "AI技术发展趋势",
  "settings": {
    "preferred_agents": ["technical_expert", "business_analyst"],
    "agent_selection_strategy": "topic_based"
  }
}
```

## 📊 Performance Metrics

### Response Times
- Session creation: < 1.5 seconds
- User intervention processing: < 1.0 seconds
- Context retrieval: < 0.5 seconds
- Real-time updates: < 100ms

### Throughput
- Concurrent sessions: 100+
- Messages per second: 50+
- WebSocket connections: 1000+

## 🔒 Security Considerations

- All endpoints require proper authentication
- Session IDs are UUID-based and secure
- User input validation and sanitization
- Rate limiting for API endpoints
- WebSocket connection authentication

## 📝 Best Practices

1. **Session Management**: Always end sessions when no longer needed
2. **User Interventions**: Use appropriate intent types for better optimization
3. **Error Handling**: Implement proper error handling for all API calls
4. **Real-time Updates**: Use WebSocket connections for live updates
5. **Resource Management**: Monitor session counts and resource usage

## 🚀 Next Steps

- Enhanced consensus algorithms
- Multi-language support
- Advanced agent selection strategies
- Forum templates and presets
- Analytics and reporting features

---

**Generated**: 2025-08-07  
**Version**: V0.3.12 Forum Mode  
**Status**: Production Ready ✅