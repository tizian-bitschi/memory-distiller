# Streamlit UX

## Ziel

Die Streamlit-App soll den manuellen MVP-Workflow möglichst klar führen. Sie ist kein Chatbot, sondern ein Arbeitswerkzeug für Memory-Extraktion.

## Grundlayout

Vorgeschlagene Hauptbereiche:

```text
1. Input
2. Extract
3. Validate
4. Merge
5. Compress
6. Export
```

Jeder Bereich sollte als eigener Tab oder Step dargestellt werden.

## Sidebar

Die Sidebar enthält globale Einstellungen:

- Modus: Prompt-only oder API
- LLM-Anbieter
- Modellname
- Temperatur
- Projektname
- Zielkontext für neuen Chat
- maximale Promptblock-Zeilen

Für den MVP ist Prompt-only der sichere Default.

## Tab 1: Input

Felder:

- Chatverlauf als Textarea
- bestehender Memory als Textarea
- optional Datei-Upload für Chatlog
- optional Datei-Upload für `memory_full.md`

Aktionen:

- Input prüfen
- geschätzte Zeichen-/Tokenlänge anzeigen
- erkannte Memory-Abschnitte anzeigen

Validierung:

- Chatverlauf darf nicht leer sein
- Memory darf leer sein, dann wird von leerem Memory ausgegangen
- offensichtliche Formatfehler im Memory anzeigen

## Tab 2: Extract

Felder:

- gerenderter Extractor-Prompt
- LLM-Antwort mit Kandidaten

Aktionen:

- Prompt kopieren
- API-Aufruf starten, falls API-Modus aktiv
- Kandidaten parsen
- Kandidaten als Tabelle anzeigen

Tabellenspalten:

- ID
- Action
- Target
- Scope
- Type
- Priority
- Stability
- Statement
- Evidence
- Reason

MVP-Editierung:

- Im ersten Schritt reicht eine Textarea für die Kandidaten.
- Tabellenbearbeitung kann später ergänzt werden.

## Tab 3: Validate

Felder:

- gerenderter Validator-Prompt
- LLM-Antwort mit validierten Kandidaten

Aktionen:

- Prompt kopieren
- API-Aufruf starten, falls API-Modus aktiv
- validierte Kandidaten parsen
- KEEP, EDIT, DROP, ASK, CONFLICT gruppiert anzeigen

Besonders sichtbar machen:

- ASK-Einträge
- CONFLICT-Einträge
- DROP-Begründungen

## Tab 4: Merge

Felder:

- gerenderter Merger-Prompt
- LLM-Antwort oder lokal erzeugtes neues Memory

Aktionen:

- Prompt kopieren
- neues `memory_full.md` anzeigen
- Diff zum alten Memory anzeigen, falls möglich

Für den MVP kann der Merger noch LLM-basiert sein. Später sollte das Mergen zunehmend deterministisch im Code passieren.

## Tab 5: Compress

Felder:

- vollständiger Memory
- Zielkontext
- gerenderter Compressor-Prompt
- erzeugter Prompt-Memoryblock

Aktionen:

- Prompt kopieren
- `memory_prompt.md` kopieren
- projektbezogenen `relevant_memory.md` erzeugen

## Tab 6: Export

Downloads:

- `memory_full.md`
- `memory_prompt.md`
- `relevant_memory.md`
- optional `candidates.txt`
- optional `validated_candidates.txt`

## Statusanzeigen

Die App sollte klar zeigen:

- welcher Schritt erledigt ist
- welcher Schritt noch fehlt
- ob geparste Outputs Fehler enthalten
- ob ASK/CONFLICT-Einträge manuell geprüft werden müssen

## UX-Prinzipien

- Niemals still Memory ändern.
- Jede Änderung muss sichtbar kopierbar oder downloadbar sein.
- Prompt-only darf kein Feature zweiter Klasse sein.
- Fehler nicht verstecken.
- Nutzer soll Outputs manuell korrigieren können.
- Kein automatisches Speichern privater Daten ohne bewusste Aktion.

## Minimaler erster Screen

Für den allerersten MVP kann die App noch einfacher sein:

```text
Links:
- Chatverlauf
- Bestehender Memory
- Zielkontext

Rechts:
- Extractor Prompt
- Validator Prompt
- Merger Prompt
- Compressor Prompt
```

Darunter:

```text
- Textareas für LLM-Antworten
- Downloadbuttons
```

Das ist weniger schön, aber sehr schnell nutzbar.

## Spätere UX-Verbesserungen

- Stepper-Layout
- editierbare Tabellen
- Diff Viewer
- farbliche Badges für Scope/Type/Priority
- automatische Konfliktliste
- Projektprofile
- lokale Historie früherer Runs
