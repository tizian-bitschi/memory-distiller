# Memory Distiller

Memory Distiller ist ein MVP für die Extraktion, Pflege und Wiederverwendung von persistentem Arbeitskontext aus LLM-Chatverläufen.

Das Projekt startet bewusst klein: Eine Streamlit-App nimmt Chatverläufe entgegen, erzeugt Memory-Kandidaten über LLM-Prompts, validiert diese Kandidaten und schreibt daraus kompakte Memory-Dateien, die anschließend in neue LLM-Chats eingefügt werden können.

## Problem

Bei täglicher Arbeit mit LLM-Chats gehen projektspezifische Regeln, persönliche Arbeitspräferenzen, Entscheidungen und wiederkehrende Constraints zwischen neuen Chats verloren. Dadurch müssen dieselben Regeln immer wieder manuell erklärt werden.

Memory Distiller soll nicht einfach Chatverläufe zusammenfassen, sondern wiederverwendbares Handlungswissen extrahieren:

- globale Arbeitsregeln
- projektbezogene Regeln
- technische Entscheidungen
- Stil- und Quellenpräferenzen
- Vermeidungsregeln
- offene Klärungen
- temporärer Kontext mit Ablaufcharakter

## MVP-Ziel

Der MVP soll einen manuellen, aber zuverlässigen Workflow unterstützen:

1. Chatverlauf einfügen oder hochladen.
2. Bestehenden Memory laden.
3. Memory-Kandidaten extrahieren.
4. Kandidaten kritisch validieren.
5. Memory-Datei aktualisieren.
6. Kompakten Prompt-Memoryblock erzeugen.

Automatische Hintergrundprozesse, User-Accounts, Vektordatenbanken und Multi-User-Support gehören nicht zum ersten MVP.

## Kernprinzipien

- Hohe Precision ist wichtiger als hoher Recall.
- Keine Assistentenvorschläge als User-Entscheidungen speichern.
- Jede dauerhafte Memory-Regel braucht einen belegbaren Ursprung.
- Globale und projektbezogene Regeln strikt trennen.
- Negative Regeln sind wichtig: "nicht tun" ist ein eigenständiger Memory-Typ.
- Memory muss kompakt genug bleiben, um in neue Chats eingefügt werden zu können.
- Das System soll einfach bleiben, aber sauber strukturiert und testbar sein.

## Geplanter Tech-Stack

- Python
- Streamlit für die MVP-Oberfläche
- Plain-Text/Markdown-Dateien als Speicherformat
- LLM-Anbieter über eine abstrahierte Adapter-Schicht
- pytest für Tests
- ruff und mypy für statische Qualitätssicherung

Konkrete Paketversionen werden später im `pyproject.toml` festgelegt.

## Dokumentation

- [MVP Scope](docs/01_mvp_scope.md)
- [Architektur](docs/02_architecture.md)
- [Memory-Modell und Speicherformat](docs/03_memory_model.md)
- [Prompt-Pipeline](docs/04_prompt_pipeline.md)
- [Streamlit UX](docs/05_streamlit_ux.md)
- [Code-Qualität und Tests](docs/06_quality_and_testing.md)
- [Privacy und Sicherheit](docs/07_security_and_privacy.md)
- [Offene Entscheidungen](docs/08_open_decisions.md)

## Nicht-Ziele für den MVP

- kein automatisches Lesen aller ChatGPT-Verläufe
- keine Browser-Extension
- keine Cloud-Synchronisierung
- keine Multi-User-Verwaltung
- keine automatische Memory-Injektion in fremde LLM-Tools
- kein komplexes RAG-System
- keine Vektordatenbank im ersten Schritt

## Lizenz

Noch offen.
