# Astra Medium zum Opus-Review

Native Rolle: 01a0fb54-ceac-7f23-82a9-ab1775c939e8. Review-Eingaben und SHA256-Manifest: <workspace-root>/temp/2026-10-02-opus-astra-review. Die gesicherten Hostmetadaten bestätigen gpt-6-astra/medium. Die folgende Aussage über fehlende Telemetrie stammt aus dem unveränderten Beraterbericht. Der eingefrorene Review-Stand enthält noch nicht die nachfolgende Korrektur zu frühem Projektnamen und direktem Texteingang.

adviser_id: astra  
consultation_reference: opus-astra-review-20261002  
Scope unverändert: Opus-Review, Workflow-Regeln und weitere Helper zur Kürzung. Angefordert: GPT-6 Astra/Medium; tatsächliches Modell und Effort sind mir nicht als Laufzeittelemetrie zugänglich.

Das Opus-Review benennt reale Komplexität, behandelt aber mehrere bestehende Garantien wie entbehrliche Fehler. Seine Empfehlungen sind deshalb nicht unverändert umzusetzen. Der Kandidat verbessert die Statusdarstellung deutlich, lässt jedoch Randwege uneindeutig.

Die folgenden Pfade beziehen sich auf `current/`; `WF` steht für `scoville-workflow-for-codex`.

- **N1 – Verhalten belegt, Fehlerbewertung nicht belegt.** `WF/references/run-feedback.md:31–50` verlangt erfolgreiche WORKING_ON-Zustellung vor Schreibfreigabe. Das garantiert einen erfolgreichen Versandversuch vor Beginn, ausdrücklich keine bereits sichtbare Anzeige. Nicht blockierend weiterzuarbeiten wäre eine bewusste Abschwächung dieser Garantie. Tatsächliche Zustellfehler oder Stillstände sind nicht nachgewiesen. Die Aussage, ein Verlust betreffe „nur“ einen Zwischenstand, unterschätzt die ausdrückliche Nutzeranforderung zur sichtbaren Fortschrittsmeldung.

- **W1/N2 – Komplexität belegt, vorgeschlagene Vereinfachung unvollständig.** `WF/SKILL.md`, „Runner start contract“ und „Steering, stop and resume“, sowie `references/operations-rollover.md`, „Manager rollover“, regeln authentifizierte Übergabe, Prüfung, Vorgängerabschluss und Freigabe getrennt. Eine Dateiübergabe beseitigt weder nach dem Snapshot eintreffende Steuerung noch offene Antworten. Ohne Ersatz für deren geordnete Übernahme würde die vorgeschlagene Kürzung eine bestehende Garantie verlieren. Auch die Schreibruhe und der vollständige Vorgängerabschluss müssen erhalten bleiben. Dass die Regeln historisch „gewachsen“ sind, lässt sich gegenüber dem nicht vorliegenden Stand `727bc1c` nicht prüfen.

- **N3 – Zustandsaufwand belegt, kein selbständiger Defekt.** Der Runner muss zwischen empfangen und sichtbar ausgegeben unterscheiden, damit Deduplizierung keine Anzeige verschluckt. Der Kandidat formuliert das bereits kürzer (`run-feedback.md:39–50`). Die Sonderfälle für Berichtsschreibrechte und unbekannte Schreibergebnisse schützen einen einzigen Berichtseigentümer und verhindern voreilig behauptete Speicherung. Diese Zustände verschwinden durch kürzeren Text nicht.

- **W4 – Streichung verändert die Fortschrittsgarantie.** `WF/references/operations.md`, „Plan progress before execution“, und `scoville-plan/references/edit.md`, „Select and finish“, verlangen gespeicherten, validierten Startzustand vor delegierter Ausführung. `progress_pending` ermöglicht den nächsten tatsächlichen Step innerhalb derselben größeren Zuweisung, ohne dass der Worker den Plan schreibt. Ausschließlich nachträgliche Fortschrittspflege würde Plan und sichtbare Meldung während der Arbeit veralten lassen. Ganze Bereiche vorab als gestartet zu markieren wäre ebenfalls keine gleichwertige Lösung.

- **W5 – Vier konkurrierende Fortschrittsquellen sind nicht belegt.** `scoville-plan/SKILL.md` und `references/edit.md`, „Step progress“/„Evidence and legacy continuation“, unterscheiden Step-Fortschritt, Gesamtstatus, zusätzliche Bedingungen und Belege. `Next action` bleibt für Altbestände; neue Einträge dürfen es nicht verwenden. Das ist komplex, aber fachlich getrennt. Ungeprüftes Zusammenlegen würde unter anderem aus abgeschlossenen Steps fälschlich abgeschlossene Acceptance ableiten können.

**Konkreter Korrekturbedarf:**

1. **Kapazitätsregeln sind nicht restlos entfernt.** Bereinigung wird zwar nirgends ausgeführt, aber besondere Kapazitätsregeln bleiben in `WF/SKILL.md:31,119`, `references/operations.md:213`, `operations-dispatch.md:138`, `operations-rollover.md:97` und `scoville-ask-for-codex/references/native.md:29–35`. Bei der ausdrücklich verlangten vollständigen Entfernung genügt die allgemeine Behandlung fehlgeschlagener/ungewisser Spawns. Diese schützt Diagnose, Fortsetzungszustand und das Verbot automatischer Wiederholung weiterhin. Die erneute Kapazitätsentscheidung aus Opus ist durch den vorliegenden Nutzerauftrag überholt.

2. **Veralteter Fallback-Verweis:** `scoville-plan/references/edit.md:213` verweist auf einen „sole no-Python fallback“, während `scoville-plan/SKILL.md`, „Runtime helpers“, jede manuelle Ersatzdurchführung verbietet. Kleinste Korrektur: den nicht existierenden Fallback-Verweis entfernen.

3. **Frühe Statusmeldungen besitzen keinen eindeutig festgelegten Projektnamen.** `run-feedback.md:18` bestimmt ihn erst nach den Startup-Prüfungen; `:117–121` verlangt davor vom Runner einen generierten Blocker. `run_feedback.py:163,219` verlangt dafür bereits `project`. Den tatsächlichen Anzeigenamen vor dem ersten fehleranfälligen Startschritt festlegen und als Kontrollmetadatum weitergeben; der Runner benötigt dafür keinen Planinhalt.

4. **Statusgenerierung während Schreibverbot ist widersprüchlich formuliert.** `run-feedback.md:67` verlangt zunächst eine UTF-8-Datei, auch für Probleme eines wartenden Nachfolgers. `operations-rollover.md`, „Manager rollover“, verbietet diesem vor Freigabe alle Writes. Damit bleibt offen, wie er den vorgeschriebenen vollständigen Status erzeugt. Ein direkter Textparameter im bestehenden Helper könnte diesen Konflikt ohne manuellen Fallback lösen.

`run_feedback.py:163–193` erzeugt ansonsten genau die gewünschte fette Statuszeile, Leerzeile und normalen Erklärungstext; alle fünf Statusarten sind abgedeckt. Frage, Grund und wartende Arbeit bleiben sinnvollerweise inhaltliche Verantwortung des Managers. Der Helper prüft lediglich nichtleeren Text. Die Identitäts- und Workspace-Regeln halten die Kommunikation beim zugehörigen Runner.

Maximal fünf Kürzungen nach Netto-Nutzen:

1. **Ohne neuen Helper: Zustandsdiagramm/-tabelle als einzige Protokollreferenz.** Heute wiederholen Runner-Skill, Rollover-Referenz und `build_manager_handoff.py` wesentliche Übergaberegeln. Eine gemeinsame knappe Referenz plus rollenspezifische Erstaktion ersetzt Wiederholungen; Gates, Identitätsprüfung und Nachrichtenreihenfolge bleiben. Kosten: Referenz muss vor der jeweiligen Aktion geladen sein.

2. **`run_feedback.py status` um direkten Texteingang erweitern.** Heute schreibt der Manager für jede Meldung erst eine temporäre Datei. Das entfernt Dateivorbereitungsregeln und löst den genannten Schreibverbotskonflikt; vollständige generierte Nachrichten bleiben verpflichtend. Kosten: sichere Argumentübergabe und eindeutige Auswahl zwischen Text und Datei.

3. **Modellauflösung in `build_dispatch_prompt.py` integrieren.** Heute löst der Manager über `resolve_model_pair.py` auf und kopiert das Paar in den Builder. Optional Route und explizite Overrides annehmen, intern dieselbe Auflösung verwenden und das tatsächlich gewählte Paar zurückgeben. Damit entfallen Kopierschritt und getrennte Aufrufanleitung; Routenentscheidung, Hostprüfung und Beibehaltung des ursprünglichen Korrekturpaares bleiben. Kosten: keine unbemerkte Neuauflösung bei Wiederaufnahme.

4. **Fortschrittsanzeige aus der bestehenden Plan-Projektion erzeugen.** Heute überträgt der Manager Plan-ID und tatsächliche Step-Gruppe manuell. Ein managerseitiger Modus von `run_feedback.py` kann `select_context.py --position` nutzen und Mehrdeutigkeit ablehnen. Die Anzeige bleibt an gespeicherten Startzustand gebunden; Runner liest weiterhin keinen Plan. Kosten: zusätzliche Abhängigkeit; keine Auswahl oder Startfreigabe durch den Helper.

Keine Tests, Änderungen oder weiteren Agenten. Ask und Plan sind zwischen den gelieferten Ständen unverändert; geändert wurden nur Workflow-Skill, Feedback-Referenz und Statushelper. Frühere Größenvergleiche, Änderungsgeschichte seit 28.09., tatsächliche Laufprobleme sowie README- und lokale 256-Konfiguration sind aus diesem Ausschnitt nicht unabhängig prüfbar.
