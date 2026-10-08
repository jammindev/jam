# 04 — Roadmap

> Statut : brouillon. Ordre revu par l'[ADR 0002](../decisions/0002-orchestrer-claude-code-avant-harness.md). Les jalons hebdomadaires seront découpés en fin d'entretien.

## Étapes

| Étape | Contenu | Statut |
|---|---|---|
| E0 | Orchestration de **Claude Code** : un worktree par agent, plusieurs agents en parallèle, interface minimale (liste d'agents, fil d'activité, diff, accepter/refuser). Interface « backend d'agent » définie dès ici. | À faire |
| E1 | Harness maison minimal en CLI : boucle + outils (read, write, shell, search) | À faire |
| E2 | Le harness maison branché dans l'outil comme deuxième backend d'agent, comparaison avec Claude Code | À faire |
| E3 | Confort : éditeur intégré, notifications, navigateur façon Design Mode | À faire |

_Les numéros E1 à E3 sont provisoires et seront renumérotés une fois le lot 1 clos._

## Périmètre du MVP

_À compléter._

## Jalons (≈ 1 semaine chacun)

| # | Jalon | Critère de « fini » vérifiable |
|---|---|---|

## Explicitement repoussé

_À compléter._

## Risques principaux

- **R-01** — Rester bloqué à E0 et reconstruire Orca sans jamais écrire le harness. _Mitigation à définir : borner E0 dans le temps._
