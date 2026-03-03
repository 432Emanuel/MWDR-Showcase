# Political Anomalies (politische_anomalien)

Dieses Modul beschreibt **Orte mit Sonderstatus** als *Souveränitäts-Interfaces* (Architektur × Recht × Macht).  
Es ist eine **Lens + Sitecards**-Sammlung: keine abschließende Deutung, keine Ontologie-Behauptungen, sondern ein Raster für Vergleichbarkeit.

## Inhalt & Struktur

- `lenses/` – analytisches Raster (`L-POLITICAL-ANOMALIES-001`)
- `sitecards/` – Seeds (konkrete Orte) als strukturierte Steckbriefe
- `notes/` – offene Fragen, Recherche-Lücken, Hypothesen (DP-002-konform)
- `assets/` – Karten, Diagramme, Skizzen (optional)

## Sitecard-Aufbau (Felder)

Jede Sitecard folgt der Lens-Template-Liste:

- **id, title, geo, type_ids, summary**
- **implementation_state**: `planned|in_progress|operational` + kurze Notiz (v. a. wichtig bei Projekt-/Zukunftszonen)
- **status_claims**: Claims als Objekte mit `epistemic_label` (`fact|inference|hypothesis`), `confidence (0..1)`, `sources[]` (bei fehlenden Quellen: `TODO`) und `notes`
- **architecture_power_interface**: 8–12 Bulletpoints, wie Architektur/Perimeter/Zugänge den Sonderstatus operationalisieren
- **axes_scoring**: Array von `{ axis_id, value, rationale }` für AX-001..AX-006 (AX-004/AX-005 sind Kategorien)
- **actors, narratives**
- **risks_and_controversies**: getrennt in *documented* vs. *hypotheses*
- **timeline, comparisons, sources**

## Achsen (Raster)

- **AX-001 Souveränitätsgrad (0..5)**: von „keine Sonderrechte“ bis „eigene internationale Souveränität“.
- **AX-002 Rechtsdifferenz (0..5)**: von normalem Recht bis eigenem Regelsystem/Gerichtsbarkeit.
- **AX-003 Zugangsregime (0..5)**: von offen bis stark kontrolliert/abgeschirmt.
- **AX-004 Machtmodus (Kategorie)**: sakral, finanziell, diplomatisch, militärisch, technokratisch, hybrid.
- **AX-005 Architekturcode (Multi-Kategorie)**: z. B. monumental-rituell, fortifiziert/perimeter, unsichtbare Architektur (Netzwerke/Daten).
- **AX-006 Hebelwirkung (0..5)**: lokal → regional → global.

## Epistemik (DP-002)

- Keine Web-Recherche im Seed-Setup: fehlende Belege werden als `TODO` markiert.
- Strittige Aussagen bleiben **gelabelt** (fact/inference/hypothesis) und werden nicht „glatt“ als Fakten formuliert.

## Index (Skalierung)

`index.json` enthält `schema_version`, `entries` sowie Lookup-Maps (`by_type`, `by_host_country`, `by_leverage_top`) für schnelle Filter/Views.
