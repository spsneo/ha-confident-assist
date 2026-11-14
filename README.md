# Confident Assist

A Home Assistant conversation agent for Assist. It acts on a voice command only
when it is sure. When it is not sure, it gives the full sentence to a fallback
agent, such as an LLM.

A decision API reads each sentence and gives typed answers with a confidence.
Decision APIs and fallback agents are providers, so new ones are easy to add.

Status: in development. Not ready to install yet.

Requires Home Assistant 2026.11 or newer.

## Development

See [CLAUDE.md](CLAUDE.md) for the rules and the checks to run.
