# Code-Qualität und Tests

## Ziel

Memory Distiller ist ein kleines Pythonprojekt, soll aber von Anfang an wie ein ernsthaft wartbares Tool aufgebaut werden. Der wichtigste Qualitätsgrundsatz: Fachlogik darf nicht in der Streamlit-UI verschwinden.

## Qualitätsstandards

- Python-Code mit Type Hints.
- Domänenlogik in eigenen Modulen.
- Streamlit nur als UI-Schicht.
- Parser und Writer vollständig testbar.
- Keine versteckten Seiteneffekte.
- Keine stillen Korrekturen bei kaputtem Input.
- Explizite Fehlerobjekte oder Exceptions mit klaren Messages.
- Kleine Funktionen mit eindeutiger Verantwortung.
- Keine unnötige Abstraktion vor tatsächlichem Bedarf.

## Tooling

Geplant:

```text
ruff      # linting und formatting
mypy      # statische Typprüfung
pytest    # Tests
coverage  # Testabdeckung
```

Später im `pyproject.toml` festlegen.

## Empfohlene pyproject-Grundsätze

- Python-Version festlegen, z. B. `>=3.11`.
- Ruff als Formatter und Linter nutzen.
- mypy mindestens für `memory_distiller/` aktivieren.
- Tests unter `tests/`.
- Keine privaten Daten in Testfixtures.

## Teststrategie

### Unit Tests

Priorität 1:

- Memory-Line-Parser
- Memory-Line-Writer
- Candidate-Parser
- Validator für Enum-Werte
- Compressor-Auswahlregeln, soweit deterministisch
- Prompt-Rendering

### Integration Tests

Priorität 2:

- vollständiger Prompt-only-Flow mit Fixture-Texten
- Memory alt + Kandidaten → Memory neu
- Fehlerhafte LLM-Antwort → parsebarer Fehler

### Snapshot Tests

Nützlich für:

- Prompt-Templates
- erzeugte Markdown-Dateien
- Beispiel-Memoryblöcke

Snapshot Tests sollten bewusst aktualisiert werden, nicht automatisch.

## Kein Test gegen echte LLMs im Standardlauf

Der normale Testlauf darf keine externen LLM-APIs aufrufen.

LLM-Tests sind optional und müssen klar markiert sein, z. B.:

```text
@pytest.mark.integration_llm
```

## Parser-Verhalten

Parser sollen streng sein:

- falsche Spaltenanzahl → ParseError
- unbekannter Scope-Typ → ParseError
- unbekannte Priority → ParseError
- unbekannte Stability → ParseError
- leere Pflichtfelder → ParseError

Aber:

- Zeilennummern in Fehlermeldungen angeben
- mehrere Fehler sammeln, wenn sinnvoll
- UI soll Fehler verständlich anzeigen

## Domänenmodell

Vorgesehene Typen:

```python
from dataclasses import dataclass
from enum import Enum

class MemoryType(str, Enum):
    RULE = "RULE"
    PREF = "PREF"
    FACT = "FACT"
    DECISION = "DECISION"
    AVOID = "AVOID"
    STYLE = "STYLE"
    SOURCE = "SOURCE"
    TERM = "TERM"
    TASK = "TASK"
    CONFLICT = "CONFLICT"

@dataclass(frozen=True)
class MemoryEntry:
    scope: str
    type: MemoryType
    priority: str
    stability: str
    statement: str
    evidence: str
```

Das ist nur eine grobe Skizze. Die konkrete Implementierung darf davon abweichen, soll aber ähnlich explizit bleiben.

## Streamlit-Regeln

Nicht direkt in Streamlit:

- Parsing
- Merging
- Prompt-Rendering-Logik
- LLM-Client-Logik
- Validierungsregeln

Streamlit darf:

- Inputs sammeln
- Services aufrufen
- Status anzeigen
- Downloads anbieten
- Session State verwalten

## Commit-Qualität

Commits sollten klein und nachvollziehbar sein.

Empfohlene Prefixe:

```text
docs:
feat:
fix:
refactor:
test:
chore:
```

## Definition of Done für Code

Ein Feature gilt als fertig, wenn:

- Fachlogik außerhalb der UI liegt,
- relevante Tests existieren,
- mypy keine relevanten Fehler meldet,
- ruff sauber ist,
- Fehlerfälle berücksichtigt sind,
- README oder Docs angepasst wurden, falls Verhalten sichtbar geändert wurde.

## Kritische Risiken

### Overengineering

Das Projekt darf nicht vor dem ersten Nutzwert in zu viele Abstraktionen zerfallen. Die Architektur soll sauber sein, aber leichtgewichtig bleiben.

### Zu viel LLM-Magie

Mergen und Komprimieren sollten langfristig so deterministisch wie möglich werden. LLMs sind gut für Extraktion und sprachliche Bewertung, aber schlecht als alleinige Quelle für Datenintegrität.

### Silent Data Corruption

Das schlimmste Ergebnis wäre ein Memory, das falsch oder unbemerkt verändert wurde. Deshalb sind Sichtbarkeit, Evidence und manuelle Kontrolle im MVP wichtiger als Automatisierung.
