# MVP Scope

## Zielbild

Memory Distiller ist zunächst ein lokales, manuell bedientes Werkzeug für eine Einzelperson. Es unterstützt dabei, aus Chatverläufen wiederverwendbares Memory zu extrahieren, zu prüfen und als kompakten Kontextblock für neue LLM-Chats aufzubereiten.

Das MVP soll nicht perfekt automatisieren. Es soll einen verlässlichen, nachvollziehbaren Workflow schaffen, der später automatisiert werden kann.

## Nutzerfluss

1. User öffnet die Streamlit-App.
2. User fügt einen Chatverlauf ein oder lädt eine Textdatei hoch.
3. User fügt optional bestehenden `memory_full.md` ein oder wählt eine lokale Datei.
4. App erzeugt einen Prompt für den Extractor oder ruft optional direkt einen LLM-Adapter auf.
5. User prüft die Kandidaten.
6. App erzeugt einen Validator-Prompt oder validiert direkt über LLM.
7. User übernimmt validierte Einträge.
8. App erzeugt aktualisiertes `memory_full.md`.
9. App erzeugt kompaktes `memory_prompt.md` oder projektbezogenes `relevant_memory.md`.

## Muss-Funktionen

- Chatverlauf als Text einfügen.
- Bestehenden Memory als Text einfügen.
- Vordefinierte Prompts bereitstellen.
- Extractor-, Validator-, Merger- und Kompressor-Schritt unterstützen.
- Memory im kompakten Line-Format darstellen.
- Ergebnisse kopierbar machen.
- Lokalen Download für `memory_full.md` und `memory_prompt.md` anbieten.
- Ohne Datenbank funktionieren.

## Soll-Funktionen

- Projektname für projektbezogene Filterung angeben.
- LLM-Anbieter konfigurierbar machen.
- Prompt-only-Modus und API-Modus unterstützen.
- Kandidaten in einer Tabelle editierbar machen.
- Konflikte und ASK-Einträge separat anzeigen.
- Einfache Token-/Zeilenlängen-Schätzung anzeigen.

## Kann-Funktionen

- Mehrere Memory-Dateien verwalten.
- Projektprofile speichern.
- Import von Markdown-, TXT- oder JSON-Chatlogs.
- Export als ZIP.
- Diff-Ansicht zwischen altem und neuem Memory.

## Nicht im MVP

- automatische ChatGPT-History-Anbindung
- OAuth oder User-Accounts
- Cloud-Speicher
- automatische Hintergrundverarbeitung
- Vektordatenbank
- semantische Suche
- Browser-Extension
- Team-Funktionen
- persistenter Serverbetrieb

## Akzeptanzkriterien

Der MVP gilt als brauchbar, wenn:

- ein kompletter Tages-Chat manuell verarbeitet werden kann,
- extrahierte Einträge getrennt nach Scope erscheinen,
- falsche oder schwache Kandidaten sichtbar verworfen werden können,
- ein kompakter Memoryblock für neue Chats erzeugt wird,
- alle Schritte ohne versteckte Seiteneffekte nachvollziehbar sind.

## Qualitätsanspruch

Auch wenn es ein kleines Pythonprojekt ist, soll die Codebasis früh sauber bleiben:

- klare Modulstruktur
- typisierte Domänenobjekte
- keine Logik direkt in Streamlit-Komponenten verstecken
- testbare Parser- und Formatierungsfunktionen
- keine hardcodierten Anbieterabhängigkeiten in der UI
- explizite Fehlerbehandlung
