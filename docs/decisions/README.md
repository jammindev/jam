# Décisions (ADR)

Une ADR courte par décision structurante. Format : Contexte → Décision → Conséquences. Numérotation séquentielle, jamais réutilisée. Une ADR remplacée passe au statut « remplacée par NNNN ». Depuis l'[ADR 0016](0016-kit-de-methode.md), une ADR peut aussi devenir « caduque » (elle réglait l'app, plus rien ne l'applique) ou « historique » (elle n'a plus d'objet, sans être contredite).

| # | Titre | Statut |
|---|---|---|
| [0001](0001-from-scratch.md) | Projet from scratch, Orca comme référence de lecture | Acceptée, historique (0016) |
| [0002](0002-orchestrer-claude-code-avant-harness.md) | Orchestrer Claude Code avant d'écrire le harness | Acceptée, caduque (0016) |
| [0003](0003-code-ecrit-par-agents.md) | Le code est écrit par des agents, le mainteneur apprend les concepts | Acceptée |
| [0004](0004-claude-code-headless-stream-json.md) | Intégrer Claude Code en mode headless `stream-json` | Acceptée, caduque (0016) |
| [0005](0005-electron-macos.md) | Electron, macOS uniquement | Acceptée, caduque (0016) |
| [0006](0006-coeur-separe-ui.md) | Cœur séparé de l'UI, version minimale | Acceptée, caduque (0016) |
| [0007](0007-commandes-ui-partagees-agent.md) | Commandes d'interface partagées entre l'humain et l'agent | Acceptée, caduque (0016) |
| [0008](0008-boucle-exterieure-pipeline.md) | Le MVP est la boucle extérieure : le pipeline du mainteneur, codé dans le cœur | Acceptée, valable en partie (0016) |
| [0009](0009-permissions-par-role.md) | Permissions par rôle, jamais de mode sans permission | Acceptée, valable en partie (0016), précisée (0018) |
| [0010](0010-persistance-sqlite.md) | État du pipeline en SQLite | Acceptée, caduque (0016) |
| [0011](0011-pratiques-et-metriques-dora.md) | Pratiques et métriques DORA | Acceptée, valable en partie (0016) |
| [0012](0012-coordinateur-role-garde-fous-hook.md) | Le coordinateur est un rôle, ses garde-fous sont tenus par un hook | Acceptée, précisée (0013, 0016) |
| [0013](0013-orchestration-deux-niveaux.md) | Orchestration à deux niveaux : coordinateur sur `main`, orchestrateur de tâche par worktree | Acceptée, précisée (0015, 0016, 0017, 0018) |
| [0014](0014-lecture-clone-orca-implementeur.md) | L'implémenteur lit le clone de référence d'Orca pour une reprise | Acceptée, historique (0016) |
| [0015](0015-remontee-carte-seule-coordinateur-flottant.md) | Remontée par la carte seule, coordinateur dans le terminal flottant d'Orca | Acceptée, en partie remplacée par 0017, valable en partie (0016) |
| [0016](0016-kit-de-methode.md) | jam est un kit de méthode, pas un outil | Acceptée, précisée (0018) |
| [0017](0017-coordinateur-main-poste-de-travail.md) | Le coordinateur vit dans le `main` du projet, sur le poste de travail | Acceptée, précisée (0018) |
| [0018](0018-process-elague.md) | Process élagué | Acceptée |
