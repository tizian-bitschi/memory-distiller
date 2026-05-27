# Offene Entscheidungen

Dieses Dokument sammelt bewusste Entscheidungen, die vor oder während der Implementierung geklärt werden sollten.

## 1. Prompt-only zuerst oder API-Modus direkt?

**Status: DONE**

Entscheidung:

- Prompt-only bleibt als Fallback erhalten.
- Der erste konkrete API-Provider wird direkt umgesetzt.
- Provider: DeepSeek V4.

Begründung:

- Der MVP soll praktisch nutzbar sein und nicht nur Prompts erzeugen.
- Prompt-only ist weiterhin wichtig für sensible Chatverläufe und Debugging.
- Die Architektur bleibt provider-unabhängig.

## 2. Erster API-Provider

**Status: DONE** (DeepSeek V4 implemented)

Entscheidung:

```text
DeepSeek V4
```

Default-Modell:

```text
deepseek-v4-pro
```

Optionales günstigeres Modell:

```text
deepseek-v4-flash
```

Nicht verwenden:

```text
deepseek-chat
deepseek-reasoner
```

Begründung:

- Memory-Extraktion und Validierung sind qualitätskritisch.
- Falsch gespeichertes Memory ist schädlicher als höhere API-Kosten.
- Veraltende Alias-Modellnamen sollen nicht neu eingebaut werden.

Details: siehe `docs/09_deepseek_provider.md`.

## 3. Merger LLM-basiert oder deterministisch?

Option A: LLM-Merger

- schneller umzusetzen
- flexibler bei unstrukturiertem Input
- Risiko für stille Änderungen

Option B: deterministischer Merger

- kontrollierbarer
- testbarer
- braucht streng parsebare Kandidaten

Empfehlung: Im ersten MVP LLM-Merger erlauben, aber Parser und Domainmodell so bauen, dass später ein deterministischer Merger möglich ist.

**Current MVP: LLM-based merger implemented.** Deterministic merger is future work.

## 4. Speicherformat Line-Format oder JSON?

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

**Current MVP decision: Line-Format is used.**

## 5. Wie streng soll der Parser sein?

Option A: sehr streng

- erkennt Fehler früh
- weniger Datenkorruption
- mehr Reibung bei manueller Bearbeitung

Option B: tolerant

- bessere UX
- Risiko stiller Fehlinterpretation

Empfehlung: streng parsen, aber gute Fehlermeldungen mit Zeilennummern geben.

## 6. Sollen echte Chatlogs gespeichert werden?

Option A: gar nicht speichern

- datenschutzfreundlich
- weniger Nachvollziehbarkeit

Option B: optional lokal speichern

- bessere Reproduzierbarkeit
- sensiblere Datenhaltung

Empfehlung: im MVP nicht automatisch speichern; optionaler Download/Export nur auf User-Aktion.

## 7. Wie wird Tokenlänge geschätzt?

Option A: einfache Heuristik Zeichen / 4

- keine Extra-Abhängigkeit
- ungenau

Option B: modellabhängiger Tokenizer

- genauer
- mehr Komplexität

Empfehlung: zunächst einfache Heuristik, später optional Tokenizer.

## 8. Mehrsprachigkeit

Das Projekt entsteht auf Deutsch, aber viele Prompts und Codebegriffe sind Englisch.

Offene Frage:

- UI komplett Deutsch?
- Code und interne Typen Englisch?
- Prompt-Templates Deutsch oder Englisch?

Empfehlung:

- Code und Typen Englisch
- UI Deutsch
- Prompts Deutsch, solange die Zielnutzung deutschsprachig bleibt

## 9. Projektprofile

MVP ohne Projektprofile, aber mit optionalem Projektname-Feld.

Später könnten Projektprofile eigene Dateien bekommen:

```text
memory/global.md
memory/projects/truewrapped.md
memory/projects/spring-backend.md
```

## 10. Evidence-Aufbewahrung

Offene Frage:

- Evidence dauerhaft speichern?
- Evidence nach einer Zeit entfernen?
- Evidence nur als kurzer Verweis speichern?

Empfehlung:

- im MVP kurze Evidence behalten
- keine langen Zitate
- in Prompt-Memory immer entfernen

## 11. Lizenz

Noch offen.

Mögliche Optionen:

- MIT, wenn möglichst permissiv
- Apache-2.0, wenn Patentklausel gewünscht
- privat lassen, wenn zunächst nur eigenes Tool

---

**Note:** Deployment is tracked separately in issues [#8](https://github.com/tizian-bitschi/memory-distiller/issues/8) and [#9](https://github.com/tizian-bitschi/memory-distiller/issues/9).
