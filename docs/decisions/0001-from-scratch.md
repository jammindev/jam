# ADR 0001 — Projet from scratch, Orca comme référence de lecture

- **Statut** : acceptée
- **Date** : 2026-10-08

## Contexte

Le projet vise un éditeur centré sur des agents IA en parallèle (un worktree par agent), dans l'esprit d'Orca (stablyai/orca, MIT). Orca orchestre des CLI d'agents existantes (Claude Code, Codex…) lancées dans des terminaux. Ce projet doit au contraire **être lui-même le harness**. Il a aussi un objectif d'apprentissage.

## Décision

- Partir d'un repo vide. Pas de fork d'Orca.
- Orca sert de référence de lecture. On peut en reprendre des morceaux, à condition de conserver la mention de licence MIT (copyright et texte de licence) dans les fichiers concernés ou dans un `THIRD_PARTY_NOTICES`.
- Construire dans cet ordre : E1 harness CLI → E2 worktrees et parallélisme → E3 interface → E4 confort.

## Conséquences

- (+) Architecture pensée autour du harness intégré, sans dette héritée d'un modèle « terminal + CLI tierce ».
- (+) L'objectif d'apprentissage est servi : chaque brique est comprise.
- (−) Plus long avant d'avoir un outil utilisable au quotidien.
- (−) Les fonctions d'Orca (terminal, diff, gestion de worktrees) sont à refaire ou à adapter.
