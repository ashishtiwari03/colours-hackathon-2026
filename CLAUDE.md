# COLOURS Hackathon 2026 — Workplace Reinvented

## Context
Building a Streamlit app for the COLOURS "Workplace Reinvented" hackathon
(Apr 28-30, 2026, Ventspils University, hybrid). Theme: workplace well-being
and mental health.

The specific project direction will be decided on Tuesday Apr 28 at ~11:00
once the regional company challenges are announced. Until then, this is a
generic Streamlit + Mistral scaffold.

## Hard constraints (always apply)
- Python 3.11+, Windows
- Stack: Streamlit, Mistral API, JSON files. Nothing else.
- No FastAPI, no LangGraph, no database, no auth, no new dependencies
  beyond requirements.txt without explicit confirmation.
- Demo-grade code, not production. Concise, working, ugly-OK.
- All Mistral calls must have a cached JSON fallback (api can fail
  during live demo).
- Free tier: be mindful of Mistral API quota.

## File layout (current)
- app.py — main Streamlit app
- utils/mistral_client.py — Mistral wrapper with caching
- utils/ — additional helpers as needed
- data/ — JSON data files
- data/mistral_cache/ — pre-generated AI fallbacks
- requirements.txt
- .env (MISTRAL_API_KEY)

## Coding style
- Concise. Demo-grade.
- f-strings, type hints on functions, minimal comments
- Streamlit idioms: st.tabs, st.columns, session_state for ephemeral data
- Cache Mistral calls with @st.cache_data when possible

## Project specifics (TO BE FILLED IN ON TUESDAY)
Project name:
One-sentence pitch:
Target user(s):
Core features (max 4):
Personas/demo data: