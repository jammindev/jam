# Glossaire

> « Provisoire » = pas encore validé.

| Terme | Définition | Statut |
|---|---|---|
| Boucle intérieure | La boucle d'un agent : modèle → outils → modèle, jusqu'à la fin de sa tâche. C'est le **harness**. | Validé |
| Boucle extérieure | Le système qui trouve le travail, le confie à des agents, fait vérifier et attend les feux verts. C'est le **pipeline** (ADR 0008). | Validé |
| Loop engineering | Pratique (2026) qui consiste à construire la boucle extérieure plutôt que de prompter un agent tour par tour. | Validé |
| Harness | Programme qui exécute la boucle intérieure : appels au modèle, outils, permissions, contexte. | Validé |
| Pipeline | La séquence d'étapes codée en dur du mainteneur : plan → TDD → relecture → recette → PR + CI → merge. | Validé |
| Étape | Un maillon du pipeline, exécuté par un rôle ou par un feu vert. | Validé |
| Rôle | Profil d'agent (prompt, outils, permissions) instancié à la demande avec un contexte neuf : planificateur, implémenteur, relecteur, recetteur. L'« équipe », c'est l'ensemble des rôles. | Validé |
| Lead | La session principale d'un worktree, à laquelle le mainteneur peut parler. | Provisoire |
| Coordinateur | Agent conversationnel au niveau du projet : cadrage, issues, arbitrages. Arrive après E0. | Provisoire |
| Feu vert | Validation humaine explicite. Il y en a trois : plan, recette, merge. | Validé |
| File « À toi » | Liste de ce qui attend le mainteneur : feux verts, questions, blocages, recettes. | Validé |
| Tâche | Une issue GitHub qui traverse le pipeline dans son worktree. | Validé |
| Worktree | Checkout git isolé (`git worktree`), un par tâche. | Validé |
| Garde-fou | Plafond d'itérations ou de budget par étape. Son dépassement fait passer la tâche à l'état « bloqué ». | Validé |
| Agent | Une instance de rôle en cours d'exécution, via un backend d'agent. | Provisoire |
| Backend d'agent | Ce qui exécute réellement un agent : Claude Code headless (E0) ou le harness maison (E2). | Validé |
| Headless / stream-json | Mode non interactif de Claude Code (`-p`), qui émet un événement JSON par ligne. | Validé |
| Tour (turn) | Un aller-retour modèle → éventuels appels d'outils. | Provisoire |
| Outil (tool) | Capacité exposée au modèle, décrite par un schéma. | Provisoire |
| Commande d'UI | Action nommée et typée de l'interface, partagée par la palette et l'agent (ADR 0007). | Validé |
| Mainteneur | Ben. Il décide, donne les feux verts, recette. Il n'écrit pas le code. | Validé |
