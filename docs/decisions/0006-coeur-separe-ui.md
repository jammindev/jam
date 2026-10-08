# ADR 0006 — Cœur séparé de l'UI, version minimale

- **Statut** : acceptée
- **Date** : 2026-10-08

## Contexte

Le cœur couvre l'orchestration, les worktrees, les backends d'agent et, plus tard, le harness. Il doit pouvoir tourner **sans interface**, pour deux raisons :

- le harness doit pouvoir être lancé en CLI ;
- il faut pouvoir, un jour, le faire tourner sur le VPS ou le piloter depuis un autre client.

OpenCode (`opencode serve`) et Orca (daemon, puis `orca serve`) font tous deux ce choix.

## Décision

- Le cœur est un **processus séparé** qui expose un **protocole typé**. L'app Electron le lance en local et s'y connecte en tant que client.
- **Version minimale au MVP** :
  - un seul processus, en local ;
  - aucune authentification réseau ;
  - aucun accès distant ;
  - aucune négociation de version.
- Les agents tournent en local uniquement.

## Conséquences

- (+) Le harness en CLI, l'exécution distante et d'éventuels clients supplémentaires deviendront possibles sans réécriture.
- (+) Les agents peuvent survivre à un rechargement de l'UI.
- (−) Une couche de plus que la solution « tout dans le main process d'Electron » : il faut un protocole, gérer le cycle de vie du processus et gérer les reconnexions.
- **Garde-fou contre la sur-ingénierie** : tout ce qui touche au distant (authentification, TLS, multi-clients, compatibilité de versions) est explicitement repoussé.
- **Langage du cœur : TypeScript** (Q-008), en mode strict, avec validation des données à l'exécution (zod). Pourquoi pas Rust : le cœur est limité par les entrées/sorties (modèle, git, réseau), et Electron, les SDK officiels et le code d'Orca sont en TS. Rust ajouterait un second langage et une seconde chaîne de build, et le rendrait illisible pour le mainteneur. Rust reste envisageable plus tard pour une pièce isolée (sandbox, binaire VPS).
