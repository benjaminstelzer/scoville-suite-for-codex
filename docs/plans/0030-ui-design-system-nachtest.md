---
format_version: 1
id: PLAN-0030
status: active
created: 2026-10-01
updated: 2026-10-02
current_item: W-004
---

# UI prüft vorgegebene Design-Systeme

## Goal

Prüfen, ob Scoville UI vorgegebene Spacing-, Schrift- und Farbrollen erkennt,
Abweichungen in Quelle und Render belegt und korrekte Varianten erhält. Allgemeine
UI und unterstütztes WordPress-Backend verwenden denselben Prüfvertrag mit ihrem
jeweiligen Owner. Reale Tests laufen seriell im gespeicherten Projekt test mit
Luna Medium; die nachfolgende Analyse ausdrücklich mit Astra Medium.
Zusätzlich Rückfragen und Blocker des Workflow über den sichtbaren Runner melden.

## Non-goals

Keine Reparatur der Testoberfläche oder Arbeit an Live-Projekten. Keine allgemeine
4px-Pflicht, erfundenen WordPress-Normen oder Wirkungsgarantie. UI-Nachtest allein
veröffentlicht nichts; W-004 hat einen ausdrücklich beauftragten Codex-Suite-Release.
PLAN-0029 und sein abgeschlossener Release bleiben erhalten.

## Work items

### W-001 Erkennbares Design-System und unabhängiger Ausgangstest

Status: paused
Depends on: []
Blocked by: []
Decisions: [ADR-0138]
Outcome: Reproduzierbare Vorlagen und unabhängige Luna-Audits gegen offene Owner-Vorgaben.
Acceptance: Allgemeiner Test beschreibt 4px-Raster, 8px Boxabstand, 4px Innenabstand sowie Schrift- und Farbrollen. WordPress-Fall liefert versionierte native Owner-Quellen. Beide enthalten gezielte Verstöße und korrekte Gegenproben. Tatsächliche Befunde, Messungen, Renders und Referenzlektüre sind mit getrennt gehaltener Fehlerliste auswertbar; offene Grenzen bleiben sichtbar.
Instructions: After W-004 completes, resume W-001 at Step 1. Auditagenten bekommen keine Fehlerliste; Artefakte und native Läufe unter C:/Users/benja/Desktop/test erhalten. WordPress nur Classic auf scoville-ui-test; temporäres Plugin nach Tests entfernen.
Steps:
1. [status: in_progress] Owner-Verträge, Ausgangsvorlagen und getrennte Sollauswertung vorbereiten; WordPress-Quelle und Runtime nachweisen.
2. [status: todo] Beide Vorlagen seriell mit frischem Luna Medium auditieren und tatsächliche Erkennung gegen die Sollauswertung prüfen.
Evidence: []

### W-004 Rückfragen und Blocker im sichtbaren Runner

Status: in_progress
Depends on: []
Blocked by: []
Decisions: [ADR-0139]
Outcome: Der Runner zeigt jede notwendige Frage und den konkreten Stillstandsgrund.
Acceptance: Kind → Manager → Runner ist für laufende Rückfragen, Manager-Blocker und Helperfehler eindeutig. Frage, Grund, betroffene Arbeit und wartender Zustand bleiben sichtbar; unveränderter Fortschrittschlüssel unterdrückt keine neue Meldung. gpt-6-luna Medium testet sichtbare Ausgabe, Astra Medium den gesamten Skill. Verifiziertes lokales Update, Hinweise an beide Workflows und Codex-Suite-Release folgen; Authentifizierung, Scope und Freigaben bleiben erhalten.
Instructions: Vor dem UI-Nachtest prüfen und korrigieren; anschließend zu W-001 zurückkehren. Astra liest nur den gebauten Workflow-Skill ohne Plan, Entwicklungsdokumentation, Testberichte oder Verlauf; prüft klare schlanke Sprache, Dopplungen und Regelkorrektheit. Keine Bearbeitung von DIVI-Projektdateien.
Steps:
1. [status: done] DIVI-Runner und Regeln prüfen, Weiterleitung mit Frage und Grund am kanonischen Skill korrigieren.
2. [status: done] Gebaute Regeln seriell mit gpt-6-luna Medium auf sichtbare Ausgabe prüfen und Astra Medium den gesamten Skill reviewen lassen; belegte Fehler korrigieren und nachtesten.
3. [status: in_progress] Verifiziert lokal installieren, Fluid Base sowie EMPCO informieren und Codex-Suite auf GitHub veröffentlichen.
Evidence: Luna zeigt Steps, Fragen und Blocker; Astra-Korrekturen freigegeben. ../../../temp/2026-10-01-ui-design-system-tests/workflow-feedback-assessment.md

### W-002 Astra analysiert tatsächliche Prüflücken

Status: todo
Depends on: [W-001]
Blocked by: []
Decisions: [ADR-0138]
Outcome: Aus beobachteten Fehlern abgeleitete, begrenzte Skill-Korrektur oder begründeter Befund ohne Änderung.
Acceptance: Astra Medium liest tatsächliche Ausgangsergebnisse, Sollauswertung und relevante Skill-Regeln. Übersehene Verstöße, falsche Befunde und Prüfgrenzen bleiben unterscheidbar. Änderungen lösen belegte Regelprobleme am kanonischen Owner und gelten allgemein wie für WordPress, ohne native Ausnahmen zu überschreiben.
Instructions: Bereits vorhandene Regeln und gelesene Referenzen gegen tatsächliche Ausführung prüfen; keine neue Regel allein für einen vorgegebenen Zahlenwert.
Steps:
1. [status: todo] Astra Medium die Ausgangsläufe unabhängig analysieren lassen und Befunde am vollständigen relevanten Vertrag prüfen.
2. [status: todo] Belegte Korrekturen an members/scoville-ui/scoville-ui umsetzen, Referenzen und gebaute Projektionen validieren.
Evidence: []

### W-003 Nachtest und lokale Aktualisierung

Status: todo
Depends on: [W-002]
Blocked by: []
Decisions: [ADR-0138]
Outcome: Unabhängiger Nachtest mit erhaltener Gegenprobe und nachvollziehbarem lokalen Skill-Stand.
Acceptance: Frisches Luna Medium prüft beide Owner-Routen mit originalen und anderen Verletzungsstellen ohne Fehlerliste. Beobachtete Erkennung und falsche Befunde werden mit dem Ausgangslauf verglichen. Nur verifizierte Änderungen werden lokal für Codex und Claude installiert; danach sind Fluid-Base- und EMPCO-Workflow informiert. Ohne Skill-Änderung wird kein Update behauptet.
Instructions: Auditprodukte unverändert erhalten. Keine neue GitHub-Veröffentlichung. Live-Skill-Reload und ungetestete WordPress-Versionen nicht behaupten.
Steps:
1. [status: todo] Gebauten Kandidaten seriell nachtesten, Auswertung und verbliebene Grenzen prüfen.
2. [status: todo] Falls geändert, Skill sauber committen, verifizierte lokale Pakete aktualisieren und beide vorhandenen Workflow-Chats informieren; Plan mit Nachweisen abschließen.
Evidence: []
