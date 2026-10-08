# Glossaire

> Définitions à stabiliser au fil de l'entretien. « Provisoire » = pas encore validé.

| Terme | Définition | Statut |
|---|---|---|
| Harness | Programme qui exécute la boucle d'agent : appels au modèle, exécution des outils, permissions, gestion du contexte. | Provisoire |
| Agent | Instance du harness qui travaille sur une tâche, avec sa configuration (modèle, outils, permissions). | Provisoire |
| Worktree | Checkout git isolé (`git worktree`) dédié à un agent. | Provisoire |
| Tâche | Unité de travail confiée à un ou plusieurs agents. | Provisoire |
| Session | _À définir_ | — |
| Run | _À définir_ | — |
| Tour (turn) | Un aller-retour modèle → éventuels appels d'outils. | Provisoire |
| Outil (tool) | Capacité exposée au modèle (read, write, shell, search…), décrite par un schéma. | Provisoire |
