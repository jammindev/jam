# 00 — Vision

> Statut : thème 1 clos le 2026-10-08.

## Pitch

Un **cockpit de loop engineering**. L'outil déroule la méthode de travail du mainteneur sur chaque issue, dans son propre worktree. Pour cela, il fait travailler des rôles d'agents (plan, TDD, relecture, recette) jusqu'au merge, et n'interrompt le mainteneur que pour trois feux verts.

Le projet tient en deux boucles :

1. **La boucle extérieure** (MVP, [ADR 0008](../decisions/0008-boucle-exterieure-pipeline.md)) : le pipeline, codé dans le cœur, qui fait d'abord travailler **Claude Code**.
2. **La boucle intérieure** (ensuite) : le harness maison, avec sa propre boucle d'agent (modèle, outils, permissions, contexte). Il devient un deuxième backend et permet d'**imposer** les rôles.

## Pourquoi

- **Envie de construire son propre outil.** La motivation de départ est le plaisir de construire un outil qu'on maîtrise (Q-004). L'analyse d'usage révèle en plus de vrais manques chez Orca : notifications bruyantes, questions invisibles, méthode qui dépend de l'obéissance des agents. Pour un projet solo mené sur le temps libre, c'est le premier facteur de réussite, il faut donc la préserver.
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
| 1 mois (fin d'E0) | Sur `house`, 3 issues réelles traversent le pipeline en parallèle jusqu'au merge. Le mainteneur n'intervient que sur la file « À toi ». L'outil a servi à au moins 5 vraies tâches. |
| 3 mois | Le harness maison, en CLI, résout seul une vraie tâche et affiche son coût. |
| 6 mois | Le harness maison est branché dans l'outil comme backend d'agent et comparé à Claude Code sur une même tâche. |

## Principes

- **Partir du minimum et grandir à l'usage.** Le squelette minimal, c'est le pipeline. Une fonction ne s'ajoute que lorsque le besoin se fait sentir à l'usage. On n'élague pas le code d'Orca ([ADR 0001](../decisions/0001-from-scratch.md)).
- **Interrompre le moins possible.** Le mainteneur n'est sollicité que pour une décision. Son attention est la ressource rare, pas le nombre d'agents.
- **Une méthode imposée plutôt qu'espérée.** Ce que le code peut garantir, comme l'ordre des étapes ou les feux verts, ne doit pas dépendre de l'obéissance d'un agent.
- **E0 dure au plus un mois.** Ensuite on passe au harness ([ADR 0002](../decisions/0002-orchestrer-claude-code-avant-harness.md)). Orca reste l'outil de repli.
- **Comprendre avant d'empiler.** Chaque brique livrée doit pouvoir s'expliquer en quelques lignes : quel concept elle met en œuvre, et pourquoi elle est conçue ainsi.

## Contraintes

- Une seule personne, sur son temps libre.
- From scratch ([ADR 0001](../decisions/0001-from-scratch.md)).
- Aucune mention d'auteur IA dans le repo, les commits ou les PR (règle du mainteneur).
