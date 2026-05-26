# Architektur

## Grundidee

Die Anwendung wird als kleines, aber sauber geschichtetes Pythonprojekt aufgebaut. Streamlit ist nur die Oberfläche. Die eigentliche Fachlogik lebt in normalen Python-Modulen und ist unabhängig von Streamlit testbar.

## Schichten

```text
streamlit ui
    ↓
application services
    ↓
domain model
    ↓
infrastructure adapters
```

## Vorgeschlagene Modulstruktur

```text
memory_distiller/
  __init__.py
  app.py                       # Streamlit entrypoint
  domain/
    __init__.py
    memory_entry.py             # MemoryEntry, Scope, Type, Priority, Stability
    candidate.py                # MemoryCandidate, Verdict, Action
    validation.py               # fachliche Validierungsregeln
  application/
    __init__.py
    extraction_service.py       # orchestriert Extractor-Schritt
    validation_service.py       # orchestriert Validator-Schritt
    merge_service.py            # erzeugt aktualisierten Memory
    compression_service.py      # erzeugt promptfähigen Memoryblock
  prompts/
    __init__.py
    templates.py                # Prompt-Templates als Konstanten oder Loader
    render.py                   # Prompt Rendering
  io/
    __init__.py
    memory_parser.py            # Line-Format zu Domain-Objekten
    memory_writer.py            # Domain-Objekte zu Line-Format
    chat_importer.py            # TXT/Markdown-Import
  llm/
    __init__.py
    base.py                     # LlmClient Protocol
    manual.py                   # Prompt-only Client
    openai_client.py            # optionaler API-Adapter
  ui/
    __init__.py
    pages.py
    components.py
    state.py
  config.py
```

Tests:

```text
tests/
  domain/
  io/
  prompts/
  application/
```

## Warum diese Trennung?

Streamlit macht es leicht, Logik direkt in UI-Callbacks zu verstecken. Das wäre für einen Prototypen schnell, aber später schwer zu testen und zu erweitern.

Darum gilt:

- UI sammelt Eingaben und zeigt Ergebnisse.
- Application Services koordinieren Use Cases.
- Domain enthält Regeln und Datentypen.
- IO parst und schreibt Dateien.
- LLM-Adapter sind austauschbar.

## Zentrale Use Cases

### 1. Extract Memory Candidates

Input:

- Chatverlauf
- optional bestehender Memory

Output:

- Prompt für manuelle LLM-Nutzung oder
- LLM-Antwort mit Kandidaten

### 2. Validate Candidates

Input:

- bestehender Memory
- Chatverlauf
- Kandidaten

Output:

- validierte Kandidaten mit KEEP, EDIT, DROP, ASK oder CONFLICT

### 3. Merge Memory

Input:

- bestehender Memory
- validierte Kandidaten

Output:

- neue `memory_full.md`
- offene Klärungen
- deprecated Einträge

### 4. Compress Memory

Input:

- `memory_full.md`
- optional Projekt/Thema/Aufgabe

Output:

- kompakter `memory_prompt.md` oder `relevant_memory.md`

## Datenfluss im MVP

```text
chat log
  → extractor prompt
  → candidate lines
  → validator prompt
  → validated lines
  → merger
  → memory_full.md
  → compressor
  → memory_prompt.md
```

## Prompt-only vs. API-Modus

Der MVP sollte beide Modi unterstützen.

### Prompt-only-Modus

Die App erzeugt Prompts, die der User in ein externes LLM kopiert. Die Antwort wird danach wieder in die App eingefügt.

Vorteile:

- keine API-Keys nötig
- geringe Komplexität
- Datenschutz bleibt beim User kontrollierbar
- gut für den ersten Test

### API-Modus

Die App ruft ein LLM direkt über einen Adapter auf.

Vorteile:

- flüssiger Workflow
- später automatisierbar
- bessere UX

Der API-Modus darf die Domainlogik nicht verändern. Er ist nur eine andere Implementierung des LLM-Interfaces.

## Fehlerbehandlung

Fehler sollen explizit und verständlich behandelt werden:

- ungültiges Memory-Line-Format
- leere Inputs
- nicht parsebare Kandidaten
- fehlende API-Konfiguration
- LLM-Antwort passt nicht zum erwarteten Format

Keine stillen Fallbacks, die Daten verändern.

## Persistenz

Für den MVP reicht Datei-basierte Persistenz:

```text
data/
  memory_full.md
  memory_prompt.md
  chats/
  exports/
```

Das Repo sollte keine privaten Memory-Dateien committen. Dafür wird später `.gitignore` ergänzt.

## Erweiterungspunkte

Später möglich:

- SQLite für lokale Historie
- semantischer Retrieval-Schritt
- Browser-Extension
- automatische Provider-Integration
- Projektprofile
- Memory-Diff und Versionierung
