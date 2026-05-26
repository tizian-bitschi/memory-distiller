# Memory-Modell und Speicherformat

## Ziel

Das Memory-Format soll im MVP drei Anforderungen erfüllen:

1. manuell lesbar und editierbar sein,
2. token-effizienter als JSON sein,
3. später trotzdem maschinell parsebar bleiben.

Darum verwendet das MVP ein kompaktes Line-Format statt JSON.

## Hauptformat

```text
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE
```

Beispiel:

```text
G|RULE|H|D|User möchte kritisch hinterfragt werden und keine blinde Zustimmung.|2026-05-26 Chat
P:SpringBackend|RULE|H|D|Keine RuntimeException als Standardlösung; fachliche Exceptions bevorzugen.|2025-01-21 Chat
P:TrueWrapped|FACT|M|D|App visualisiert erweiterte Spotify-Historie und soll bessere Wrapped-Insights liefern.|2025-06-28 Chat
```

## Scope

```text
G = global
P:<projekt> = projektbezogen
R:<repo/codebase> = repo- oder codebasebezogen
T = temporär
```

Regel:

- Globale Einträge nur verwenden, wenn sie wirklich projektübergreifend gelten.
- Projektregeln immer mit Projektname speichern.
- Temporäre Einträge dürfen nicht in dauerhafte Promptblöcke gelangen.

## Type

```text
RULE = verbindliche Regel
PREF = Präferenz
FACT = Fakt
DECISION = getroffene Entscheidung
AVOID = explizit vermeiden
STYLE = Schreib-/Antwortstil
SOURCE = Quellenregel
TERM = Begriff/Naming
TASK = offene Aufgabe
CONFLICT = Konflikt/Änderung
```

## Priority

```text
H = hoch, meistens relevant
M = mittel, bei Kontexttreffer relevant
L = niedrig, nur selten relevant
```

Priorität beeinflusst später, ob ein Eintrag in `memory_prompt.md` aufgenommen wird.

## Stability

```text
D = dauerhaft
M = mittelfristig oder projektlebensdauer
T = temporär
```

Stability ist nicht identisch mit Scope. Ein projektbezogener Eintrag kann dauerhaft innerhalb des Projekts gelten.

## Evidence

Evidence ist eine kurze Belegstelle. Sie soll nachvollziehbar machen, warum der Eintrag existiert.

Gute Evidence:

```text
2025-03-25 Chat: "mit Sternchen gendern"
```

Schlechte Evidence:

```text
irgendwann besprochen
```

Für `memory_prompt.md` wird Evidence entfernt. Für `memory_full.md` bleibt sie erhalten.

## Kandidatenformat

Extractor und Validator verwenden ein erweitertes Format:

```text
ID|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
```

Bei Extractor ohne bestehenden Memory kann `TARGET` entfallen oder `-` sein.

## Actions

```text
ADD = neuer Memory-Eintrag
UPDATE = bestehenden Eintrag ändern
DEPRECATE = bestehenden Eintrag als veraltet markieren
IGNORE = nicht speichern
CONFLICT = widerspricht bestehendem Memory
ASK = User sollte entscheiden
```

## Validator Verdicts

```text
KEEP = übernehmen
EDIT = korrigiert übernehmen
DROP = nicht übernehmen
ASK = User sollte gefragt werden
CONFLICT = manuell prüfen
```

## Dateien

### memory_full.md

Vollständige, manuell pflegbare Memory-Datei mit Evidence.

Struktur:

```text
# MEMORY_FULL

## GLOBAL
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE

## PROJECTS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE

## REPOS
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE

## TEMPORARY
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE

## DEPRECATED
SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|DEPRECATION_REASON

## OFFENE_KLÄRUNGEN
QUESTION|WHY_IT_MATTERS
```

### memory_prompt.md

Kompakter Block für neue Chats.

```text
# MEMORY_PROMPT
Beachte dauerhaft:
- ...

Projektkontext, falls relevant:
- ...

Arbeitsweise:
- ...

Nicht tun:
- ...
```

### relevant_memory.md

Noch stärker gefilterter Block für ein konkretes Projekt oder eine konkrete Aufgabe.

```text
# RELEVANT_MEMORY
- ...
```

## Parser-Regeln

- Leere Zeilen ignorieren.
- Markdown-Headings als Abschnittsmarker behandeln.
- Zeilen mit falscher Spaltenanzahl als Parse-Fehler markieren, nicht still korrigieren.
- Pipe-Zeichen innerhalb von Statements im MVP vermeiden.
- Whitespace an Feldrändern trimmen.
- Unbekannte Enum-Werte als Validierungsfehler behandeln.

## Token-Effizienz

Das Line-Format spart gegenüber JSON Tokens, weil keine wiederholten Keys benötigt werden. Dafür ist es empfindlicher gegen Formatfehler. Für den MVP ist dieser Trade-off akzeptabel, weil der User die Dateien manuell prüft.

Später kann intern trotzdem ein typisiertes Domainmodell verwendet werden. Das Line-Format ist nur das Speicher- und Austauschformat.

## Qualitätsregeln für Memory-Einträge

Ein guter Eintrag ist:

- atomar
- eindeutig gescoped
- knapp formuliert
- belegt
- zukunftsrelevant
- nicht bloß eine Chat-Zusammenfassung

Ein schlechter Eintrag ist:

- zu lang
- aus mehreren Regeln gemischt
- nur vom Assistenten vorgeschlagen
- temporär, aber dauerhaft markiert
- global, obwohl nur für ein Projekt relevant
- sensibel ohne klaren Nutzen
