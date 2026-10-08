# ADR 0002 — Orchestrer Claude Code avant d'écrire le harness

- **Statut** : acceptée (le principe). Le mode d'intégration reste ouvert : voir Q-003.
- **Date** : 2026-10-08
- **Remplace** : la section « ordre de construction » de l'[ADR 0001](0001-from-scratch.md)

## Contexte

L'ordre initial commençait par le harness en CLI (E1), avant les worktrees et l'interface. Or Ben veut **utiliser l'outil dès le début**. Claude Code fonctionne déjà bien et passe par son abonnement existant.

## Décision

- Nouvelle première étape **E0** : l'éditeur orchestre des agents **Claude Code** (un worktree par agent, en parallèle), à la manière d'Orca.
- Le harness maison arrive **ensuite**, une fois que Claude Code tourne bien dans l'outil. Il devient alors un deuxième type d'agent, au même niveau que Claude Code.
- La comparaison entre le harness maison et Claude Code sur une même tâche devient une fonctionnalité naturelle.

## Conséquences

- (+) L'outil sert dès les premières semaines, ce qui garantit un retour d'usage réel.
- (+) Pas de coût API au départ : Claude Code utilise l'abonnement.
- (+) Les briques worktree, UI et diff sont construites et éprouvées avant le harness, qui s'y branche.
- (−) **On reconstruit d'abord une partie d'Orca**, outil que Ben utilise déjà. L'apprentissage du harness est repoussé, avec le risque de ne jamais y arriver.
- (−) Selon le mode d'intégration choisi (Q-003), on hérite de la partie la plus fragile d'Orca : PTY, détection de l'état d'une TUI, perte de prompts (voir [références Orca §4](../references/orca.md)).
- Contrainte d'architecture : une **interface « backend d'agent »** commune (Claude Code et harness maison) doit être définie dès E0, sinon l'arrivée du harness imposera une réécriture.
