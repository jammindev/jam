# ADR 0003 — Le code est écrit par des agents, le mainteneur apprend les concepts

- **Statut** : acceptée
- **Date** : 2026-10-08

## Contexte

L'objectif d'apprentissage pouvait laisser penser que le mainteneur écrirait lui-même le cœur du harness. Ce n'est pas le cas. Il ne code pas : ce qui l'intéresse, ce sont les **concepts** (boucle d'agent, outils, permissions, contexte, orchestration), dans une pratique où le code est désormais produit par des agents.

## Décision

- 100 % du code est écrit par des agents. Le mainteneur rédige les specs, arbitre, relit les diffs et décide des merges.
- On apprend en lisant et en comprenant, pas en tapant. Les docs et les ADR doivent donc expliquer le *pourquoi* des choix, et chaque brique livrée doit être explicable simplement.
- Aucune mention d'auteur IA n'apparaît dans le repo, les messages de commit ou les PR.

## Conséquences

- (+) Le rythme n'est plus limité par la vitesse de frappe du mainteneur ni par sa maîtrise d'un langage.
- (+) Le critère « le mainteneur débute en Rust, Tauri ou Electron » pèse moins dans le choix de stack. Ce qui pèse davantage, c'est la lisibilité du code et la qualité de production des agents dans ce langage.
- (−) Risque de ne plus comprendre son propre outil. Mitigation : des docs de concepts tenues à jour, et des briques petites et relues.
- (−) La qualité dépend de la précision des specs et de la revue. Les docs de `docs/specs/` deviennent le contexte de travail des agents.
