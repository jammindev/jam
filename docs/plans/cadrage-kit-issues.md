# Brouillons d'issues — cadrage `cadrage-kit`

> Rédigés par le rédacteur. Le coordinateur les publie sur `jammindev/jam` après le feu vert de cadrage, une fois la PR du cadrage mergée (feu vert merge) : leurs renvois vers les docs fonctionnent alors sur `main`.
> Découpage fixé par RET-016 : **trois issues au plus**, pour deux à trois jours de travail ; le kit est ensuite gelé ([ADR 0016](../decisions/0016-kit-de-methode.md)). Aucune date d'échéance sur les milestones (décision du mainteneur).

**Lecture des sections d'issue** : le titre publié est le texte après « K1-x — ». Le corps publié commence à la ligne **Exigences** et va jusqu'à la fin de la section. Les repères K1-1 à K1-3 ne sont pas des numéros GitHub : à la publication, chaque renvoi « K1-x » d'un corps est remplacé par le numéro réel de l'issue, dans une seconde passe une fois les trois issues créées.

## 1. Actions de publication

À faire par le coordinateur, dans cet ordre, après le merge de la PR du cadrage. Le tag `app-electron`, la fermeture des issues #13 à #20 et celle du milestone #2 « E0-S2 Issue → worktree → un rôle » sont déjà faits, hors de ce cadrage.

| # | Action | Pourquoi |
|---|---|---|
| 1 | Fermer le milestone #3 « E0-S3 Pipeline jusqu'à la PR », sans le renommer, en ajoutant en tête de sa description : « Abandonné le 2026-10-11 : jam devient un kit de méthode (ADR 0016). » | Son périmètre (pipeline codé dans le cœur, file « À toi », notifications) n'a rien de commun avec le kit. Le renommer mêlerait l'historique de l'app à celui du kit. |
| 2 | Fermer le milestone #4 « E0-S4 Merge, nettoyage, parallélisme, métriques », sans le renommer, avec la même mention. | Même raison : merge par le cœur, écran des métriques. |
| 3 | Créer le milestone **`K1 Kit de la méthode`**, avec la description ci-dessous. | Jalon du kit (`04-ROADMAP.md`). |
| 4 | Publier K1-1, K1-2 et K1-3 dans l'ordre, milestone `K1 Kit de la méthode`, puis remplacer les renvois « K1-x » par les numéros réels. | — |

**Description du milestone K1** :
> Le kit de la méthode : un plugin Claude Code minimal, installé sur le poste de travail, puis gelé (ADR 0016). Trois issues, deux à trois jours de travail. Fini quand : le repo ne contient plus le code de l'app ; le plugin s'installe depuis le repo, et ses hooks et scripts passent leurs tests en CI ; le process et les profils sont génériques et tiennent sous leur plafond de taille ; jam a sa fiche `docs/methode.md` ; le `README.md` est la page publique, avec le temps du mainteneur mesuré sur K1-1 et K1-2 ; la fiche concept « plugin Claude Code et hooks comme garde-fous » est écrite.

## 2. Ordre, niveaux et recette

| Issue | Dépend de | Niveau | Code (hooks, scripts) |
|---|---|---|---|
| K1-1 — le repo devient le kit | — | *standard* | Oui |
| K1-2 — process élagué | K1-1 | *standard* | Un peu (hook de reprise) |
| K1-3 — page publique | K1-2 | *léger* | Non |

**Ordre** : strictement K1-1, K1-2, K1-3, chacune lancée après le merge de la précédente. Les niveaux n'existent qu'une fois K1-2 mergée : K1-1 et K1-2 suivent le déroulé actuel, avec orchestrateur de tâche ; K1-3 suit le niveau *léger* que la fiche de jam fixe (ADR 0016).

**Commandes des rôles pour K1-1 et K1-2** : les profils de `docs/process/roles/` sont ceux de l'app. Ce cadrage y ajoute, comme passages contredits par l'ADR 0016, les seules formes dont ces tâches ont besoin : `python3 -m unittest` pour l'implémenteur, le relecteur et le recetteur ; pour l'implémenteur, le retrait des fichiers de l'app (K1-1) et le déplacement de `docs/process/` vers `process/` et `roles/` (K1-2) ; le chargement du plugin du worktree pour la seule session du recetteur. Pour K1-1, l'orchestrateur de tâche donne en plus au planificateur et à l'implémenteur le chemin du dossier des hooks du poste de travail, dans le brief seulement, jamais dans le repo, et ajoute `--add-dir <dossier des hooks du poste>` à leur commande : ils le lisent, l'implémenteur n'y écrit pas (`Edit(./**)` ne le couvre pas). Seul le poste de travail est inventorié ; les autres postes n'ont pas d'agent pour le faire. Entre le merge de K1-1 et celui de K1-2, les commandes `pnpm` des profils ne servent plus : seule K1-2 tourne dans cet intervalle, avec ces formes. K1-2 réécrit ensuite les commandes pour le kit.

**Recette sans app** (RET-010) : la recette d'une tâche du kit part d'une **installation neuve du plugin**, depuis le worktree de la tâche, pour la seule session de recette (`claude --plugin-dir <chemin du worktree>`, à vérifier au plan de K1-1) : l'installation du poste n'est pas touchée. Elle déroule d'abord la check-list du mainteneur, puis les tests (`python3 -m unittest`). Ce que les commandes du recetteur ne permettent pas (session lancée avec `JAM_ROLE`, `git commit`, carte Orca, lancement d'un script ou d'une session `claude`) est noté « non reproduit » dans son rapport, sur le modèle de la règle « Clavier » de son profil : il le couvre par les tests, et seul le mainteneur le déroule.

**Mesure** (RET-016) : le corps de chaque PR du jalon note le temps passé par le mainteneur sur l'issue, qu'il donne lui-même au feu vert merge. K1-3 reprend ces chiffres.

**Orca** (RET-011) : aucune issue de ce jalon ne reprend de code d'Orca ; le kit pilote Orca par sa CLI. Le plan de chaque tâche le dit en une ligne. Pas de clone de référence : le planificateur est lancé sans `--add-dir <clone-orca>`, malgré son profil, que K1-2 réécrit (ADR 0016, ADR 0014 historique).

---

## K1-1 — Le repo devient le kit : retrait de l'app, hooks et scripts

- **Milestone** : `K1 Kit de la méthode` · **Labels** : `enhancement`

**Exigences** : FR-042, FR-044, FR-046, NFR-013, NFR-014, NFR-004 ; [ADR 0016](../decisions/0016-kit-de-methode.md), [ADR 0012](../decisions/0012-coordinateur-role-garde-fous-hook.md) ; Q-055.

**But** : le repo cesse d'être une app et devient le plugin. Les hooks qui tiennent les garde-fous vivent aujourd'hui sur les postes, hors de tout dépôt, et ont déjà divergé d'un poste à l'autre faute d'être versionnés ; trois gardes s'y recouvrent pour les sorties. Ils entrent dans jam, avec leurs tests, et la sortie est gardée par un seul hook.

**Où vit chaque morceau dans le plugin** :
- manifeste : `.claude-plugin/plugin.json`, à la racine du repo ; câblage : `hooks/hooks.json` ;
- hooks : `hooks/`, avec leurs tests ;
- scripts : `scripts/`, avec leurs tests, les sorties de la CLI Orca simulées ;
- fiche concept : `docs/concepts/plugin-et-hooks.md`.

**À faire** :
1. **Retrait de l'app** : supprimer `apps/`, `packages/`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `tsconfig.base.json`, `vitest.config.ts`, `.node-version` et les entrées de l'app dans `.gitignore` ; remplacer le job pnpm de `.github/workflows/ci.yml` par un job qui lance `python3 -m unittest`. Le dernier état de l'app est au tag `app-electron`. Par le rédacteur : retirer la section « L'app (en cours de retrait) » de `README.md` et la ligne correspondante d'`AGENTS.md` ; marquer historiques les fiches concept de l'app, sans les supprimer.
2. **Hooks**, en TDD, rendus génériques (ils contiennent aujourd'hui le nom du mainteneur, des chemins du poste, dont celui du binaire Orca, et le nom d'un autre projet ; le binaire Orca se trouve par le `PATH` ou une variable d'environnement) :

| Hook | Événement | Rôle |
|---|---|---|
| Garde de sortie unique | `PreToolUse` (Bash) | Refuse commit, push, merge (`gh pr merge`) et écritures `gh` (issues, PR, commentaires, `gh api` en écriture…) sans accord explicite dans le dernier message du mainteneur, dans la session qui lance la commande. Remplace les gardes de sortie du poste ; si la garde du coordinateur traite aussi des sorties, cette part lui est retirée. Cas nommé : un feu vert donné dans un worktree et remonté par la carte (merge, publication) ne suffit pas ; le mainteneur le confirme dans le terminal du coordinateur avant que celui-ci agisse. Un test couvre ce cas. |
| Garde du coordinateur | `PreToolUse` (Edit, Write, NotebookEdit, Bash) | Inchangée : refuse au coordinateur (`JAM_ROLE=coordinateur`) toute écriture de fichier hors des emplacements autorisés (ADR 0012). |
| Reprise de contexte | `SessionStart` | Inchangée : récapitulatif au démarrage. |
| Contrôle d'état git | `UserPromptSubmit` | Inchangé : une ligne d'état git à chaque message. |

   Le plan inventorie les gardes de sortie actuelles du poste de travail et la liste exacte des écritures `gh` couvertes. Les hooks sans tests en reçoivent d'abord, sur leur comportement actuel. Chaque message d'un hook du plugin (refus, récapitulatif) porte une marque propre au plugin, par exemple un préfixe `[jam]`, pour le distinguer d'un hook du poste.
3. **Scripts** : *veille des cartes* (attend qu'une carte du projet passe en `⏸` ou `⛔`, ou porte un segment `✓` ou `💬`, puis affiche les cartes et rend la main ; le projet se désigne par un argument) ; *lancement d'une tâche* (worktree, session de l'orchestrateur de tâche ou d'un rôle avec sa variable `JAM_ROLE`, brief lu dans un fichier ; refus si le nombre d'agents en cours atteint le plafond donné). Le plan dit si le schéma de la CLI Orca, aujourd'hui hors dépôt sur le poste, doit être versionné.
4. **Installation** : trancher Q-055 au plan, et l'écrire en quelques lignes dans `README.md` (par le rédacteur). Le plan confirme l'installation pour tout le poste de travail : la garde de sortie s'applique alors à tous les projets du poste, y compris ceux sans fiche, ce qui est voulu (ADR 0016) ; la recette le dit.
5. **Fiche concept** `docs/concepts/plugin-et-hooks.md` : ce qu'est un plugin Claude Code, et pourquoi un hook tient un garde-fou qu'une consigne ne tient pas (`AGENTS.md`, règle 3).

Le plan découpe ce lot en étapes vérifiables séparément.

**Commandes des rôles** : les profils de l'implémenteur, du relecteur et du recetteur portent, depuis ce cadrage, les formes dont cette tâche a besoin : `python3 -m unittest` pour les trois ; pour l'implémenteur, la forme exacte `git rm` des fichiers de l'app ; pour le recetteur, `--plugin-dir <chemin du worktree>`. Le planificateur et l'implémenteur lisent les hooks du poste de travail par `--add-dir <dossier des hooks du poste>`, chemin donné dans le brief seulement. Le plan vérifie que `--plugin-dir` charge le plugin pour la seule session du recetteur, et que la liste des fichiers retirés correspond à la forme exacte du profil de l'implémenteur.

**Hors périmètre** : process et profils (K1-2) ; garde étendue à d'autres rôles et exception « installation d'un hook relu » (Q-056) ; skills, modèles, script de relais d'un feu vert (Q-062).

**Critère de fin** :
- `apps/` et `packages/` n'existent plus ; la CI passe avec les seuls tests du kit ;
- les tests des hooks et des scripts passent en CI ;
- chargé pour une session depuis le worktree, le plugin câble les quatre hooks : la session affiche le récapitulatif marqué du plugin ; avec `JAM_ROLE=coordinateur`, une écriture dans le repo est refusée ; un `git commit`, un `git push` et une écriture `gh` sans accord sont refusés. Seul un refus qui porte la marque du plugin compte : les hooks du poste tournent aussi pendant la vérification ;
- aucun nom de personne, chemin du poste ni nom d'un autre projet dans `hooks/`, `scripts/` ni le manifeste ;
- la fiche concept est écrite ; le corps de la PR note le temps passé par le mainteneur.

**Recette** : installation neuve du plugin depuis le worktree, pour la seule session de recette. Le recetteur lance les tests et note « non reproduits » les points de la check-list que ses commandes ne permettent pas : session lancée avec `JAM_ROLE`, `git commit`, carte Orca, lancement d'un script ou d'une session `claude`. Check-list du mainteneur, qu'il déroule seul : récapitulatif marqué du plugin au démarrage ; refus marqué d'une écriture du coordinateur ; dans un repo jetable hors de jam, refus marqué d'un `git commit` sans accord ; la veille des cartes, lancée sur jam, se réveille quand une carte de test passe en `⏸` et ignore un simple `▶`. Les tests couvrent aussi le passage après un accord, le cas du feu vert remonté par la carte et le refus de lancement au plafond.

**Orca** : aucune brique d'Orca à reprendre ; les scripts pilotent sa CLI. Pas de clone de référence : le planificateur est lancé sans `--add-dir <clone-orca>` (ADR 0016, ADR 0014 historique).

---

## K1-2 — Process élagué : process et profils génériques, niveaux, fiche projet

- **Milestone** : `K1 Kit de la méthode` · **Labels** : `documentation`

**Exigences** : FR-043, FR-045, FR-049 à FR-055, NFR-013 à NFR-016 ; [ADR 0016](../decisions/0016-kit-de-methode.md), [ADR 0017](../decisions/0017-coordinateur-main-poste-de-travail.md) ; Q-058, Q-027.

**But** : la référence de la méthode quitte `docs/process/` pour le plugin, générique et plus courte. Elle s'est alourdie d'essai en essai ; une méthode qui demande plus de temps qu'elle n'en fait gagner manque son but.

**Où vit chaque morceau dans le plugin** :
- déroulé : `process/README.md`, depuis `docs/process/README.md` ;
- profils : `roles/<rôle>.md`, les sept profils de `docs/process/roles/` ;
- gabarit de la fiche projet : `process/fiche-projet.md` ;
- hooks : le hook de reprise de contexte, dans `hooks/` ;
- hors du plugin : la fiche de jam, `docs/methode.md` ; un `docs/process/README.md` réduit à un renvoi vers `process/` et `roles/` ; `AGENTS.md`, qui renvoie au process du plugin et à la fiche.

**Qui écrit quoi** : l'implémenteur déplace d'abord `docs/process/` par les deux formes exactes de son profil, dans cet ordre (`git mv docs/process/roles roles`, puis `git mv docs/process process`), ce qui garde l'historique des profils ; il écrit ensuite les dossiers du plugin (`Edit(./**)` couvre la racine) et le hook. Le rédacteur recrée `docs/process/README.md` en renvoi, et écrit `docs/` et `AGENTS.md`. Pendant cette tâche, l'orchestrateur de tâche lit le process et fait lire aux rôles les profils du worktree principal (`main`), par leur chemin absolu donné dans le brief, et non ceux du worktree de la tâche, que l'implémenteur déplace et réécrit.

**À faire** :
1. **Élaguer** : plafond de taille de NFR-015 (process et profils, au plus la moitié du nombre de mots de `docs/process/` sur `main` au départ de la tâche, `wc -w`). L'historique d'une règle (« Origine : … ») est remplacé par un renvoi à l'ADR ou au RET qui la porte ; une origine qui n'est dans aucun des deux y est ajoutée par le rédacteur. Toute nouvelle règle dit laquelle elle remplace ou retire (NFR-016).
2. **Rendre générique** : plus de nom de projet, de commande propre à un projet (`pnpm`…) ni de chemin ; les commandes des rôles prennent la commande de test et la recette dans la fiche projet ; les passages « Kit » ajoutés aux profils par `cadrage-kit` deviennent les commandes normales. Retirer ce qui décrivait l'app : introduction, colonne « Cible (jam E0) », « Ce qu'Orca ne permet pas (et que jam fera) », renvois au cœur. Les règles propres au développement de jam (clone de référence d'Orca) sortent du générique.
3. **Écrire les règles de RET-014 à RET-016** :
   - niveaux selon le risque du projet, montée d'un niveau motivée, *renforcé* sans contenu (FR-049, Q-061 laissée ouverte) ;
   - niveau *léger* sans orchestrateur de tâche ni planificateur, conduit par le coordinateur, un seul relecteur (FR-052), dans le process et le profil du coordinateur ;
   - seuil « assez bon » (FR-050) : proposition à valider au feu vert plan, par exemple une classe « cosmétique » de constat, dont un tour sans autre constat conclut `RELECTURE : OK` ;
   - plafond d'agents global, compté en agents en cours, et plafond du projet comme borne propre au projet, pas comme part du global (FR-051) ; les passages sur les « agents actifs » du process sont alignés ;
   - relais d'un feu vert allégé (FR-053) ; un feu vert remonté par la carte pour une action du coordinateur (merge, publication) est confirmé par le mainteneur dans le terminal du coordinateur, puisque la garde de sortie ne lit que les messages de la session qui agit (K1-1) ;
   - règle 6 d'`AGENTS.md`, par le rédacteur : relais allégé, et commit et PR par le coordinateur au niveau *léger* ;
   - recette d'une interface par captures ou enregistrement, dans le profil du recetteur (FR-054) ;
   - mesure : temps du mainteneur noté dans la PR (FR-055) ;
   - ADR 0017 : lancement par Orca, rien d'indispensable en dossier temporaire (trancher Q-058), fenêtre d'autorisation du système.
4. **Permissions** : transposer les interdits qui protègent les profils lus par les rôles suivants (aujourd'hui `Edit(docs/process/**)` chez l'implémenteur). Pour les tâches qui suivront K1-2, le plan vérifie l'hypothèse que les rôles lisent les profils du plugin installé, et non ceux du worktree.
5. **Hook de reprise** : il désigne le process du plugin et la fiche projet du repo, au lieu de `docs/process/README.md`. TDD : le test d'abord.
6. **Fiche projet** : gabarit (niveau par défaut, commande de test, grille de relecture, recette, sens d'un merge, plafond d'agents du projet) ; fiche de jam au niveau *léger*.

**Hors périmètre** : contenu du niveau *renforcé* (Q-061) ; skills, modèles (Q-062) ; adoption de la fiche par les autres projets du mainteneur (chacun quand il en a besoin, sans tâche dans jam).

**Critère de fin** :
- `process/`, `roles/` et `process/fiche-projet.md` existent, et `docs/process/` ne contient plus qu'un renvoi ;
- le process et les profils tiennent sous le plafond de NFR-015 (nombres de mots avant et après dans la PR) ;
- aucun nom d'un autre projet, chemin du poste ni nom d'hôte dans `process/` et `roles/`, et aucune commande `pnpm` ;
- chaque règle du point 3 figure dans le process et dans le profil du rôle qui l'applique ; le profil du planificateur exige un niveau motivé quand une tâche monte d'un niveau ;
- la règle 6 d'`AGENTS.md` est cohérente avec FR-052 et FR-053 ;
- jam a sa fiche `docs/methode.md`, au niveau *léger* ; Q-058 tranchée ;
- les tests du hook de reprise passent en CI ; le corps de la PR note le temps passé par le mainteneur.

**Recette** : installation neuve du plugin depuis le worktree, pour la seule session de recette. Check-list du mainteneur d'abord : récapitulatif d'une session neuve dans jam (process du plugin, fiche de jam) ; comptage des mots ; recherche des noms interdits dans les dossiers du plugin ; liens des docs déplacées. Ensuite, les tests. La recette en usage est K1-3, première tâche conduite au niveau *léger* avec ces profils ; son rapport le dit.

**Après le merge de K1-2** (entrée en vigueur des règles de l'ADR 0016), par le mainteneur : installer le plugin sur le poste selon la décision de Q-055 ; retirer des réglages du poste les hooks devenus doublons ; vérifier qu'une session neuve n'affiche plus qu'un récapitulatif.

**Orca** : aucune brique d'Orca à reprendre. Pas de clone de référence : le planificateur est lancé sans `--add-dir <clone-orca>` (ADR 0016, ADR 0014 historique).

---

## K1-3 — Page publique : comment je travaille avec des agents

- **Milestone** : `K1 Kit de la méthode` · **Labels** : `documentation`

**Exigences** : FR-055, FR-056, NFR-002 ; [ADR 0016](../decisions/0016-kit-de-methode.md).

**But** : le `README.md` de jam devient la page publique de la méthode : ce qu'elle est, comment elle tourne, ce qu'elle coûte en temps au mainteneur, chiffres mesurés à l'appui.

**Où vit chaque morceau** : `README.md` à la racine du repo ; rien dans les dossiers du plugin.

**À faire** :
- Écrire une page courte (au plus 800 mots), strictement factuelle : le principe (rôles neufs, feux verts, niveaux selon le risque, garde-fous en hooks), l'installation du plugin (reprise de K1-1), un renvoi au process et aux ADR.
- Chiffres : seulement ceux qui ont été mesurés, le temps du mainteneur noté dans les PR de K1-1 et K1-2, chacun avec le lien de sa PR. Rien d'inventé, aucune estimation présentée comme une mesure.
- Rien sur la vie personnelle du mainteneur, sur des tiers ni sur ses autres projets.
- Conduite au niveau *léger* : le coordinateur lance le rédacteur, puis un relecteur ; pas de recette par un agent.

**Critère de fin** : le `README.md` tient en 800 mots au plus ; chaque chiffre renvoie à la PR qui le porte ; aucune mention d'un autre projet, de tiers ni de la vie du mainteneur ; le corps de la PR note le temps passé par le mainteneur.

**Recette** : le mainteneur lit la page sur GitHub depuis la branche et vérifie chaque chiffre sur sa PR.

**Orca** : aucune brique d'Orca à reprendre.
