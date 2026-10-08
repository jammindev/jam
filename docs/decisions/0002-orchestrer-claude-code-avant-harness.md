# ADR 0002 — Orchestrer Claude Code avant d'écrire le harness

- **Statut** : acceptée. Mode d'intégration : [ADR 0004](0004-claude-code-headless-stream-json.md).
- **Date** : 2026-10-08
- **Remplace** : la section « ordre de construction » de l'[ADR 0001](0001-from-scratch.md)

## Contexte

L'ordre initial commençait par le harness en CLI (E1), avant les worktrees et l'interface. Or Ben veut **utiliser l'outil dès le début**. Claude Code fonctionne déjà bien et passe par son abonnement existant.

## Décision

- Nouvelle première étape **E0** : l'éditeur orchestre des agents **Claude Code** (un worktree par agent, en parallèle), à la manière d'Orca.
- Le harness maison arrive **ensuite**, une fois que Claude Code tourne bien dans l'outil. Il devient alors un deuxième type d'agent, au même niveau que Claude Code.
- La comparaison entre le harness maison et Claude Code sur une même tâche devient une fonctionnalité naturelle.
- **E0 est limitée à environ 1 mois.** Une fois ce délai écoulé, on passe au harness même si E0 n'est pas parfaite. Orca reste l'outil de repli.
- E0 part du strict minimum et s'enrichit fonction par fonction, au gré des besoins rencontrés à l'usage.

## Conséquences

- (+) L'outil sert dès les premières semaines, ce qui garantit un retour d'usage réel.
- (+) Pas de coût API au départ : Claude Code utilise l'abonnement.
- (+) Les briques worktree, UI et diff sont construites et éprouvées avant le harness, qui s'y branche.
- (−) **On reconstruit d'abord une partie d'Orca**, outil que Ben utilise déjà. L'apprentissage du harness est repoussé, avec le risque de ne jamais y arriver.
- (−) Avec un terminal interactif, on hériterait de la partie la plus fragile d'Orca : PTY, détection de l'état d'une TUI, perte de prompts (voir [références Orca §4](../references/orca.md)). L'ADR 0004 évite ce piège.
- Contrainte d'architecture : une **interface « backend d'agent »** commune (Claude Code et harness maison) doit être définie dès E0, sinon l'arrivée du harness imposera une réécriture.
