# Relecture #23, axe justesse, tour 3

Périmètre : tout le travail non commité de la branche (`git status`, `git diff`, fichiers non suivis), lu contre le plan validé `docs/plans/23-process-elague.md`.

Tests : `python3 -m unittest`, 178 tests, OK (70 s).

Vérifié sans constat :
- **Refonte de `hooks/guard_outbound.py`** : `maintainer_words(event)` reprend le corps de la boucle de `last_user_message` à l'identique (chaque `continue` devient `return None`, chaque `return` est conservé, le `""` d'une commande `/` sans argument aussi). `hooks/test_guard_outbound.py` n'est pas modifié et reste vert.
- **Hook de reprise** (`hooks/session_start_recap.py:15-24`, `:172-176`) : chemins absolus déduits du fichier du hook ; les cas « repo avec son propre `process/` et `docs/process/` », « sans fiche » et « fiche qui est un dossier » sont testés. Le message de refus de `guard_coordinator.py` vise le process du plugin, et son test le vérifie.
- **Repo public** : aucun chemin du poste, nom de personne, d'hôte ou d'autre projet dans `process/`, `roles/`, `hooks/`, `scripts/`, `docs/methode.md`, l'ADR 0018, la fiche concept ou les specs touchées.

## Bloquant

Aucun.

## À corriger

### 1. Mesure : seul le dernier bloc de texte du coordinateur sert au rattachement, pas sa dernière réponse

`scripts/maintainer_time.py:225-230` (et `answers`, `:149-164`). `attached` ne regarde que le dernier évènement `assistant` à texte avant le message. Or Claude Code écrit un évènement par bloc : une réponse du coordinateur faite de « texte, appel d'outil, texte » donne deux évènements, et seul le second est lu. Le plan (annexe B) parle de « la dernière réponse du coordinateur », c'est-à-dire de tout le tour.

**Scénario d'échec** : session du coordinateur sur `main` :
1. 10:00, réponse texte « La carte 23-tache attend ton feu vert recette. » ;
2. 10:00, appel Bash qui relance `watch_cards.py` en arrière-plan, que le profil du coordinateur demande après chaque réveil ;
3. 10:00, texte « Veille relancée. » ;
4. 10:02, message du mainteneur « ok ».

Le script compare « ok » au seul « Veille relancée. », qui ne nomme pas la tâche, et classe le message « hors tâche ». Le feu vert est perdu, et avec lui un moment entier (3 min). Le motif « annonce, relance de la veille, phrase de fin » est le tour ordinaire du coordinateur : l'écart à ±1 moment de la recette peut être dépassé sur une tâche à plusieurs feux verts.

**Correction attendue** : rattacher le message si l'un des textes du coordinateur écrits depuis le message précédent du mainteneur dans la session (tout le tour) nomme la tâche. Ajouter un test « texte qui nomme la tâche, appel d'outil, texte qui ne la nomme pas, puis « ok » » : 1 message retenu.

### 2. Mesure : un relais écarte toutes les copies de son texte, même tapées plus tard par le mainteneur

`scripts/maintainer_time.py:214` (et `relayed_texts`, `:122-146`). Les relais forment un **ensemble** de textes, sans compte ni date. Tout message d'une session de la tâche dont le texte figure dans cet ensemble est écarté, quel que soit son moment et quel que soit le nombre de relais. Or le process (`process/README.md:71`, `:74`) relaie le plan et la recette par un simple « ok », et permet au mainteneur de donner un feu vert directement dans le worktree.

**Scénario d'échec** :
1. 10:00, le mainteneur écrit « ok » au coordinateur pour le plan de #23 ;
2. 10:01, le coordinateur relaie `orca terminal send --text "ok"` à l'orchestrateur ;
3. 15:00, le mainteneur tape lui-même « ok » dans le terminal de l'orchestrateur pour la recette.

Le « ok » de 15:00 est compté comme un relais et écarté : la mesure rend 1 moment et 3 min au lieu de 2 moments et 6 min. Cette perte ne figure pas parmi les limites écrites (docstring `:24-26`, fiche concept, plan).

**Correction attendue** : consommer chaque relais une seule fois, et seulement pour le premier message de même texte qui suit l'envoi dans une session de la tâche (garder des couples (texte, heure de l'envoi) plutôt qu'un ensemble). À défaut, écrire cette limite avec les autres. Ajouter le test du scénario : 2 moments, « 1 relais ».

### 3. Veille : un changement de commentaire masque un agent bloqué au même relevé, qui est alors compté comme vu

`scripts/watch_cards.py:182-186`. La chaîne `if / elif` ne retient qu'une raison par carte. Quand le commentaire change et appelle le coordinateur (`✓` ou `💬` présent) au même relevé qu'un agent qui entre en `waiting`, le réveil sort sans « (agent en attente d'une autorisation) ». Le `paneKey` bloqué est pourtant enregistré dans `self.blocked`, puis repris dans la base de la veille relancée, et ne réveillera plus jamais comme « bloqué ».

**Scénario d'échec** : la carte porte `▶ relecture tour 2 en cours · 💬 retour : …` (le `💬` reste jusqu'à l'accusé de réception) et un relecteur `working`. L'orchestrateur met à jour la carte (`▶ relecture tour 2, 2 relecteurs · 💬 …`), puis tombe dans les 30 s sur une invite d'autorisation (`waiting`). La veille sort « Carte(s) à traiter : 23-tache », sans la raison. Le coordinateur traite le `💬` et relance la veille, qui prend l'agent bloqué pour déjà vu. Le relecteur est au travail, donc la carte n'est pas inactive : aucun réveil tant que le relecteur tourne, puis 10 min de plus. L'orchestrateur reste bloqué pendant tout ce temps sans que le mainteneur soit prévenu. Cela contredit le réveil sur agent bloqué du critère de fin (`watch_cards.py` gagne deux réveils).

**Correction attendue** : réunir les raisons d'une carte (par exemple `💬…, agent en attente d'une autorisation`) au lieu de n'en garder qu'une. Ajouter un test : commentaire avec `💬` et agent `waiting` au même relevé, la ligne de réveil nomme le blocage.

## Suggestions

1. **`scripts/test_watch_cards.py:258`** : `quiet` est construit une fois avant la boucle. Ses `stateStartedAt` ont donc plus d'une seconde dès le 2ᵉ sous-test, chaque sous-test durant plus de 1 s (`end["sleep"] = 1`). Au 3ᵉ relevé, l'âge précédent dépasse déjà le seuil (0,6 s) : le volet « inactivité » ne prouve rien pour `completed`, `⏸`, `⛔` et « sans segment ». Le volet « bloqué » suffit à couvrir `running()`, mais le commentaire du test annonce les deux. Construire `quiet` dans la boucle.
2. **`scripts/test_watch_cards.py:239-250`** : le cas négatif ne prouve quelque chose que si le 2ᵉ relevé tombe moins de 0,6 s après la création des agents. Il faut trois démarrages d'interpréteur, et sur un runner lent le test passe à vide. Ce n'est pas un faux rouge, mais une fausse preuve. Prendre un seuil plus large (`0.05`, avec un `sleep` de 4 s), ou dater les agents à `now_ms()` plus quelques secondes.
3. **`scripts/watch_cards.py:187-188`** : une carte qui *devient* `▶` pendant la veille alors que ses agents sont déjà inactifs depuis plus de N min ne réveille jamais. Au premier relevé `▶`, l'âge précédent est absent, puis il est déjà au-delà de N. Exemple au niveau *léger* : le coordinateur pose `▶ implémenteur en cours` sur une carte dont le terminal du relecteur précédent est resté ouvert (`done` depuis 30 min), et le lancement échoue. Le plan ne règle que le cas « au lancement » de la veille. Écrire la limite, ou traiter un passage à `▶` comme le début d'un épisode.
4. **`scripts/watch_cards.py:228-231`** : `--idle-minutes nan` est accepté (`nan <= 0` est faux) : la comparaison de `:188` est alors toujours fausse et la veille ne réveille jamais pour une carte inactive. `--interval nan` finit en trace Python (`time.sleep`). Refuser les valeurs non finies (`math.isfinite`).
5. **`scripts/test_maintainer_time.py`**, cas limites manquants des options de `main()` :
   - `--since` ou `--until` illisible (sortie 2, préfixe `[jam]`) ;
   - message exactement à la borne de la fenêtre (gardé, `:218`) ;
   - commande `/` du mainteneur (`maintainer_words` rend ses arguments, ou `""`) ;
   - `--issue "#23"`, qui donne le motif `##23` et ne rattache plus rien. Retirer un `#` initial dans `measure`.
6. **`scripts/maintainer_time.py:59-62`** : une date sans fuseau passée à `--since` ou `--until` est lue en UTC sans le dire. Un `--since 2026-10-12T09:00` pensé en heure de Paris décale la fenêtre de 2 h. Le dire dans l'aide (« UTC si aucun fuseau »), puisque le rapport affiche des heures `Z`.
7. **`scripts/maintainer_time.py:85`** : un transcript illisible (`PermissionError`, ou un dossier nommé `*.jsonl`) arrête le script sur une trace Python. Attraper `OSError`, ignorer le fichier, et le compter dans le rapport.
8. **`hooks/test_plugin.py:46-50`** : `method_pages` ne lit que le premier niveau de `process/` et `roles/`. Une page rangée dans un sous-dossier échapperait au plafond de mots et au contrôle de généricité. Le contrôle ne voit pas non plus un chemin du poste écrit `~/…`. Parcourir les dossiers en profondeur (`os.walk`) et ajouter `~/` aux interdits, ou dire pourquoi ce n'est pas utile.

RELECTURE : CORRECTIONS (3)
