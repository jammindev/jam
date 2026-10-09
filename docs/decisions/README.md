# Décisions (ADR)

Une ADR courte par décision structurante. Format : Contexte → Décision → Conséquences. Numérotation séquentielle, jamais réutilisée. Une ADR remplacée passe au statut « remplacée par NNNN ».

| # | Titre | Statut |
|---|---|---|
| [0001](0001-from-scratch.md) | Projet from scratch, Orca comme référence de lecture | Acceptée |
| [0002](0002-orchestrer-claude-code-avant-harness.md) | Orchestrer Claude Code avant d'écrire le harness | Acceptée |
| [0003](0003-code-ecrit-par-agents.md) | Le code est écrit par des agents, le mainteneur apprend les concepts | Acceptée |
| [0004](0004-claude-code-headless-stream-json.md) | Intégrer Claude Code en mode headless `stream-json` | Acceptée |
| [0005](0005-electron-macos.md) | Electron, macOS uniquement | Acceptée |
| [0006](0006-coeur-separe-ui.md) | Cœur séparé de l'UI, version minimale | Acceptée |
| [0007](0007-commandes-ui-partagees-agent.md) | Commandes d'interface partagées entre l'humain et l'agent | Acceptée |
| [0008](0008-boucle-exterieure-pipeline.md) | Le MVP est la boucle extérieure : le pipeline du mainteneur, codé dans le cœur | Acceptée |
| [0009](0009-permissions-par-role.md) | Permissions par rôle, jamais de mode sans permission | Acceptée |
| [0010](0010-persistance-sqlite.md) | État du pipeline en SQLite | Acceptée |
| [0011](0011-pratiques-et-metriques-dora.md) | Pratiques et métriques DORA | Proposée |
| [0012](0012-coordinateur-role-garde-fous-hook.md) | Le coordinateur est un rôle, ses garde-fous sont tenus par un hook | Proposée |
| [0014](0014-lecture-clone-orca-implementeur.md) | L'implémenteur lit le clone de référence d'Orca pour une reprise | Acceptée |
