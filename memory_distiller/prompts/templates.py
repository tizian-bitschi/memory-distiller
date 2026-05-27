# ruff: noqa: E501
"""Prompt template constants for Memory Distiller."""

EXTRACTOR_V1 = """Du bist ein Memory-Extractor und vergleichst einen neuen Chatverlauf mit bestehendem Memory.

Ziel:
Extrahiere neue, geänderte oder widersprüchliche Memory-Kandidaten aus dem Chat.

Bestehender Memory:
\u003c\u003c\u003cMEMORY
{existing_memory}
MEMORY\u003e\u003e\u003e

Neuer Chatverlauf:
\u003c\u003c\u003cCHAT
{chat_log}
CHAT\u003e\u003e\u003e

Aufgabe:
1. Finde neue wiederverwendbare Regeln, Präferenzen, Projektfakten, Entscheidungen, Vermeidungsregeln, Terminologie und offene Aufgaben.
2. Prüfe, ob bestehende Memory-Einträge aktualisiert, abgeschwächt, ersetzt oder gelöscht werden sollten.
3. Speichere keine temporären Details als dauerhaft.
4. Speichere keine Assistentenvorschläge, außer sie wurden vom User bestätigt.
5. Markiere unklare Fälle als ASK.
6. Markiere Widersprüche als CONFLICT.
7. Vermeide Duplikate zu bestehendem Memory.

Output-Format:
Gib ausschließlich Zeilen in diesem Format aus:

ID|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON

Legende:
ACTION = ADD, UPDATE, DEPRECATE, IGNORE, CONFLICT, ASK
TARGET = ID oder Kurztext des betroffenen bestehenden Memory-Eintrags; bei ADD: -
SCOPE = G oder P:<Projektname> oder R:<Repo/Codebase> oder T
TYPE = RULE, PREF, FACT, DECISION, AVOID, STYLE, SOURCE, TERM, TASK, CONFLICT
PRIO = H, M, L
STABILITY = D, M, T

Beurteilungskriterien:
- Hohe Precision ist wichtiger als hoher Recall.
- Lieber einen zweifelhaften Eintrag als ASK markieren als falsch speichern.
- Globale Regeln nur verwenden, wenn sie wirklich projektübergreifend gelten.
- Projektregeln immer mit Projektname versehen.
- Aussagen über den User nicht unnötig persönlich formulieren.
- Sensible Informationen nur aufnehmen, wenn sie explizit als dauerhaft relevant erscheinen.

Gib keine Erklärung außerhalb der Kandidatenliste aus."""

VALIDATOR_V1 = """Du bist ein strenger Memory-Validator.

Aufgabe:
Prüfe die folgenden Memory-Kandidaten gegen den Chatverlauf und den bestehenden Memory.

Du sollst Kandidaten entfernen, abschwächen oder korrigieren, wenn sie:
- nicht ausreichend belegt sind
- zu stark verallgemeinern
- nur vom Assistenten behauptet wurden
- temporär sind, aber dauerhaft markiert wurden
- mehrere Aussagen vermischen
- redundant zum bestehenden Memory sind
- falsch scoped sind, z. B. global statt projektbezogen
- eine Präferenz als harte Regel formulieren
- eine einmalige Situation als dauerhafte Regel speichern
- sensible oder unnötig persönliche Informationen enthalten

Bestehender Memory:
\u003c\u003c\u003cMEMORY
{existing_memory}
MEMORY\u003e\u003e\u003e

Chatverlauf:
\u003c\u003c\u003cCHAT
{chat_log}
CHAT\u003e\u003e\u003e

Memory-Kandidaten:
\u003c\u003c\u003cCANDIDATES
{candidates}
CANDIDATES\u003e\u003e\u003e

Output-Format:
Gib ausschließlich validierte Zeilen in diesem Format aus:

ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON

VERDICT:
KEEP = übernehmen
EDIT = übernehmen, aber korrigiert
DROP = nicht übernehmen
ASK = User sollte gefragt werden
CONFLICT = Konflikt muss manuell geprüft werden

Regeln:
- Bei KEEP oder EDIT muss STATEMENT final verwendbar sein.
- Bei DROP erkläre kurz in REASON, warum.
- Bei ASK formuliere STATEMENT als konkrete Prüffrage.
- Bei CONFLICT benenne den Konflikt knapp.
- Gib keine allgemeine Zusammenfassung aus."""

MERGER_V1 = """Du bist ein Memory-Merger.

Ziel:
Erzeuge eine aktualisierte Memory-Datei aus bestehendem Memory und validierten Kandidaten.

Bestehender Memory:
\u003c\u003c\u003cMEMORY
{existing_memory}
MEMORY\u003e\u003e\u003e

Validierte Kandidaten:
\u003c\u003c\u003cVALIDATED
{validated_candidates}
VALIDATED\u003e\u003e\u003e

Aufgabe:
1. Übernimm KEEP- und EDIT-Einträge.
2. Wende UPDATE auf bestehende Einträge an.
3. Entferne oder markiere DEPRECATE-Einträge als veraltet.
4. Übernimm keine DROP-Einträge.
5. Übernimm ASK-Einträge nicht als Memory, sondern liste sie separat unter "Offene Klärungen".
6. Führe Duplikate zusammen.
7. Halte jeden Memory-Eintrag atomar.
8. Erhalte Evidence, aber kürze sie auf das Nötigste.
9. Sortiere nach Scope: GLOBAL, dann PROJECTS, dann REPOS, dann TEMPORARY, dann DEPRECATED.
10. Nutze ein kompaktes, manuell pflegbares Format.

Output-Format:

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

Regeln:
- Keine JSON-Ausgabe.
- Keine langen Erklärungen.
- Keine normalen Zusammenfassungen.
- STATEMENT muss direkt als zukünftiger Kontext nutzbar sein."""

COMPRESSOR_V1 = """Du bist ein Memory-Kompressor für LLM-Prompts.

Ziel:
Erzeuge aus dem vollständigen Memory einen sehr kompakten Kontextblock, der am Anfang neuer Chats eingefügt werden kann.

Vollständiger Memory:
\u003c\u003c\u003cMEMORY_FULL
{memory_full}
MEMORY_FULL\u003e\u003e\u003e

Optionaler Zielkontext des nächsten Chats:
\u003c\u003c\u003cNEXT_CONTEXT
{next_context}
NEXT_CONTEXT\u003e\u003e\u003e

Aufgabe:
1. Entferne Evidence.
2. Entferne temporäre, veraltete und irrelevante Einträge.
3. Behalte globale High-Priority-Regeln.
4. Behalte projektbezogene Einträge nur, wenn sie zum Zielkontext passen.
5. Formuliere extrem kompakt.
6. Keine vollständigen Sätze, wenn Stichpunkte reichen.
7. Maximal 25 Zeilen.
8. Priorisiere Regeln, die das Verhalten des Assistenten konkret ändern.
9. Keine privaten Details ohne Nutzwert.
10. Keine Wiederholungen.

Output-Format:

# MEMORY_PROMPT
Beachte dauerhaft:
- ...

Projektkontext, falls relevant:
- ...

Arbeitsweise:
- ...

Nicht tun:
- ...

Regeln:
- Keine Evidence.
- Keine Meta-Erklärung.
- Keine JSON-Ausgabe.
- Nur den finalen Promptblock ausgeben."""
