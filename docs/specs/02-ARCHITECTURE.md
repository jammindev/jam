# 02 — Architecture

> Statut : vide. Rempli aux thèmes 4 (orchestration) et 6 (plateforme et stack).

## Vue d'ensemble

```mermaid
flowchart LR
  UI[Interface] <--> Core[Core / orchestrateur]
  Core --> H1[Harness agent 1] --> W1[(Worktree 1)]
  Core --> H2[Harness agent 2] --> W2[(Worktree 2)]
  H1 & H2 --> LLM[API modèle]
```

_Schéma provisoire, à valider._

## Composants

_À compléter._

## Flux principaux

_À compléter._

## Stack

| Couche | Choix | ADR |
|---|---|---|
| Shell desktop | _?_ | — |
| Langage du harness | _?_ | — |
| UI | _?_ | — |
| Persistance | _?_ | — |

## Exécution locale / distante

_À compléter._
