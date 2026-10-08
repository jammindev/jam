# ADR 0011 : pratiques et métriques DORA

- **Statut** : proposée
- **Date** : 2026-10-08
- **Tranche** : RET-002, RET-006

## Contexte

Le mainteneur veut appliquer la méthode DORA ([RET-002](../specs/RETOURS.md)). DORA est un programme de recherche sur la performance de livraison logicielle ([dora.dev](https://dora.dev)). Deux apports sont utiles ici.

**Les métriques de livraison.** Depuis le rapport 2024, DORA en retient cinq, réparties en deux groupes ([dora.dev/guides/dora-metrics](https://dora.dev/guides/dora-metrics/)) :

| Groupe | Métrique | Définition DORA |
|---|---|---|
| Débit | Délai de changement (*change lead time*) | Temps entre le commit d'un changement et son déploiement en production. |
| Débit | Fréquence de déploiement (*deployment frequency*) | Nombre de déploiements sur une période, ou temps entre deux déploiements. |
| Débit | Temps de rétablissement (*failed deployment recovery time*) | Temps pour se remettre d'un déploiement en échec qui exige une intervention immédiate. Remplace depuis 2023 le MTTR (temps moyen de rétablissement), qui comptait aussi les pannes sans lien avec un changement. |
| Instabilité | Taux d'échec des changements (*change fail rate*) | Part des déploiements qui exigent une intervention immédiate. |
| Instabilité | Taux de reprise (*deployment rework rate*) | Part des déploiements non planifiés, faits en réponse à un incident en production. Ajouté en 2024. |

**Le modèle de capacités pour le développement assisté par IA** (rapport 2025, *State of AI-assisted Software Development*). Constat central : l'IA est un **amplificateur** des forces et des faiblesses existantes. Sept capacités en démultiplient le bénéfice : une position claire et communiquée sur l'IA, des données saines, des données internes accessibles à l'IA, une gestion de version rigoureuse, le travail en petits lots, l'attention portée à l'utilisateur, des plateformes internes de qualité.

jam est un pipeline de livraison : il voit passer chaque tâche, chaque étape et chaque merge. C'est l'endroit naturel pour mesurer. Le risque inverse est de construire des tableaux de bord avant d'avoir un pipeline qui tourne.

## Décision

### 1. Les pratiques DORA sont des principes de jam, dès maintenant

| Capacité DORA | Ce qu'elle donne chez jam |
|---|---|
| Petits lots | Une tâche = une issue petite, mergée en quelques jours. Une issue trop grosse est redécoupée au cadrage. |
| Gestion de version rigoureuse | Branches courtes vers `main`, une par worktree. Rien de ce qui compte ne vit hors de git ou de l'état du cœur, sauf, provisoirement, l'outillage du poste du mainteneur (ADR 0012). |
| Position claire sur l'IA | Déjà posée : le code est écrit par des agents ([ADR 0003](0003-code-ecrit-par-agents.md)), avec des permissions par rôle ([ADR 0009](0009-permissions-par-role.md)). |
| Données internes accessibles à l'IA | Specs, ADR et glossaire forment le contexte de travail des agents. Ils sont tenus à jour (RET-003). |
| Données saines | Une seule source par fait : l'état du cœur ([ADR 0010](0010-persistance-sqlite.md)) et l'historique GitHub. |
| Attention à l'utilisateur | Le mainteneur est le premier utilisateur. La recette valide le comportement, pas seulement les tests. |
| Plateforme interne de qualité | jam lui-même. |

Les boucles d'implémentation et de CI n'ont pour critère que des vérifications automatiques (tests, CI). La boucle de relecture, déjà présente dans l'ADR 0008, a pour critère le verdict des relecteurs, et pour bornes les garde-fous (NFR-010, RET-006). Cela précise la règle des critères objectifs de l'ADR 0008, qui reste vraie pour les boucles de code. À l'acceptation de cette ADR, le statut de l'ADR 0008 mentionne cette précision (critère de la boucle de relecture).

### 2. Les métriques DORA sont calculées par repo

**Livrer** dépend du repo :
- par défaut, **livrer = merger dans `main`** (cas de jam) ;
- pour un repo dont `main` est déployé (cas de `house`), **livrer = déployer** : c'est une exécution réussie du workflow de déploiement désigné dans la configuration du repo.

**Incident** : défaut constaté après une livraison et qui exige une correction immédiate (CI rouge sur `main`, régression, déploiement en échec). On le signale par une issue étiquetée `incident`, qui désigne la PR fautive. Pour un repo déployé, le passage de la PR au déploiement fautif sera fixé au cadrage du S4 (Q-035).

| Métrique | Définition adaptée |
|---|---|
| Délai de changement | Du premier commit de la branche à la livraison. |
| Fréquence de livraison | Nombre de livraisons par semaine. |
| Temps de rétablissement | De la livraison fautive à la livraison de son correctif. |
| Taux d'échec des changements | Part des livraisons désignées par une issue `incident`. |
| Taux de reprise | Part des livraisons qui ferment une issue `incident`. |

Dans le pipeline, les rôles ne committent pas : le premier commit arrive après le feu vert 2. Le délai de changement ne couvre donc que la PR, la CI, le feu vert 3 et le déploiement. C'est conforme à DORA, mais cela ne dit rien du temps passé en amont. D'où la durée de tâche ci-dessous.

### 3. Indicateurs propres aux agents

En complément, par tâche, à partir de l'état que le cœur tient déjà (FR-027) :
- **itérations** d'implémentation (garde-fou : 8) ;
- **tours de relecture**, jusqu'à `RELECTURE : OK` ([RET-006](../specs/RETOURS.md)) ;
- **coût** cumulé des étapes ;
- **durée de tâche**, de la création du worktree au merge, dont le temps d'attente des feux verts.

### 4. Données et affichage

- Aucune saisie manuelle : tout vient des événements horodatés du pipeline et de GitHub (PR, merges, labels, exécutions de workflow).
- Un écran minimal au S4 : par repo, les cinq métriques et les indicateurs agents sur les quatre dernières semaines. Des valeurs, sans graphique ni comparaison avec les niveaux de référence de DORA.
- Les métriques servent à ajuster la méthode (taille des issues, garde-fous, profils de rôle). **Elles ne deviennent jamais des objectifs chiffrés** : une mesure qui devient un objectif cesse d'être une bonne mesure.

### 5. jam se mesure lui-même

jam est un repo comme les autres : ses métriques DORA se calculent depuis l'historique GitHub, y compris pour la période où le pipeline est déroulé à la main dans Orca. Les indicateurs agents de cette période sont perdus (pas d'état persistant) et on l'accepte.

## Conséquences

- (+) La méthode a un retour chiffré : on voit si une modification du pipeline accélère ou fragilise la livraison.
- (+) Peu de coût : le cœur persiste déjà les étapes, et GitHub fournit le reste.
- (+) Le principe des petits lots donne un critère concret au cadrage.
- (−) Sur un projet solo, les volumes sont faibles et les chiffres bruités. On lit des tendances, pas des valeurs isolées.
- (−) Le taux d'échec et le taux de reprise dépendent d'un étiquetage `incident` discipliné.
- (−) Une configuration de plus par repo : le workflow de déploiement, quand il existe.
