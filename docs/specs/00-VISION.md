# 00 — Vision

> Statut : réécrite le 2026-10-11 pour le kit (RET-014, RET-016, [ADR 0016](../decisions/0016-kit-de-methode.md)). De sa création au 2026-10-11, jam visait une app Electron, un cockpit qui déroule le pipeline en code ; la vision de l'app se lit au tag `app-electron`.

## Pitch

jam est le **kit d'une méthode de *loop engineering***. Pour chaque issue, des rôles d'agents travaillent dans un worktree dédié (plan, TDD, relecture, recette) jusqu'au merge ; le mainteneur n'intervient que pour les feux verts. Le régime dépend du risque du projet : léger par défaut, complet pour un projet en production qui touche à l'argent ou à des données de personnes. La méthode tourne dans Orca, avec Claude Code.

Le kit est un **plugin Claude Code**, minimal, installé une fois sur le poste de travail : le process, les profils de rôle, les hooks qui tiennent les garde-fous et deux scripts. Chaque projet n'a qu'une fiche, `docs/methode.md`. Le `README.md` de jam est la page publique de la méthode.

## Pourquoi

- **La méthode marche déjà.** Elle tourne sur trois projets du mainteneur, dans Orca, sans app. Construire un outil dédié prendrait un temps qu'il n'a pas.
- **Elle vit mal.** Chaque projet la recopie et la transpose, ses garde-fous en code vivent hors de tout dépôt et ont divergé d'un poste à l'autre, et le process s'est alourdi. Un kit versionné et élagué règle cela.

## Pour qui

- **Le mainteneur, d'abord**, pour ses projets, sur son poste de travail.
- **Un projet public** sur GitHub, sans promesse de support. Sa page publique montre, chiffres mesurés à l'appui, comment le mainteneur travaille avec des agents.

## Objectifs

1. **Une seule référence de la méthode**, versionnée, courte, installée une fois.
2. **Des garde-fous en code**, versionnés et testés : ce qu'un hook peut garantir ne dépend pas de l'obéissance d'un agent.
3. **Des projets légers** : une fiche, et rien d'autre.
4. **La méthode sert les livraisons**, pas l'inverse : une fois livré, le kit est gelé.

## Non-objectifs

- (a) Une app, un cockpit, un harness d'agent maison.
- (b) Remplacer Orca ou Claude Code : le kit s'appuie sur eux.
- (c) Multi-utilisateur, support de tiers, marketplace publique de plugins.
- (d) Un autre système que macOS : le poste de travail en est un.
- (e) Pendant le jalon K1 : étendre le kit aux autres projets du mainteneur, skills, modèles, indicateurs calculés.

## Critères de succès

| Horizon | Critère vérifiable |
|---|---|
| Fin du jalon K1 (deux à trois jours de travail) | Le repo ne contient plus le code de l'app. Le plugin s'installe sur le poste depuis le repo ; ses hooks et scripts passent leurs tests en CI. Le process et les profils sont génériques et tiennent sous leur plafond de taille. jam a sa fiche. Le `README.md` est la page publique, avec le temps du mainteneur mesuré sur les deux premières issues du jalon. Le kit est alors gelé. |

## Principes

- **Kit gelé.** Une fois livré, le kit ne change que sur une friction vécue dans un projet. Toute nouvelle règle dit laquelle elle remplace ou retire.
- **Le régime suit le risque.** Un projet passe en léger, sauf s'il est en production et touche à l'argent ou à des données de personnes ; une tâche peut monter d'un niveau, en le motivant.
- **Interrompre le moins possible.** Le mainteneur n'est sollicité que pour une décision. Son attention est la ressource rare.
- **Imposer ce qui peut l'être.** Ce qu'un hook peut garantir (aucune écriture du coordinateur, aucune sortie sans accord) ne repose pas sur un agent.
- **Assez bon.** Une relecture qui ne trouve plus que du cosmétique s'arrête. La justesse prime sur l'exhaustivité.
- **Petits lots** (pratiques DORA, [ADR 0011](../decisions/0011-pratiques-et-metriques-dora.md) §1). Des tâches petites, mergées vite dans `main`, vérifiées par des tests et une CI.
- **Rien d'inventé.** La page publique ne cite que ce qui a été mesuré.

## Contraintes

- Le temps du mainteneur est la contrainte principale.
- Le mainteneur ne code pas ([ADR 0003](../decisions/0003-code-ecrit-par-agents.md)).
- Aucune mention d'auteur IA dans le repo, les commits ou les PR.
- Repo public : rien de propre à un autre projet, à des tiers ni au poste.
