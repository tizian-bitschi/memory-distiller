# Known MVP Limitations

This document describes known limitations of the current MVP implementation. These are not bugs to fix in the MVP itself — they are scoped out or tracked separately.

## LLM Output Format

The parsers expect LLM responses in specific pipe-delimited formats. Malformed output can cause parse failures. Users must manually correct LLM output or re-prompt when format expectations are not met.

## No Deterministic Merger

The merge step still relies on an LLM call. There is no deterministic merge logic yet. The same inputs may produce different outputs across runs.

## No Persistence

The app holds all data in Streamlit session state. Refreshing the page or restarting the app clears all data. There is no database and no automatic file writing.

## No User Accounts

There is no authentication or user management. Anyone with access to the running app can use it.

## No Automatic ChatGPT History Import

The app does not read or import ChatGPT conversation history automatically. Users must manually paste or upload chat logs.

## No Built-in Authentication

The Streamlit app has no password protection or access control. Deployment-related authentication is tracked separately.

## No Production Deployment

The app is not yet deployed to a hosting platform. Deployment steps are tracked in separate issues.

## Privacy Depends on LLM Provider

In API mode, chat logs and memory content are sent to DeepSeek. Privacy depends on the provider's policies. Users must ensure they are comfortable with this before using API mode.

## Compression Output in Prompt-Only Mode

In prompt-only mode, the Compress tab displays only the generated prompt. There is no output parsing or display of the resulting memory prompt block. Users must paste the LLM response and interpret it themselves.

## UI Modularization

The MVP UI has been split into smaller tab modules, but further UX improvements may still be useful.