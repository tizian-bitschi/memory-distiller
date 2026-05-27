# Memory Distiller

Memory Distiller ist ein MVP für die Extraktion, Pflege und Wiederverwendung von persistentem Arbeitskontext aus LLM-Chatverläufen.

Das Projekt startet bewusst klein: Eine Streamlit-App nimmt Chatverläufe entgegen, erzeugt Memory-Kandidaten über LLM-Prompts, validiert diese Kandidaten und schreibt daraus kompakte Memory-Dateien, die anschließend in neue LLM-Chats eingefügt werden können.

## Problem

Bei täglicher Arbeit mit LLM-Chats gehen projektspezifische Regeln, persönliche Arbeitspräferenzen, Entscheidungen und wiederkehrende Constraints zwischen neuen Chats verloren. Dadurch müssen dieselben Regeln immer wieder manuell erklärt werden.

Memory Distiller soll nicht einfach Chatverläufe zusammenfassen, sondern wiederverwendbares Handlungswissen extrahieren:

- globale Arbeitsregeln
- projektbezogene Regeln
- technische Entscheidungen
- Stil- und Quellenpräferenzen
- Vermeidungsregeln
- offene Klärungen
- temporärer Kontext mit Ablaufcharakter

## What It Does

Memory Distiller extracts reusable working knowledge from LLM chat logs:

- global work rules
- project-specific rules
- technical decisions
- style and source preferences
- avoidance rules
- open questions
- temporary context with expiration

## Current MVP Capabilities

The MVP supports two modes:

**Prompt-only mode** (no API key required):
- Extract memory candidates from chat logs via generated prompts
- User runs the prompts externally in their LLM chat
- User pastes the LLM response back into the app
- App parses and processes the response

**API mode with DeepSeek** (requires `DEEPSEEK_API_KEY`):
- Runs the full pipeline automatically
- Extract candidates, validate with LLM, merge results
- Compress into prompt-friendly format

**Shared features**:
- Streamlit UI with 6-tab pipeline
- Upload `.txt`, `.md`, `.markdown` files
- Session-only uploads (no hidden file writes)
- Download results as artifacts
- Global and project-specific memory separation

## MVP-Ziel

Der MVP soll einen manuellen, aber zuverlässigen Workflow unterstützen:

1. Chatverlauf einfügen oder hochladen.
2. Bestehenden Memory laden.
3. Memory-Kandidaten extrahieren.
4. Kandidaten kritisch validieren.
5. Memory-Datei aktualisieren.
6. Kompakten Prompt-Memoryblock erzeugen.

Automatische Hintergrundprozesse, User-Accounts, Vektordatenbanken und Multi-User-Support gehören nicht zum ersten MVP.

## Erste API-Integration

Der erste konkrete API-Provider für die Umsetzung ist DeepSeek V4.

Geplanter Default:

```text
deepseek-v4-pro
```

Prompt-only bleibt als Fallback erhalten. DeepSeek wird über eine austauschbare LLM-Adapter-Schicht integriert und darf nicht direkt in der Streamlit-UI oder Domainlogik verdrahtet werden.

## Kernprinzipien

- Hohe Precision ist wichtiger als hoher Recall.
- Keine Assistentenvorschläge als User-Entscheidungen speichern.
- Jede dauerhafte Memory-Regel braucht einen belegbaren Ursprung.
- Globale und projektbezogene Regeln strikt trennen.
- Negative Regeln sind wichtig: "nicht tun" ist ein eigenständiger Memory-Typ.
- Memory muss kompakt genug bleiben, um in neue Chats eingefügt werden zu können.
- Das System soll einfach bleiben, aber sauber strukturiert und testbar sein.

## Geplanter Tech-Stack

- Python
- Streamlit für die MVP-Oberfläche
- Plain-Text/Markdown-Dateien als Speicherformat
- DeepSeek V4 als erster API-Provider
- LLM-Anbieter über eine abstrahierte Adapter-Schicht
- pytest für Tests
- ruff und mypy für statische Qualitätssicherung

Konkrete Paketversionen werden später im `pyproject.toml` festgelegt.

## Dokumentation

- [MVP Scope](docs/01_mvp_scope.md)
- [Architektur](docs/02_architecture.md)
- [Memory-Modell und Speicherformat](docs/03_memory_model.md)
- [Prompt-Pipeline](docs/04_prompt_pipeline.md)
- [Streamlit UX](docs/05_streamlit_ux.md)
- [Code-Qualität und Tests](docs/06_quality_and_testing.md)
- [Privacy und Sicherheit](docs/07_security_and_privacy.md)
- [Offene Entscheidungen](docs/08_open_decisions.md)
- [DeepSeek V4 Provider](docs/09_deepseek_provider.md)
- [Known Limitations](docs/known_limitations.md)

## Usage

See [docs/usage.md](docs/usage.md) for detailed usage instructions.

See [examples/README.md](examples/README.md) for a walkthrough with synthetic data.

See [docs/known_limitations.md](docs/known_limitations.md) for current limitations.

## Nicht-Ziele für den MVP

- kein automatisches Lesen aller ChatGPT-Verläufe
- keine Browser-Extension
- keine Cloud-Synchronisierung
- keine Multi-User-Verwaltung
- keine automatische Memory-Injektion in fremde LLM-Tools
- kein komplexes RAG-System
- keine Vektordatenbank im ersten Schritt

## CI and Deployment

CI and deployment workflows are defined in `.github/workflows/`.

- [Deployment documentation](infra/deploy/github-actions.md)
- [VPS deployment guide](infra/deploy/README.md)

## Future Work

- Streamlit UI refactor: [#7](https://github.com/tizian-bitschi/memory-distiller/issues/7)
- Production deployment with Docker/Nginx: [#8](https://github.com/tizian-bitschi/memory-distiller/issues/8)
- GitHub Actions deployment workflow: [#9](https://github.com/tizian-bitschi/memory-distiller/issues/9)

## Lizenz

Noch offen.

## Local Setup

### Requirements

- Python >= 3.11

### Installation

```bash
python -m pip install -e ".[dev]"
```

### Validation

Run tests:

```bash
pytest
```

Run linters:

```bash
ruff check .
ruff format --check .
```

Run type checker:

```bash
mypy memory_distiller
```

### Start App

```bash
streamlit run memory_distiller/app.py
```

### Upload & Export

Unterstützte Upload-Typen: `.txt`, `.md`, `.markdown`

Exporte werden als Download generiert, nicht automatisch gespeichert. Kein verstecktes Schreiben auf die lokale Festplatte.

API-Key wird ausschliesslich ueber die Environment-Variable `DEEPSEEK_API_KEY` gelesen.
