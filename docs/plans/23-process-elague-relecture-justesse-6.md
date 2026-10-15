# Relecture #23 — axe justesse, tour 6

Périmètre : tout le travail non commité de la branche (`git status`, `git diff`, fichiers non suivis), centré sur `scripts/watch_cards.py`, `scripts/maintainer_time.py`, `hooks/session_start_recap.py`, `hooks/guard_outbound.py`, `hooks/guard_coordinator.py`, `hooks/test_plugin.py` et leurs tests.

Tests : `python3 -m unittest` → **185 tests, OK** (72,6 s).

## Vérifié, sans constat

- **Refonte de la garde de sortie** : `maintainer_words(event)` (`hooks/guard_outbound.py:195-254`) reprend ligne à ligne le corps de l'ancienne boucle ; chaque `continue` devient `return None`, et `last_user_message` (l. 181-192) garde le même parcours à rebours. `hooks/test_guard_outbound.py` n'est pas modifié et passe. Aucun changement de comportement.
- **Hook de reprise** : la ligne « Méthode » ne sort que si `docs/methode.md` est un fichier à la racine du repo (`os.path.isfile`, l. 172), avec des chemins tirés de `PLUGIN_ROOT`, déduit du fichier du hook. Les tests couvrent un sous-dossier, un repo sans fiche mais avec ses propres `process/` et `docs/process/`, et une fiche qui est un dossier. Le message de refus de `guard_coordinator.py` vise le process du plugin, et son test le vérifie.
- **Veille** : les réveils sur agent bloqué (par `state` ou `mainAgent.state`), un par `paneKey` entrant ; la baseline au lancement ; le réveil d'inactivité au franchissement de N, ou à la première lecture inactive déjà au-delà ; le repli sur l'horloge du script pour une date illisible (chaîne ISO, booléen, absente) ; les cartes exclues (`main`, `completed`, `⏸`, `⛔`, sans segment d'état) ; la raison de l'agent gardée quand le commentaire change à la même lecture ; `--idle-minutes` ≤ 0 ou non numérique refusé. Chaque cas a son test, et un test qui régresse échoue sur `TimeoutExpired` (30 s), sans bloquer la suite.
- **Sensibilité au temps** : les tests à seuil court (0,01 min) se datent sur l'horloge du script, donc indépendamment du démarrage des interpréteurs. Les deux tests datés (`test_wakes_on_idle_card`, `test_agent_still_blocked_after_threshold_is_named_so`) laissent 3 s entre `now_ms()` et la première lecture, ce qui suffit largement sur `ubuntu-latest`. Les tests du type « ne réveille pas » (`sleep` de 1 s pour un seuil de 0,6 s) ne peuvent pas échouer à tort sur un runner lent : la lenteur ne fait qu'allonger l'écart.
- **Mesure** : moments (strictement moins de 10 min, l'écart de 10 min exactes testé) et marge de 3 min ; messages injectés écartés ; sidechain ; brief en tête de chaque session de la tâche ; relais pris une seule fois, à l'apostrophe près, et non appliqués côté coordinateur ; rattachement par le message ou par tout le dernier tour, un tour s'ouvrant aussi sur une notification ; fenêtre en heure locale sans décalage ; dossier pris dans l'argument, puis `CLAUDE_CONFIG_DIR`, puis le dossier personnel ; dossier absent → code 2 ; chemin relatif rendu absolu. Le mot témoin est vérifié absent de stdout et de stderr dans chaque cas.
- **`hooks/test_plugin.py`** : plafond de 4904 mots compté comme `wc -w`, liste fermée des pages (un nouveau `.md` fait échouer le test), interdits `pnpm`, `/Users/`, `/home/`, et fichiers parasites (`.DS_Store`, `~`) ignorés.
- **Repo public** : les chemins `/Users/...` présents dans les tests sont synthétiques (`testhome`, `x`) et préexistants. Aucun nom de personne, d'hôte ni d'autre projet dans les fichiers relus.

## Bloquant

Aucun.

## À corriger

Aucun.

## Suggestions

1. **`scripts/watch_cards.py:147-157` et `188-199` — retour en `▶` avec un agent périmé.** Une carte qui repasse de `⏸` à `▶` après le lancement est lue avec `previous_age = None` : si son seul agent est une session `done` depuis longtemps, restée ouverte (au niveau *léger*, la session de recette du mainteneur, par exemple), et que la lecture tombe avant que le nouveau rôle apparaisse, la veille réveille aussitôt, avec « aucun agent au travail depuis 10 min », pour une carte en `▶` depuis quelques secondes. L'impact est faible : un réveil de trop, que le coordinateur, qui vient de lancer le rôle, reconnaît. **Correction possible** : pour une carte qui entre en `▶` après le lancement, prendre comme référence le plus tardif entre le dernier `stateStartedAt` et l'heure de cette lecture. Le test serait : `⏸` avec un agent `done` daté de 20 min, puis `▶` avec le même agent, sans réveil à cette lecture. Le cas « le dernier agent au travail part » (`test_wakes_on_card_idle_beyond_threshold_once_its_last_worker_leaves`) n'est pas concerné : la carte y était déjà `▶`.
2. **`scripts/watch_cards.py:239-242` — `nan` et `inf` acceptés.** `--idle-minutes nan` passe le contrôle `<= 0`, et toute comparaison avec `nan` étant fausse, le réveil d'inactivité est désactivé sans message ; `inf` aussi. `--interval nan` ou `inf` finit en trace Python (`time.sleep`). **Correction** : refuser les valeurs non finies (`math.isfinite`), et ajouter `"nan"` aux valeurs de `test_idle_minutes_must_be_positive`.
3. **`scripts/maintainer_time.py:97-126` — aucun dédoublonnage des évènements.** Si une session reprise (`--continue`, `--resume`) recopie l'historique dans un nouveau fichier, ses messages comptent deux fois : le compte de messages double, et la copie d'un brief, en deuxième position après son original de même horodatage, compte comme un message du mainteneur (3 min si elle est isolée). Je n'ai pas vérifié le format réel des reprises : à contrôler au recoupement sur #22. **Correction si c'est confirmé** : écarter un évènement dont l'`uuid` a déjà été lu.
4. **`scripts/maintainer_time.py:275-277` — `--issue "#23"`.** L'aide dit « sans # », mais la valeur n'est pas contrôlée : `#23` donne le motif `##23\b`, qui ne trouve rien. Les messages du coordinateur qui ne nomment que `#23` passent alors « hors tâche » sans avertissement, et le chiffre sort trop bas. **Correction** : `issue.lstrip("#")`, ou refuser une valeur non numérique par `parser.error`.
5. **`scripts/test_maintainer_time.py` — branches sans test** : la forme `--text=…` (`maintainer_time.py:171-172`), l'ouverture de tour par « SYSTEM NOTIFICATION » (l. 219), une commande que `shlex` ne sait pas découper (l. 161-164), et un lancement sans `--issue` (rattachement par le seul nom du worktree). Un cas chacun, ou au moins la forme `--text=`.
6. **`scripts/maintainer_time.py:160` et `201-202` — transcript malformé.** Un bloc `tool_use` dont `input` n'est pas un objet, ou un bloc `text` dont `text` n'est pas une chaîne, lève `AttributeError` ou `TypeError` et sort en trace Python au lieu d'être ignoré, comme le sont les lignes illisibles. **Correction** : tester `isinstance(..., dict)` et `isinstance(..., str)`.
7. **`hooks/test_plugin.py:46-50` — `method_pages` ne descend pas dans les sous-dossiers.** Une page `roles/archives/x.md` échapperait au plafond comme au contrôle de généricité. **Correction** : parcourir l'arborescence avec `os.walk`.

RELECTURE : OK
