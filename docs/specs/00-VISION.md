# 00 — Vision

> Statut : thème 1 clos le 2026-10-08.

## Pitch

Un éditeur centré sur la gestion d'agents IA. Plusieurs agents travaillent en parallèle, chacun dans son git worktree, et on les suit, on relit leurs diffs et on merge depuis une seule interface.

Le projet se construit en deux temps :

1. Il orchestre d'abord **Claude Code**, comme le fait Orca.
2. Il devient ensuite **lui-même le harness**, avec sa propre boucle d'agent : appels au modèle, outils, permissions, contexte.

## Pourquoi

- **Envie de construire son propre outil.** Orca couvre déjà le besoin fonctionnel : rien de précis ne lui manque (Q-004). La motivation, c'est le plaisir de construire un outil qu'on maîtrise. Pour un projet solo mené sur le temps libre, c'est le premier facteur de réussite, il faut donc la préserver.
- **Comprendre les concepts** d'un harness d'agent de l'intérieur : la boucle, les outils, les permissions, le contexte, l'orchestration.

## Pour qui

- **Ben, d'abord.** C'est son outil de travail quotidien.
- **Un projet public** sur GitHub, sans promesse de support. Le repo sert aussi de vitrine et d'exemple d'apprentissage. Le choix de licence est traité au thème 11.

## Objectifs

1. **Apprendre les concepts**, pas écrire du code. Le code est écrit à 100 % par des agents ([ADR 0003](../decisions/0003-code-ecrit-par-agents.md)). Ben pilote, relit, décide et comprend.
2. **Obtenir un outil utilisé au quotidien**, dès E0.
3. **Pour le code d'abord.** À terme, l'outil doit pouvoir servir à d'autres tâches (documents, recherche, ops…). On garde donc un vocabulaire générique (« espace de travail », « agent ») quand ça ne coûte rien. Mais aucune fonction propre au non-code n'entre dans le MVP.

## Non-objectifs

- (a) Multi-utilisateur, collaboration en temps réel.
- (b) Remplacer VS Code : pas d'extensions, LSP minimal ou absent.
- (c) Windows.
- (d) Modèles locaux, mode hors ligne. _À revoir au thème 3._
- (e) SaaS ou hébergement pour des tiers.
- (f) Marketplace de plugins.

## Critères de succès

| Horizon | Critère vérifiable |
|---|---|
| 1 mois (fin d'E0) | Depuis l'outil, 3 agents Claude Code tournent en parallèle sur `house`, chacun dans son worktree, avec diff et merge. L'outil a servi à au moins 5 vraies tâches. |
| 3 mois | Le harness maison, en CLI, résout seul une vraie tâche et affiche son coût. |
| 6 mois | Le harness maison est branché dans l'outil comme backend d'agent et comparé à Claude Code sur une même tâche. |

## Principes

- **Un Orca nu, qui grandit à l'usage.** On part d'un squelette minimal du concept d'Orca : agents dans des worktrees, suivi, diff, merge. Une fonction ne s'ajoute que lorsque le besoin se fait sentir à l'usage. Il ne s'agit pas d'élaguer le code d'Orca ([ADR 0001](../decisions/0001-from-scratch.md)).
- **E0 dure au plus un mois.** Ensuite on passe au harness ([ADR 0002](../decisions/0002-orchestrer-claude-code-avant-harness.md)). Orca reste l'outil de repli.
- **Comprendre avant d'empiler.** Chaque brique livrée doit pouvoir s'expliquer en quelques lignes : quel concept elle met en œuvre, et pourquoi elle est conçue ainsi.

## Contraintes

- Une seule personne, sur son temps libre.
- From scratch ([ADR 0001](../decisions/0001-from-scratch.md)).
- Aucune mention d'auteur IA dans le repo, les commits ou les PR (règle du mainteneur).
