# Style Guide — Sitecards (political_anomalies)

10 Regeln für **Konsistenz, Skalierbarkeit und DP-002-Hygiene**:

1) **Jeder Status-Claim braucht** `epistemic_label` + `confidence (0..1)` + `sources[]` + `notes`.
2) **Ohne Quelle kein harter Fakt:** wenn Beleg fehlt → `sources: ["TODO: …"]` und `confidence` senken; bei Unsicherheit `inference`/`hypothesis` statt `fact`.
3) **Versprechen ≠ Umsetzung:** bei Projekten/Programmen (z. B. NEOM) in `notes` klar markieren: *announced/promised* vs. *implemented*.
4) **Keine unmarkierte Spekulation:** alles Strittige muss gelabelt sein (insb. Governance, Zugangsregime, „Hebelwirkung“).
5) **Achsen vollständig:** `axes_scoring` immer AX-001..AX-006, in gleicher Reihenfolge; jede Achse braucht eine kurze, überprüfbare Begründung.
6) **Architektur als Interface:** `architecture_power_interface` sind 8–12 kurze Bulletpoints zu Perimeter, Zugängen, Achsen, Clustern, Infrastruktur, Schwellenräumen (kein Essay).
7) **Kontroversen trennen:** `risks_and_controversies.documented` nur mit Quellen; ohne Quellen in `hypotheses` (keine impliziten Schuldzuweisungen).
8) **Zeitpunkte nur mit Beleg:** in `timeline` keine Jahreszahlen/Datierungen ohne Quelle; sonst `TODO` + niedrige Confidence.
9) **Vergleiche strukturell:** `comparisons` vergleicht Achsen/Architekturcode/Access-Regime; keine „History Dumps“ und keine externen Fakten ohne Quelle.
10) **Update-Disziplin:** wenn neue Quellen ergänzt werden, Labels/Confidence/Rationales aktiv nachziehen (Index-Mappings und Axen-Scores mitaktualisieren).

