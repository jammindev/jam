# Relecture — cadrage `cadrage-s2`, tour 5

> Relecteur seul (deux axes), contexte neuf. Objet : `git diff` (quatre fichiers modifiés) et le nouveau fichier `docs/plans/cadrage-s2-issues.md`. Les rapports des tours précédents n'ont pas été lus (profil du relecteur, « Indépendance ») ; seul un motif de chemin y a été cherché, sans lecture du contenu, pour la vérification « aucun chemin propre au poste dans le repo » demandée par le brief.

## Vérifications faites

- **Carte d'Orca** (`docs/references/orca.md`, lignes 38 et 50 à 53) : les huit fichiers ajoutés existent au tag `v1.4.218` dans le clone de référence, et chaque description est exacte :
  - `src/main/github/issues.ts` : `listIssues` filtre les entrées qui portent `pull_request` et renvoie `{ items: [], error }` sur échec, distinct d'une liste vide ; `gh-error-classification.ts` exporte `classifyListIssuesError` ; `auth-diagnose.ts` rend `ghAvailable` et les comptes connectés ;
  - `src/shared/workspace-name.ts` : `slugifyForWorkspaceName` remplace tout caractère hors `[a-z0-9._-]` par un tiret, donc une lettre accentuée ; `getLinkedWorkItemWorkspaceName` existe ; `src/main/ipc/worktree-logic.ts` : `sanitizeWorktreeName` garde `\p{L}\p{N}` et lève une erreur sur un nom vide, `.` ou `..` ;
  - `src/shared/commit-message-agent-specs-primary.ts` : `claude -p --output-format text --permission-mode plan`, prompt sur l'entrée standard (`promptDelivery: 'stdin'`) ; `src/main/text-generation/source-control-local-process.ts` : délai maximal et arrêt du processus enfant (`SIGKILL`) ;
  - `src/main/claude/claude-result-outcome.ts` : `is_error` décide, pas le sous-type.
  - Les entrées de la carte citées par les corps d'issues (`preamble.ts`, `claude-stream-json-frame-schema.ts`, `source-control-agent-launch.ts`, `worktree-add.ts`, `gh-utils.ts`) existent aussi au tag.
- **Chemin du clone** : absent de tous les fichiers relus. Voir le constat 1 pour un autre fichier du lot.
- **État GitHub** (`gh api 'repos/jammindev/jam/milestones?state=all'`, `gh issue list --state all`) : conforme au §1 et au §2. Milestone #1 fermé ; #2, #3 et #4 ouverts, sans échéance ; #4 s'appelle encore `E0-S4 Merge et parallélisme` ; les descriptions en ligne sont les anciennes, plus courtes ; les issues #2, #3 et #4 sont ouvertes, avec les titres cités et le label `enhancement` ; #1 et #7 sont fermées.
- **Code cité** : l'app passe `--db <userData>/jam.db` au cœur (`apps/desktop/src/main/index.ts:43`, `core-process.ts:25`) ; le cœur en CLI suit `JAM_DATA_DIR` (`packages/core/src/paths.ts`) ; le cœur refuse une base plus récente que son code (`packages/core/src/db/database.ts:46-50`) ; l'app envoie `SIGKILL` au bout de 2 s (`core-process.ts:39-46`) ; les commandes « Lister les repos » et « Ajouter un repo » existent (`packages/core/src/commands.ts`) ; `pnpm check` existe.
- **Numérotation** : Q-052 et Q-053 suivent Q-051 ; aucun RET ni ADR nouveau. Les trous Q-044 à Q-049 existaient déjà sur `main`.
- **Commandes du §6** : formes correctes (`gh api -X PATCH … -F description=@<fichier>`, `gh issue create --body-file`, `gh issue close --reason 'not planned'`, commentaire posté d'abord faute de `--body-file` sur `close`). Les renvois cités en exemple (S2-b vers S2-c et S2-e, S2-d vers S2-f et S2-g) figurent bien dans les corps.
- **Cohérence** : critères du S2 de `04-ROADMAP.md` tous couverts (S2-c, S2-e, S2-g, S2-h ; fiches worktree et stream-json dans S2-c et S2-f) ; ADR 0009 respectée (`dontAsk`, planificateur sans écriture, ni `bypassPermissions` ni `--dangerously-skip-permissions`) ; ordre et dépendances justifiés (S2-a avant la première migration) ; RET-010 appliqué à chaque recette ; RET-011 (bloc « Orca » et liste noire dans chaque issue) ; ADR 0013 et 0015 (conduite par un orchestrateur de tâche). Vocabulaire du glossaire respecté.
- **Repo public** : aucun chemin propre au poste, aucune donnée personnelle, aucune mention d'assistant dans les fichiers du diff et le brouillon.

## Constats

### Bloquant

Aucun.

### À corriger

1. **`docs/plans/cadrage-s2-relecture-4.md`, ligne 10** : la ligne contient un chemin du dossier temporaire du poste (motif propre à la session, celui du clone de référence ou d'un dossier voisin). Ce fichier non suivi fait partie du lot du cadrage, et les rapports de relecture sont committés (voir `docs/plans/E0-S1-squelette-relecture-A.md`). Il entrerait donc dans le repo public, à l'encontre de la règle 7 d'`AGENTS.md` (NFR-002) et du brief, qui demande que ce chemin n'apparaisse nulle part.
   **Correction attendue** : avant le commit, remplacer ce chemin par un nom générique (`<clone-orca>`, ou « dossier temporaire du poste »). Le rédacteur ne peut pas modifier un rapport de relecture : c'est à l'orchestrateur de tâche de choisir la voie, par exemple relancer le relecteur du tour 4 sur son seul fichier, ou soumettre la retouche au mainteneur.

2. **Q-022 absente du cadrage, alors que le S2 est le premier jalon où jam lance lui-même des sessions de rôle**. Références : `docs/plans/cadrage-s2-issues.md`, lignes 162 (S2-d : les profils de jam n'auront pas les formes `rtk`), 172-174 (questions renvoyées au plan de S2-d), 247 (essai réel de S2-g) et 278-292 (§5).
   Q-022 demande : « Faut-il lancer les sessions de rôle sans le hook RTK ? ». Or le Claude Code lancé par jam sur le poste du mainteneur charge les réglages et les hooks de l'utilisateur (`~/.claude`), comme toute session. Le hook RTK y réécrit `git log` en `rtk git log`, puis la permission porte sur la forme réécrite (process, « Hook RTK du poste du mainteneur »). Un profil de jam sans forme `rtk`, ce que prévoit S2-d ligne 162, verra donc refuser à l'essai réel de S2-g et S2-h les commandes git que l'ADR 0009 donne au planificateur. Le hook de démarrage du poste (RET-004) s'appliquerait aussi et ajouterait au brief un contexte Orca. L'étape se terminerait quand même, et le critère de S2-g serait rempli, mais avec des refus inattendus, et sans que le planificateur ait pu lire l'historique git.
   **Correction attendue** :
   - ajouter Q-022 au tableau du §5, avec son sort : renvoyée au plan de S2-d, ou laissée ouverte avec l'effet attendu à l'essai réel ;
   - dans les « Questions renvoyées au plan » de S2-d, une ligne : les réglages et hooks du poste (hook RTK, Q-022 ; hook de démarrage) s'appliquent au Claude Code lancé par jam. Le plan dit si jam les écarte (par une option de la CLI qui limite les sources de réglages, à vérifier), ajoute les formes `rtk` au profil, ou accepte des refus à l'essai réel ;
   - dans la recette de S2-g (ligne 247), dire ce que la check-list du mainteneur attend sur ce point : par exemple, aucun refus sur `git log/diff/status`, ou des refus attendus et enregistrés.

### Suggestions

3. **`docs/process/roles/recetteur.md`, ligne 16** : « Les commandes du recetteur (`pnpm dev`, `pnpm core:ping`) en héritent ». `pnpm core:ping` lance le cœur avec `--db :memory:` (`packages/core/package.json:13`) : il n'ouvre aucune base et ignore `JAM_DATA_DIR`. La conclusion reste vraie, mais la phrase dit l'inverse du code. Proposer : « `pnpm dev` en hérite (`pnpm core:ping` n'ouvre qu'une base en mémoire) ».

4. **Check-lists de plus de 5 étapes** : le profil du recetteur (`recetteur.md`, ligne 28) limite la check-list du mainteneur à 5 étapes. Les recettes de S2-c, S2-g et S2-h (`cadrage-s2-issues.md`, lignes 143, 247 et 272) en demandent au moins six : installation neuve, lancement avec `JAM_DATA_DIR`, ajout de `house`, choix de l'issue et relevé du worktree, redémarrage ou lancement du planificateur, suppression du worktree et de la branche. Le recetteur peut regrouper des actions dans une étape, mais il recevra deux consignes qui tirent en sens contraire. Proposer, dans le profil, que l'installation neuve et le nettoyage ne comptent pas dans les 5 étapes, ou le dire dans ces trois recettes.

5. **S2-g, ADR 0010** (`cadrage-s2-issues.md`, ligne 238) : l'ADR 0010 dit que l'outil « ne garde que l'identifiant de session de chaque étape, plus un résumé d'événements ». S2-g enregistre aussi la ligne de commande, le brief envoyé et le texte final du résultat (le plan). L'intention de l'ADR est respectée, puisque la transcription détaillée reste celle de Claude Code et que le plan doit survivre au redémarrage (critère du S2). Mais une lecture stricte y verrait un écart. Proposer une demi-phrase dans S2-g : « ce ne sont pas des transcriptions, qui restent celles de Claude Code (ADR 0010) ».

6. **S2-g, arrêt du cœur pendant une étape** (`cadrage-s2-issues.md`, lignes 239-240) : aujourd'hui, à la fermeture de son entrée standard, le cœur répond d'abord à toutes les requêtes en cours avant de sortir (`packages/core/src/server.ts:76-88`). Si « Lancer le planificateur » ne répond qu'à la fin de l'étape, comme le suggère la ligne 239, le cœur attendrait la fin de l'étape, et l'app le tuerait au bout de 2 s, en laissant Claude Code orphelin. Le test de la ligne 246 l'attrapera, mais une ligne dans les « Questions renvoyées au plan » éviterait un aller-retour : la requête répond-elle au lancement ou à la fin de l'étape, et comment la fermeture de l'entrée standard l'interrompt-elle ?

7. **Taille de S2-g** (lignes 228-251) : lancement du processus, lecture du flux, migration, commande de palette, arrêt propre de l'enfant, marquage « interrompue » au démarrage, tests au faux Claude Code et essai réel. C'est le plus gros lot du S2. Une découpe possible : S2-g lance et enregistre l'étape ; une issue suivante traite l'arrêt de l'enfant quand le cœur s'arrête et le marquage « interrompue » (R-02). À trancher par le mainteneur, sans obligation.

8. **Flux de test de S2-f** (`cadrage-s2-issues.md`, lignes 224-226) : au tag `v1.4.218`, Orca a des flux `stream-json` capturés qui contiennent `permission_denials` (`src/main/claude/__fixtures__/claude-adapter-capture-*.jsonl`). Ce sont des exemples réels du format, utiles pour la question « provenance des flux de test ». Ils pourraient figurer dans l'entrée « Fin d'un tour : résultat `stream-json` » de la carte, comme exemples de format, avec la règle habituelle : inspiré, ou repris avec sa licence.

9. **`docs/references/orca.md`, ligne 53** : `claude-result-outcome.ts` distingue aussi une annulation d'un échec, par `terminal_reason` (`aborted_streaming`, `aborted_tools`). C'est utile pour l'état « interrompue » de S2-g. Proposer d'ajouter : « `terminal_reason` sépare une annulation d'un échec ».

10. **Table de correspondance du §3** (`cadrage-s2-issues.md`, ligne 75) : la ligne « S2-c, lecture du flux → S2-f » omet que S2-f reprend aussi le repérage des refus de l'ancienne S2-d (ligne 209 : refus relevés par la lecture du flux). Proposer « S2-c, lecture du flux ; repérage des refus de S2-d → S2-f », et « enregistrement des refus » dans la ligne de S2-g (ligne 76).

RELECTURE : CORRECTIONS (2)
