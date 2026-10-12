# Recette : issue #22, le repo devient le kit

Recette du travail non commité du worktree (retrait de l'app, `hooks/`, `scripts/`, `.claude-plugin/`, docs), selon le plan [`22-repo-devient-le-kit.md`](22-repo-devient-le-kit.md) (§4 « Recette », ajustement c) et RET-010. La session du recetteur est lancée avec `--plugin-dir <worktree>` : le plugin du worktree n'est chargé que pour elle. L'app étant retirée, l'installation neuve se réduit à constater qu'il n'y a rien à installer (Python 3, bibliothèque standard).

## Vérifications, dans l'ordre où elles ont été faites

| # | Commande | Résultat obtenu | Verdict |
|---|---|---|---|
| 0 | Check-list du mainteneur écrite (section suivante) | Écrite avant toute commande. | OK |
| 1 | Installation neuve | Rien à installer : ni `package.json` ni dépendance tierce ; hooks et scripts en Python 3, bibliothèque standard. `ls apps packages` → « No such file or directory » pour les deux. | OK |
| 2 | Démarrage de la session du recetteur (`claude --plugin-dir <worktree>`, hook `SessionStart`) | Le contexte de démarrage contient deux récapitulatifs : celui du poste, non marqué (« ## Reprise de contexte (hook SessionStart) »), et celui du plugin, qui commence par `[jam] Reprise de contexte (hook SessionStart)` : worktree, branche, nombre de fichiers non commités, 5 derniers commits, worktree secondaire, bloc Orca (carte, terminal, autre agent actif, chemin de la CLI Orca à l'emplacement standard de l'app). | OK |
| 3 | Message reçu par la session (hook `UserPromptSubmit`) | Le message (le brief) porte deux lignes d'état git : celle du poste, `[état git] worktree=22-repo-devient-le-kit · branche=… · pas d'upstream · 75 fichier(s) non commité(s) · (worktree secondaire)`, et celle du plugin, identique précédée de `[jam] `. La session n'a reçu qu'un message : le constat porte sur celui-là. | OK |
| 4 | `python3 -m unittest` (depuis `<worktree>`) | `Ran 137 tests in 45.921s` puis `OK`. | OK |
| 5 | `Grep`, sans la casse, des noms de personne, chemins du poste, nom d'hôte, adresse IP et noms des autres projets du mainteneur, donnés par le brief du recetteur (hors du repo), dans `hooks/`, `scripts/`, `.claude-plugin/` | `scripts/` et `.claude-plugin/` : aucune occurrence. `hooks/` : quatre occurrences, toutes des chemins fictifs de tests (`/Users/testhome`, `/Users/testhome/code/repo`, `/Users/x/orca/workspaces/jam/…`), admis. | OK |
| 6 | Même recherche dans les docs modifiées ou créées : `README.md`, `AGENTS.md`, `.gitignore`, `.github/workflows/ci.yml`, `docs/concepts/{README,coeur-separe-protocole,processus-electron,plugin-et-hooks}.md`, `docs/specs/{02-ARCHITECTURE,OPEN-QUESTIONS}.md`, `docs/plans/22-repo-devient-le-kit*.md` | Docs du kit (README, AGENTS, concepts, specs, CI) : aucune occurrence. Rapports de relecture : seulement des citations des chemins fictifs des tests. **Le plan `docs/plans/22-repo-devient-le-kit.md`, ligne 48 (étape 4), écrit le prénom complet du mainteneur entre guillemets** (« … » remplacé par « le mainteneur »). Hors du critère de fin de l'issue (qui porte sur `hooks/`, `scripts/` et le manifeste), mais contraire à la règle 7 d'`AGENTS.md` pour un fichier qui sera publié. | Écart (voir « Écarts ») |
| 7 | Point 4 du plan, veille des cartes : **fait par l'orchestrateur de tâche**, résultat tiré de son relevé (`<dossier de recette>/controles-orchestrateur.md`) | `python3 scripts/watch_cards.py jam --interval 5`, sans `JAM_ORCA_BIN`, avec un `PATH` d'où Orca était retiré : la CLI n'a été trouvée qu'à l'emplacement standard de l'app (ajustement a). Commentaire de la carte du worktree passé à « ▶ test … » : 15 s plus tard, pas de réveil. Passé à « ⏸ test … » : la veille s'est terminée en moins de 12 s, code 0, en affichant `[jam] Carte(s) à traiter : 22-repo-devient-le-kit` puis les deux cartes du projet (nom · statut · commentaire). Commentaire rétabli ensuite. | OK (orchestrateur) |
| 8 | Point 5 du plan, `claude plugin validate .` : **fait par l'orchestrateur de tâche**, sortie dans `<dossier de recette>/plugin-validate.txt` | `marketplace.json` puis `plugin.json` validés : « ✔ Validation passed with warnings », code de sortie 0. Avertissements : pas de `version`, pas d'`author`, pour chacun des deux fichiers ; voulus par le plan. Aucun avertissement sur `"source": "."`. | OK (orchestrateur) |

### Non reproduits

Les commandes du recetteur ne les permettent pas ; ils sont couverts par les tests unitaires et par la check-list du mainteneur.

- Session lancée avec `JAM_ROLE=coordinateur` (refus marqué d'une écriture du coordinateur) : point 2 de la check-list.
- `git commit` et `git push` sans accord (refus de la garde de sortie) : point 3 de la check-list pour `git commit`.
- Écriture `gh` sans accord (`gh` interdit au recetteur) : point 3 de la check-list.
- Lancement d'une session `claude`, ou de `scripts/launch_task.py`, contre le vrai Orca : couvert seulement par les tests à faux `orca` (`scripts/test_launch_task.py`).

### Écarts et limites

- **Prénom du mainteneur dans le plan** (vérification 6) : `docs/plans/22-repo-devient-le-kit.md`, ligne 48. À remplacer avant le commit, par exemple par « le prénom du mainteneur remplacé par « le mainteneur » ». N'affecte pas le critère de fin. Pour mémoire, `docs/specs/OPEN-QUESTIONS.md` porte déjà le diminutif du mainteneur dans sa colonne des responsables ; cet état préexiste sur `main` (relecture de conformité 1, ligne 18) et n'est pas du fait de cette tâche.
- **Fichier de recette écrit hors du repo** : l'écriture de `docs/plans/22-repo-devient-le-kit-recette.md` a été refusée par les permissions de la session (Write et Edit, mode `dontAsk`), alors que l'écriture dans le dossier de recette passait. La règle relative `Edit(docs/plans/…)` ne semble pas reconnue ; la forme absolue (`Edit(//<worktree>/docs/plans/22-repo-devient-le-kit-recette.md)`) l'est, comme pour le dossier de recette. Ce fichier a donc été écrit dans `<dossier de recette>/22-repo-devient-le-kit-recette.md`, à recopier tel quel dans `docs/plans/`. Il y a été recopié par le rédacteur, la liste des termes recherchés (vérification 5) rendue générique.
- **CI non exécutée en local** : elle lance la même commande `python3 -m unittest` ; elle sera vérifiée sur la PR.
- Aucun fichier suivi par git n'a été modifié par le recetteur.

## Check-list de recette manuelle du mainteneur

Écrite avant toute vérification (RET-010). Points 1 à 3 du plan (ajustement c) ; les points 4 et 5 ont été faits par l'orchestrateur de tâche (vérifications 7 et 8). Pendant ces essais, les hooks du poste tournent aussi : ils affichent leur propre récapitulatif et leurs propres refus, sans la marque `[jam]`. **Seul ce qui commence par `[jam]` compte.**

1. **Récapitulatif marqué au démarrage** : depuis la racine du worktree (`<worktree>`), `claude --plugin-dir .`
   Attendu : le contexte de démarrage contient un bloc qui commence par `[jam] Reprise de contexte (hook SessionStart)` (worktree, branche, 5 derniers commits, bloc Orca). Le récapitulatif du poste, non marqué, s'affiche aussi. Au premier message envoyé, une ligne `[jam] [état git] worktree=… · branche=…` apparaît.
2. **Refus marqué d'une écriture du coordinateur** : depuis `<worktree>`, `JAM_ROLE=coordinateur claude --plugin-dir .`, puis demander : « crée le fichier essai.txt à la racine du repo avec le texte test ».
   Attendu : l'écriture est refusée par un message qui commence par `[jam] BLOQUÉ :`. Aucun fichier `essai.txt` n'est créé (`git status` inchangé).
3. **La garde de sortie vaut hors de jam** : créer un repo jetable hors de jam, et hors de `/tmp/claude-*` (exemptés pour commit et push), par exemple `mkdir ~/essai-garde && cd ~/essai-garde && git init && echo a > a.txt && git add a.txt`, puis `claude --plugin-dir <worktree>`. Demander « fais un git commit -m test », puis « lance gh issue create --title test », sans jamais écrire d'accord (pas de « ok », « go », « vas-y »…).
   Attendu : deux refus qui commencent par `[jam] BLOQUÉ :`, l'un pour `git commit`, l'autre pour l'écriture `gh`. `git log` reste vide, aucune issue créée. Supprimer ensuite le repo jetable.

## Recette rejouée après les corrections demandées par le mainteneur

Depuis la recette ci-dessus, à la demande du mainteneur, la garde de sortie `hooks/guard_outbound.py` a été corrigée (commandes `!` et `/` dans la lecture de l'accord, plantage qui bloque, options globales de git), relue (relecture de justesse, tour 8 : OK), et des docstrings ainsi que `docs/concepts/plugin-et-hooks.md` ont changé. Nouvelle session du recetteur, lancée elle aussi avec `--plugin-dir <worktree>`.

| # | Commande | Résultat obtenu | Verdict |
|---|---|---|---|
| R1 | Démarrage de la session (hook `SessionStart`) et message reçu (hook `UserPromptSubmit`) | Le contexte de démarrage contient le récapitulatif du plugin, qui commence par `[jam] Reprise de contexte (hook SessionStart)` (worktree, branche, 78 fichiers non commités, 5 derniers commits, worktree secondaire, bloc Orca), à côté de celui du poste, non marqué. Le message (le brief) porte la ligne `[jam] [état git] worktree=22-repo-devient-le-kit · branche=… · pas d'upstream · 78 fichier(s) non commité(s) · (worktree secondaire)`, à côté de celle du poste, non marquée. | OK |
| R2 | `python3 -m unittest` (depuis `<worktree>`) | `Ran 141 tests in 44.744s` puis `OK` (137 tests à la première recette). | OK |
| R3 | `Grep`, sans la casse, des termes donnés par le brief, dans `hooks/`, `scripts/`, `.claude-plugin/` et `docs/concepts/plugin-et-hooks.md` | `scripts/`, `.claude-plugin/` et `docs/concepts/plugin-et-hooks.md` : aucune occurrence. `hooks/` : cinq occurrences, toutes des chemins fictifs de tests (`/Users/testhome`, `/Users/testhome/code/repo`, `/Users/x/orca/workspaces/jam/…`, dans `test_guard_coordinator.py`, `test_guard_outbound.py` et `test_session_start_recap.py`), admis. | OK |

La check-list du mainteneur reste valable telle quelle : les messages de refus de `hooks/guard_outbound.py` et `hooks/guard_coordinator.py` commencent toujours par `[jam] BLOQUÉ :`, y compris celui du cas de plantage.

Limite : l'écriture de `docs/plans/22-repo-devient-le-kit-recette.md` a de nouveau été refusée par les permissions de la session (Edit, mode `dontAsk`). Ce fichier complet a été écrit dans `<dossier de recette>/22-repo-devient-le-kit-recette.md`, à recopier tel quel dans `docs/plans/`. Aucun fichier suivi par git n'a été modifié par le recetteur. Il a été recopié dans `docs/plans/` par le rédacteur.

## Check-list du mainteneur, déroulée par l'orchestrateur de tâche

Le mainteneur, sur téléphone, a demandé à l'orchestrateur de tâche de dérouler lui-même les points 1 à 3. Mots exacts, relayés par le coordinateur : « Ok », le 2026-10-12 à 21:41, dans la session du coordinateur sur le main de jam. L'orchestrateur a ouvert de vraies sessions interactives `claude --plugin-dir …` dans des terminaux Orca, le 2026-10-12 entre 21:42 et 21:46. Il a lu l'écran avec `orca terminal read`. Les extraits ci-dessous sont ce que l'écran affichait. Seules modifications : chemins du poste remplacés par `<worktree>`, bannière de démarrage retirée.

Les captures complètes sont dans le dossier de recette (`<dossier de recette>`), noms entre parenthèses.

### 1. Récapitulatif (`check-1-ecran.txt`, `check-1b-ecran.txt`) : OK

En mode interactif, le récapitulatif de `SessionStart` n'apparaît pas sur l'écran principal. Il ne figure pas non plus dans la vue détaillée (ctrl+o) tant qu'aucun message n'a été envoyé : il est versé dans le contexte du modèle.

Demande : « Recopie mot pour mot, dans un bloc de code, le texte que le hook SessionStart t'a fourni au démarrage de cette session, sans rien y ajouter ni utiliser d'outil. »

```
[jam] Reprise de contexte (hook SessionStart)
**Worktree** `22-repo-devient-le-kit` · **branche** `jammin-dev/22-repo-devient-le-kit` · 78 fichier(s) non commité(s)
Process du repo : `docs/process/README.md`
**5 derniers commits**
- 7b861a0 Merge pull request #21 from jammindev/jammin-dev/cadrage-kit
- 1863892 docs: jam devient un kit de méthode (cadrage-kit, ADR 0016 et 0017)
- ae18f19 Merge pull request #12 from jammindev/jammin-dev/cadrage-s2
- 91d31d7 docs: découpage du jalon E0-S2 en huit issues (cadrage-s2)
- 21ba489 Merge pull request #11 from jammindev/jammin-dev/cadrage-orca-reference
**1 worktree(s) secondaire(s) actif(s)**
- `22-repo-devient-le-kit` → `jammin-dev/22-repo-devient-le-kit`
## Orca
Worktree `22-repo-devient-le-kit` · carte in-review « ⏸ feu vert recette :
<worktree>/docs/plans/22-repo-devient-le-ki » · issue #22
Ce terminal : « ✳ Claude Code » · session libre (sans rôle) : ne pas écrire là où un rôle travaille
⚠ Autre agent actif dans ce worktree : « ◑ Issue #22 de jam »
⚠ Autre agent actif dans ce worktree : « ✳ Garde outbound : boucle de correction issue #22 »
CLI Orca : `/Applications/Orca.app/Contents/Resources/bin/orca` (chemin complet, toujours --json) · doc : orca skills get orca-cli
_Ne relis pas cet état, il est déjà à jour. Utilise-le pour éviter de te tromper de branche ou de worktree._
```

Seconde session, demande : « Recopie mot pour mot, dans un bloc de code, les lignes que le hook UserPromptSubmit a jointes à ce message, sans utiliser d'outil. » La vue détaillée (ctrl+o) affiche deux lignes : celle du poste, sans marque, et celle du plugin.

```
⏺ UserPromptSubmit hook success: [état git] worktree=22-repo-devient-le-kit · branche=jammin-dev/22-repo-devient-le-kit · pas d'upstream · 78
  fichier(s) non commité(s) · (worktree secondaire)
  UserPromptSubmit hook success: [jam] [état git] worktree=22-repo-devient-le-kit · branche=jammin-dev/22-repo-devient-le-kit · pas d'upstream · 78
  fichier(s) non commité(s) · (worktree secondaire)
```

Observation : tant que les hooks du poste tournent, récapitulatif et état git arrivent en double (poste et plugin). C'est attendu, la check-list le dit. Le double disparaîtra quand le poste passera au plugin (après K1-2).

### 2. Refus d'écriture du coordinateur (`check-2-ecran.txt`) : OK

Commande : `JAM_ROLE=coordinateur claude --plugin-dir .`, depuis `<worktree>`. Demande : « Écris le fichier essai-coordinateur.txt à la racine du dépôt, avec pour contenu le mot essai. Utilise l'outil Write. »

```
⏺ Write(essai-coordinateur.txt)
  ⎿  Error: PreToolUse:Write hook error: [python3 "<worktree>/hooks/guard_coordinator.py"]:
     [jam] BLOQUÉ : Write sur <worktree>/essai-coordinateur.txt.
     Le coordinateur ne produit pas de livrable : délègue à un rôle (docs/process/README.md).
     Écritures permises : la mémoire (~/.claude/projects/*/memory/), le plan (~/.claude/plans/*.md), /tmp/claude-*/ et /private/tmp/claude-*/, et
     l'installation d'un hook relu (cp depuis .../hooks-staging/ vers ~/.claude/hooks/).
     This hook comes from the jam@inline plugin.
```

Le fichier n'a pas été créé (vérifié avec `ls`).

### 3. Garde de sortie hors de jam (`check-3a-ecran.txt`, `check-3b-ecran.txt`) : OK

Repo jetable : `/tmp/jam-recette-22`, hors de `/tmp/claude-*`, sans remote. `git init`, un commit initial et un fichier `b.txt` non suivi. Commande : `claude --plugin-dir <worktree>`. Le dossier a été supprimé ensuite.

Demande 1 : « Enregistre le fichier b.txt dans l'historique git avec le message essai, en une seule commande Bash, sans me poser de question. Si c'est refusé, ne cherche pas d'autre moyen. »

```
⏺ Bash(git add b.txt && git commit -m "essai")
  ⎿  Error: PreToolUse:Bash hook error: [python3
     "<worktree>/hooks/guard_outbound.py"]: [jam] BLOQUÉ : git
     commit alors que le mainteneur ne l'a pas validé.
     Son dernier message était : « Enregistre le fichier b.txt dans l'historique git avec le message essai, en une seule
     commande Bash, sans me poser de question. Si c'est ref »
     Règle permanente : commit, push et écritures gh (PR, issues, merge…) demandent un accord explicite à chaque étape
     sortante.
     Annonce ce que tu comptes faire (branche, message de commit, cible) et attends sa réponse. Ne relance pas la
     commande avant.
     This hook comes from the jam@inline plugin.
```

`git log` : seulement le commit initial. `b.txt` toujours non suivi.

Demande 2 : « Exécute directement, en une seule commande Bash et sans vérification préalable : gh issue create --title test --body essai. Si c'est refusé, ne cherche pas d'autre moyen. »

```
⏺ Bash(gh issue create --title test --body essai)
  ⎿  Error: PreToolUse:Bash hook error: [python3
     "<worktree>/hooks/guard_outbound.py"]: [jam] BLOQUÉ : gh
     issue create alors que le mainteneur ne l'a pas validé.
     Son dernier message était : « Exécute directement, en une seule commande Bash et sans vérification préalable : gh
     issue create --title test --body essai. Si c'est refusé, »
     Règle permanente : commit, push et écritures gh (PR, issues, merge…) demandent un accord explicite à chaque étape
     sortante.
     Annonce ce que tu comptes faire (branche, message de commit, cible) et attends sa réponse. Ne relance pas la
     commande avant.
     This hook comes from the jam@inline plugin.
```

Aucune issue créée.

### Écart avec la check-list, point 3

- Les demandes écrites dans la check-list, « fais un git commit -m test » et « lance gh issue create --title test », contiennent des mots du vocabulaire d'accord de la garde : « commit » et « lance ».
- Vérifié avec l'expression `APPROVAL` de `hooks/guard_outbound.py` : ces deux phrases sont lues comme un accord. Avec elles, la garde aurait laissé passer les deux commandes. La check-list se contredit donc avec sa propre consigne : « sans jamais écrire d'accord ».
- L'orchestrateur a reformulé les demandes sans aucun mot d'accord. Il a vérifié avec la même expression que ces reformulations ne sont pas lues comme un accord.
- Ce n'est pas un défaut du code. C'est la largeur connue du vocabulaire, gardée au plan (question 3 du §7) et notée dans `docs/concepts/plugin-et-hooks.md`.
- Conséquence : une demande directe du mainteneur sans mot d'accord (« Exécute directement… ») est refusée. La session d'essai l'a d'ailleurs prise pour un faux positif. C'est voulu : refus par défaut.

RECETTE AGENT : OK
