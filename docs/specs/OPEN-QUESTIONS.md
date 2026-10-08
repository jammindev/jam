# Questions ouvertes

| # | Question | Thème | Qui ou quoi tranche | Statut |
|---|---|---|---|---|
| Q-001 | Nom du projet (pistes : Musher, Bœuf, Riff, Attelage, Pod, Shoal) | 11 — Identité | Ben, après vérification GitHub / npm / .dev | Ouvert. Nom provisoire : `jam` |
| Q-002 | Facturation : un harness maison doit passer par une **clé API** (paiement à l'usage), pas par un abonnement claude.ai. Quel budget mensuel est acceptable, et à quel moment ce coût met-il l'usage quotidien en danger ? | 3 — Harness | Ben, avec le suivi de coûts mesuré en E1 | Ouvert |
| Q-003 | Mode d'intégration de Claude Code en E0 : TUI dans un terminal (PTY), mode headless `stream-json`, ou Agent SDK ? | 1 / 3 — Harness | Ben | **Tranché** : headless `stream-json` (ADR 0004) |
| Q-004 | Que manque-t-il à Orca pour que l'outil E0 vaille la peine de l'utiliser à sa place ? | 1 / 2 — Cas d'usage | Ben | **Tranché, puis nuancé** : Ben ne cite aucun manque, c'est l'envie de construire (voir 00-VISION). L'analyse d'usage (`docs/research/usage-2026-10.md`) révèle pourtant des frictions concrètes avec Orca : notifications bruyantes, questions en attente invisibles, visibilité des worktrees, lancement peu fiable, collisions. |
| Q-005 | Ordre des briques d'E0 | Roadmap | Ben | **Tranché** par l'ADR 0008 : squelette → issue/worktree → rôle → pipeline → file « À toi » → PR/CI/merge (voir 04-ROADMAP) |
| Q-006 | Licence du projet public | 11 — Identité | Ben | **Tranché** : MIT |
| Q-007 | Faut-il un dossier `docs/concepts/`, une fiche courte par concept appris (boucle, worktree, stream-json…) ? | Qualité / apprentissage | Ben | **Tranché** : oui, voir `docs/concepts/README.md` |
| Q-008 | Langage du cœur : TypeScript ou Rust ? | 6 — Stack | Ben | **Tranché** : TypeScript strict + validation zod (ADR 0006) |
| Q-009 | L'ADR 0007 (l'agent pilote l'UI à la voix) suppose un agent conversationnel. Or le coordinateur arrive en E0.5. Faut-il un mini-assistant en E0, qui ne fait que lire l'état et lancer des commandes d'UI, ou décaler FR-015 et FR-016 en E0.5 ? | Cohérence | Ben | **Tranché** : reporté en E0.5, la palette reste disponible dès E0 |
| Q-010 | Mode de permissions de Claude Code headless pour des étapes qui tournent sans surveillance (planificateur en lecture seule, implémenteur limité au worktree…) | 7 — Sécurité | Ben | **Tranché** : ADR 0009 |
| Q-011 | Persistance de l'état du pipeline (SQLite via `node:sqlite` comme Orca, ou fichiers) | 8 — Données | Ben | **Tranché** : ADR 0010 |
| Q-012 | Où vivent les profils de rôle : dans le repo cible (`.claude/agents/*.md`), dans l'outil, ou les deux ? | 3 / 4 | Ben | Provisoire : `docs/process/roles/` dans le repo, en Markdown générique. À réviser en E0 (S2). |
| Q-013 | Créer le repo public `jammindev/jam` sur GitHub (nécessaire pour les issues, les PR et la CI du pipeline) | 9 — Intégrations | Ben | Ouvert |
