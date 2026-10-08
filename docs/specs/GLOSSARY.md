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
| Backend d'agent | Ce qui exécute réellement un agent derrière l'interface commune : Claude Code (E0) ou le harness maison (E2). | Provisoire |
| Mainteneur | Ben : il décide, relit et merge. Il n'écrit pas le code. | Validé |
| Headless / stream-json | Mode non interactif de Claude Code (`-p`), qui émet un événement JSON par ligne au lieu d'afficher une interface terminal. | Provisoire |
