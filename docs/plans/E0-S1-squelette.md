# Plan — E0 · S1 « Squelette »

> Rôle : planificateur. Sources : `04-ROADMAP.md` (S1), FR-014, FR-028, FR-030, NFR-005/006, ADR 0005, 0006, 0007, 0009, 0010.

## 1. Objectif et critère de fin

Poser l'ossature : un monorepo avec un **cœur** (processus Node séparé, utilisable seul en CLI), un **protocole typé** partagé et une **app Electron** qui lance le cœur, s'y connecte et offre une palette Cmd+K adossée à un registre de commandes. Les repos, avec leur commande de tests et leur commande de recette, sont persistés en SQLite.

**Fini quand** :
- `pnpm dev` lance l'app ; Cmd+K liste les commandes « Ajouter un repo » et « Lister les repos », et les exécute ;
- `pnpm core:ping` (cœur seul, sans Electron) renvoie une réponse `ping` sur la sortie standard ;
- un repo ajouté est toujours listé après avoir quitté puis relancé l'app ;
- `pnpm check` (typecheck, tests, build) passe en local, et la CI (`.github/workflows/ci.yml`, même commande) est **verte sur la PR** vers `main` de `github.com/jammindev/jam` (le remote existe désormais) ;
- les deux fiches concept sont écrites.

## 2. Choix techniques

Versions vérifiées le 2026-10-08.

| Sujet | Choix | Justification |
|---|---|---|
| Electron | **44.7.0** (Node 24.21.0, Chromium 152) | Dernière stable, supportée jusqu'en mars 2027. Orca est en 43, l'écart est sans conséquence. |
| `node:sqlite` | **Disponible** dans Node 24.21 : sans flag depuis 22.13, stabilité 1.2 « release candidate », sans avertissement | Confirme l'ADR 0010. `better-sqlite3` n'est pas nécessaire. |
| Node hors Electron | **24.21.0** épinglé (`.node-version`, `engines`) | Même version majeure que le Node d'Electron : le cœur se comporte pareil en CLI, en CI et dans l'app. |
| Gestionnaire de paquets | **pnpm 12** (workspaces) | Workspaces matures et stricts, déjà prévus dans la liste blanche de l'implémenteur. Il faut autoriser les scripts d'installation d'`electron` et d'`esbuild` dans `pnpm-workspace.yaml`. |
| TypeScript | **7.0** (`tsc` natif), `strict`, `erasableSyntaxOnly`, imports en `.ts` | `tsc` sert uniquement au typecheck. La syntaxe effaçable (ni `enum` ni propriétés de paramètre) permet à Node d'exécuter le TS directement. |
| Exécution du cœur | **Type stripping natif de Node 24** (stable depuis 24.12) : `node packages/core/src/cli.ts` | Le cœur n'a pas d'étape de build, et le même fichier tourne en CLI, en test et sous Electron. |
| Build de l'app | **electron-vite 5** + **Vite 7** + `@vitejs/plugin-react` | Outil standard pour main, preload et renderer, déjà utilisé par Orca. electron-vite 5 plafonne à Vite 7, que Vitest 5 accepte aussi. |
| UI | **React 19.3**, palette avec **cmdk 1.1** | cmdk fournit le filtrage, le clavier et l'accessibilité de la palette. Aucun design au S1. |
| Validation | **zod 4** | Il fournit `z.toJSONSchema()` nativement : les paramètres des commandes sont décrits en JSON Schema, le format qu'attendront les outils MCP (ADR 0007). |
| Tests | **Vitest 5** | Compatible avec Vite, exécute le TS sans configuration, un seul outil pour tout le monorepo. |
| Transport du protocole | **JSON-RPC 2.0, un message JSON par ligne (NDJSON), sur stdin/stdout** du cœur ; logs sur stderr | Format standard (LSP, MCP stdio), lisible au terminal, testable en CLI avec un simple `echo`. Le cadrage NDJSON marche sur n'importe quel flux : passer plus tard à un socket Unix ne changera pas le protocole. |
| Lancement du cœur par l'app | `child_process.spawn(process.execPath, [cli.ts, "serve", "--db", …], { env: ELECTRON_RUN_AS_NODE=1 })` | `utilityProcess` ne permet pas de brancher stdin, et son transport par MessagePort n'existerait pas en CLI. `ELECTRON_RUN_AS_NODE` réutilise le Node embarqué d'Electron, sans dépendre d'un Node système. |
| Sécurité Electron | `contextIsolation`, `sandbox`, pas de `nodeIntegration` ; le preload n'expose que `jam.call(method, params)` | Le renderer ne voit ni Node ni le cœur. Le main vérifie que la méthode appelée existe dans le protocole. |

**ADR** : aucune contradiction. ADR 0006 : un seul processus local, sans authentification ni version. ADR 0010 : `node:sqlite`, migrations numérotées. ADR 0007 : un seul registre de commandes, paramètres validés par zod. ADR 0009 ne s'applique pas encore (aucun agent).

## 3. Étapes (TDD : le test d'abord)

1. **Monorepo** : `package.json` racine (scripts `dev`, `test`, `typecheck`, `build`, `check`, `core:ping`), `pnpm-workspace.yaml`, `tsconfig.base.json`, `.node-version`. *Preuve* : `pnpm install` puis `pnpm typecheck` passent sur des paquets vides.
2. **Protocole : enveloppe et cadrage** (`packages/protocol`). Schémas zod des requêtes et réponses JSON-RPC, codes d'erreur standard (-32700, -32600, -32601, -32602, -32603) plus `-32001 REPO_INVALID`, et un découpeur NDJSON. *Tests* : enveloppe valide ou invalide ; message coupé en deux morceaux ; deux messages dans un morceau ; ligne non JSON qui donne -32700.
3. **Protocole : méthodes**. Un objet `methods` associe chaque nom à `{ params, result }` en zod, et les types en sont inférés :
   - `ping` → `{ pong: true, pid }` ;
   - `repos.list` → `Repo[]` ;
   - `repos.add { path, testCommand, acceptanceCommand? }` → `Repo` ;
   - `commands.list` → `{ id, title, method, paramsSchema }[]`.
   
   Un `Repo` vaut `{ id, path, testCommand, acceptanceCommand \| null, createdAt }`. *Tests* : chemin relatif refusé ; `testCommand` vide refusé ; inférence des types vérifiée avec `expectTypeOf`.
4. **Cœur : base et migrations** (`packages/core/src/db`). `openDatabase(path)` ouvre `DatabaseSync` et applique les migrations numérotées dans une transaction, en suivant `PRAGMA user_version`. La migration 1 crée la table `repos` (`path` unique). *Tests* : base neuve, version 1 ; une seconde ouverture ne rejoue rien.
5. **Cœur : dépôt des repos** (`repos.ts`). `addRepo` vérifie que le chemin existe et contient `.git`, et refuse les doublons. `listRepos` trie par date d'ajout. *Tests* : ajout puis liste ; doublon refusé ; dossier sans `.git` refusé ; **fermer la base puis la rouvrir garde les repos** (survie au redémarrage).
6. **Cœur : registre de commandes** (`commands.ts`). Deux entrées, `repo.add` (« Ajouter un repo », méthode `repos.add`) et `repo.list` (« Lister les repos », méthode `repos.list`). `paramsSchema` est dérivé du schéma zod de la méthode via `z.toJSONSchema`, sans double déclaration. *Tests* : chaque commande pointe vers une méthode existante ; `paramsSchema` de `repo.add` contient `path` et `testCommand` dans `required`.
7. **Cœur : serveur** (`server.ts`). Le serveur relie les messages entrants aux gestionnaires typés : il valide les paramètres et transforme les erreurs en erreurs JSON-RPC. *Tests* sur des flux en mémoire : `ping`, méthode inconnue (-32601), paramètres invalides (-32602), erreur de repo (-32001), requêtes concurrentes.
8. **Cœur : CLI** (`cli.ts`). `serve --db <chemin>` ; si `--db` est absent, le chemin vient de `$JAM_DATA_DIR` ou vaut `~/Library/Application Support/jam/jam.db`. *Test e2e* : lancer `node src/cli.ts serve --db <tmp>`, écrire `ping` sur stdin et lire la réponse ; ajouter un repo, arrêter le processus, le relancer et lister. `pnpm core:ping` fait un `echo` de la requête vers le CLI.
9. **Client typé** (`packages/protocol/src/client.ts`). `createClient(stream)` fournit `call<M>(method, params): Promise<Result<M>>`, avec la corrélation par `id` et le rejet des appels en cours si le flux se ferme. *Tests* : client branché sur le serveur en mémoire ; une erreur JSON-RPC devient une exception typée.
10. **App : main et preload** (`apps/desktop`). Le main lance le cœur avec `--db` dans `app.getPath('userData')/jam.db`, crée le client, répond à `ipcMain.handle('core:call')` et arrête le cœur en quittant. Le preload expose `jam.call`. *Preuve* : `pnpm --filter desktop build` passe, puis contrôle manuel (étape 12).
11. **App : palette** (renderer). Cmd+K ouvre une palette cmdk alimentée par `commands.list`. Une commande avec paramètres affiche un champ par propriété du `paramsSchema` (le formulaire générique ne gère que des objets plats de chaînes). L'exécution appelle `jam.call(method, params)`. Le résultat de `repos.list` s'affiche en liste, et une erreur s'affiche en texte. *Test unitaire* : `fieldsFromSchema(paramsSchema)` sur le schéma de `repo.add`.
12. **CI et vérification finale**. `.github/workflows/ci.yml`, déclenché sur `pull_request` et sur `push` vers `main` (ubuntu, Node 24.21, pnpm, `ELECTRON_SKIP_BINARY_DOWNLOAD=1`, `pnpm check`). Le cœur est portable : un runner macOS n'est pas nécessaire. *Preuve* : `pnpm check` vert en local ; lancement manuel, ajout d'un repo, redémarrage, repo toujours listé. La CI réelle tourne ensuite sur la PR que le coordinateur ouvre après le feu vert 2 ; si elle échoue, la correction repart vers l'implémenteur.
13. **Fiches concept**, puis mise à jour de `docs/concepts/README.md` et de la ligne « Persistance » de `02-ARCHITECTURE.md`.

## 4. Fichiers créés ou modifiés

- Racine : `package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml`, `tsconfig.base.json`, `.node-version`, `vitest.config.ts` (ou `projects`), `.gitignore` (ajouter `node_modules`, `out`, `*.db`), `.github/workflows/ci.yml`.
- `packages/protocol/` : `package.json`, `tsconfig.json`, `src/{index,jsonrpc,ndjson,methods,client}.ts`, `test/*.test.ts`.
- `packages/core/` : `package.json`, `tsconfig.json`, `src/{cli,server,commands,repos,paths}.ts`, `src/db/{database,migrations}.ts`, `test/*.test.ts` (dont `cli.e2e.test.ts`).
- `apps/desktop/` : `package.json`, `electron.vite.config.ts`, `tsconfig*.json`, `src/main/{index,core-process}.ts`, `src/preload/index.ts`, `src/renderer/{index.html,main.tsx,App.tsx,CommandPalette.tsx,schema-fields.ts}`, `test/schema-fields.test.ts`.
- Docs : `docs/concepts/processus-electron.md`, `docs/concepts/coeur-separe-protocole.md`, `docs/concepts/README.md`, `docs/specs/02-ARCHITECTURE.md` (ligne Persistance), `docs/specs/OPEN-QUESTIONS.md` (points repoussés, voir section 5, et Q-013 passée à « tranché » : le repo `jammindev/jam` existe).

## 5. Hors périmètre

Issues, worktrees, agents, pipeline, file « À toi », notifications. Design de l'UI (aucun style au-delà du minimum lisible). Packaging, signature et icône. Redémarrage automatique du cœur s'il plante (une erreur s'affiche simplement). Cœur qui survit à la fermeture de l'app, socket Unix, multi-clients. Commandes purement d'UI exécutées par le cœur (`commands.execute`, notifications cœur → UI), édition et suppression de repo, sélecteur de dossier natif, linter, test e2e Electron (Playwright). Les éléments « pour plus tard » sont notés dans `OPEN-QUESTIONS.md`.

## 6. Questions au mainteneur

1. **Transport** : stdio maintenant (le cœur meurt avec l'app), ou socket Unix tout de suite (le cœur peut survivre à l'app, utile quand des agents tourneront des heures) ? *Recommandation : stdio au S1. Le cadrage NDJSON rend le passage au socket local, à rediscuter au S3.*
2. **Exécution des commandes** : chaque commande pointe vers une méthode du protocole (pas de `commands.execute`), et le renderer gère l'affichage du résultat. *Recommandation : oui, cela respecte les quatre méthodes demandées. Ajouter `commands.execute` quand une commande d'UI pure apparaîtra (S2 ou E0.5).*
3. **Commande de recette facultative ?** *Recommandation : tests obligatoires, recette facultative (`null`), puisque FR-028 parle de « commande ou skill ».*
4. **Base partagée entre CLI et app** : le CLI utilise par défaut le même fichier que l'app (`~/Library/Application Support/jam/jam.db`). *Recommandation : oui, `jam-core` montre ainsi les repos de l'app. Les tests utilisent toujours un dossier temporaire.*
5. **LICENSE MIT** (Q-006 tranchée, NFR-002) : ajouter le fichier dans ce jalon ? *Recommandation : oui, un seul fichier, et `"license": "MIT"` dans les `package.json`.*
6. **TypeScript 7** : si un outil le refuse, revenir à TS 5.9 ? *Recommandation : oui, sans repasser par toi ; l'écart est signalé dans la sortie de l'implémenteur.*

## 7. Concepts (fiches à écrire dans `docs/concepts/`)

- **`processus-electron.md`** : main, preload et renderer ; isolation de contexte et sandbox ; IPC `invoke`/`handle` ; pourquoi le renderer ne voit pas Node ; `ELECTRON_RUN_AS_NODE`.
- **`coeur-separe-protocole.md`** : pourquoi un processus séparé (ADR 0006) ; JSON-RPC 2.0 et NDJSON sur stdio ; schémas zod comme source unique des types et de la validation ; registre de commandes et JSON Schema (pont vers MCP, ADR 0007) ; migrations SQLite par `user_version`.

PLAN PRÊT : docs/plans/E0-S1-squelette.md
