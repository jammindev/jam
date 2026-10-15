# Relecture justesse, tour 7 : issue #23 (K1-2, « Process élagué »)

Relecteur A, axe justesse. Périmètre : tout le travail non commité de la branche (`git status`, `git diff -M`), d'abord les changements depuis le refus de la recette agent : mesure limitée aux sessions du coordinateur, transcript illisible ignoré, friction 18, règle « Messages au mainteneur », retrait de « Le mainteneur valide le chiffre », Q-064.

Tests : `python3 -m unittest` : **182 tests, OK** (71,8 s).

## Vérifié sans constat

- **`hooks/guard_outbound.py`** : l'extraction de `maintainer_words(event)` est ligne à ligne le corps de l'ancienne boucle (`continue` devenu `return None`, `return` des commandes `/` inchangé). Aucun changement de comportement ; les tests existants de la garde passent.
- **Hook de reprise** (`hooks/session_start_recap.py`) : la ligne « Méthode » ne sort que si `docs/methode.md` est un fichier à la racine du repo (un dossier de ce nom ne compte pas, testé), et nomme le process et les profils du plugin qui exécute le hook, jamais les copies `process/` ou `docs/process/` du repo (testé dans les deux sens). Même chose pour le message de refus de `guard_coordinator.py`.
- **`hooks/test_plugin.py`** : le plafond (4904 mots) compte toutes les pages `.md` de `process/` et `roles/`, et un fichier nouveau ne peut pas échapper au compte. Aucune espace insécable dans ces pages : le `split()` de Python et `wc -w` donnent le même compte. Les interdits (`pnpm`, `/Users/`, `/home/`) sont absents.
- **`scripts/watch_cards.py`** : transitions (bloqué, inactif, toujours bloqué), un seul réveil par épisode, cartes exclues (principale, `completed`, `⏸`, `⛔`, sans segment d'état), dates illisibles ramenées à l'horloge du script, `--idle-minutes` ≤ 0 ou non numérique refusé. Chaque fonction exposée a son cas limite. Sensibilité au temps : les tests négatifs (`test_working_agents_keep_the_card_awake`, `test_only_running_task_cards_watched_for_agents`) échouent dans le cas fautif quelle que soit la lenteur du runner ; les deux tests positifs datés gardent 3 s de marge, ce qu'ils écrivent. Sur un runner très lent, l'échec serait un `TimeoutExpired` après 30 s plutôt qu'une assertion, mais il resterait visible.
- **`scripts/maintainer_time.py`** : seules les sessions dont le premier `cwd` est le worktree principal sont lues ; un lien cassé est ignoré sans arrêter la mesure (testé) ; le rapport ne contient aucun contenu de message (témoin `ZORGLUB` vérifié à chaque test) ; les messages injectés sont écartés (`isMeta`, résultat d'outil, notification, `!`, résumé de compaction, sidechain) ; fenêtre en heure locale ; dossier des transcripts depuis `--transcripts`, `CLAUDE_CONFIG_DIR` ou le dossier personnel.
- « Le mainteneur valide le chiffre » n'apparaît plus que dans la note de suivi `docs/plans/23-process-elague-retours.md`, qui cite le retour.
- Repo public : aucun chemin du poste, nom de personne, d'hôte ou d'un autre projet dans les fichiers relus. Les chemins des tests sont fictifs (`/work/projet`, `/Users/testhome`, `/Users/x/...`).

## Bloquant

Aucun.

## À corriger

### 1. Un transcript sans `cwd` est compté comme une session du coordinateur

- **Fichier** : `scripts/maintainer_time.py`, l. 122-138 (`read_transcript`) ; promesse de la docstring, l. 33-35 ; ligne du rapport, l. 248.
- **Constat** : un fichier n'est écarté que si son premier `cwd` diffère du worktree principal. Si aucun évènement du fichier ne porte de `cwd`, `cwd` reste `None` et **tous** ses évènements sont gardés. Le fichier compte alors comme une session du coordinateur (clé `sessionId`, ou le chemin du fichier à défaut). Le cas limite de `session_cwd` (aucun `cwd`) n'est pas testé.
- **Scénario d'échec** : `--main` est mal tapé (`--main /work/projet-typo`), et le dossier des transcripts contient un fichier dont les lignes ne portent pas de `cwd` (par exemple un fichier qui ne contient que des lignes `{"type": "summary", ...}`). Le rapport affiche « 0 min en 0 moment(s), 0 message(s) retenu(s) » puis « 1 session(s) du coordinateur lue(s) ». Le zéro se lit alors comme une mesure (« la session du coordinateur a été lue, et le mainteneur n'a rien fait »), alors que le garde-fou du compte de sessions existe justement pour qu'un mauvais chemin se voie. Si un tel fichier contient un message utilisateur qui nomme `#23`, ce message est en plus compté.
- **Correction attendue** : dans `read_transcript`, rendre `[]` en fin de fichier quand `cwd` est resté `None`, car une session qu'on ne sait pas situer n'est pas celle du coordinateur. Ajouter un test : un fichier sans `cwd` qui nomme `#23` donne `0 session(s) du coordinateur lue(s)` et `0 message(s) retenu(s)`.

### 2. La veille relancée « après chaque réveil » perd un agent bloqué pendant le traitement

- **Fichiers** : `roles/coordinateur.md`, l. 20 (« relancé après chaque réveil ») ; `process/README.md`, l. 79 ; limites : docstring de `scripts/watch_cards.py`, l. 27-28, et `docs/concepts/veille-et-mesure.md`, l. 40.
- **Constat** : au lancement, un agent déjà `waiting` ou une carte déjà inactive au-delà de N compte comme vu, définitivement (aucun fichier d'état). Le profil fait relancer la veille *après* le réveil, sans dire quand. Tout ce qui devient bloqué ou inactif pendant que le coordinateur traite le réveil (relais, vérification de 30 s par `orca terminal read`, réponse au mainteneur) est donc vu au relancement et ne réveille jamais. Contrairement à un changement de commentaire, l'état des agents n'apparaît pas non plus dans la liste imprimée au réveil (`describe`).
- **Scénario d'échec** : à 10:00, la veille se réveille pour la carte A (`⏸ feu vert plan`). Le coordinateur relaie au mainteneur, puis attend 30 s pour vérifier son relais. À 10:00:20, l'orchestrateur de la carte B tombe sur une invite d'autorisation (`waiting`). À 10:01, le coordinateur relance la veille : B compte comme vue. Elle reste `▶` sans réveil, puisque l'agent bloqué n'est pas au travail mais que la lecture de lancement a déjà fixé l'âge. C'est le cas que FR-046 (« la veille se réveille aussi quand un agent attend une autorisation ») et RET-017 doivent couvrir. Même perte pour une carte qui franchit N pendant ce temps.
- **Correction attendue** (rédaction, sans code) : dans `roles/coordinateur.md` et `process/README.md`, écrire « relancée aussitôt, avant de traiter le réveil ». Ajouter aux limites (docstring et « Les pièges » de la fiche concept) qu'un agent bloqué entre la sortie de la veille et son relancement n'est jamais signalé. Autre voie, au choix du planificateur : `describe` ajoute à chaque carte `▶` l'état de ses agents (en attente, inactive depuis X min), pour que le coordinateur le voie à la lecture de la liste.

## Suggestions

1. **`scripts/maintainer_time.py`, l. 116-118** : les évènements ne sont pas dédoublonnés. Si la reprise d'une session (`--continue`, prévue par le profil du coordinateur) recopie l'historique dans un nouveau fichier, chaque message ancien est compté une fois par fichier. Le total en minutes ne bouge pas (les heures sont identiques et se fondent dans les mêmes moments), mais « N message(s) retenu(s) » gonfle. Dédoublonner sur le champ `uuid` de l'évènement quand il existe ne coûte qu'un ensemble.
2. **`scripts/maintainer_time.py`, l. 141-145 et 134** : `session_cwd(events)` prend une liste mais ne reçoit plus que `[event]`. C'est un reste de la lecture des sessions entières, retirée avec le côté tâche. Le remplacer par un test direct sur `event.get("cwd")`. De même, dans `scripts/test_maintainer_time.py`, l. 41-52, `assistant(send=...)` construit encore une commande `orca terminal send` de relais, vestige du côté tâche, alors qu'il ne sert plus qu'à produire « un appel d'outil seul ». Un `tool_use` neutre suffirait et ne suggérerait plus une détection de relais qui n'existe plus.
3. **`scripts/maintainer_time.py`, l. 218** : `--issue "#23"` donne le motif `##23` et ne rattache plus rien par le numéro, sans message (seul le nom du worktree rattache encore). Retirer un `#` initial (`args.issue.lstrip("#")`), ou refuser une valeur non numérique avec un message `[jam]`.
4. **`scripts/maintainer_time.py`, l. 159-172** : une notification de fond qui arrive entre la question du coordinateur et le « ok » du mainteneur ouvre un nouveau tour. Si ce tour ne nomme pas la tâche (une tâche de fond quelconque qui se termine, suivie de « Veille relancée. »), le « ok » est perdu. Le comportement est voulu (le test `test_background_notification_opens_a_new_turn` le fixe), mais la limite n'est pas écrite. L'ajouter à la docstring (l. 29-31) et à « Les pièges » de la fiche concept.
5. **`scripts/watch_cards.py`, l. 239-242** : `--idle-minutes nan` (ou `inf`) passe le contrôle `<= 0`. Le réveil d'inactivité est alors désactivé sans message (`age >= nan` est toujours faux). Refuser une valeur non finie (`math.isfinite`), et faire de même pour `--interval`, où `nan` fait planter `time.sleep` avec une trace.

RELECTURE : CORRECTIONS (2)
