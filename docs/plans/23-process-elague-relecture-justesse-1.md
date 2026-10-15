# Relecture #23 — axe justesse, tour 1

Périmètre : tout le travail non commité de la branche (`git status`, `git diff`, fichiers non suivis), lu contre le plan validé `docs/plans/23-process-elague.md`.

Tests : `python3 -m unittest` → **172 tests, OK** (66 s).

Vérifié sans constat :
- **Refonte de `hooks/guard_outbound.py`** : `maintainer_words(event)` reprend le corps de la boucle à l'identique (`continue` devient `return None`, les deux `return` restent). `hooks/test_guard_outbound.py` n'est pas modifié et passe. Comportement inchangé.
- **Hook de reprise** : la fiche est cherchée à la racine du repo, et un dossier `docs/methode.md` ne compte pas. Les chemins viennent de `PLUGIN_ROOT`, déduit du fichier du hook, jamais du worktree. Le cas d'un repo qui a son propre `process/` et `docs/process/` est couvert, de même que l'absence de fiche. Le refus de `guard_coordinator.py` renvoie au process du plugin, et son test calcule le chemin de la même façon.
- **`hooks/test_plugin.py`** : le plafond de 4904 mots est compté avec `split()`, aucune espace insécable dans `process/` ni `roles/`. Le test « aucun fichier hors du compte » et les interdits `pnpm`, `/Users/`, `/home/` sont en place.
- **Repo public** : aucun chemin du poste, nom d'hôte ou nom d'un autre projet dans `process/`, `roles/`, `hooks/`, `scripts/`, `docs/methode.md`, l'ADR 0018 et la fiche concept. Les `/Users/testhome` et `/Users/x` des tests sont inventés. Les mentions « Ben » de `OPEN-QUESTIONS.md` et `GLOSSARY.md` existaient avant la tâche : c'est à l'axe conformité d'en juger.

## Bloquant

### B1. Un « ok » relayé efface le feu vert du mainteneur dans la session du coordinateur
- **Fichier** : `scripts/maintainer_time.py:174-176` et `:185`.
- **Constat** : les textes relayés (`relays`) sont relevés dans **toutes** les sessions retenues, dont celle du coordinateur. Ensuite, le filtre `words.strip() in relays` s'applique aussi aux messages de la session du coordinateur. Or le process demande de relayer un feu vert plan ou recette par un simple « ok » (`process/README.md:71`, `roles/coordinateur.md:21`).
- **Scénario d'échec** : le mainteneur tape « ok » dans la session du coordinateur, qui envoie `orca terminal send --terminal … --text "ok" --enter` à l'orchestrateur. Le « ok » du mainteneur, côté coordinateur, est écarté comme « relais », et sa copie, côté tâche, aussi. Le feu vert n'est compté nulle part, et il en va de même pour tout autre message identique à un texte relayé. Cela touche le message le plus fréquent du mainteneur, dans la forme de relais que recommande le process. La mesure sous-estime donc systématiquement, et la recette sur #22 (même nombre de moments à ±1 près) peut échouer pour cette raison seule. Le test `test_relayed_text_left_out` emploie deux textes différents (« ok pour le plan de #23 » et « 23-tache : feu vert plan, « ok » »), si bien qu'il ne voit pas le cas.
- **Correction attendue** : n'écarter un relais que dans les sessions du worktree de la tâche, là où il arrive (`elif in_task and words.strip() in relays`). Ajouter un test où le message du mainteneur au coordinateur est identique au texte relayé : il doit être retenu une fois, et sa copie côté tâche écartée.

## À corriger

### C1. Un relais qui contient une apostrophe n'est pas reconnu
- **Fichier** : `scripts/maintainer_time.py:118`, `:120` et `:185`.
- **Constat** : la comparaison est une égalité stricte entre le `--text` de la commande et le message reçu. Or la garde de sortie note qu'un relais envoyé par `orca terminal send` perd son apostrophe (« ce n est pas », `hooks/guard_outbound.py:119-121`).
- **Scénario d'échec** : le coordinateur relaie `--text "feu vert recette : c'est bon"`, et la session de l'orchestrateur reçoit « feu vert recette : c est bon ». Le relais n'est pas reconnu et compte comme un message du mainteneur : un moment fictif de 3 min, ou un moment réel allongé.
- **Correction attendue** : normaliser les deux côtés avant de comparer (retirer `'` et `’`, réduire les espaces) ; ajouter un test avec une apostrophe perdue à l'arrivée.

### C2. Un agent bloqué réveille une seconde fois comme « carte inactive », ce qui pousse le coordinateur à relancer un orchestrateur qui attend seulement une autorisation
- **Fichiers** : `scripts/watch_cards.py:141-151` et `:183-186` ; `roles/coordinateur.md:19` ; le diagramme de `docs/concepts/veille-et-mesure.md:16-27`, qui ne montre pas ce passage.
- **Constat** : un agent `waiting` n'est pas « au travail ». L'âge de la carte part donc de son `stateStartedAt`, c'est-à-dire du début de l'attente.
- **Scénario d'échec** : à T, l'orchestrateur tombe sur une invite d'autorisation. La veille réveille (« agent en attente d'une autorisation »), le coordinateur prévient le mainteneur et relance la veille ; l'agent bloqué compte alors comme déjà vu. À T + 10 min, si le mainteneur n'a pas encore répondu, la veille réveille de nouveau, cette fois « aucun agent au travail depuis 10 min ». La règle du coordinateur pour une carte inactive est de **relancer l'orchestrateur de tâche** ou de passer la carte en `⛔`. Il lance alors un second orchestrateur dans un worktree où le premier attend juste une réponse, ou bloque une tâche saine.
- **Correction attendue** : garder ce second réveil, utile en filet de sécurité (voir S1), mais le nommer juste. Quand une carte inactive a un agent `waiting`, la raison doit être « agent en attente d'une autorisation depuis N min », et le coordinateur doit appliquer la règle « agent bloqué » (prévenir le mainteneur), pas celle de la carte inactive. Ajouter un test : un seul agent `waiting`, lancement avant N, réveil après N avec cette raison. Mettre à jour le diagramme de la fiche concept.

### C3. `test_wakes_on_idle_card` peut tourner jusqu'au délai de 30 s sur un runner CI lent
- **Fichier** : `scripts/test_watch_cards.py:177-184`.
- **Constat** : l'agent est daté par `now_ms()` au moment où le test construit la réponse, et le seuil vaut 0,6 s. La première lecture n'a lieu qu'après le démarrage de deux interpréteurs Python : `watch_cards.py`, puis le faux `orca`.
- **Scénario d'échec** : sur un runner chargé, cette première lecture arrive plus de 0,6 s après `now_ms()`. La carte est alors « déjà au-delà de N au lancement » et ne réveille jamais. Le script boucle jusqu'au `timeout=30` de `subprocess.run`, et le test finit en erreur `TimeoutExpired`. Les autres tests de veille datent la carte par l'horloge du script, ou s'éloignent nettement du seuil : ils ne sont pas exposés.
- **Correction attendue** : laisser une marge au démarrage. Par exemple, dater l'agent dans le futur (`started=now_ms(minutes_ago=-0.05)`, 3 s), ce qui donne un âge négatif au lancement et un franchissement de 0,6 s plus tard. Ou bien prendre `--idle-minutes 0.05` (3 s), avec un commentaire qui explique la marge.

### C4. La mesure charge en mémoire tous les transcripts du poste
- **Fichier** : `scripts/maintainer_time.py:71-87`, appelé en `:240`.
- **Constat** : `read_sessions` lit chaque `*.jsonl` de `~/.claude/projects` et garde **tous** les évènements de toutes les sessions en mémoire. Le filtre sur le `cwd` ne vient qu'après, dans `measure`. Le dossier couvre tous les projets du poste, et la garde de sortie rappelle qu'une session atteint des dizaines de Mo (`hooks/guard_outbound.py:165`).
- **Scénario d'échec** : avec quelques Go de transcripts, le script garde l'équivalent de plusieurs fois cette taille en objets Python. Il devient très lent, ou il est tué faute de mémoire, au moment où l'orchestrateur prépare le corps de la PR.
- **Correction attendue** : filtrer fichier par fichier. On lit les lignes jusqu'au premier `cwd`, et on abandonne le fichier s'il n'est ni le worktree principal ni celui de la tâche. On ne garde ensuite que les évènements des fichiers retenus. Un test peut vérifier qu'une session d'un autre `cwd` n'est pas lue au-delà de son premier évènement, ou plus simplement que le résultat ne change pas.

### C5. Un chemin relatif ou mal tapé donne « 0 min » sans erreur
- **Fichier** : `scripts/maintainer_time.py:240-241` ; le cas inverse est traité en `:236-238`.
- **Constat** : `--main` et `--worktree` ne passent que par `os.path.normpath`. Un chemin relatif ne correspond donc jamais au `cwd` absolu des transcripts. Le script refuse un dossier de transcripts introuvable, parce que « 0 min » serait une fausse mesure (commentaire du test `test_missing_folder_is_an_error`), mais il accepte en silence un worktree qui ne désigne aucune session.
- **Scénario d'échec** : lancé depuis le worktree de la tâche avec `--worktree .`, ou avec une faute de frappe dans le chemin, le script répond « 0 min en 0 moment(s) » et sort avec le code 0. Le corps de la PR porte alors une fausse mesure.
- **Correction attendue** : `os.path.abspath` sur les deux chemins. Ajouter au rapport une ligne de comptage, du type « N session(s) lue(s) : x du coordinateur, y de la tâche », pour qu'un zéro se voie. Ajouter un test avec un chemin relatif.

## Suggestions

- **S1.** `scripts/watch_cards.py:178-186` : avec la chaîne de `elif`, une carte ne donne qu'une raison par lecture. Si un segment `✓` arrive dans la même lecture qu'un nouvel agent bloqué, seul le `✓` est signalé. Après la relance, l'agent bloqué compte comme déjà vu, et il ne revient qu'à travers le réveil d'inactivité, N minutes plus tard (d'où l'intérêt de garder ce réveil, voir C2). Mieux vaudrait cumuler les raisons de la carte dans le message.
- **S2.** `scripts/test_watch_cards.py` : trois cas limites ne sont pas couverts.
  - Le choix du **plus récent** `stateStartedAt` entre plusieurs agents : un `min` à la place de `max` passerait tous les tests.
  - Une nouvelle inactivité après une reprise du travail, qui ouvre un nouvel épisode.
  - Une carte qui quitte `▶` puis y revient avec un agent toujours bloqué, ce que promet le commentaire « a later ▶ starts afresh », ligne 169.
- **S3.** `scripts/test_watch_cards.py:222-237` : sur un runner lent, si la première lecture vient après le seuil, un `at_work` cassé ne ferait pas réveiller la carte, et le test passerait sans rien prouver. Dater les agents comme proposé en C3 règle aussi ce cas.
- **S4.** `hooks/test_plugin.py:115` : `os.listdir` compte aussi les fichiers cachés. Un `.DS_Store` créé par le Finder dans `process/` ou `roles/` fait échouer le test sur le poste du mainteneur. Il suffit d'ignorer les noms qui commencent par `.`.
- **S5.** `scripts/maintainer_time.py:227-229` : deux précisions d'usage.
  - Une date `--since` ou `--until` sans fuseau est lue en UTC. Le recetteur qui tape une heure locale se décale de 1 h ou 2 h : le dire dans l'aide.
  - Un `--issue "#23"` ne trouve jamais rien : retirer un `#` en tête.
- **S6.** `scripts/maintainer_time.py:85-86` : une session reprise (`--continue`, prévu pour le coordinateur) peut recopier des évènements. Ignorer les doublons sur le champ `uuid` éviterait de gonfler le nombre de messages retenus. Le temps, lui, ne change pas.
- **S7.** `scripts/watch_cards.py:220-223` : `--idle-minutes nan` est accepté (`nan <= 0` est faux) et désactive en silence le réveil d'inactivité. Il faudrait exiger un nombre fini.

RELECTURE : CORRECTIONS (6)
