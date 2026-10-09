# Recette : issue #7, `pnpm dev` sur une installation neuve

Recette du correctif non commité du worktree (`apps/desktop/package.json`, `.github/workflows/ci.yml`, `pnpm-workspace.yaml`, `README.md`, `docs/concepts/processus-electron.md`), selon RET-010 : la check-list du mainteneur est écrite d'abord, puis déroulée depuis une installation neuve, avant tout contrôle outillé.

## Vérifications, dans l'ordre où elles ont été faites

| # | Commande | Résultat obtenu | Verdict |
|---|---|---|---|
| 0 | Check-list du mainteneur écrite (section suivante) | Écrite avant toute commande | OK |
| 1 | `rm -rf node_modules apps/desktop/node_modules packages/core/node_modules packages/protocol/node_modules` | Tous les `node_modules` du worktree supprimés. Le store pnpm du poste, hors du worktree, est conservé (RET-010). | OK |
| 2 | `pnpm install` | Installation terminée sans erreur. `node_modules/.modules.yaml` indique `ignoredBuilds: []` : aucun build ignoré. | OK |
| 3 | `ls apps/desktop/node_modules/electron/` | Ni `path.txt` ni `dist/` : le binaire est absent, comme sur le poste du mainteneur. Electron est une dépendance de `apps/desktop` : `node_modules/electron` n'existe pas à la racine. | OK (état de départ conforme) |
| 4 | `pnpm dev` (premier contrôle après l'installation, en tâche de fond ; rien n'a chargé Electron avant) | `install-electron` s'exécute, puis electron-vite construit main et preload, sert le renderer et affiche `starting electron app...`. Aucun `Error: Electron uninstall`. `path.txt` contient `Electron.app/Contents/MacOS/Electron`. Processus Electron du worktree lancés : main, GPU, réseau, renderer (`--app-path=…/apps/desktop`) et le cœur (`packages/core/src/cli.ts serve`). Capture : une fenêtre « jam » au premier plan, titre « jam », texte « ⌘K ouvre la palette de commandes. ». | OK |
| 5 | Cmd+K au vrai clavier | **Non reproduit** : l'agent n'a pas de clavier, et AppleScript ainsi que l'envoi de la touche par CDP ont été refusés par ses permissions. | Non vérifié (voir « Écarts ») |
| 6 | Fermeture de l'app | Arrêt de la tâche de fond `pnpm dev`. `pgrep -fl 7-electron-install-neuve` ne trouve plus aucun processus. | OK |
| 7 | `pnpm check` | Typecheck des 3 paquets OK, `vitest run` : 13 fichiers, 102 tests passés, build electron-vite OK. Seuls avertissements : SQLite expérimental et des commentaires de zod retirés par Rollup, sans lien avec l'issue. | OK |
| 8 | `pnpm core:ping` | `{"jsonrpc":"2.0","id":1,"result":{"pong":true,"pid":22966}}` | OK |
| 9 | Contrôle outillé : `pnpm dev --remoteDebuggingPort 9333`, puis `curl -s http://localhost:9333/json` | L'argument parvient jusqu'à `electron-vite dev --remoteDebuggingPort 9333`. Une seule page : `"title": "jam"`, `"type": "page"`, `"url": "http://localhost:5174/"`. Cette URL est celle du serveur de dev de cette instance (l'autre instance, voir « Écarts », occupe 5173) : la fenêtre capturée est donc bien celle du worktree. Nouvelle capture identique. Ensuite, l'app est arrêtée et il ne reste plus aucun processus. | OK |

Journaux et captures, hors repo, dans le dossier de travail de la recette : `02-pnpm-dev.log`, `03-fenetre-pnpm-dev.png`, `04-pnpm-dev-debug.log` et `05-fenetre-debug.png`.

### Écarts et limites

- **Cmd+K non vérifié par l'agent.** Le vrai clavier ne peut pas être reproduit. L'envoi de la touche par CDP (`Input.dispatchKeyEvent`) était prévu, mais l'exécution du script a été refusée par les permissions de l'agent. La palette ne fait pas partie du critère de fin de l'issue #7 et n'est pas touchée par le correctif. Elle reste à l'étape 3 de la check-list du mainteneur.
- **Les commandes d'arrêt prévues n'ont pas été lancées.** `pkill -f electron-vite` et `pkill -f node_modules/electron/dist` auraient aussi tué une autre instance de jam lancée depuis le worktree principal du mainteneur (`…/projects/jam`, port 5173). L'app de la recette a été arrêtée en stoppant sa propre tâche de fond, puis l'absence de processus du worktree a été vérifiée avec `pgrep`. L'instance du mainteneur n'a pas été touchée.
- **Les deux instances partagent la même base** (`~/Library/Application Support/jam/jam.db`). C'est sans effet sur cette recette, mais ce point est à garder en tête quand plusieurs worktrees lancent l'app en même temps.
- **Sortie de `pnpm install` filtrée** par le proxy de sortie du poste : l'absence de build ignoré est constatée dans `node_modules/.modules.yaml` (`ignoredBuilds: []`), et non dans le texte affiché.
- **L'étape de CI n'est pas exécutée en local.** Elle appelle le même script `electron:install` et lit le même `path.txt` que l'étape 4. Elle sera vérifiée sur la PR.
- Aucun fichier suivi par git n'a été modifié. Le build écrit dans `out/`, qui est ignoré par `.gitignore`.

## Check-list de recette manuelle du mainteneur

Écrite avant tout contrôle (RET-010). À dérouler dans cet ordre, depuis la racine du worktree. Si l'app de `main` est ouverte, la fermer d'abord pour ne pas confondre les deux fenêtres.

1. **Installation neuve** : `rm -rf node_modules apps/desktop/node_modules packages/core/node_modules packages/protocol/node_modules && pnpm install`
   Attendu : l'installation se termine sans erreur et sans avertissement « Ignored build scripts » pour electron.
2. **Lancer l'app** : `pnpm dev`
   Attendu : au premier lancement, le binaire Electron se télécharge (réseau requis), puis la fenêtre « jam » s'ouvre. Aucun `Error: Electron uninstall`.
3. **Palette** : dans la fenêtre, `Cmd+K`
   Attendu : la palette de commandes s'ouvre. Fermer l'app (`Cmd+Q`, ou `Ctrl+C` dans le terminal).
4. **Contrôles du repo** : `pnpm check`
   Attendu : typecheck, tests et build passent (code de sortie 0).
5. **Cœur seul** : `pnpm core:ping`
   Attendu : une ligne JSON-RPC de réponse (`"id":1` avec un `result` contenant `"pong":true`), sans erreur.

RECETTE AGENT : OK
