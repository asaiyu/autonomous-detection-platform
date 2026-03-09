# MCP Integration (Recommended)

This platform uses MCP (Model Context Protocol) to expose agent capabilities as tools.
The goal is to keep agents loosely coupled and composable.

## High-level
- Each agent may run an MCP server exposing tools.
- The orchestrator (Solutions Agent or a host) calls tools across agents.

## SIEM Agent MCP Tools (examples)
- search_events(query, time_range)
- search_alerts(query, time_range)
- get_alert_context(alert_id)
- run_replay(dataset_id, ruleset_id, mode)
- create_rule_proposal(rule_yaml, metadata)

## Attack Agent MCP Tools (examples)
- run_shannon(target, config)
- get_findings(run_id)
- run_synthetic_scenario(scenario_id, seed)
- export_dataset(run_id)

## Solutions Agent MCP Tools (examples)
- evaluate_coverage(finding_id)
- propose_rule(finding_id)
- validate_rule(proposal_id)

## Implementation Note (MVP)
MCP can be introduced incrementally:
- Start with HTTP APIs between services
- Add MCP wrappers for tool-like access
