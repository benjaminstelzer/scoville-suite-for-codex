# Workflow-Vereinfachung: Nachweise vom 02.10.2026

## Auftrag und Ausgangsstand

PLAN-0033 setzt die drei noch offenen Astra-Empfehlungen um: ein gemeinsames
Managerprotokoll, interne Modellauflösung im Dispatch-Builder und Fortschritt
aus gespeichertem Plan-Zustand. Zusätzlich beauftragte der Benutzer während
der Umsetzung die einzeilige WORKING_ON-Anzeige ohne Scope im Runner sowie
einen nachvollziehbaren Abschlusscommit. Blocker und Fragen bleiben erklärend.

Der tatsächliche Ausgangsstand einschließlich fremder Änderungen ist unter
`<workspace-root>/state/2026-10-02-workflow-simplification/baseline/` gesichert.
Dort liegen auch die Sicherungen vor Installation und die Originalkonfiguration.
Prüfausgaben liegen unter `temp/2026-10-02-workflow-simplification/`.
Ausgangs-HEAD: `a5079a4`. Eine andere Session nahm die frühen Helper-Änderungen,
PROJECT_INDEX und PLAN-0033 bereits in `bc50ade` auf. `0e74f90` änderte danach
Plan-Dateiformatierung. Diese Historie bleibt erhalten; der Abschlusscommit
ergänzt nur das offene Workflow-Ergebnis. Kein Push und keine Veröffentlichung.

## Ergebnis und deterministische Prüfungen

- `manager-protocol.md` besitzt Startup, direkte Übergabe, Empfängerbindung,
  geordnete Steuerung/Antworten und Freigabe nach Vorgängerabschluss. Runner,
  Rollover und Managerauftrag verweisen darauf. Rollenspezifische Erstaktionen
  bleiben erhalten. Schreibruhe und WORKING_ON vor Schreibfreigabe bleiben Pflicht.
- `build_dispatch_prompt.py --route` nutzt die vorhandene Auflösung und gibt
  vollständige native Argumente zurück. Einzelne Overrides gelten für neue
  Routen. Ein vollständiges gespeichertes Paar liest keine neue Konfiguration;
  Wiederaufnahme/Korrektur ohne dieses Paar scheitert konkret.
- `run_feedback.py progress --project-root` konsumiert den gebauten
  `select_context.py --position`. Kein Start oder keine eindeutige Step-Gruppe
  ergibt eine Diagnose, keinen angenommenen Fortschritt. Der Helper schreibt
  nicht und wählt keine Arbeit. WORKING_ON enthält ausschließlich seine fette
  Statuszeile. Das alte optionale `--scope-file` wird ohne Dateizugriff ignoriert,
  damit laufende Aufrufer nach dem lokalen Update weiter funktionieren.

Windows, Python 3.14.3: **56 Workflow-Tests bestanden**, nach der Scope-Korrektur
erneut bestanden. Die Paketprüfung meldet `valid: true`. Die neuen Tests nutzen
den tatsächlich gebauten Selector, Rollenauflösung, Status-Consumer und die
native Argumentstruktur; sie ersetzen den nativen Lauf nicht. Abgedeckt sind
Routen/Overrides, geänderte Konfiguration bei Wiederaufnahme/Korrektur, ungültige
Aufrufe samt erfolgreicher Korrektur, fehlende/mehrdeutige/unmarkierte Starts,
einzelne Steps, Gruppen, Legacy-Work-Items und unveränderte erklärende Statuskörper.

Skill Creator `quick_validate.py` scheitert am bereits bestehenden Feld
`compatibility`, das seine erlaubte Feldliste nicht enthält. Die Suite-Prüfung
akzeptiert den bestehenden Paketvertrag. Keine Behauptung eines bestandenen
Skill-Creator-Checks oder neuer macOS/Linux-Laufzeitnachweise.

## Kürzung

Gezählt wurden Whitespace-Wörter derselben fünf betroffenen Markdown-Dateien,
einschließlich der neuen Protokolltabelle: **6.006 → 5.705**, also 301 weniger.
Der Erstauftrag schrumpfte von 361 auf 236 Wörter, der Nachfolgerauftrag von
439 auf 234 vor der zusätzlichen kleinen Scope-Korrektur. Das sind Textgrößen,
keine Tokenmessung oder Behauptung einer allgemeinen Modellverbesserung.
Vergleichsdaten und vollständige generierte Aufträge liegen im genannten
temporären Nachweisordner.

## Nativer Lauf PLAN-0011

Gespeichertes Projekt `test`, frischer Runner, alle sechs Rollen angefordert
und in nativen Startargumenten mit `gpt-6-luna` / `medium` beobachtet. Seriell:
Runner, Manager 1, Worker 1 mit Fortsetzung, Manager 2, Worker 2, Reviewer.

| Rolle | Native Thread-ID |
| --- | --- |
| Runner | `01a0fba3-71f8-7c73-8e27-9755d33dd63c` |
| Manager 1 | `01a0fba5-5113-73a2-a9b0-e982f4648cfa` |
| Worker 1 | `01a0fba7-49dd-7d73-b870-0abb9f8a51b0` |
| Manager 2 | `01a0fbab-323a-7220-bac2-20a0eb5ed920` |
| Worker 2 | `01a0fbad-f211-7730-ba12-6e2b89f99067` |
| Reviewer | `01a0fbaf-72bf-7921-bec1-873279ffd108` |

Beobachtet: gespeicherter/validierter Start, WORKING_ON vor Dispatch,
`progress_pending`, Fortsetzung desselben Workers, kontextbedingte direkte
Managerübergabe und unverändertes Modellpaar, finale read-only Review,
Planabschluss und Berichtsausgabe. Fehlender gespeicherter Start wurde im
echten Manageraufruf abgelehnt und nach korrigiertem Plan erfolgreich projiziert.
Alle Rollen sind nach gesicherten Ergebnissen archiviert.

Ein Fehler der Testvorbereitung setzte worker_percent auf 100; erlaubt sind
1–99. Der Checkpoint blockierte konkret. Der Manager korrigierte auf 99 und
setzte denselben Worker erst zum Checkpoint/progress_pending und danach zu
Step 2 fort. Dieser Fehlversuch ist erhalten, kein sauberer Erstlauf behauptet.
Der Runner gab den vollständigen bereinigten Bericht aus, aber keine generierte
Completed-Überschrift. Englische Texte trotz deutscher Aktivierung bleiben
beobachtete Grenzen. Nachrichtenverlust, falsche Sender und gleichzeitig
eintreffende Steuerung wurden nicht künstlich injiziert; dafür wird kein
vollständiger nativer Fehlerpfadnachweis behauptet.

## Nativer Nachtest und Auslieferung

PLAN-0012 prüfte den finalen Build mit einzeiligem WORKING_ON und erneutem
progress_pending. Alle Rollen liefen seriell mit GPT-6 Luna/Medium:

| Rolle | Native Thread-ID |
| --- | --- |
| Runner | `01a0fbb5-796a-7043-800f-3c5f00e4a4e2` |
| Manager | `01a0fbb6-b823-75c2-bc02-15f48bd8eee9` |
| Worker | `01a0fbb8-3902-7391-bd5f-54a54dba78d6` |
| Reviewer | `01a0fbba-5c18-79f0-9cd0-d5c543947e33` |

Beide Meldungen entsprachen exakt `**Working on: test → PLAN-0012 →
W-001/step-1**` beziehungsweise `step-2`, ohne Scope oder weiteren Text.
Derselbe Worker setzte nach progress_pending fort; Review und Planabschluss
bestanden. Der Runner zeigte auch die generierte Completed-Meldung und den
bereinigten Bericht: `No issues occurred during this run.` Der Manager begann
mit Step 1 statt der angefragten Zweiergruppe; dieser Lauf beweist deshalb
die Step-Fortsetzung, nicht die unveränderte Übernahme der Gruppierung.

Die beiden Manager gaben trotz --route das Modellpaar explizit an. Deshalb
folgte ein begrenzter read-only Consumer-Test: Der gebaute Builder erhielt
nur --route medium, löste Luna/Medium aus der Projektkonfiguration auf und
seine vollständigen Argumente starteten unverändert den nativen Reviewer
`01a0fbbe-480f-76e3-aa37-0ddf00f10a47`. Ergebnis: pass, vorhandene Profildateien
und tatsächliches Validatorresultat mit null Fehlern/Warnungen bestätigt.
Ein anfänglich falscher Validatorpfad in der Vorbereitung wurde korrigiert;
erfolgreiche Helper-Ausgaben wurden nicht repariert.

Alle elf Testrollen sind nach gesicherten Ergebnissen archiviert. Originale
Testkonfiguration und PROJECT_INDEX wurden bytegenau wiederhergestellt;
die abschließende Profilprüfung meldet null Fehler/Warnungen. Abgeschlossene
Testpläne und Ergebnisse bleiben erhalten. Vollständige Thread-Ausgaben,
native Modellpaare, Paket-Hashes und Installationsnachweis liegen im
temporären Nachweisordner; die ursprüngliche Vergleichssicherung bleibt erhalten.

Das unveränderte, durch Hashes eingefrorene Paket wurde lokal nach
`~/.codex/skills/scoville-workflow-for-codex` und in das feste öffentliche
Suite-Verzeichnis synchronisiert, ohne Push oder Veröffentlichung. Ein danach
von einer anderen Session ergänzter Plattformfix in run_feedback.py bleibt
im Quell-Checkout, außerhalb dieses getesteten Pakets und Abschlusscommits.
Generierte Konfigurationshelper stammen weiterhin aus ihren Build-Quellen.

Die verifizierten Runner von Fluid Base (`01a0f713-7580-7ba3-b109-b6c12de97e65`)
und EMPCO (`01a0f73e-235e-7dd2-aeaf-9d7ebea41569`) erhielten die Updatehinweise
mit unverändertem Scope und bestehenden Stopps/Freigaben. Die Sendetools
bestätigten beide Zustellungen; eine spätere Übernahme wird nicht behauptet.
