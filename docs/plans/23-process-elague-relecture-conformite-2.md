# Relecture #23, axe conformité, tour 2

Périmètre : tout le travail non commité de la branche `jammin-dev/23-process-elague` (implémenteur et rédacteur), comparé au plan validé `docs/plans/23-process-elague.md`, au brouillon de l'issue (`docs/plans/cadrage-kit-issues.md`, K1-2), aux ADR 0013, 0015, 0016, 0017 et 0018, et à l'ancien `docs/process/` du worktree principal.

Tests : `python3 -m unittest` → 177 tests, OK.

## Critère de fin, point par point

| Point | Verdict |
|---|---|
| `process/`, `roles/`, `process/fiche-projet.md` existent ; `docs/process/` ne contient plus que le renvoi | OK (`docs/process/README.md` seul) |
| Plafond de 4904 mots pour `process/` et `roles/` | OK (`hooks/test_plugin.py`, `test_under_word_cap` vert ; tout fichier ajouté entre dans le compte) |
| Ni `pnpm`, ni chemin du poste, ni nom d'hôte ou d'autre projet dans `process/` et `roles/` | OK (Grep : aucun nom de personne, d'hôte ou de projet ; `jammindev` sorti du profil du relecteur) |
| Chaque règle du point 3 dans le process **et** dans le profil du rôle qui l'applique, avec sa référence | **Incomplet** : constat 2 |
| Profil du planificateur : niveau motivé quand une tâche monte | OK (`roles/planificateur.md:16`, FR-049) |
| Règle 6 d'`AGENTS.md` cohérente avec FR-052 et FR-053 | OK |
| `docs/methode.md` au niveau *léger* | OK |
| Q-058 tranchée, cohérente avec le profil de l'orchestrateur de tâche et les ADR | OK sur le fond (ADR 0018, `roles/orchestrateur-tache.md:7`, process l. 35, glossaire, Q-058) ; formulation : suggestion S2 ; statut des ADR touchées : constat 3 |
| NFR-016 : chaque règle nouvelle dit ce qu'elle remplace ou retire | OK pour l'essentiel (table de l'ADR 0018) ; quelques retraits muets : suggestion S4 |
| Historique « Origine : … » remplacé par un renvoi | **Incomplet** : constat 1 |
| Décisions des ADR acceptées | Aucune perdue : la vérification à la main (ADR 0013, 0017) est remplacée et tracée, sauf pour la fenêtre d'autorisation du système, gardée ; les mentions de statut sont prévues à l'acceptation de l'ADR 0018 (voir constat 3) |
| Règles propres à jam sorties des profils | OK : section « Orca », clone de référence, carte du §0, contrôle des reprises, nommage des worktrees, `--plugin-dir`, section « Concepts », tout dans `docs/methode.md` |
| ADR existantes : seulement les liens et les mentions de statut prévues | OK (0009, 0012 et 0013 : liens seuls ; 0016 et 0017 intactes) |
| Liens vers l'ancien `docs/process/` hors `docs/plans/` | OK : aucun lien cassé ; un nom de section périmé (S1) |
| Vocabulaire du glossaire | OK (« Agent en cours », « Épisode », « Moment », « Note de suivi », « Session libre », « Veille des cartes » ajoutés) |
| Sur-ingénierie | Rien hors plan : `--since/--until` et le dossier des transcripts sont au plan (étape 6), la normalisation des apostrophes est justifiée dans le code |
| Repo public (diff) | OK : fixtures inventées, aucun chemin réel |

## Bloquant

Aucun.

## À corriger

### 1. Des origines retirées sans renvoi propre à la règle

- **Fichiers** : `process/README.md:12`, `:49`, `:57`, `:84`, `:85`, `:102-103` ; `roles/implementeur.md:11`.
- **Exigence violée** : plan, §2 « Origines » : « **chaque** « Origine : … » devient un renvoi (ADR 0018, ADR ou RET existants) » ; issue, point 1 (« remplacé par un renvoi à l'ADR ou au RET qui la porte »).
- **Constat** : ces règles portaient une origine dans l'ancien process. Elles n'ont plus qu'un renvoi global (l. 3 : « surtout les ADR 0013, 0016, 0017 et 0018 »). La règle « la carte est le seul canal » (l. 57) vient de RET-013 et de l'ADR 0015, qui ne figure même pas dans cette liste.
- **Scénario d'échec** : le mainteneur se demande pourquoi l'orchestrateur de tâche n'écrit jamais dans le terminal du coordinateur. La l. 57 ne donne aucune référence. La l. 3 l'envoie vers quatre ADR, dont aucune ne porte la décision (ADR 0015). Il ne trouve la trace qu'en lisant le tableau « Origines retirées » de l'ADR 0018 en entier. C'est le coût que NFR-015 voulait éviter en mettant l'historique dans une ADR plutôt que de le supprimer.
- **Correction attendue** : un renvoi court par règle, quelques mots chacun :
  - l. 12 `(RET-001)` ;
  - l. 49, après « jamais dans un worktree », `(ADR 0018)` ;
  - l. 57 `(RET-013, ADR 0015)` ;
  - l. 84 et l. 85 `(ADR 0018)` ;
  - l. 103 (RTK) `(ADR 0018)` ;
  - `roles/implementeur.md:11` `(ADR 0018)`.

  Relancer ensuite le test de taille.

### 2. Des règles du point 3 absentes ou sans référence dans le profil qui les applique

- **Fichiers** : `roles/coordinateur.md:5`, `:17`, `:18` ; `roles/orchestrateur-tache.md:14` ; `process/README.md:39`.
- **Exigence violée** : le critère de fin, tel que le brief le reprend : « chaque règle du point 3 dans le process ET dans le profil du rôle qui l'applique, avec sa référence RET ou FR ».
- **Constat** :
  - *niveaux* (FR-049) : le coordinateur choisit le déroulé d'une tâche (*standard* ou *léger*), mais son profil ne dit pas d'où vient le niveau : la fiche, ou la montée motivée dans l'issue. FR-049 n'y figure pas ;
  - *plafonds* (FR-051) : `coordinateur.md:17` (« sous les plafonds ») et `orchestrateur-tache.md:14` (« Jamais plus d'agents à la fois que le brief ne le permet ») n'ont pas de référence. Le *léger* (`coordinateur.md:18`), où le coordinateur lance lui-même les rôles, ne dit pas qu'il les lance par le script, qui compte les agents ;
  - *seuil « assez bon »* : cité sans FR-050 dans `coordinateur.md:18` ;
  - *ADR 0017* (lancement par Orca, rien d'indispensable en dossier temporaire) : `process/README.md:39` et `coordinateur.md:5` n'ont pas de référence (ADR 0017, NFR-013).
- **Scénario d'échec** : au niveau *léger* de jam, une issue motive une montée en *standard*, comme l'a fait K1-2 dans `cadrage-kit-issues.md`. Le coordinateur suit son profil : le *léger* y est décrit sans dire que l'issue peut fixer un autre niveau. Il conduit donc la tâche lui-même, avec un seul relecteur. Autre cas : il lance l'implémenteur par `orca terminal create`, comme avant #23, sans passer par le script qui compte les agents en cours, et dépasse le plafond de 3 de jam. À la recette, la vérification « chaque règle du point 3 dans le profil, avec sa référence » échoue sur ces lignes.
- **Correction attendue** :
  - `coordinateur.md` : en tête des règles, ajouter « Niveau de la tâche : celui de la fiche, ou celui que motive l'issue (FR-049). » ;
  - l. 17 : « sous les plafonds (FR-051) » ;
  - l. 18 : « il lance par le script de lancement l'implémenteur (ou le rédacteur)… (seuil « assez bon », FR-050) » ;
  - l. 5 : `(ADR 0017)` ;
  - `orchestrateur-tache.md:14` : « … que le brief ne le permet (FR-051) » ;
  - `process/README.md:39` : `(ADR 0017, NFR-013)`.

### 3. Rien ne fait passer l'ADR 0018 à « acceptée », ni RET-017 et RET-018 à « appliqué »

- **Fichiers** : `roles/redacteur.md:16` ; `docs/decisions/0018-process-elague.md:3` et `:94` ; `docs/decisions/README.md:24` ; `docs/specs/RETOURS.md:241` et `:252`.
- **Exigence violée** : la règle du rédacteur (une ADR passe à « acceptée » au feu vert, avec ses mentions dans le statut des ADR touchées), et l'ADR 0018 elle-même (l. 94 : « À l'acceptation de cette ADR, le statut de l'ADR 0016… 0017… 0013 mentionne… »).
- **Constat** : la règle ne prévoit le passage qu'« après le feu vert de cadrage ». L'ADR 0018 naît dans une tâche, sans feu vert de cadrage : ni le plan, ni le process, ni un profil ne dit quand elle passe à « acceptée ». Les retours RET-017 et RET-018 sont dans le même cas (« en application »).
- **Scénario d'échec** : #23 est mergée avec l'ADR 0018 « Proposée » dans l'index. Le statut de l'ADR 0013 ne dit pas « précisée (0018) ». Or sa décision « [l'orchestrateur de tâche] a les mêmes interdits d'écriture que le coordinateur » (l. 51) contredit alors, sans trace, `roles/orchestrateur-tache.md:7`, qui l'autorise à écrire `docs/plans/<tâche>-retours.md`. Les décisions de Q-058, Q-027 et des plafonds reposent sur une ADR restée « proposée ».
- **Correction attendue** :
  - pour #23 : après le feu vert recette et avant le commit, un rédacteur passe l'ADR 0018 à « acceptée (feu vert recette du … ) », reporte les trois mentions de la l. 94 dans le statut des ADR 0013, 0016 et 0017, met à jour l'index et passe RET-017 et RET-018 à « appliqué » ;
  - pour la suite : `roles/redacteur.md:16` devient « Après le feu vert de cadrage, ou le feu vert recette d'une tâche qui en écrit une, … », avec une ligne dans le tableau de l'ADR 0018 (NFR-016 ; friction vécue ici).

## Suggestions

- **S1** `docs/decisions/0013-orchestration-deux-niveaux.md:37` : le lien est juste, mais le texte renvoie à la « table « Signalement d'attente » », qui n'existe plus. La remplacer par « Carte, feux verts et veille ». C'est un changement de lien, permis.
- **S2** `roles/orchestrateur-tache.md:7` et `docs/decisions/0018-process-elague.md:28` : la note de suivi « n'est pas un livrable », mais elle est présentée comme la « seule exception à son interdit d'écrire un livrable ». Écrire plutôt « seule exception à son interdit d'écrire dans le repo ».
- **S3** `process/fiche-projet.md:13` (« En production, le feu vert merge se relaie sous sa forme complète »), `docs/methode.md:14` (« donc ») et `AGENTS.md`, règle 6 (« celui de jam compris (fiche) ») : ces phrases laissent croire qu'un merge hors production se relaie par un « ok ». FR-053 ne l'allège pas, et tout merge est une action du coordinateur, confirmée dans son terminal (process, l. 74). Retirer la phrase du gabarit et simplifier les deux autres.
- **S4** Retraits muets (NFR-016), absents de la liste « Retirés sans remplacement » de l'ADR 0018 :
  - dans le profil du relecteur, la vérification « priorité et étape justifiées » d'un cadrage ;
  - dans celui du coordinateur, « il n'entre dans le détail d'une tâche que si le mainteneur le demande » ;
  - le relecteur n'écrit plus que son rapport exact, au lieu de tout `*-relecture*.md` : cela retire une limite de l'ancien process.

  Les ajouter à cette liste ou au tableau.
- **S5** `roles/coordinateur.md:9` : la garde accepte toujours « l'installation d'un hook relu » (`hooks/guard_coordinator.py`, message de refus). Le profil ne la cite plus. La citer, ou noter son retrait (Q-056) dans l'ADR 0018.
- **S6** `docs/specs/01-REQUIREMENTS.md:14` (FR-045) : la liste des champs de la fiche n'a pas « À lire avant toute tâche » ni « Règles propres », que le gabarit et le glossaire ajoutent. Et FR-050 (l. 19) parle encore de « cosmétique ». Les aligner sur le glossaire et l'ADR 0018.
- **S7** `roles/redacteur.md:21` : au niveau *léger*, une montée de niveau ne se motive que dans l'issue (pas de plan). Ajouter aux brouillons d'issues « le niveau, s'il monte, motivé (FR-049) ».
- **S8** `AGENTS.md:22` : « il conduit lui-même chaque tâche » est faux pour une tâche montée en *standard* (`docs/methode.md:13`). Écrire « chaque tâche de niveau *léger* ».
- **S9** `process/README.md:20` : le *léger* dit « committe et ouvre la PR » ; le profil du coordinateur (l. 18) dit « committe, pousse et ouvre la PR ». Aligner.
- **S10** `docs/concepts/veille-et-mesure.md:42` : au niveau *léger* de jam, le mainteneur recette dans une session qu'il ouvre lui-même dans le worktree (`docs/methode.md:13`). La limite « perd son premier message » y est donc systématique, pas occasionnelle. Le dire dans la fiche concept.

RELECTURE : CORRECTIONS (3)
