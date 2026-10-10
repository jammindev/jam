# Relecture du cadrage `cadrage-s2`, tour 4 (relecteur seul, deux axes)

Objet relu : `git diff` (4 fichiers : `docs/plans/specs-retours-dora-issues.md`, `docs/process/roles/recetteur.md`, `docs/references/orca.md`, `docs/specs/OPEN-QUESTIONS.md`) et le nouveau fichier `docs/plans/cadrage-s2-issues.md`. Les relectures des tours précédents n'ont pas été lues.

## Vérifications faites

| Point | Résultat |
|---|---|
| Carte d'Orca (§0), 4 lignes ajoutées | Les 7 fichiers cités existent au tag `v1.4.218` (clone vérifié : `refs/tags/v1.4.218` dans `packed-refs`). Chaque annotation correspond au code : `listIssues` filtre les PR (`'pull_request' in d`) et renvoie `{ items, error }` au lieu d'une liste vide ; `classifyListIssuesError` est défini dans `gh-error-classification.ts` (réexporté par `gh-utils.ts`) ; `auth-diagnose.ts` traite `gh` absent (`ENOENT`) et parse `gh auth status` ; `slugifyForWorkspaceName` remplace tout caractère hors `[a-z0-9._-]` par un tiret, sans normalisation NFD, donc une lettre accentuée devient un tiret ; `sanitizeWorktreeName` garde `\p{L}\p{N}` et lève une erreur sur un nom vide, `.` ou `..` ; la spec `claude` construit `-p --output-format text … --permission-mode plan` avec `promptDelivery: 'stdin'` ; `source-control-local-process.ts` a un délai maximal et un `SIGKILL` de l'enfant ; `claudeResultOutcome` décide sur `is_error`, jamais sur le sous-type. |
| Chemin du clone dans le repo | Absent du diff et de `docs/` (recherche sur les motifs du dossier temporaire du poste et du clone de référence). |
| État GitHub (`gh` en lecture) | Milestone #1 `E0-S1 Squelette` fermé ; #2, #3 ouverts avec leurs titres ; #4 encore titré `E0-S4 Merge et parallélisme` ; descriptions en ligne plus courtes que l'ancien brouillon, aucune échéance. Issues #2, #3, #4 ouvertes, #2 au label `enhancement` (le label existe). Les affirmations du §1 et du §2 sont exactes. |
| Faits sur le code de jam | L'app passe `--db <userData>/jam.db` au cœur (`apps/desktop/src/main/index.ts:43`, `core-process.ts:25`) ; le cœur en CLI suit `JAM_DATA_DIR` (`packages/core/src/paths.ts`) et crée le dossier (`database.ts:14`) ; il refuse une base de version plus récente (`database.ts:46`) ; l'app envoie `SIGKILL` au bout de 2 s (`core-process.ts:39`) ; `pnpm check` et `pnpm core:ping` existent. Les affirmations de S2-a, S2-g et Q-050 sont exactes. |
| Numérotation | Q-052 et Q-053 suivent Q-051 ; aucun RET ni ADR nouveau. |
| Repo public | Aucun chemin propre au poste, aucune donnée personnelle, aucune mention d'assistant (les occurrences de « Claude Code » désignent le backend d'agent). |
| Publication (§6) | Ordre cohérent (milestones avant les commentaires qui y renvoient ; création puis substitution) ; `-F description=@<fichier>`, `--body-file`, `--reason 'not planned'` sont des formes valides de `gh` ; aucun corps ne contient « S2- » hors renvois aux lettres. |
| Conduite et Orca par issue | Chaque issue a son bloc « Orca » avec la liste noire (RET-011) ; la conduite par un orchestrateur de tâche est rappelée (ADR 0013, 0015). Chaque recette part d'une installation neuve, check-list du mainteneur d'abord (RET-010). |

## Bloquant

Aucun.

## À corriger

1. **Les lettres S2-x ne restent pas « dans ce brouillon »** — `docs/plans/cadrage-s2-issues.md:7` ; `docs/specs/OPEN-QUESTIONS.md:19` (Q-015), `:31` (Q-027), `:50` (Q-052) ; `docs/process/roles/recetteur.md:16`.
   La ligne 7 affirme que les lettres S2-a à S2-h n'existent que dans le brouillon et sont remplacées par les numéros à la publication. Or la rédaction les inscrit dans des docs durables : `OPEN-QUESTIONS.md` (Q-012, Q-015, Q-027, Q-050, Q-052, Q-053) et le profil du recetteur. La substitution du §6 ne touche que les corps d'issues : sur `main`, ces renvois resteront des lettres, et rien n'enregistre la correspondance lettre → numéro. Q-012, Q-053 et le profil du recetteur donnent le titre de l'issue, qui permet de la retrouver sur GitHub ; Q-015, Q-027 et Q-052 ne le donnent pas.
   **Correction attendue** : reformuler la ligne 7 (les lettres servent aussi de renvoi dans `OPEN-QUESTIONS.md` et le profil du recetteur, où l'issue se retrouve par son titre publié) et ajouter le titre entre guillemets dans Q-015, Q-027 et Q-052, comme dans Q-012.

2. **S2-b manque à Q-053** — `docs/specs/OPEN-QUESTIONS.md:51` ; `docs/plans/cadrage-s2-issues.md:117` et `:291`.
   Le critère principal de S2-b (« Cmd+K → Choisir une issue liste les issues ouvertes », ligne 115) passe par la palette, et la recette de S2-b (ligne 117) le laisse au mainteneur. L'agent ne vérifie donc que l'installation et le lancement. C'est exactement le cas que décrit Q-053, qui ne cite pourtant que S2-c, S2-g et S2-h, comme la ligne 291 du §5.
   **Correction attendue** : ajouter S2-b (« lister les issues ») à Q-053 et à la ligne 291, et renvoyer à Q-053 dans la recette de S2-b, comme le font S2-c, S2-g et S2-h.

3. **Description du milestone S4 : la fiche concept ne suit pas la roadmap** — `docs/plans/cadrage-s2-issues.md:29`.
   `04-ROADMAP.md:46` dit que la seconde phrase du critère, « comme la fiche « métriques DORA » », tombe si l'écran est coupé. Le texte à publier fait tomber le second critère mais termine sans condition par « Fiche concept : métriques DORA. » Or la ligne 20 annonce des textes « alignés sur `04-ROADMAP.md` ».
   **Correction attendue** : par exemple « Ce second critère, comme la fiche concept métriques DORA, tombe si l'écran est coupé, et se limite à `house` si le multi-repo est coupé. »

4. **S2-h : le suivi de l'étape en cours n'a pas de critère** — `docs/plans/cadrage-s2-issues.md:264`, critère de fin lignes 266-271.
   Le périmètre exige que la vue suive l'étape en cours sans relancer l'app (Q-015, Q-017). Aucun critère ne le vérifie : « le plan s'affiche » peut être satisfait par une vue qu'on rouvre à la main, ou par une commande qui bloque jusqu'à la fin, comme la commande de S2-g. Le relecteur d'un cadrage vérifie que chaque exigence est vérifiable.
   **Correction attendue** : ajouter un critère, par exemple « Vue de la tâche ouverte pendant l'étape : elle passe d'« en cours » à « terminée » et affiche le plan sans être rouverte ni relancée. » Préciser s'il revient à la check-list du mainteneur (Q-053).

## Suggestions

1. **Profil du recetteur, `JAM_DATA_DIR`** (`docs/process/roles/recetteur.md:16`, commande ligne 9) : la variable n'apparaît que dans une puce, pas dans la commande qu'on copie, et elle dépend d'un jugement de l'orchestrateur de tâche (« une tâche qui écrit dans la base »). La mettre toujours, en tête de la commande (`JAM_DATA_DIR=<dossier de recette>/data claude …`), ne coûte rien et ôte ce jugement.
2. **S2-b, filtrage des PR** (`docs/plans/cadrage-s2-issues.md:110`) : « Les pull requests n'y figurent pas » n'a pas de test. Si le plan lit les issues par l'API REST, comme Orca (la carte le signale), un test avec une PR dans la sortie simulée de `gh` le prouverait ; si le plan choisit `gh issue list`, une ligne du plan suffit.
3. **S2-c, slug vide** (`docs/plans/cadrage-s2-issues.md:142`) : ajouter le cas limite d'un titre dont le slug serait vide (titre fait seulement d'emoji ou de caractères non latins). La carte montre qu'Orca le traite (`sanitizeWorktreeName` refuse un nom vide, `getLinkedWorkItemWorkspaceName` renvoie `null`). Le worktree s'appellerait alors `<n>` ou `<n>-`.
4. **S2-g, test d'arrêt** (`docs/plans/cadrage-s2-issues.md:246`) : « entrée standard fermée, puis signal d'arrêt » peut se lire comme un seul test qui enchaîne les deux. Écrire « deux cas : entrée standard fermée ; signal d'arrêt ». Et comme l'app envoie `SIGKILL` au cœur au bout de 2 s (`core-process.ts:39`), exiger que l'enfant soit arrêté dans ce délai : sinon, un arrêt normal depuis l'app finit en cœur tué, et l'agent orphelin hors périmètre devient le cas courant.
5. **Q-052, portée** (`docs/specs/OPEN-QUESTIONS.md:50` contre `docs/plans/cadrage-s2-issues.md:290`) : Q-052 dit « chaque recette prend une issue qui n'a servi à aucune recette précédente », le §5 limite la règle aux check-lists de S2-g et S2-h, et S2-c ne la mentionne pas. S2-c ne lance pas Claude Code, la règle n'y sert donc à rien : aligner Q-052 sur le §5.
6. **Q-043, premier plan** (`docs/plans/cadrage-s2-issues.md:285`) : le planificateur de S2-a reçoit le clone mais n'a aucune entrée de la carte à lire (ligne 101) ; il ne l'ouvrira peut-être pas. S2-b est le premier plan qui doit le lire. Écrire « au premier plan qui lit le clone » plutôt que « celui de S2-a ».

RELECTURE : CORRECTIONS (4)
