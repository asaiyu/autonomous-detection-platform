# Agents Architecture

The platform contains three logical agents:

1. **Attack Agent**
2. **SIEM Agent**
3. **Solutions Agent**

Agents should be loosely coupled. Communication occurs via:
- HTTP APIs between services
- MCP tool interfaces for AI-orchestrated operations (recommended)

## Agent Communication Contract

All agents must share stable data contracts for:
- Finding objects
- Canonical Events (docs/08_event_schema.md)
- Coverage Evaluation results
- Rule Proposals
- Replay Validation reports

## Anti-goals
- Direct database coupling between agents
- Hidden, undocumented internal calls
