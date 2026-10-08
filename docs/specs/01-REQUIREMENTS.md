# 01 — Exigences

> Statut : brouillon. Priorités MoSCoW : **M**ust, **S**hould, **C**ould, **W**on't (pour l'instant).
> Étapes de roadmap : **E1** harness CLI · **E2** worktrees + parallélisme · **E3** interface · **E4** confort.

## Exigences fonctionnelles

| ID | Exigence | Priorité | Étape | Source |
|---|---|---|---|---|
| FR-001 | Le harness exécute une boucle d'agent (modèle → outils → modèle) jusqu'à la fin de la tâche. | M | E1 | Prompt initial |
| FR-002 | Outils minimaux : `read`, `write`, `shell`, `search`. | M | E1 | Prompt initial |
| FR-003 | Chaque agent travaille dans son propre git worktree. | M | E2 | Prompt initial |
| FR-004 | Plusieurs agents tournent en parallèle. | M | E2 | Prompt initial |
| FR-005 | L'interface liste les agents et affiche le fil d'activité de chacun. | M | E3 | Prompt initial |
| FR-006 | L'interface affiche le diff d'un agent et permet d'accepter ou de refuser. | M | E3 | Prompt initial |
| FR-007 | Éditeur intégré. | _?_ | E4 | Prompt initial |
| FR-008 | Notifications. | _?_ | E4 | Prompt initial |
| FR-009 | Navigateur intégré façon Design Mode. | _?_ | E4 | Prompt initial |

## Exigences non fonctionnelles

| ID | Exigence | Priorité | Étape | Source |
|---|---|---|---|---|
| NFR-001 | Le MVP est réalisable par une personne seule sur du temps libre. | M | — | Prompt initial |

_À compléter au fil des lots._
