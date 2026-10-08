# ADR 0007 — Des commandes d'interface partagées entre l'humain et l'agent

- **Statut** : acceptée
- **Date** : 2026-10-08

## Contexte

Le mainteneur pilote déjà ses agents à la voix, avec la dictée Wispr Flow, et veut que l'agent puisse agir sur l'interface : ouvrir un panneau, afficher un fichier, passer sur un worktree. L'analyse d'usage révèle aussi une gêne quand l'interface change toute seule (« pk il s'est ouvert tout seul ? »).

## Décision

- **Un seul registre de commandes.** Chaque action de l'UI est une commande nommée dont les paramètres sont validés (zod), par exemple `worktree.switch`, `panel.open`, `file.show`.
  - L'humain y accède par une palette (Cmd+K) et par des raccourcis.
  - L'agent y accède par des outils exposés par le cœur (MCP).
  - Ce que l'humain peut faire, l'agent peut le faire, sans code dupliqué.
- **Priorité des commandes** :
  1. passer sur un worktree ou un agent ;
  2. ouvrir la file « À toi » ;
  3. afficher l'état d'un agent ;
  4. ouvrir l'app d'un worktree pour la recette ;
  5. afficher un fichier ou un doc ;
  6. ouvrir la PR ou la CI ;
  7. afficher le diff.
- **Garde-fou** : l'agent ne modifie l'interface **que sur demande explicite**. Sans demande, il propose l'action (par exemple un lien « Voir le worktree 132 ») et ne vole pas le focus.
- **Voix** : aucune reconnaissance vocale maison. Un champ de conversation est accessible partout via un raccourci global, et la dictée système ou Wispr Flow y écrit.

## Conséquences

- (+) La palette, les raccourcis et le pilotage par l'agent reposent sur la même mécanique.
- (+) Le registre et la palette sont livrés dès le squelette d'E0 : ils coûtent peu à poser tôt et beaucoup à ajouter plus tard. Le pilotage de l'UI par l'agent dépend d'un agent conversationnel (Q-009).
- (−) Toute nouvelle fonction de l'UI doit passer par une commande. C'est une discipline à tenir.
