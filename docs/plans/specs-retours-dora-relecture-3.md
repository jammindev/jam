# Relecture — cadrage `specs-retours-dora`, tour 3

> Relecteur seul, contexte neuf. Objet : changements non commités du worktree (10 fichiers modifiés, 6 nouveaux hors relectures). Les relectures des tours précédents n'ont pas été lues.
> Décisions du mainteneur prises en compte : pas d'échéance sur les milestones ; RET-007 validé (instances Claude neuves, diversité de modèles en E2) ; les trois compléments de RET-002 validés (indicateurs agents au S4, écran en première coupe, écran pour `house` et pour jam).

## Synthèse

- **Cohérence** : numéros FR (036, 037, 038), NFR, ADR (0011, 0012) et RET (001 à 007) uniques et bien référencés. Restent des écarts avec des fichiers non touchés (`02-ARCHITECTURE.md`, `OPEN-QUESTIONS.md`) et quelques trous de glossaire.
- **Fidélité** : les sept retours sont traduits, ainsi que les décisions du mainteneur. En revanche, un bloc de changements (hook RTK, durcissement des profils) ne se rattache à aucun retour.
- **Repo public** : rien trouvé. Pas de secret, pas d'adresse, pas de chemin machine. Le hook du coordinateur est décrit sans chemin.
- **Permissions** : aucun profil de rôle n'ouvre commit, push ou `gh` en écriture. La variante `gh` du relecteur n'utilise que des formes exactes et en lecture. Le coordinateur est la seule exception, et elle est tracée (ADR 0012).
- **Brouillon d'issues** : découpage du S2 en six petits lots, critères de fin vérifiables pour la plupart. Deux issues sont à préciser (S2-d, S2-e).

## Bloquant

Aucun.

## À corriger

### C1. L'architecture contredit RET-001 et ignore la mesure
- **Fichier** : `docs/specs/02-ARCHITECTURE.md:37` (et `:30`, `:35`)
- **Constat** : la ligne « Coordinateur » dit « Agent conversationnel : cadrage, issues, pilotage de l'UI ». Or, d'après RET-001 et FR-040, le coordinateur orchestre et ne produit aucune issue : c'est le rédacteur qui les rédige. Par ailleurs, l'écran « Métriques » (FR-037) n'apparaît nulle part dans les composants, pas plus que les données GitHub qu'il exige (labels `incident`, exécutions de workflow).
- **Correction attendue** : ligne 37, par exemple « Agent conversationnel : orchestre le cadrage (rédacteur → relecteur → feu vert), arbitre, pilote l'UI (FR-040) ». Ligne 30, ajouter « écran Métriques (FR-037) ». Ligne 35, ajouter « lecture des labels et des exécutions de workflow pour les métriques (ADR 0011) ».

### C2. Glossaire : le coordinateur n'est pas instancié avec un contexte neuf
- **Fichier** : `docs/specs/GLOSSARY.md:13`
- **Constat** : la définition de « Rôle » dit « instancié à la demande avec un contexte neuf : … et le coordinateur qui les orchestre ». Or le coordinateur est une session conversationnelle qui dure (`process/README.md:8`, `roles/coordinateur.md:10`). La phrase est donc fausse pour lui.
- **Correction attendue** : par exemple « Profil d'agent (prompt, outils, permissions). Les rôles du pipeline et du cadrage (…) sont instanciés à la demande avec un contexte neuf ; le coordinateur, qui les orchestre, est une session conversationnelle. »

### C3. « Coordinateur dans jam » : deux réponses différentes
- **Fichiers** : `docs/specs/GLOSSARY.md:17` ; `docs/process/README.md:8` ; `docs/decisions/0012-coordinateur-role-garde-fous-hook.md:22`
- **Constat** : selon le glossaire, le coordinateur arrive dans jam « après E0 ». Selon le process et l'ADR 0012, « dans jam, c'est le cœur qui tiendra ce rôle », donc dès E0. Les deux sont vrais pour des parties différentes du rôle (l'orchestration et le commit d'un côté, la conversation de cadrage de l'autre), mais un lecteur qui ne code pas ne peut pas le deviner.
- **Correction attendue** : dans le glossaire, distinguer les deux parties : « dans jam, l'orchestration, le commit et le merge sont tenus par le cœur dès E0 ; le coordinateur conversationnel (cadrage, FR-040) arrive après E0 ».

### C4. Le terme « cadrage » n'est pas défini
- **Fichiers** : `docs/specs/GLOSSARY.md` (terme absent) ; utilisé dans `process/README.md:18-28`, `04-ROADMAP.md:39`, `roles/redacteur.md:23`, `roles/relecteur.md:29`, et dans les feux verts.
- **Constat** : le cadrage est devenu un élément du process, avec son worktree `cadrage-<slug>`, son feu vert et ses brouillons d'issues. Le terme n'est pourtant pas dans le glossaire, alors que la règle du rédacteur (`redacteur.md:19`) exige d'y ajouter tout terme nouveau.
- **Correction attendue** : ajouter « Cadrage | Travail qui produit ou modifie specs, ADR et issues avant qu'une tâche n'entre dans le pipeline : rédacteur → relecteur → feu vert de cadrage. Il n'a pas d'issue, son worktree s'appelle `cadrage-<slug>`. | Provisoire ».

### C5. Q-013 toujours « ouvert » alors que le repo existe
- **Fichier** : `docs/specs/OPEN-QUESTIONS.md:17`
- **Constat** : Q-013 (« Créer le repo public `jammindev/jam` ») est encore « Ouvert ». Or le process retire tous les replis « si le repo distant existe » (`process/README.md:34`, `:42`, `:44`), renvoie aux milestones de `jammindev/jam` (`:15`, `04-ROADMAP.md:39`), et RET-001 parle des issues #1 à #4 déjà publiées.
- **Correction attendue** : passer Q-013 à « **Tranché** : repo créé, milestones S1 à S4 et issues publiées (voir RET-001) ».

### C6. L'ADR 0011 tranche aussi RET-006 sans le dire
- **Fichiers** : `docs/decisions/0011-pratiques-et-metriques-dora.md:5` et `:39` ; `docs/decisions/0008-boucle-exterieure-pipeline.md:45`
- **Constat** : l'ADR 0011 pose (ligne 39) que la boucle de relecture a pour critère le verdict des relecteurs. Cela précise l'ADR 0008, qui n'autorise de boucles automatiques que « sur des critères objectifs : tests verts, CI verte ». RET-006 cite bien l'ADR 0011 dans son impact, mais l'en-tête de l'ADR ne mentionne que RET-002. Le mainteneur a tranché que l'ADR 0008 n'est pas modifiée : il faut donc que la nouvelle ADR porte la précision de façon visible, puisqu'une décision actée ne se contourne pas.
- **Correction attendue** : ligne 5, écrire « Tranche : RET-002, RET-006 ». Ligne 39, ajouter « Cela précise la règle des critères objectifs de l'ADR 0008, qui reste vraie pour les boucles de code. »

### C7. Le passage d'un retour à « appliqué » n'a pas d'acteur
- **Fichiers** : `docs/specs/RETOURS.md:5` ; `docs/process/README.md:28`
- **Constat** : le statut « appliqué » exige « relu, feu vert donné, committé ». Mais le commit est fait par le coordinateur, qui ne peut écrire aucun fichier (RET-001, ADR 0012), après le dernier passage du rédacteur. Personne ne peut donc passer un retour à « appliqué » sans un commit supplémentaire. De plus, l'étape 4 du process ne mentionne que le passage des ADR à « acceptée », pas celui des RET.
- **Correction attendue** : redéfinir « appliqué » par « relu, feu vert de cadrage donné », sans « committé ». À l'étape 4 du process, écrire : « Le rédacteur passe alors les ADR concernées à « acceptée » et les retours concernés à « appliqué ». »

### C8. Des changements sans retour d'origine : hook RTK et durcissement des profils
- **Fichiers** : `docs/process/README.md:64-72` (section « Hook RTK ») et `:107-109` ; formes `rtk …`, `Edit(.claude/**)` et `git -C` dans `roles/implementeur.md:9-11`, `roles/planificateur.md:9-11`, `roles/relecteur.md:7-9` et `roles/redacteur.md:9`
- **Constat** : ces changements ne se rattachent à aucun des retours RET-001 à RET-007. Le process (`:3`) veut pourtant que chaque friction soit notée dans `OPEN-QUESTIONS.md`, et RET-003 que chaque remarque du mainteneur soit consignée dans `RETOURS.md`. Aucune entrée ne les trace. Le passage de l'implémenteur de `acceptEdits` à `dontAsk` se justifie, lui, par la mise en conformité avec l'ADR 0009 (`0009:14`, refus sans invite), mais rien ne le dit non plus.
- **Correction attendue** : tracer l'origine de ces changements. Si c'est une remarque du mainteneur, créer un RET-008. Si c'est une friction constatée, ajouter une question Q-014 (« Hook RTK et listes de permissions : doubler chaque règle »), statut « tranché par le process ». Pour le passage à `dontAsk`, une phrase suffit dans `implementeur.md` : « conformité à l'ADR 0009 ». Faute de quoi, sortir ces changements de ce cadrage.

### C9. Le planificateur peut réécrire les rapports de relecture
- **Fichier** : `docs/process/roles/planificateur.md:9` (et `:5`)
- **Constat** : `Edit(docs/plans/**)` lui permet d'écrire n'importe quel fichier de `docs/plans/` : rapports de relecture, brouillons d'issues, recettes. Or son profil dit (ligne 5) que « le seul fichier qu'il peut écrire est `docs/plans/<tâche>.md` ». Le rédacteur, lui, a la protection explicite (`redacteur.md:9`). L'indépendance de la relecture n'est donc pas garantie de la même façon pour les deux rôles.
- **Correction attendue** : ajouter `"Edit(docs/plans/*-relecture*.md)"` dans le `--disallowedTools` du planificateur, et de même pour `*-issues.md` et `*-recette.md`. Ou bien corriger la ligne 5 pour qu'elle décrive ce que la commande permet réellement.

### C10. Brouillon S2-d : l'issue tranche à l'avance Q-012, et le profil serait introuvable
- **Fichier** : `docs/plans/specs-retours-dora-issues.md:98` et `:102`
- **Constat** : « Le backend construit la ligne de commande d'un rôle à partir de son profil de permissions (`docs/process/roles/<rôle>.md`) » pose trois problèmes :
  1. l'emplacement et le format des profils sont l'objet de Q-012 (`OPEN-QUESTIONS.md:16`), « à réviser en E0 (S2) » : l'issue tranche la question à l'avance ;
  2. le rôle tourne dans un worktree de `house`, où `docs/process/roles/` n'existe pas : ces profils sont ceux de jam ;
  3. ces fichiers sont du Markdown destiné à Orca, et contiennent les formes `rtk` propres au poste.
- **Correction attendue** : écrire « à partir du profil de rôle, dont l'emplacement et le format sont tranchés dans le plan (Q-012) ». Ajouter Q-012 aux « Exigences ». Ajouter au critère de fin : « un test vérifie que la ligne de commande ne contient jamais `bypassPermissions` (NFR-011) ».

### C11. Brouillon S2-e et FR-038 : « process suivi » ne se vérifie pas
- **Fichiers** : `docs/plans/specs-retours-dora-issues.md:113` et `:117` ; `docs/specs/01-REQUIREMENTS.md:15`
- **Constat** : le critère « le brief contient ces quatre éléments » ne peut pas être vérifié pour le quatrième, « le process suivi », dont le contenu n'est défini nulle part. Les trois autres éléments sont concrets (worktree, issue, étape).
- **Correction attendue** : préciser dans FR-038 et dans S2-e ce que contient « le process suivi », par exemple « la liste des étapes du pipeline, la place de l'étape en cours et les feux verts qui suivent ». Le critère de fin reprend ces éléments.

## Suggestions

- **S1.** `specs-retours-dora-issues.md:87` (S2-c) : l'essai réel lance un rôle avant que les profils existent (S2-d). Préciser qu'il tourne en `dontAsk` avec des outils en lecture seule, sans mode sans permission (ADR 0009), et nommer le repo de test.
- **S2.** `specs-retours-dora-issues.md:64` (S2-b) : la première mise en place de SQLite (ADR 0010 : `node:sqlite`, migrations numérotées) est implicite, alors qu'elle peut être la plus grosse partie de l'issue. La rendre explicite dans le périmètre.
- **S3.** `process/README.md:101` : dans Orca, rien ne mesure le « budget de l'étape ». Préciser comment le coordinateur l'applique aujourd'hui (par exemple, l'alerte de quota du mainteneur), ou dire que seule l'absence de progrès s'applique dans Orca.
- **S4.** `process/README.md:76` et `:81`, FR-022 (`01-REQUIREMENTS.md:14`) : « code applicatif » décide du nombre de relecteurs mais n'est pas défini (tests ? configuration ? CI ?). L'ajouter au glossaire.
- **S5.** La mention « hook en cours de mise en place » est répétée dans six endroits (`process/README.md:8` et `:103`, `roles/coordinateur.md:8`, `0012:22`, `RETOURS.md:54`, `specs-retours-dora-issues.md:140`). Elle deviendra fausse partout à la fois. Suivre le sujet dans une seule question de `OPEN-QUESTIONS.md`, et y renvoyer.
- **S6.** `0012:27` dit « `orca`, `git`, `gh`, avec l'accord du mainteneur », alors que `roles/coordinateur.md:7` et `:14` réservent l'accord au commit, au push, à la publication et au merge, ou aux commandes hors des réglages du poste. Aligner la table de l'ADR sur le profil.
- **S7.** FR-028 (`01-REQUIREMENTS.md:21`), qui décrit la configuration par repo, ne cite pas le workflow de déploiement qu'exigent l'ADR 0011 (`:45`, `:84`) et FR-037. Ajouter « et, si le repo est déployé, le workflow de déploiement (ADR 0011) ».
- **S8.** `process/README.md:62` : le brief contient « la tâche (numéro d'issue) », mais un cadrage n'a pas d'issue. Écrire « (numéro d'issue, ou `cadrage-<slug>`) ».
- **S9.** `roles/relecteur.md:9` : `pnpm test*` et `npx vitest*` exécutent le script de test du repo, que l'implémenteur a pu modifier. Le chemin vers n'importe quelle commande, `git push` compris, reste donc ouvert pour le relecteur aussi. Le dire dans « Ce qu'Orca ne permet pas » (`process/README.md:108`), qui ne le dit aujourd'hui que pour l'implémenteur.
- **S10.** `roles/implementeur.md:11` : `Edit(./**)` permet à l'implémenteur de modifier `AGENTS.md` et `docs/process/roles/`, que liront les rôles lancés après lui. C'est le même raisonnement que pour `.claude/`, avec un risque moindre. Au minimum, demander à l'axe B de la relecture de signaler tout changement de ces fichiers.

RELECTURE : CORRECTIONS (11)
