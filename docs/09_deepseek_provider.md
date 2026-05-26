# DeepSeek V4 Provider

Stand: 2026-05-26

## Entscheidung

Der erste konkrete API-Provider für Memory Distiller ist DeepSeek V4.

Der MVP bleibt trotzdem so gebaut, dass der Provider austauschbar ist. DeepSeek ist der erste Adapter, nicht Teil der Domainlogik.

## Ziel

Der DeepSeek-Adapter soll die Prompt-Pipeline direkt aus der Streamlit-App ausführen können:

```text
Extractor → Validator → Merger → Compressor
```

Prompt-only bleibt als Fallback erhalten.

## Offizielle API-Formate

DeepSeek bietet eine OpenAI-kompatible und eine Anthropic-kompatible API an.

Für den MVP wird nur das OpenAI-kompatible Format umgesetzt.

```text
OpenAI-compatible base_url: https://api.deepseek.com
Anthropic-compatible base_url: https://api.deepseek.com/anthropic
```

Quelle:

```text
https://api-docs.deepseek.com/
https://api-docs.deepseek.com/quick_start/pricing
```

## Modelle

Für den MVP werden nur die aktuellen V4-Modellnamen verwendet:

```text
deepseek-v4-pro
deepseek-v4-flash
```

Nicht verwenden:

```text
deepseek-chat
deepseek-reasoner
```

Diese Alias-Namen sind nur aus Kompatibilitätsgründen vorhanden und sollen laut DeepSeek-Doku zum 2026-07-24 auslaufen. Sie entsprechen aktuell Modi von `deepseek-v4-flash`.

## Default-Modell

Default für die erste Umsetzung:

```text
deepseek-v4-pro
```

Begründung:

- Memory-Extraktion und Validierung sind qualitätskritisch.
- Falsch gespeichertes Memory ist schädlicher als ein etwas höherer API-Preis.
- Für den MVP ist Qualität wichtiger als maximal niedrige Kosten.

Optionales günstigeres Modell:

```text
deepseek-v4-flash
```

Geeignet für:

- erste Entwürfe
- Compressor-Schritt
- schnelle Tests
- nicht-kritische Runs

## Thinking Mode

DeepSeek V4 unterstützt Thinking und Non-Thinking.

Empfohlene Defaults:

| Pipeline-Schritt | Modell | Thinking | Reasoning Effort |
|---|---|---:|---|
| Extractor | `deepseek-v4-pro` | ja | high |
| Validator | `deepseek-v4-pro` | ja | high |
| Merger | `deepseek-v4-pro` | ja | medium |
| Compressor | `deepseek-v4-flash` oder `deepseek-v4-pro` | nein oder ja | low/medium |

Der Compressor sollte nicht unnötig teuer sein. Er braucht eher Kürzung und Auswahl als tiefe Analyse.

## Konfiguration

Vorgeschlagene Konfiguration:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class LlmConfig:
    provider: str = "deepseek"
    model: str = "deepseek-v4-pro"
    base_url: str = "https://api.deepseek.com"
    api_key_env: str = "DEEPSEEK_API_KEY"
    temperature: float = 0.2
    max_tokens: int | None = None
    thinking_enabled: bool = True
    reasoning_effort: str = "high"
    timeout_seconds: int = 120
```

## Environment Variable

Der API-Key wird nicht im Code gespeichert.

```text
DEEPSEEK_API_KEY=...
```

Streamlit Secrets sind für lokale Nutzung ebenfalls möglich:

```toml
DEEPSEEK_API_KEY = "..."
```

`.streamlit/secrets.toml` darf nicht committed werden.

## Adapter-Interface

Der DeepSeek-Adapter implementiert ein generisches LLM-Interface.

```python
from typing import Protocol

class LlmClient(Protocol):
    def complete(self, *, system_prompt: str, user_prompt: str) -> str:
        ...
```

Für spätere Erweiterung können Parameter ergänzt werden:

```python
class LlmClient(Protocol):
    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        config: LlmConfig,
    ) -> str:
        ...
```

## Beispiel mit OpenAI SDK

```python
import os

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

response = client.chat.completions.create(
    model="deepseek-v4-pro",
    messages=[
        {"role": "system", "content": "Du bist ein strenger Memory-Extractor."},
        {"role": "user", "content": "..."},
    ],
    temperature=0.2,
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}},
    stream=False,
)

text = response.choices[0].message.content
```

## Payload-Regeln

- Kein DeepSeek-Code direkt in Streamlit-Komponenten.
- API-Aufrufe nur über `llm/deepseek_client.py` oder einen OpenAI-kompatiblen Basisadapter.
- Prompt-Rendering bleibt im Prompt-Modul.
- Application Services entscheiden, welcher Pipeline-Schritt mit welcher LLM-Konfiguration läuft.
- LLM-Antworten werden zuerst als Rohtext sichtbar gemacht und dann geparst.

## Fehlerfälle

Der Adapter muss mindestens diese Fehler sauber behandeln:

- fehlender API-Key
- ungültiger Modellname
- Timeout
- Rate Limit
- Netzwerkfehler
- leere LLM-Antwort
- LLM-Antwort passt nicht zum erwarteten Line-Format

Fehler dürfen nicht zu stillen Memory-Änderungen führen.

## Tests

Standardtests rufen keine echte DeepSeek-API auf.

Testen:

- Config-Erzeugung
- API-Key-Auflösung aus Environment
- Payload-Building
- Thinking-Parameter
- Fehler bei fehlendem API-Key
- Mock-Response zu Text
- Parser-Verhalten bei DeepSeek-Antwort

Echte API-Tests nur optional:

```python
@pytest.mark.integration_llm
```

## Privacy-Hinweis

Im API-Modus werden Chatverlauf, bestehender Memory und Kandidaten an DeepSeek gesendet. Die UI muss das sichtbar machen, bevor ein API-Run gestartet wird.

Prompt-only bleibt für sensible Chatverläufe der sichere Default.

## Preis- und Modelländerungen

Preise, Limits und Modellverfügbarkeit sind extern und können sich ändern. Deshalb:

- Preise nicht fest im Code hinterlegen.
- Modellnamen konfigurierbar halten.
- Offizielle DeepSeek-Doku regelmäßig prüfen.
- Keine deprecated Aliase verwenden.
