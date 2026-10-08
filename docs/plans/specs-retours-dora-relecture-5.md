# Relecture — cadrage `specs-retours-dora`, tour 5

> Relecteur seul (docs), contexte neuf. Objet : `git diff main` (un commit local), hors fichiers de relecture des tours précédents, non lus.
> Décisions du mainteneur prises comme acquises : pas d'échéance sur les milestones ; RET-007 validé (instances Claude neuves, diversité de modèles en E2) ; les trois compléments DORA validés. Faits pris comme vérifiés : S1 mergé (PR #5), issue #1 fermée, hook de démarrage et garde du coordinateur installés hors repo, garde active seulement avec `JAM_ROLE=coordinateur`.

## Ce qui a été vérifié

- **Cohérence entre fichiers** : numéros FR (FR-036, FR-037, FR-038 nouveaux, aucun doublon), ADR (0011 et 0012 « proposées », listées dans `decisions/README.md`), Q-022 à Q-033 (suite continue, chaque renvoi pointe vers la bonne question), glossaire, roadmap (S2 à S4 alignés sur les descriptions de milestones du brouillon), process, profils de rôles, ADR 0011 et 0012. Les définitions DORA de l'ADR 0011 (cinq métriques, groupes débit / instabilité, sept capacités du rapport 2025) sont exactes.
- **Fidélité aux retours** : RET-001 à RET-007 sont tous traduits. Les ajouts hors retours (hook RTK, durcissement des profils, Q-022 à Q-025, Q-033) sont signalés comme frictions du coordinateur, pas comme retours du mainteneur.
- **Repo public** : aucun secret, aucune adresse, aucun chemin propre à une machine dans le diff. « Ben » (glossaire) existait déjà sur `main`. `~/.claude` (Q-024) est un chemin générique.
- **Permissions** : aucun profil n'ouvre commit, push ou `gh` en écriture. Variante du relecteur : `gh api repos/jammindev/jam/milestones` est une règle exacte, sans joker, et ne couvre donc pas `-X POST`. `gh issue view` et `gh issue list` sont en lecture. Le rédacteur n'a pas de shell. L'implémenteur est en `dontAsk` avec une liste blanche ; les voies `node`, `npx`, `pnpm` et le script de test sont déjà reconnues comme ouvertes (process, Q-025, R-03).
- **Brouillon d'issues** : chaque issue S2 tient en un petit lot et a un critère de fin vérifiable. Ensemble, elles couvrent le critère du milestone S2 (voir une réserve en suggestion). Le sort de #1 à #4 est cohérent avec la roadmap. `docs/plans/E0-S1-squelette.md` existe bien.

## Bloquant

Aucun.

## À corriger

### 1. RET-006 dit que l'ADR 0008 n'est pas modifiée, l'ADR 0011 dit que son statut le sera

- **Fichiers** : `docs/specs/RETOURS.md:68` contre `docs/decisions/0011-pratiques-et-metriques-dora.md:39`.
- **Constat** : RET-006 affirme : « L'ADR 0008 n'est pas modifiée ». L'ADR 0011 §1 prévoit au contraire qu'« à l'acceptation de cette ADR, le statut de l'ADR 0008 mentionne cette précision ». L'ADR 0011 a raison sur le fond : la décision de l'ADR 0008 (« boucles automatiques uniquement sur des critères objectifs : tests verts, CI verte ») ne couvre pas une boucle qui s'arrête sur le verdict des relecteurs. Il faut donc une précision tracée, ce que fait l'ADR 0011. Mais au feu vert, le rédacteur trouvera deux consignes contraires sur l'ADR 0008.
- **Correction attendue** : dans RET-006, remplacer la phrase par, par exemple : « La décision de l'ADR 0008 est conservée. L'ADR 0011 (§1) précise que sa règle des critères objectifs vaut pour les boucles de code, et la boucle de relecture s'arrête sur le verdict des relecteurs. À l'acceptation de l'ADR 0011, le statut de l'ADR 0008 mentionnera cette précision. » La phrase de RET-007 (ligne 81) peut rester : elle porte sur le nombre de relecteurs, que l'ADR 0011 ne touche pas.

### 2. Le workflow de déploiement est en priorité M (FR-028) alors qu'il ne sert qu'aux métriques, en priorité S (FR-037), et aucun jalon ne le porte

- **Fichiers** : `docs/specs/01-REQUIREMENTS.md:21` (FR-028), `:47` (FR-037) ; `docs/specs/04-ROADMAP.md:46` (S4).
- **Constat** : FR-028 (M, E0) ajoute à la configuration minimale d'un repo « si le repo est déployé, le workflow de déploiement (ADR 0011) ». Ce réglage ne sert qu'au calcul de la livraison pour les métriques. Or FR-037 est en S et constitue la première coupe d'E0. Si l'écran est coupé, FR-028 reste un Must pour une donnée inutile en E0. Et cette donnée n'a pas besoin d'être enregistrée tôt : les exécutions de workflow restent dans l'historique GitHub, à la différence des horodatages de FR-036. Enfin, aucun jalon ne cite ce réglage : le S1 a livré la configuration (tests, recette), et le S4 ne mentionne pas le workflow de déploiement. Pourtant, le critère de fin du S4 en dépend pour `house` (livraison = déploiement).
- **Correction attendue** : retirer la clause de FR-028 et la porter dans FR-037 (S, S4), par exemple : « … ou déploiement si le repo désigne un workflow de déploiement, réglage ajouté à la configuration du repo. » Ajouter « désignation du workflow de déploiement par repo (FR-037) » au périmètre du S4 dans `04-ROADMAP.md:46` et dans la description du milestone E0-S4 (`docs/plans/specs-retours-dora-issues.md:24`). Les cinq métriques de `house` ne peuvent pas s'afficher sans ce réglage.

## Suggestions

1. **`docs/process/README.md:28` et `docs/process/roles/redacteur.md:15`** : au feu vert de cadrage, le rédacteur passe les ADR de « proposée » à « acceptée ». Ajouter qu'il reporte aussi les mentions prévues dans les statuts des ADR qu'elles complètent : l'ADR 0008 pour l'ADR 0011 (ligne 39), l'ADR 0009 pour l'ADR 0012 (ligne 31). Sinon, cette étape repose sur la seule lecture des ADR.
2. **`docs/specs/01-REQUIREMENTS.md:90` (NFR-010)** : ajouter « ADR 0011 » dans la colonne Source, puisque c'est elle qui tranche le critère de la boucle de relecture.
3. **`docs/process/README.md:121`** : le durcissement est attribué à « Q-022 à Q-024 », mais seules les formes `rtk` relèvent d'une de ces questions (Q-022). `Edit(.claude/**)` est justifié à la ligne 120, et `git -C` n'a de trace nulle part (Q-024 parle de `~/.claude`, pas du `.claude/` du projet). Écrire plutôt : « formes `rtk` (Q-022) ; `Edit(.claude/**)` et `git -C`, ajoutés par précaution par le coordinateur », ou ouvrir une Q pour ces deux règles.
4. **`docs/process/roles/planificateur.md:3`** : « une tâche (issue ou jalon) » est un reste de l'ancien process, où une tâche pouvait être un jalon. Écrire « une tâche (issue) », comme le process (ligne 62).
5. **`docs/plans/specs-retours-dora-issues.md:15`** : le titre du S4 change (« …, métriques »), contrairement à ceux de S1 à S3 marqués « (inchangé) ». Écrire « (renommé, ancien titre : `…`) » pour que le coordinateur sache qu'il doit le modifier au moment de publier.
6. **`docs/plans/specs-retours-dora-issues.md:31`** : « #a à #f » est un emplacement réservé. Préciser « (numéros réels des issues S2-a à S2-f, à substituer à la publication) ».
7. **`docs/plans/specs-retours-dora-issues.md:133-135` (S2-f)** : le critère du milestone S2 dit « le planificateur est lancé avec son profil de permissions ». S2-d le vérifie par un test unitaire seulement, et le critère de bout en bout de S2-f ne le mentionne pas. Ajouter à S2-f : « le planificateur est lancé avec la ligne de commande construite depuis son profil (S2-d), visible dans l'état de l'étape ».
8. **`docs/process/README.md:66` et `docs/process/roles/coordinateur.md:8`** : la tournure « hors du repo, installé, » se lit mal. Écrire « Un hook personnel du poste, installé hors du repo, donne… » et « …: un hook personnel du poste du mainteneur, installé hors du repo ».
9. **`docs/specs/RETOURS.md:24`** : « proposés à la rédaction » est ambigu (proposés par qui, à qui ?). Écrire « transmis au rédacteur ».

RELECTURE : CORRECTIONS (2)
