# 01 — Exigences

> Statut : brouillon. Priorités MoSCoW : **M**ust, **S**hould, **C**ould, **W**on't (pour l'instant).
> Étapes de roadmap (provisoire, voir 04-ROADMAP) : **E0** orchestration de Claude Code · **E1** harness maison · **E2** harness dans l'outil, en parallèle · **E3** confort.

## Exigences fonctionnelles

| ID | Exigence | Priorité | Étape | Source |
|---|---|---|---|---|
| FR-010 | L'outil lance des agents **Claude Code**, chacun dans son worktree, en parallèle. | M | E0 | ADR 0002 |
| FR-012 | Claude Code est piloté en mode headless (`claude -p --output-format stream-json`, reprise par `--resume`). L'outil affiche ses événements structurés : messages, appels d'outils, coût. | M | E0 | ADR 0004 |
| FR-011 | Claude Code et le harness maison passent par une même interface « backend d'agent ». | M | E0 | ADR 0002 |
| FR-001 | Le harness exécute une boucle d'agent (modèle → outils → modèle) jusqu'à la fin de la tâche. | M | E1 | Prompt initial |
| FR-002 | Outils minimaux : `read`, `write`, `shell`, `search`. | M | E1 | Prompt initial |
| FR-003 | Chaque agent travaille dans son propre git worktree. | M | E0 | Prompt initial |
| FR-004 | Plusieurs agents tournent en parallèle. | M | E0 | Prompt initial |
| FR-005 | L'interface liste les agents et affiche le fil d'activité de chacun. | M | E0 | Prompt initial |
| FR-006 | L'interface affiche le diff d'un agent et permet d'accepter ou de refuser. | M | E0 | Prompt initial |
| FR-007 | Éditeur intégré. | _?_ | E3 | Prompt initial |
| FR-008 | Notifications. | _?_ | E3 | Prompt initial |
| FR-009 | Navigateur intégré façon Design Mode. | _?_ | E3 | Prompt initial |

## Exigences non fonctionnelles

| ID | Exigence | Priorité | Étape | Source |
|---|---|---|---|---|
| NFR-001 | Le MVP est réalisable par une personne seule sur du temps libre. | M | — | Prompt initial |
| NFR-002 | Repo public : aucun secret, aucune donnée perso ni chemin machine dans le code ou les docs. Licence explicite. | M | E0 | Thème 1 |
| NFR-003 | Aucune mention d'auteur IA (trailer de commit, signature de PR, texte des docs). | M | — | Thème 1 |
| NFR-004 | Chaque brique livrée est accompagnée d'une explication courte du concept qu'elle met en œuvre. | S | — | ADR 0003 |
| NFR-005 | macOS est la seule plateforme ciblée au MVP. Windows est exclu. | M | E0 | Thème 1 (non-objectif c) |

_À compléter au fil des lots._
