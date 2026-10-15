## Décidé : feu vert recette

Feu vert recette du mainteneur le 2026-10-15 : accord sur les trois recommandations.

Projet jam, tâche « Process élagué » (#23). La recette agent, refaite après les corrections, est bonne : la mesure du temps du mainteneur, rejouée sur la tâche précédente « le repo devient le kit » (#22), donne 5 moments et 44 min, contre 5 moments et 43,5 min au relevé à la main, sans plantage ; 186 tests passent ; le process et les profils font 4904 mots, pile au plafond (la moitié de l'ancien process). Trois points à trancher ; un « ok » vaut accord sur les trois recommandations.

1. **Deux règles ajoutées en cours de tâche** pour combler des trous du niveau léger relevés par le coordinateur. (a) Au niveau léger, l'implémenteur ou le rédacteur écrit, à la fin de son travail, la check-list de recette du mainteneur ; pour cela, l'implémenteur n'a plus d'interdit sur tout docs/plans/, seulement sur le plan et les rapports de relecture. (b) En conflit avec main, la carte passe en bloqué, et le coordinateur décide avec le mainteneur ; s'il faut résoudre le conflit, l'implémenteur (le rédacteur pour des docs) le fait, puis les tests sont relancés, et la branche n'est poussée qu'après un nouveau feu vert. Recommandation : garder les deux.
2. **Deux coupes faites pour tenir le plafond de mots**, sans retirer de règle : la phrase du process qui décrivait le contenu du récapitulatif de démarrage, et la liste des décisions d'architecture citées dans son introduction. Recommandation : garder les coupes ; le plafond étant atteint au mot près, toute règle future devra retrancher autant qu'elle ajoute.
3. **Limite de la mesure**, écrite dans la PR et dans le process : seules les sessions du coordinateur sont lues, donc ni la recette du mainteneur, faite dans une session du worktree de la tâche, ni un feu vert tapé là ne sont comptés. Une question ouverte demande s'il faut compter ce temps sans que le mainteneur le relève lui-même. Recommandation : en rester là pour cette tâche.

## Première recette (refusée sur la mesure du temps)

# Recette — #23 Process élagué (K1-2), niveau *standard*

> Repli (friction 18) : ce rapport est écrit dans le dossier de recette, l'écriture de `docs/plans/23-process-elague-recette.md` ayant été refusée (voir « Friction 18 » plus bas). Un rédacteur le recopie tel quel dans `docs/plans/23-process-elague-recette.md`. Chemins du poste remplacés par `<worktree>` (worktree de #23), `<worktree #22>`, `<main>` (worktree principal) et `<dossier>` (dossier des transcripts).

## Check-list du mainteneur

Chaque point se fait dans une session neuve `claude --plugin-dir <worktree>`, ouverte dans un terminal Orca du worktree `23-process-elague`, par la demande citée entre guillemets. Aucune de ces demandes ne vaut accord ni refus : relues contre `APPROVAL` et `NEGATION` de `hooks/guard_outbound.py`, elles ne contiennent aucun de leurs mots.

1. **Récapitulatif de démarrage**. Demande : « Recopie mot pour mot la ligne Méthode du récapitulatif de démarrage, et dis s'il porte la marque [jam]. »
   Attendu : le récapitulatif porte `[jam]` ; la ligne est « Méthode : fiche `docs/methode.md` · process `<worktree>/process/README.md` · profils `<worktree>/roles/` », en chemins absolus du worktree (le plugin chargé) ; il n'y a plus de ligne « Process du repo » dans ce récapitulatif. Un second récapitulatif sans `[jam]`, venu des hooks actuels du poste, est attendu avant l'installation du plugin (issue, « Après le merge de #23 ») et se note à part.

2. **Comptage des mots**. Demande : « Exécute `wc -w process/README.md process/fiche-projet.md roles/*.md` et donne le total. »
   Attendu : un total de 4904 mots au plus (la moitié des 9808 de `docs/process/` sur `main` à a4794df, NFR-015).

3. **Noms interdits**. Demande : « Cherche, en ignorant la casse, dans process/, roles/, hooks/, scripts/ et .claude-plugin/ les noms de cette liste : <liste donnée hors du repo>. Cherche aussi pnpm, /Users/ et /home/ dans process/ et roles/. Donne chaque occurrence avec son fichier et sa ligne. »
   Attendu : aucune occurrence (NFR-014).

4. **Liens des docs déplacées**. Demande : « Dans process/, roles/, AGENTS.md, README.md et docs/ hors docs/plans/, vérifie chaque lien Markdown relatif. Liste ceux dont la cible est absente, puis ceux qui visent encore docs/process/. »
   Attendu : aucune cible absente ; aucun lien vers `docs/process/`, hormis le renvoi `docs/process/README.md` lui-même, qui pointe vers `process/`.

5. **Réveils de la veille**, sur le worktree jetable `essai-veille` du repo jam, préparé par l'orchestrateur de tâche (aucune vraie carte touchée).
   - **a. Agent bloqué**. Préparation : carte `essai-veille` au commentaire « ▶ essai veille », un agent au travail dans son terminal. Demande, *avant* que cet agent tombe sur l'invite : « Exécute en tâche de fond `python3 scripts/watch_cards.py jam --idle-minutes 2 --interval 10`, puis recopie sa sortie et son code de retour dès qu'il rend la main. » Ensuite, l'agent d'`essai-veille` reçoit une commande hors de sa liste blanche et s'arrête sur l'invite d'autorisation.
     Attendu : dans les 10 s qui suivent l'invite, `[jam] Carte(s) à traiter : essai-veille (agent en attente d'une autorisation)`, puis la liste des cartes de jam ; code 0. (Si la veille démarre alors que l'agent est déjà sur l'invite, ce réveil-là n'a pas lieu : seul vient, 2 min plus tard, « agent en attente d'une autorisation depuis 2 min ».)
   - **b. Carte ▶ sans agent au travail**. Préparation : l'agent d'`essai-veille` fermé, le commentaire « ▶ essai veille » gardé. Demande, dans la minute qui suit la fermeture : la même que pour **a**.
     Attendu : `[jam] Carte(s) à traiter : essai-veille (aucun agent au travail depuis 2 min)`, 2 min après la fermeture de l'agent, au plus tard 2 min 10 s après le lancement de la veille ; code 0.
   - **c. Avant N minutes, un simple ▶ reste muet**. Pendant la première minute de **b**, l'orchestrateur change le commentaire de la carte en « ▶ essai veille 2 ».
     Attendu : rien ne s'affiche avant le réveil de **b**, qui garde son heure.

   Le réveil ne doit nommer qu'`essai-veille` ; une autre carte nommée (celle de `23-process-elague`, par exemple) est relevée au rapport.

## Vérifications, dans l'ordre

### 0. Installation neuve

Session de recette lancée avec `--plugin-dir <worktree>` : le plugin du worktree est chargé pour cette seule session (récapitulatif `[jam]` à ligne « Méthode » vu au démarrage de la session du recetteur). Aucune dépendance à installer (bibliothèque standard seule).

### 1. Check-list, déroulée par l'orchestrateur de tâche

Session `claude --plugin-dir <worktree>` dans un terminal Orca du worktree, mode automatique du poste, demandes de la check-list mot pour mot. Écrans dans le dossier de recette.

| Point | Demande | Écran utile | Résultat | Verdict |
|---|---|---|---|---|
| 1 | Point 1 ; puis, la session n'ayant pas recopié la ligne, « Redonne seulement la ligne Méthode du récapitulatif marqué [jam], mot pour mot, sur une ligne, rien d'autre. » | `ecran-1.txt`, `ecran-1b.txt` | Marque `[jam]` présente. Ligne : « Méthode : fiche docs/methode.md · process `<worktree>/process/README.md` · profils `<worktree>/roles/` ». Second récapitulatif sans `[jam]` avec « Process du repo : docs/process/README.md » : hooks actuels du poste, attendu avant l'installation (de même, une seconde ligne `[état git]` sans marque). | OK |
| 2 | Point 2 ; puis « Redonne seulement la ligne total de wc, telle quelle, sur une ligne. » | `ecran-2.txt`, `ecran-2b.txt` | `4641 total` (process/README.md : 46 % du total). | OK (4641 ≤ 4904) |
| 3 | Point 3, liste donnée hors du repo, avec en plus le nombre total d'occurrences | `ecran-3.txt` | Aucune occurrence, total 0, dans les cinq dossiers pour la liste, dans `process/` et `roles/` pour `pnpm`, `/Users/`, `/home/`. | OK |
| 4 | Point 4, avec en plus les deux nombres en fin de réponse | `ecran-4.txt` | 219 liens relatifs vérifiés dans 48 fichiers ; cibles absentes : 0 ; liens vers `docs/process/` : 0. Ancres `#…` non contrôlées. | OK |
| 5a | Point 5a | `ecran-5a.txt` | `[jam] Carte(s) à traiter : essai-veille (agent en attente d'une autorisation)`, puis les trois cartes de jam ; code 0. État Orca relevé par l'orchestrateur : `waiting` (invite Bash). Délai entre l'invite et le réveil non chronométré. | OK |
| 5b | Point 5b | `ecran-5b.txt`, `chrono-5b.txt` | Fermeture de l'agent 20:16:59, veille lancée 20:17:05, réveil vu 20:19:10 : `essai-veille (aucun agent au travail depuis 2 min)` ; code 0. Fenêtre attendue : 20:18:59 à 20:19:15. | OK |
| 5c | Point 5c | `chrono-5b.txt`, `ecran-5b.txt` | Commentaire passé à « ▶ essai veille 2 » à 20:17:21 ; rien avant le réveil de 20:19:10, qui garde son heure. | OK |

Dans les deux réveils, seule `essai-veille` est nommée ; la carte `23-process-elague` (▶, agents au travail) ne l'est pas.

Défaut de rédaction de la check-list, point 1 : la demande en deux parties a fait répondre la session à la seconde seule ; une relance a été nécessaire. Pour une prochaine check-list, une seule question par demande.

### 2. Friction 18 : écriture refusée sous `--plugin-dir`

- **Mon refus** (premier geste d'écriture de la session, outil Write, création de `docs/plans/23-process-elague-recette.md`, règle `Edit(/docs/plans/23-process-elague-recette.md)`, session lancée avec `--plugin-dir <worktree>` et `--permission-mode dontAsk`) : « Permission to use Write has been denied because Claude Code is running in don't ask mode. … » Pas de préfixe `[jam]` : ce n'est pas un hook. L'écriture dans le dossier de recette est passée.
- **Sonde de l'orchestrateur** (`sonde-friction-18.md`) : trois sessions jetables, Write, trois formes de règle (relative, ancrée par `/`, absolue `//`). Sans `--plugin-dir` : les trois passent. Avec `--plugin-dir` sur un autre dossier : les trois passent. Avec `--plugin-dir` sur le dossier écrit : les trois sont refusées, même message.
- **Ce que cela change** :
  - le diagnostic du plan (§2, « Friction 18 ») est faux : la cause est le `--plugin-dir` qui vise le dossier écrit, pas la forme relative de la règle. Le plan l'écartait expressément (« `--plugin-dir` n'y est pour rien ») ;
  - la règle de `process/README.md` (l. 101) reste inoffensive, mais sa justification est fausse : elle présente l'ancrage comme ce qui fait passer l'écriture, et le repli comme un cas rare. Pour jam au niveau *standard*, le recetteur est toujours lancé avec `--plugin-dir <worktree>` (fiche, « Recette ») : son écriture dans le worktree est **toujours** refusée, et le repli est la seule voie. Même erreur dans l'ADR 0018 (tableau, ligne « Toute règle `Edit` ancrée par `/` », origine « Friction 18 de #22 ») ;
  - le profil générique du recetteur (`roles/recetteur.md`) n'est pas faux (« Si l'écriture du rapport est refusée malgré sa règle… »), mais la fiche de jam devrait dire que, sous `--plugin-dir <worktree>`, le rapport va d'emblée dans le dossier de recette.
- **Classement** : une correction avant le feu vert recette, pas un KO à elle seule. Le comportement livré marche (le repli a fonctionné deux fois) ; c'est l'explication écrite dans le process, l'ADR 0018 et la fiche qui est fausse, et le grief de la grille (« une règle nouvelle […] dit ce qu'elle remplace ») porte sur une règle dont la raison est inexacte.

### 3. Contrôles outillés

| Commande | Résultat | Verdict |
|---|---|---|
| `python3 -m unittest` | `Ran 185 tests in 72.521s` — `OK` (dont le test de taille de `hooks/test_plugin.py`, ≤ 4904 mots) | OK |
| `wc -w process/README.md process/fiche-projet.md roles/*.md`, puis sa forme `rtk` | Refusé par les permissions de la session (même message « don't ask mode »), alors que l'annexe A du plan l'autorise : la règle n'était pas dans la commande de lancement. Couvert par le point 2 de la check-list (4641) et par le test de taille. | non reproduit |

### 4. Mesure sur #22

**Fenêtre** : début de #22 = premier évènement daté des transcripts du worktree de #22, `2026-10-11T17:48:06Z` (aucun évènement plus tôt dans ce dossier) ; fin `2026-10-13T10:57:00Z`.

**Commande du brief** : `python3 scripts/maintainer_time.py --main <main> --worktree <worktree #22> --issue 22 --transcripts <dossier> --since 2026-10-11T17:48:06Z --until 2026-10-13T10:57:00Z`.
Résultat, deux fois de suite : **plantage** (`FileNotFoundError`, code 1). `read_sessions` ouvre chaque `*.jsonl` sous `<dossier>` sans garde ; un lien symbolique cassé (transcript de sous-agent d'un autre projet, qui vise un dossier disparu) l'arrête. Le dossier des transcripts d'un poste réel en contient : avec la commande par défaut, le mainteneur obtiendrait le même plantage. Les tests n'ont pas ce cas.

**Repli, pour recouper malgré tout** : le script lancé deux fois, `--transcripts` sur le seul dossier du worktree de #22, puis sur le seul dossier de `<main>`.

| Côté | Sessions lues | Script | Relevé à la main |
|---|---|---|---|
| Coordinateur (`<main>`) | 4 du coordinateur (1 dans la fenêtre) | 15 messages, 5 moments, 44 min ; écartés : 75 hors tâche, 6 hors fenêtre | 17 messages du mainteneur dans la fenêtre ; 15 rattachés à #22 selon la règle de l'annexe B, 2 sans renvoi à #22 ni dans le message ni dans le tour précédent ; mêmes 5 moments : 11/10 17:56→18:09 (15 min), 20:04 (3), 20:48→20:50 (5), 12/10 19:37→19:51 (17), 13/10 10:56 (3) ; total 43,5 min |
| Tâche (`<worktree #22>`) | 31 | 13 messages, 8 moments, 56 min ; écartés : 31 briefs, 0 relais | **0** message du mainteneur. Les 13 messages retenus sont des relais d'agents : 5 du coordinateur à l'orchestrateur (préfixe « [coordinateur] » ou relais annoncé), 8 de l'orchestrateur aux rôles (consignes de tour) |

Côté coordinateur, le script et le relevé concordent exactement. Les messages de pairs (`origin.kind` = `peer`, `isMeta`) sont bien écartés. Un message collé par le mainteneur depuis un autre coordinateur (`origin.kind` = `human`) compte, comme au relevé.

Côté tâche, le script ne reconnaît aucun relais, pour deux causes vues dans les transcripts :
1. l'orchestrateur met le texte dans une variable shell (`B='…'`) puis envoie `--text "$B"` : `relay_sends` lit `$B`, pas le texte ;
2. un texte long arrive dans la session cible enveloppé dans un bloc `<pasted_content>` : même lu, il ne serait plus identique au `--text`.

**Comparaison avec la tolérance du plan** (moments ±1, total ±15 % ou ±5 min, le plus large) :
- relevé : 5 moments, 43,5 min ;
- script, sur les deux côtés réunis (ce qu'aurait rendu la commande du brief sans le plantage) : 28 messages ; d'après les heures des deux sorties, environ 9 moments et environ 80 min ;
- écart : environ +4 moments, environ +36 min (≈ +85 %). **Hors tolérance.**

## Verdict

- Check-list : 5 points OK, dont la veille dans ses trois phases.
- Tests : 185 OK.
- Friction 18 : diagnostic du plan faux (sonde) ; correction du texte du process, de l'ADR 0018 et de la fiche avant le feu vert recette.
- Mesure : KO. Le script plante sur le dossier des transcripts du poste (lien cassé), et, côté tâche, il compte comme messages du mainteneur les relais envoyés par variable shell ou arrivés en collage ; le chiffre sort de la tolérance du plan.

RECETTE AGENT : KO (maintainer_time.py plante sur un lien symbolique cassé du dossier des transcripts, et compte comme messages du mainteneur 13 relais d'agents dans le worktree de #22 : environ 9 moments et 80 min contre 5 moments et 43,5 min au relevé)

## Recette après correction — #23 Process élagué (K1-2), niveau *standard*

> Rapport écrit dans le dossier de recette : la session est lancée avec `--plugin-dir <worktree>` et ne peut écrire dans le worktree (process, « Permissions »). Un rédacteur le recopie tel quel à la suite de `docs/plans/23-process-elague-recette.md`. Chemins du poste remplacés par `<worktree>` (worktree de #23), `<worktree #22>`, `<main>` (worktree principal) et `<dossier>` (dossier des transcripts).

Décisions du mainteneur appliquées depuis la première recette : la mesure ne lit que les sessions du coordinateur, sur le worktree principal ; un transcript illisible est ignoré ; le rapport du recetteur va dans son dossier de recette, recopié par un rédacteur.

Aucun contenu de transcript n'a été lu à la main : la mesure n'a montré aucun écart à lever.

### 1. Mesure sur la tâche « le repo devient le kit » (#22)

**Commande** (dossier des transcripts par défaut, sans `--transcripts`) :
`python3 scripts/maintainer_time.py --main <main> --worktree <worktree #22> --issue 22 --since 2026-10-11T17:48:06Z --until 2026-10-13T10:57:00Z`

**Résultat**, identique aux trois lancements (deux avec `--issue 22`, un avec `--issue "#22"`) :

```
[jam] Temps du mainteneur : 44 min en 5 moment(s), 15 message(s) retenu(s)
8 session(s) du worktree principal lue(s)
- 2026-10-11 17:56Z → 18:09Z : 15 min
- 2026-10-11 20:04Z → 20:04Z : 3 min
- 2026-10-11 20:48Z → 20:50Z : 5 min
- 2026-10-12 19:37Z → 19:51Z : 17 min
- 2026-10-13 10:56Z → 10:56Z : 3 min
Écartés : 83 hors tâche, 7 hors fenêtre
Non comptés : recette du mainteneur et feux verts tapés dans le worktree de la tâche
```

- **Plantage** : aucun. Le dossier par défaut, celui qui contenait le lien symbolique cassé à la première recette, est lu jusqu'au bout. Code de retour 0 : l'outil de la session signale tout code non nul comme une erreur, et n'en a signalé aucune (un `; echo $?` ajouté à la commande sort de la liste blanche et a été refusé).
- **Contenu de message** : aucun. Le rapport ne donne que des heures, des durées et des comptes.
- **Comparaison au relevé à la main de la première recette** (côté coordinateur : 15 messages rattachés, 5 moments, 43,5 min) :

| | Relevé | Script | Écart | Tolérance du plan | Verdict |
|---|---|---|---|---|---|
| Messages rattachés | 15 | 15 | 0 | — | OK |
| Moments | 5, mêmes bornes | 5, mêmes bornes | 0 | ±1 | OK |
| Total | 43,5 min | 44 min | +0,5 min | ±6,5 min (15 %, plus large que 5 min) | OK |

- **Différences avec la première recette, sans effet sur le chiffre** : 8 sessions du worktree principal lues au lieu de 4, et 83 messages hors tâche au lieu de 75, 7 hors fenêtre au lieu de 6. Le coordinateur a ouvert ou poursuivi des sessions sur `<main>` depuis ; leurs messages tombent hors de la tâche ou hors de la fenêtre. Les sessions du worktree de #22 ne sont plus lues : les 13 relais d'agents comptés à tort la première fois ont disparu.
- **Tests qui fixent ces deux corrections** : `scripts/test_maintainer_time.py`, `test_task_worktree_sessions_not_read` et `test_unreadable_transcript_skipped` (dans la suite du point 3).

**Verdict : OK.**

### 2. Contrôles de la check-list sur l'état final

| Point | Commande | Résultat | Verdict |
|---|---|---|---|
| 2. Comptage des mots | `wc -w process/README.md process/fiche-projet.md roles/*.md` (réécrite en `rtk`) | process/README.md 2310, fiche-projet.md 179, coordinateur 602, implementeur 222, orchestrateur-tache 480, planificateur 200, recetteur 342, redacteur 274, relecteur 295 ; **total 4904** (recompté à la main) | OK (≤ 4904), **sans aucune marge** : 263 mots de plus qu'à la première recette (4641) |
| 3. Noms interdits, réduit | Recherche de `pnpm`, `/Users/`, `/home/`, casse ignorée, dans `process/` et `roles/` | Aucune occurrence | OK |
| 3. Liste des autres projets | — | Non refait, couvert par la première recette et les relectures | non refait |
| 4. Liens Markdown relatifs | Extraction des liens `](…)` de `process/`, `roles/`, `AGENTS.md`, `README.md` et `docs/` ; liens `http(s)` et `docs/plans/` écartés ; chaque cible confrontée à la liste des fichiers du worktree | Cibles absentes : 0 (fichiers et dossiers `roles/`, `docs/specs/`, `docs/decisions/` présents ; ADR 0001 à 0018 toutes présentes). Liens vers `docs/process/` : 0, hormis le renvoi `docs/process/README.md` lui-même, dont les liens visent `process/`, `roles/`, `process/fiche-projet.md`, `docs/methode.md` et l'ADR 0018. Aucune ancre `#…` dans ces liens. | OK |

Remarque (pas un KO) : le plafond de mots est atteint au mot près. La moindre phrase ajoutée au process ou à un profil fera échouer le test de taille de `hooks/test_plugin.py` ; toute correction à venir devra retrancher autant qu'elle ajoute.

### 3. Tests

| Commande | Résultat | Verdict |
|---|---|---|
| `python3 -m unittest` | `Ran 186 tests in 76.196s` — `OK` (185 à la première recette) | OK |

### 4. Reprise de session

- `hooks/hooks.json` : le groupe `SessionStart` a le matcher `startup|clear|resume` et lance `hooks/session_start_recap.py` ; pas de `compact`.
- `hooks/test_plugin.py` fixe ce matcher (tableau attendu des hooks, ligne 27) et `test_recap_on_start_clear_and_resume` vérifie que `startup`, `clear` et `resume` y sont, sans `compact` : passé dans la suite du point 3.
- Une reprise réelle (`claude --continue`) : non reproduit, couvert par le test.

**Verdict : OK.**

### 5. Points non refaits

- **Point 1, récapitulatif de démarrage** : non refait. Ce qui a changé depuis : le récapitulatif vient aussi à la reprise (point 4 ci-dessus). Le récapitulatif `[jam]` à ligne « Méthode » a été vu au démarrage de cette session.
- **Point 5, réveils de la veille** : non refait. Ce qui a changé depuis : un agent en attente sur son invite n'est plus compté au travail, la carte franchit donc aussi le seuil et le second réveil le dit (« agent en attente d'une autorisation ») ; couvert par `scripts/test_watch_cards.py`, `test_agent_still_blocked_after_threshold_is_named_so` (attente lue sur la ligne ou sur `mainAgent`), passé dans la suite du point 3.

### Check-list du mainteneur

Celle de la première recette reste valable telle quelle, avec un seul attendu mis à jour : au point 2, le total est maintenant de 4904 mots, pile au plafond. La mesure n'y figure pas : le mainteneur ne valide pas le chiffre (retours, point 2).

### Verdict

- Mesure sur #22 : OK, sans plantage, stable sur trois lancements, 5 moments et 44 min contre 5 moments et 43,5 min au relevé.
- Contrôles 2, 3 réduit et 4 : OK ; plafond de mots atteint sans marge.
- Tests : 186 OK.
- Reprise : matcher et test présents ; reprise réelle non reproduite.

RECETTE AGENT : OK
