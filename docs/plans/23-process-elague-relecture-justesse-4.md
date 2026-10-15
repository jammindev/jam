# Relecture — #23 Process élagué, axe justesse, tour 4

Périmètre : tout le travail non commité de la branche (`git status`, `git diff`, fichiers non suivis). Tests : `python3 -m unittest`, **181 tests OK** (71 s).

Vérifié sans constat :
- **Refonte de `hooks/guard_outbound.py`** : `maintainer_words(event)` reprend le corps de la boucle de `last_user_message` à l'identique (chaque `continue` devient `return None`, le retour du texte est inchangé). `hooks/test_guard_outbound.py` n'est pas modifié et passe.
- **Hook de reprise** : la ligne « Méthode » se déduit de `__file__`, pas du worktree. Elle n'apparaît que si `docs/methode.md` est un fichier. Les tests couvrent un repo qui a son propre `process/` et `docs/process/`, l'absence de fiche, et une fiche qui est un dossier. Le refus de `guard_coordinator.py` renvoie au process du plugin.
- **`hooks/test_plugin.py`** : le plafond de 4904 mots est compté avec `split()`. Un fichier ajouté dans `process/` ou `roles/` doit entrer dans le compte, et les fichiers parasites (`.DS_Store`, `~`) sont ignorés. Les interdits `pnpm`, `/Users/` et `/home/` sont vérifiés.
- **`maintainer_time.py`** : aucun contenu de message ne sort (mot témoin vérifié à chaque lancement). Un dossier introuvable sort en erreur, et un relevé vide affiche le nombre de sessions lues.
- **Repo public** : les fichiers relus ne contiennent ni chemin du poste, ni nom de personne, d'hôte ou d'autre projet. Les seuls chemins `/Users/` sont des chemins fictifs de tests déjà présents.

## Bloquant

Aucun.

## À corriger

### 1. Une carte qui devient inactive déjà au-delà de N ne réveille jamais

- **Fichier** : `scripts/watch_cards.py:186-187`.
- **Défaut** : le réveil « inactif » exige `previous_age is not None`. Or `previous_age` vaut `None` à la première lecture où la carte est inactive : à la lecture précédente, un agent y travaillait, ou la carte n'était pas `▶`. Si, à cette première lecture, le plus récent `stateStartedAt` de ses agents est déjà vieux de plus de N, l'âge vaut déjà au moins N. Aucune lecture ne voit alors l'âge franchir N, et l'épisode passe sans un seul réveil. La règle « déjà au-delà de N, compte comme vu » ne devrait valoir que pour la lecture de lancement. Elle vaut ici pour toute la vie de la veille.
- **Scénario d'échec** :
  1. La carte `▶ relecture en cours` a deux agents : l'orchestrateur `working` (`pane-1`) et une session libre ouverte par le mainteneur, `done` depuis 30 min (`pane-2`).
  2. Le terminal de l'orchestrateur se ferme (plantage, fermeture par erreur) : sa ligne disparaît du relevé.
  3. À la lecture suivante, personne ne travaille, et l'âge vaut 30 min, soit au moins N. Mais `previous_age` vaut `None` : pas de réveil.
  4. Aux lectures suivantes, `previous_age` vaut au moins N : pas de réveil non plus.

  La carte reste `▶` sans personne, et la veille ne se réveille jamais. C'est le cas que visent FR-046 (« quand aucun agent n'y travaille depuis N minutes ») et l'ADR 0018 (« une carte que personne ne tient réveille le coordinateur »), et la fiche concept le nomme (« arrêté »). Le même trou existe pour une carte qui repasse en `▶` alors que ses agents se sont arrêtés depuis plus de N minutes.
- **Correction attendue** :
  - Réveiller quand `age >= N` et que `previous_age` vaut `None` ou reste sous N. La lecture de lancement reste sans effet, puisque `watch()` ignore son résultat.
  - Ajouter un test : une première lecture avec `[working pane-1, done il y a 20 min pane-2]`, puis une lecture avec `[done il y a 20 min pane-2]`. Le réveil attendu est « 22-tache (aucun agent au travail depuis 10 min) ».
  - Ajuster le docstring et la fiche concept, qui disent aujourd'hui « franchit N entre deux lectures ».

### 2. Le test des cartes exclues ne prouve pas l'exclusion du réveil « inactif »

- **Fichier** : `scripts/test_watch_cards.py:269`.
- **Défaut** : `quiet` est construit une seule fois, avant la boucle des sous-tests. Ses agents sont donc datés avant le premier sous-test. Chaque sous-test dure plus d'1 s (`end["sleep"] = 1`). Dès le 2ᵉ sous-test (`completed`, `⏸`, `⛔`, sans segment d'état), ces agents ont plus de 0,6 s, le seuil du test, dès leur première lecture inactive. Même si le code surveillait ces cartes, l'âge ne pourrait plus franchir le seuil entre deux lectures. Ces quatre sous-tests ne prouvent donc que l'exclusion du réveil « bloqué ».
  - Le 1er sous-test (`main`) n'est sensible que si les trois premières lectures tiennent dans 0,6 s après la construction, ce qui n'est pas garanti sur un runner CI lent.
  - Le plan (étape 5) demande « pas de réveil … ni sur une carte `main`, `completed`, `⏸`, `⛔` ou sans segment d'état ».
- **Scénario d'échec** : une régression sort `self.idle_age_now(card, now)` du `if running(card)` et calcule l'âge pour toute carte. Elle réveillerait le coordinateur pour une carte `⏸` qui attend déjà le mainteneur. Les sous-tests `completed`, `paused`, `blocked` et `no state` restent verts.
- **Correction attendue** :
  - Construire `quiet` dans la boucle, après `self.setUp()`.
  - Donner à ses agents un `stateStartedAt` illisible (supprimé), pour que l'âge parte de l'horloge du script à la première lecture inactive. La régression réveillerait alors à la 4ᵉ lecture, quel que soit le temps de démarrage des interpréteurs.
  - Même remède pour `test_working_agents_keep_the_card_awake`, lignes 255-261. Ce test n'est sensible que si la 2ᵉ lecture arrive moins de 0,6 s après la construction de `busy`. Sur un runner lent, il ne peut plus échouer.

### 3. Une fenêtre sans fuseau est lue en UTC, sans le dire

- **Fichiers** : `scripts/maintainer_time.py:63` et `:308` (aide des options, lignes 303-304).
- **Défaut** : `timestamp()` complète une date sans fuseau en UTC. C'est juste pour les transcripts, toujours en `Z`, mais pas pour `--since` et `--until`. Une date ISO 8601 sans fuseau désigne d'usage l'heure locale, et l'aide ne dit que « ISO 8601 ».
- **Scénario d'échec** : le brief de recette donne la fenêtre de #22 en heure de Paris, `--since 2026-10-11T09:00 --until 2026-10-11T18:00`. Le script lit 09:00Z-18:00Z, soit 11:00-20:00 en heure locale.
  - Les messages de 09:00 à 11:00 sont comptés « hors fenêtre », et ceux de 18:00 à 20:00 sont gardés.
  - Le recoupement sur #22 échoue, ou un chiffre faux entre dans la PR (FR-055), sans aucune alerte.
- **Correction attendue** :
  - Pour `--since` et `--until`, lire une date sans fuseau en heure locale (`moment.astimezone()`), ou la refuser par une erreur `[jam]`.
  - Le dire dans l'aide.
  - Ajouter un test avec une valeur sans fuseau. Le cas « date illisible » de `main()` (ligne 309) n'a pas de test non plus.

## Suggestions

1. **`--issue` avec son `#`** (`scripts/maintainer_time.py:232-234`) : `--issue '#23'` donne le motif `##23`. Tous les messages du coordinateur qui ne nomment que `#23` passent alors en « hors tâche », sans erreur. Retirer un `#` initial ou n'accepter que des chiffres. Aucun test ne lance le script sans `--issue`.
2. **Deux envois dans une même commande** (`scripts/maintainer_time.py:142-149`) : une commande qui chaîne deux `orca terminal send … && orca terminal send …` compte deux fois le `--text` du second. En effet, `rest` court jusqu'à la fin de la ligne. Un message du mainteneur identique à ce texte peut alors être pris pour un relais. Arrêter `rest` au `terminal send` suivant ou à un opérateur shell (`&&`, `;`, `|`). La forme `--text=` (ligne 148) n'a pas de test.
3. **Relais envoyé vers une autre tâche** (`scripts/maintainer_time.py:153-169`) : un envoi n'est pas rattaché au terminal qu'il vise. Si le coordinateur relaie un « ok » au terminal de #24, le premier « ok » tapé ensuite par le mainteneur dans un terminal de #23 est écarté comme relais. C'est conforme à la règle 4 de l'annexe B du plan, mais absent des limites écrites (docstring, fiche concept, PR) : l'y ajouter.
4. **Fichier illisible** (`scripts/maintainer_time.py:86`) : un `.jsonl` illisible (lien cassé, droits) lève une trace Python sans préfixe `[jam]`. Attraper `OSError`, puis écarter le fichier ou le signaler.
5. **Agent sans `paneKey`** (`scripts/watch_cards.py:115`) : `str(agent.get("paneKey"))` donne `"None"` à tout agent sans `paneKey`. Si deux agents sans `paneKey` se bloquent l'un après l'autre, le second ne réveille pas. Utiliser une clé de repli, par exemple l'index de l'agent.
6. **Carte inactive au niveau *léger*** (`roles/coordinateur.md:20`, `process/README.md:77`) : la consigne « il relance l'orchestrateur de tâche » ne s'applique pas au niveau de jam, qui n'a pas d'orchestrateur. Ajouter « au niveau *léger*, il reprend la tâche ».

RELECTURE : CORRECTIONS (3)
