# Relecture conformité, tour 3 — #22 Le repo devient le kit

> Relecteur B (axe conformité), contexte neuf. Lu : profil du relecteur, `AGENTS.md`, ADR 0016, plan `22-repo-devient-le-kit.md` (ajustements a à c compris), section K1-1 de `cadrage-kit-issues.md`, le diff des fichiers suivis et tous les fichiers non suivis de `hooks/`, `scripts/`, `.claude-plugin/`, `docs/concepts/plugin-et-hooks.md`. Aucune relecture des tours précédents lue.

## Tests

`python3 -m unittest` depuis la racine : **135 tests, OK** (44 s).

## Conformité au plan, au critère de fin et aux ADR

| Point | Constat |
|---|---|
| Retrait de l'app (étape 1) | `apps/`, `packages/`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `tsconfig.base.json`, `vitest.config.ts`, `.node-version` supprimés ; aucun fichier resté dans `apps/` ou `packages/`. `.gitignore` : blocs de l'app retirés, `__pycache__/` ajouté, `CLAUDE.md` et `.claude/settings.local.json` gardés. Conforme. |
| CI | Job pnpm remplacé par `python3 -m unittest` sur `ubuntu-latest`, `permissions: contents: read` et `timeout-minutes: 10` gardés. Conforme. |
| Hooks rapatriés et génériques (étapes 2 à 4) | Quatre hooks, `hooks/__init__.py`, `scripts/__init__.py`. Marque `[jam]` sur chaque sortie ; plus de prénom ; binaire Orca résolu par `scripts/orca_cli.py` seul (ajustement b) ; `session_start_recap.py` ne résout plus le binaire lui-même. Tests du PATH sans `JAM_ORCA_BIN` (`test_cli_found_on_path`) et du message sans chemin (`test_cli_missing_everywhere`, `test_not_found_message_has_no_path`) présents. Conforme. |
| Garde de sortie unique (étape 5, annexe B) | Liste de lectures `GH_READS` identique à l'annexe B ; refus par défaut (question 2) ; exemption `/tmp/claude-*` limitée à commit et push ; formes `rtk`, `rtk proxy`, chemin absolu, `-R`/`--repo` couvertes. Tests : chaque écriture de l'annexe refusée sans accord et passée après accord, lectures jamais refusées (même transcript illisible), cas du feu vert remonté par la carte (refusé, puis passé après « ok merge »), ligne `[jam] [état git]` retirée. Conforme. |
| Câblage (étape 6) | `plugin.json` (`name`, `description`, `license`, `repository`, ni `author` ni `version`), `marketplace.json` (`"source": "."`), `hooks.json` avec l'enveloppe `"hooks"`, les quatre événements et matchers du plan, commandes `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/<fichier>"`. `hooks/test_plugin.py` couvre le tout. Conforme. |
| Veille des cartes (étape 7) | Filtre `repo`/`repoId`, état mémorisé au lancement, réveil sur `⏸`/`⛔` en premier segment ou `✓`/`💬` dans un segment, cartes `completed` ignorées, liste nom · statut · commentaire, sortie 2 sur CLI en échec ou JSON illisible. Tests du plan tous présents. Conforme. |
| Lancement d'une tâche (étape 8) | Comptage avant tout autre appel, terminaux sans agent ou déconnectés non comptés, plafond global et du projet, liste tronquée refusée, worktree existant réutilisé, arguments exacts vérifiés au faux `orca`, brief envoyé à l'identique, `--role` limité à `[a-z-]+`. Conforme. |
| Fiche concept (étape 9) | Format de `docs/concepts/README.md` respecté ; plugin, RET-005, les trois pièges demandés présents. Conforme. |
| Docs du rédacteur (étape 10) | `README.md` (section « Installation », section de l'app retirée), `AGENTS.md`, deux fiches marquées historiques, tableau des fiches, Q-055 tranchée, ligne « Distribution » de `02-ARCHITECTURE.md`. Conforme. |
| Python 3.9 | Ni `match`, ni annotation `X \| Y`, ni `:=`. Conforme. |
| Orca (règle 9) | Aucune reprise de code d'Orca déclarée ni repérée ; pas d'entrée `THIRD_PARTY_NOTICES.md` attendue. Conforme. |
| ADR 0012, 0016 | Garde du coordinateur inchangée hors marque (exception « hook relu » gardée, Q-056 hors périmètre) ; garde de sortie unique distincte. Aucune contradiction. |

## Écarts déclarés par l'implémenteur

| Écart | Jugement |
|---|---|
| `owner.name` « jammindev » dans `marketplace.json` | Accepté : le champ `owner` est exigé par le format des marketplaces ; c'est le nom de l'organisation GitHub, déjà dans `repository`, pas un nom de personne. |
| `launch_task.py` prend l'id du worktree dans la réponse de `orca worktree create`, sans relire `ps` | Accepté : un appel de moins, et une réponse sans id échoue bruyamment (sortie 2, aucun terminal créé, testé par `test_created_worktree_without_id`). Voir suggestion 4. |
| `watch_cards` sort en 2 si le projet n'a aucune carte ; intervalle 30 s par défaut | Accepté : le plan ne fixe pas l'intervalle ; la sortie 2 évite une veille sans fin sur une faute de frappe. Petit, testé. |
| `launch_task` refuse de créer si la liste `ps` est tronquée ; codes 0/1/2 | Accepté : même règle que la liste des terminaux tronquée du plan ; codes documentés dans la docstring. |
| `gh`, `gh --help`, `gh pr` seuls passent comme lecture ; commande illisible contenant `gh` refusée | Accepté : affichage d'aide pour les premiers ; refus par défaut (question 2) pour le dernier. |
| `gh api graphql` avec `--input` ou `-F …=@fichier` compte comme écriture | Accepté : requête hors de vue, donc invérifiable ; cohérent avec le refus par défaut. |
| Résumés de compaction ignorés comme messages du mainteneur | Accepté : resserre la lecture de l'accord, n'en élargit aucune ; touche directement le cas du feu vert remonté par la carte (une veille longue compacte le contexte). Testé et décrit dans la fiche. |
| `JAM_ORCA_BIN` non exécutable = CLI introuvable, sans repli | Accepté : un choix explicite raté est signalé plutôt que remplacé en silence ; documenté dans `orca_cli.py`. Voir suggestion 2. |
| Première ligne du récapitulatif « [jam] Reprise de contexte » au lieu d'un titre `##` | Accepté : seule façon de commencer le message par la marque ; perte cosmétique du titre. |
| `scripts/fixtures/fake_orca.py` et `scripts/fixtures/__init__.py` ajoutés | Accepté : faux binaire partagé par les trois tests des scripts, toujours écrit dans un dossier temporaire comme le veut le plan. |
| Délai de la CLI porté à 5 s dans les tests qui attendent une réponse, 1 s gardée pour le test de lenteur | Accepté : la constante du hook reste à 1 s ; seul le test la remplace. |

## Repo public

Recherche dans `hooks/`, `scripts/`, `.claude-plugin/` et dans les docs modifiées : aucun nom de personne, aucun nom d'un autre projet, aucun chemin du poste. Seuls chemins absolus : `/Applications/Orca.app/Contents/Resources/bin/orca` (emplacement standard, admis) et des chemins fictifs de test (`/Users/testhome/…`, `/Users/x/…`, `/work/…`).

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestion

1. `hooks/test_guard_outbound.py:2` : la docstring dit « the PreToolUse guard of commit and push » ; le fichier teste aussi les écritures `gh`. Correction : « the single outbound guard: commit, push and gh writes ».
2. `README.md`, puce « CLI Orca » de la section Installation : ajouter qu'un `JAM_ORCA_BIN` qui ne pointe pas vers un exécutable désactive les deux replis (comportement voulu de `scripts/orca_cli.py:7-8`), pour qu'un mainteneur qui voit « CLI Orca introuvable » sache où regarder.
3. `docs/concepts/plugin-et-hooks.md:46` : vérifier l'URL `https://code.claude.com/docs/en/plugins/marketplace-reference` ; la page de référence des marketplaces est à ma connaissance `…/docs/en/plugin-marketplaces`. Je n'ai pas pu l'ouvrir pour confirmer.
4. `scripts/launch_task.py:91-96` : la forme `result.worktree.id` de `orca worktree create` ne repose que sur la fixture `scripts/fixtures/orca/worktree-create.json`, et aucun point de la recette ne lance le script. Si l'orchestrateur de tâche n'a pas relu cette forme dans `orca skills get orca-cli`, le noter dans le fichier de recette.
5. `scripts/watch_cards.py:102-103` : la sortie 130 sur Ctrl-C n'est pas listée dans les codes de sortie de la docstring (l. 15-17). Cosmétique.

RELECTURE : OK
