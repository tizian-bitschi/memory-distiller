# Prompt-Pipeline

## Ziel

Die Prompt-Pipeline erzeugt aus Chatverläufen keinen normalen Summary-Text, sondern überprüfbare Memory-Einträge.

Der MVP startet mit vier Schritten:

```text
Chatverlauf → Extractor → Validator → Merger → Compressor
```

Optional kommt ein fünfter Schritt hinzu:

```text
ASK/CONFLICT → Conflict Clarifier → User-Antwort → Memory Update
```

## Schritt 1: Extractor

Zweck:

- Kandidaten für neue oder geänderte Memory-Einträge finden.
- Zwischen globalem, projektbezogenem und temporärem Kontext unterscheiden.
- User-Korrekturen besonders berücksichtigen.

Input:

- Chatverlauf
- optional bestehender Memory

Output:

```text
ID|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
```

Qualitätskriterien:

- keine Assistentenvorschläge ohne User-Bestätigung
- keine normalen Zusammenfassungen
- keine zu breiten Generalisierungen
- atomare Einträge

## Schritt 2: Validator

Zweck:

- Extractor-Kandidaten kritisch prüfen.
- Falsche, zu allgemeine oder schlecht belegte Einträge verwerfen.
- Scope und Stability korrigieren.

Output:

```text
ID|VERDICT|ACTION|TARGET|SCOPE|TYPE|PRIO|STABILITY|STATEMENT|EVIDENCE|REASON
```

Validator-Regel:

Hohe Precision ist wichtiger als hoher Recall. Lieber nichts speichern als falsches dauerhaftes Memory.

## Schritt 3: Merger

Zweck:

- bestehendes Memory und validierte Kandidaten zu einer neuen `memory_full.md` zusammenführen.
- Updates, Deprecations und Konflikte sichtbar machen.
- offene Klärungen separat sammeln.

Output:

```text
# MEMORY_FULL
...
```

## Schritt 4: Compressor

Zweck:

- aus `memory_full.md` einen kompakten Promptblock erzeugen.
- Evidence entfernen.
- irrelevante Projektregeln weglassen.
- nicht mehr als ca. 20-25 Zeilen erzeugen.

Output:

```text
# MEMORY_PROMPT
...
```

## Prompt: Extractor mit bestehendem Memory

```text
Du bist ein Memory-Extractor und vergleichst einen neuen Chatverlauf mit bestehendem Memory.

Ziel:
Extrahiere neue, geänderte oder widersprüchliche Memory-Kandidaten aus dem Chat.

Bestehender Memory:
<<<MEMORY
[HIER BESTEHENDEN MEMORY EINFÜGEN]
MEMORY>>>

Neuer Chatverlauf:
<<<CHAT
[HIER CHATVERLAUF EINFÜGEN]
CHAT>>>

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

Gib keine Erklärung außerhalb der Kandidatenliste aus.
```

## Prompt: Validator

```text
Du bist ein strenger Memory-Validator.

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
<<<MEMORY
[HIER BESTEHENDEN MEMORY EINFÜGEN]
MEMORY>>>

Chatverlauf:
<<<CHAT
[HIER CHATVERLAUF EINFÜGEN]
CHAT>>>

Memory-Kandidaten:
<<<CANDIDATES
[HIER KANDIDATEN AUS PROMPT 1 ODER 2 EINFÜGEN]
CANDIDATES>>>

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
- Gib keine allgemeine Zusammenfassung aus.
```

## Prompt: Merger

```text
Du bist ein Memory-Merger.

Ziel:
Erzeuge eine aktualisierte Memory-Datei aus bestehendem Memory und validierten Kandidaten.

Bestehender Memory:
<<<MEMORY
[HIER BESTEHENDEN MEMORY EINFÜGEN]
MEMORY>>>

Validierte Kandidaten:
<<<VALIDATED
[HIER OUTPUT DES VALIDATORS EINFÜGEN]
VALIDATED>>>

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
- STATEMENT muss direkt als zukünftiger Kontext nutzbar sein.
```

## Prompt: Compressor

```text
Du bist ein Memory-Kompressor für LLM-Prompts.

Ziel:
Erzeuge aus dem vollständigen Memory einen sehr kompakten Kontextblock, der am Anfang neuer Chats eingefügt werden kann.

Vollständiger Memory:
<<<MEMORY_FULL
[HIER MEMORY_FULL EINFÜGEN]
MEMORY_FULL>>>

Optionaler Zielkontext des nächsten Chats:
<<<NEXT_CONTEXT
[HIER KURZ BESCHREIBEN, WORUM ES IM NÄCHSTEN CHAT GEHT; WENN UNBEKANNT, LEER LASSEN]
NEXT_CONTEXT>>>

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
- Nur den finalen Promptblock ausgeben.
```

## Prompt-Versionierung

Prompt-Templates sollten im Code versioniert werden, z. B.:

```text
extractor_v1
validator_v1
merger_v1
compressor_v1
```

Jeder erzeugte Output sollte später optional speichern können, mit welcher Prompt-Version er entstanden ist. Für den MVP reicht eine sichtbare Konstante im Prompt-Template.
