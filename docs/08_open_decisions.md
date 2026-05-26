# Offene Entscheidungen

Dieses Dokument sammelt bewusste Entscheidungen, die vor oder während der Implementierung geklärt werden sollten.

## 1. Prompt-only zuerst oder API-Modus direkt?

Option A: Prompt-only zuerst

- schneller und sicherer
- keine API-Key-Verwaltung
- ideal zum Testen der Promptqualität
- weniger gute UX

Option B: API-Modus direkt

- besserer Workflow
- mehr Implementierungsaufwand
- Datenschutzhinweise nötig
- Provider-Abstraktion nötig

Empfehlung für MVP: Prompt-only zuerst, API-Adapter direkt architektonisch vorbereiten.

## 2. Merger LLM-basiert oder deterministisch?

Option A: LLM-Merger

- schneller umzusetzen
- flexibler bei unstrukturiertem Input
- Risiko für stille Änderungen

Option B: deterministischer Merger

- kontrollierbarer
- testbarer
- braucht streng parsebare Kandidaten

Empfehlung: Im ersten MVP LLM-Merger erlauben, aber Parser und Domainmodell so bauen, dass später ein deterministischer Merger möglich ist.

## 3. Speicherformat Line-Format oder JSON?

Option A: Line-Format

- token-effizienter
- gut manuell editierbar
- anfälliger für Formatfehler

Option B: JSON

- maschinenfreundlicher
- robuster für verschachtelte Daten
- tokenlastiger
- manuell sperriger

Empfehlung: Line-Format für Dateien, intern typisierte Python-Objekte.

## 4. Wie streng soll der Parser sein?

Option A: sehr streng

- erkennt Fehler früh
- weniger Datenkorruption
- mehr Reibung bei manueller Bearbeitung

Option B: tolerant

- bessere UX
- Risiko stiller Fehlinterpretation

Empfehlung: streng parsen, aber gute Fehlermeldungen mit Zeilennummern geben.

## 5. Sollen echte Chatlogs gespeichert werden?

Option A: gar nicht speichern

- datenschutzfreundlich
- weniger Nachvollziehbarkeit

Option B: optional lokal speichern

- bessere Reproduzierbarkeit
- sensiblere Datenhaltung

Empfehlung: im MVP nicht automatisch speichern; optionaler Download/Export nur auf User-Aktion.

## 6. Wie wird Tokenlänge geschätzt?

Option A: einfache Heuristik Zeichen / 4

- keine Extra-Abhängigkeit
- ungenau

Option B: modellabhängiger Tokenizer

- genauer
- mehr Komplexität

Empfehlung: zunächst einfache Heuristik, später optional Tokenizer.

## 7. Mehrsprachigkeit

Das Projekt entsteht auf Deutsch, aber viele Prompts und Codebegriffe sind Englisch.

Offene Frage:

- UI komplett Deutsch?
- Code und interne Typen Englisch?
- Prompt-Templates Deutsch oder Englisch?

Empfehlung:

- Code und Typen Englisch
- UI Deutsch
- Prompts Deutsch, solange die Zielnutzung deutschsprachig bleibt

## 8. Projektprofile

MVP ohne Projektprofile, aber mit optionalem Projektname-Feld.

Später könnten Projektprofile eigene Dateien bekommen:

```text
memory/global.md
memory/projects/truewrapped.md
memory/projects/spring-backend.md
```

## 9. Evidence-Aufbewahrung

Offene Frage:

- Evidence dauerhaft speichern?
- Evidence nach einer Zeit entfernen?
- Evidence nur als kurzer Verweis speichern?

Empfehlung:

- im MVP kurze Evidence behalten
- keine langen Zitate
- in Prompt-Memory immer entfernen

## 10. Lizenz

Noch offen.

Mögliche Optionen:

- MIT, wenn möglichst permissiv
- Apache-2.0, wenn Patentklausel gewünscht
- privat lassen, wenn zunächst nur eigenes Tool
