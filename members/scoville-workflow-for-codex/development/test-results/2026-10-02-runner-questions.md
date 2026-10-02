# Native Testprojekt: Ausgangslauf

Getestet wurden die installierten Paketbytes vor der neuen Hervorhebung.
Testprojekt und Nachweise: `<test-root>/workflow-runner-notifications-20261002`.
`evidence/package-inputs.json` hält die SHA256-Werte aller 87 Laufzeitdateien fest.

## Beobachtet

- Runner `01a0fb2f-bee4-7a52-b49d-29ea9c1d8abd`, Manager `01a0fb30-fa5a-7652-985e-303fb2f3b13f`, Worker 1 `01a0fb32-c40a-7ec0-b7da-67f84d721de2`, Worker 2 `01a0fb35-dc0e-7f31-a726-a0820929f5ba`: native Metadaten jeweils gpt-6-luna / medium, tatsächliches Testprojekt. Keine parallelen Worker.
- Formatfrage vor Step 2 kam vom Manager. Nach tatsächlicher Antwort `plain` startete Worker 2.
- Worker 2 meldete die fehlende Freigabedatei am 02.10.2026 um 06:03:51 UTC über `send_message` an seinen tatsächlichen Manager. Sein natives Ergebnis bestätigte `needs_user_decision` und die fehlende Ergebnisdatei.
- Manager meldete die Ursache an seinen ursprünglichen Runner um 06:04:06 UTC. Dort erschien sie um 06:04:11 UTC mit PLAN-0006 / W-001/step-2, genauer Datei und wartender Ausgabe. Derselbe Fortschrittsschlüssel unterdrückte die neue Ursache nicht.
- Erst danach stellte der Testinhaber die Datei bereit. Derselbe Worker wurde wiederaufgenommen. Tatsächliche Ausgaben: `Ready\n`, `approved\n`, `Inspection receipt\n`. request.json blieb unverändert.
- Der Manager schloss Plan und Bericht. Der Runner verwendete den Lesehelper und zeigte den vollständigen Bericht. Manager und beide Worker sind abgeschlossen und wurden nach Sicherung der IDs/Nachweise erfolgreich archiviert. Der Runner bleibt für den seriellen Folgetest offen.
- Ursprüngliche Konfiguration ist bytegleich wiederhergestellt. Testprofil validiert: 11 Dateien, 6 Pläne, 12 Arbeitspunkte, 4 Entscheidungen, keine Fehler.

## Grenzen und erhaltene Fehler

Der erste Handoff-Aufruf verwendete einen geratenen Berichtspfad und scheiterte vor dem Managerstart. Der korrigierte Aufruf verwendete den tatsächlich erzeugten Pfad. Die Fortschrittsanzeige übernahm den langen Aktivierungstext als Scope. Beides ist erhalten, nicht als fehlerfreier Gesamtstart bewertet.

Die Formatfrage war kein Worker-Ursprung. Die fehlende externe Freigabe belegt dagegen den tatsächlichen Worker → Manager → Runner-Weg. Sie wurde als notwendige Nutzeraktion gemeldet, nicht als separater technischer BLOCKED-Code. Der Lauf beweist diesen Fall, keine Plattform-Isolation gegenüber jedem anderen Thread. Verschlüsselte Transporttexte wurden nicht entschlüsselt. Native Empfänger, Zeitpunkte, Ergebnisse, Bericht und tatsächliche Runner-Ausgabe liefern die Zuordnung.

## Erster Darstellungsnachtest: PLAN-0007

Runner unverändert, neuer Manager `01a0fb41-39d5-7a61-b118-c16b58e81e60`, Worker `01a0fb45-4a06-7183-b89f-65dcdc665600`: tatsächliche native Metadaten gpt-6-luna / medium. Nachweise unter `<test-root>/workflow-bold-question-20261002/evidence`.

Der Manager erkannte die beiden unterschiedlichen aktiven Adressen schon vor Worker-Dispatch. Der Runner zeigte um 06:16:56 UTC eine fette Entscheidungsüberschrift, fette Frage, PLAN-0007 / W-001/step-1 und Wartegrund. Vor der Antwort war die Exportdatei abwesend. Anschließend erzeugte der Worker die tatsächlich gewählte Adresse `service@example.test` mit einem abschließenden Zeilenumbruch. Eingaben und eingefrorene Paketdateien sind unverändert. Manager/Worker abgeschlossen und archiviert, Konfiguration bytegleich wiederhergestellt.

Dieser Lauf belegt die damalige Darstellungsregel, keine neue Worker-Ursprungsfrage. Der Manager las die Kontakte bereits im Preflight. Während des Laufs präzisierte der Nutzer die Darstellung: vollständige Zuordnung in fetter Statuszeile, Frage normal, Erzeugung durch Pflichthelper. Der neue Helper-Kandidat ist ein weiterer Stand und braucht seinen eigenen nativen Consumer-Nachweis.

## Helper-Nachtest: PLAN-0008

Runner unverändert, Manager `01a0fb62-7bf1-75a2-9435-d78b81e500b9`, Worker `01a0fb64-4323-7e10-8a05-d3fc32b09ad0` und `01a0fb6c-0460-7261-9914-dd00a4ddab37`. Alle nativen Rollenmetadaten bestätigen gpt-6-luna/medium im Testprojekt. Nachweise: `<test-root>/workflow-helper-status-20261002/evidence`.

Working on, Decision needed, Blocked und Completed erschienen mit fetter vollständiger Zuordnung und normalem Erklärungstext. Der Manager erkannte Formatwahl und belegtes Exportziel vor Worker-Dispatch. Nach der tatsächlichen Antwort plain blieb der andere Blocker am selben Step sichtbar. Erst nach externer Bereitstellung des Verzeichnisses schrieb der Worker `Status receipt\n`. Beide Berichtseinträge sind aufgelöst, Ausgabe und Eingaben geprüft, Paketbytes unverändert. Konfiguration bytegleich wiederhergestellt und beide Worker sowie Manager nach Sicherung der Nachweise archiviert.

**Consumer-Fehler erhalten:** Gegenüber der tatsächlichen Helper-JSON-Ausgabe wurden im sichtbaren Frage- und Blockertext zusätzliche Backticks eingefügt. Die Abschlussmeldung war unverändert. Der verändernde Akteur im Übergabe-/Anzeigepfad ist aus den zugänglichen Transportdaten nicht eindeutig belegbar. `helper-consumer.json` und `verification.json` halten den Vergleich fest. Dieser Lauf besteht die unveränderte Übernahme deshalb nicht. Die zentrale Kopierregel wurde für beide beteiligten Rollen präzisiert; PLAN-0009 prüft den neuen Paketstand seriell.

## Trennung von Steuerung und Anzeige: PLAN-0009

Runner unverändert, Manager `01a0fb75-48a8-75b0-9f57-3c3ee9f35507`, Worker `01a0fb7a-30a2-7833-aab5-30f5bb87cee9`. Native Metadaten bestätigen überall gpt-6-luna/medium. Nachweise: `<test-root>/workflow-literal-status-20261002/evidence`.

Der Inhalt wurde unverändert übernommen, aber der Runner zeigte zusätzlich die Protokollzeilen NEEDS_USER_DECISION, BLOCKED, WORKING_ON mit Schlüssel und COMPLETED. Das besteht die reine Textübernahme nicht. Nach tatsächlicher Formatantwort und externer Verzeichnisbereitstellung wurde `Literal receipt\n` korrekt erzeugt. Eingaben/Paketbytes unverändert, beide Berichtseinträge aufgelöst, Plan geschlossen, Konfiguration bytegleich wiederhergestellt. Worker und Manager nach Beweissicherung archiviert.

Die zentrale Regel benennt jetzt die erste Nachrichtenzeile als Protokollmetadatum und lässt den Runner ausschließlich den folgenden Markdowntext übernehmen. PLAN-0010 prüft diesen Stand seriell; kein aktiver Test erhielt nachträglich geänderte Skillbytes.

## Unveränderte Statusübernahme: PLAN-0010

Runner unverändert, Manager `01a0fb7e-3f72-7972-9b8e-ee62284d4ad9`, Worker `01a0fb83-7372-7df1-9c66-ec5cb49fca00`. Native Metadaten bestätigen gpt-6-luna/medium im Testprojekt. Nachweise: `<test-root>/workflow-display-status-20261002/evidence`.

`verification.json` vergleicht die tatsächliche Helper-JSON-Ausgabe mit den nativen Runner-Meldungen: Working on, Decision needed, Blocked und Completed wurden exakt übernommen; keine Steuerzeilen erschienen. Nach wirklicher Formatantwort und externer Verzeichnisbereitstellung entstand genau `Display receipt\n`. Eingaben und eingefrorene Paketbytes unverändert. Plan/Bericht geschlossen, Konfiguration bytegleich wiederhergestellt. Worker und Manager nach Sicherung der IDs und Nachweise archiviert.

Grenzen: Frage und Blocker wurden vom Manager auf Englisch formuliert, obwohl die Aktivierung deutsch war. Dieser erhaltene Sprachfehler ist keine erfolgreiche Prüfung der gesamten Skillbefolgung. Ein erster Dispatch-Builder-Aufruf scheiterte wegen einer noch nicht erzeugten Kontextdatei; nach deren Erstellung wurde seine erfolgreiche Ausgabe verwendet. Paused und frühes Startup sind durch CLI-Consumer-Prüfungen abgedeckt, nicht durch diesen nativen Lauf. Übernahme und agentenübergreifender Kontextwechsel wurden hier nicht ausgelöst.

Die inzwischen gemeldeten sichtbaren HTML-Buchhaltungsmarker stammen aus der unveränderten gespeicherten Berichtsversion. Die neue Ausgabeprojektion display_text wird gesondert mit dem abgeschlossenen tatsächlichen Bericht geprüft; keine Marker werden aus der Datei gelöscht.

## Berichtsanzeige ohne Buchhaltungsmarker

Derselbe Luna-Medium-Runner prüfte den aktuellen Paketstand als nachgelagerten Lese-/Anzeigeconsumer mit dem tatsächlichen abgeschlossenen PLAN-0010-Bericht. Er startete weder Workflow noch weitere Agenten. Nachweise: `<test-root>/workflow-report-display-20261002/evidence`.

Die sichtbare Ausgabe entspricht vollständig dem erfolgreichen read-Ergebnis display_text. Beide Fragen und Auflösungen bleiben erhalten, interne Marker erscheinen nicht. Gespeicherter Bericht, Konfiguration und Paketbytes bleiben unverändert. Native Metadaten bestätigen gpt-6-luna/medium. Nach Sicherung dieser Nachweise wurde auch der Test-Runner archiviert. Testprofil validiert: 18 Dateien, 10 Pläne, 16 Arbeitspunkte, 7 Entscheidungen, keine Fehler.

Die vier eigenen Workflow-Laufzeitdateien wurden aus genau diesem geprüften Paket lokal installiert. Alle anderen 14 installierten Workflow-Dateien wurden bytegleich erhalten, einschließlich der parallel gepflegten Review-Regeln. Installation und vorherige Bytes: `<workspace-state>/2026-10-02-workflow-status-helper`. Die Berichtsanzeige wurde separat nativ geprüft, nicht als weiterer vollständiger Workflow-Lauf. Zehn Feedback-Tests bestanden; die fünfzehn zuvor geprüften Start-Consumer-Tests decken die Projektname-Übergabe ab.

Die autorisierten Live-Runner wurden über die lokale Änderung informiert: Fluid Base `01a0f713-7580-7ba3-b109-b6c12de97e65` in DIVI5 Plugin und EMPCO `01a0f73e-235e-7dd2-aeaf-9d7ebea41569` in EMPCO Check. Beide Nachrichtenzustellungen sind bestätigt; das beweist noch keine erneute Lektüre durch bereits laufende Rollen. Der getrennte Astra-Medium-Bericht zu Opus und weiteren Helpern liegt in `2026-10-02-opus-astra-review.md`. Dessen Review-Stand und Grenzen sind dort festgehalten. Weitergehende Umbauten sind nicht umgesetzt.
