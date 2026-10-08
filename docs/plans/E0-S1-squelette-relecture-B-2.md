# Relecture B (tour 2) — E0 · S1 « Squelette » — axe conformité

> Rôle : relecteur, contexte neuf. Axe B : conformité au plan, au critère de fin et aux ADR (0005, 0006, 0007, 0009, 0010), sur-ingénierie, lisibilité, repo public, sécurité Electron, CI, fiches concept.
> Objet : l'implémentation non commitée du worktree `e0-s1-squelette`. Les relectures des tours précédents n'ont pas été lues.
> Écarts déjà acceptés et non relevés : pnpm 10.20 (Q-018), Node 25 en local et 24.21 en CI et dans Electron, `@vitejs/plugin-react` 5.2, TypeScript 7.

## Ce qui a été vérifié

| Point | Résultat |
|---|---|
| `pnpm test` | **Vert** : 13 fichiers, 89 tests. Seul bruit : un `ExperimentalWarning` de `node:sqlite` sous Node 25, que la fiche concept signale. |
| Critère de fin du plan (§1) | Scripts `dev`, `core:ping`, `check` présents. Les deux commandes de la palette sont dans le registre. La survie au redémarrage est testée au niveau du cœur (`repos.test.ts`, `cli.e2e.test.ts`). La CI lance la même commande, `pnpm check`. Les deux fiches concept sont écrites. |
| Étapes 1 à 13 du plan | Toutes couvertes. Fichiers en plus du plan, tous justifiés : `renderer/errors.ts` (retire le préfixe d'erreur IPC), `renderer/global.d.ts` (type de `window.jam`) et `test/core-process.test.ts`. Le test du client vit dans `packages/core/test/` parce qu'il a besoin du serveur, ce qui est cohérent. |
| ADR 0005 (Electron, macOS) | Respectée. Le cœur n'utilise aucune API propre à macOS. Seul le chemin par défaut de la base l'est (voir S7). |
| ADR 0006 (cœur séparé) | Respectée. Le cœur est un processus séparé, il tourne seul en CLI, sur un seul processus local, sans authentification ni négociation de version. |
| ADR 0007 (registre de commandes) | Respectée. Le registre est unique, dans le cœur. `paramsSchema` est dérivé du schéma zod, sans double déclaration, et la palette se construit à partir du registre. |
| ADR 0009 (permissions) | Sans objet au S1 : aucun agent n'est lancé. |
| ADR 0010 (SQLite) | Respectée. `node:sqlite`, migrations numérotées appliquées par `PRAGMA user_version` dans une transaction, un seul fichier dans le dossier de données de l'app. |
| Repo public | Aucun secret, aucune donnée personnelle, aucun chemin propre à une machine dans le code, les tests, la CI ou le lockfile (les tests utilisent `/Users/someone`). `LICENSE` MIT présent et `"license": "MIT"` dans les quatre `package.json`. Aucun code repris d'Orca, donc `THIRD_PARTY_NOTICES.md` n'est pas requis. `.gitignore` couvre `node_modules`, `out` et `*.db` (le dossier `apps/desktop/out/` présent en local est bien ignoré). Aucune mention d'auteur IA. |
| Sécurité Electron | `contextIsolation`, `sandbox`, pas de `nodeIntegration`. Le preload n'expose que `jam.call`. CSP `script-src 'self'`. Pop-ups refusés, navigation bloquée. `core:call` est refusé à tout autre émetteur que la fenêtre de l'app, et la méthode est vérifiée dans le main. Le risque du fuse `RunAsNode` est noté en Q-019. |
| CI | Déclenchée sur `pull_request` et sur `push` vers `main`, `permissions: contents: read`, sans secret. Node lu dans `.node-version`, pnpm lu dans `packageManager`, `--frozen-lockfile`, `ELECTRON_SKIP_BINARY_DOWNLOAD`, puis `pnpm check`. Conforme au plan (étape 12). |
| Lisibilité | Bonne. Noms explicites, et les commentaires expliquent le *pourquoi* (cast dans `server.ts`, `BEGIN IMMEDIATE`, `realpath`, CJS du preload, EPIPE). Code en anglais, docs en français. |
| Sur-ingénierie | Rien de notable. Les garde-fous ajoutés (verrou `IMMEDIATE`, `timeout` SQLite, refus d'une base plus récente) sont justifiés par la base partagée entre l'app et le CLI (question 4 du plan). Une seule réserve, mineure : le `bin` (S5). |
| Docs | `concepts/README.md`, la ligne « Persistance » et la ligne « État persistant » de `02-ARCHITECTURE.md`, et `OPEN-QUESTIONS.md` (Q-013 tranchée, Q-014 à Q-020 ajoutées) sont conformes à l'étape 13 et à la section 5 du plan. |

### Non vérifié (hors des permissions du relecteur)

- `pnpm typecheck` et `pnpm build` : je n'ai pas le droit de les lancer. Seul `pnpm test` est autorisé.
- `pnpm dev` et le contrôle manuel de l'étape 12 (Cmd+K, ajout d'un repo, redémarrage, repo toujours listé).
- CI verte sur la PR : elle ne tournera qu'après le feu vert 2.

**Au coordinateur** : avant la PR, confirmer que `pnpm check` passe en entier et que le contrôle manuel a été fait.

## Bloquant

Aucun.

## À corriger

Aucun.

## Suggestions

**S1 — `README.md:12` : statut périmé, et aucune consigne de lancement.**
Le README annonce « Statut : spécifications », alors que le repo contient désormais une app. Pour la recette, le mainteneur a besoin des commandes de lancement.
*Correction proposée* : passer le statut à « E0, jalon S1 (squelette) » et ajouter une section « Démarrer » de 4 lignes : `pnpm install`, `pnpm dev` (puis Cmd+K), `pnpm core:ping`, `pnpm check`.

**S2 — `apps/desktop/src/main/index.ts:32` : `ELECTRON_RENDERER_URL` est lu sans condition.**
Une variable d'environnement suffit à faire charger n'importe quelle URL dans la fenêtre, qui expose `window.jam`. Le risque est faible tant que l'app n'est pas packagée, puisqu'il faut déjà pouvoir lancer des commandes sur la machine. Les modèles d'electron-vite limitent cette lecture au mode dev.
*Correction proposée* : `const devServerUrl = app.isPackaged ? undefined : process.env.ELECTRON_RENDERER_URL;`. À défaut, l'ajouter à Q-019 (packaging).

**S3 — `.github/workflows/ci.yml:13-15` : pas de `timeout-minutes`.**
Un test qui lance un sous-processus (`cli.e2e`, `core-process`) et reste bloqué occuperait le runner pendant 6 h, la valeur par défaut.
*Correction proposée* : `timeout-minutes: 10` sur le job `check`. En option, sur un repo public : épingler `actions/checkout`, `pnpm/action-setup` et `actions/setup-node` par SHA plutôt que par tag majeur.

**S4 — Fiches concept : un peu de jargon non expliqué pour un non-codeur.**
- `docs/concepts/processus-electron.md:31` : « CommonJS », « module ES » et « `.mjs` ». Ajouter une phrase : ce sont deux formats de fichiers JavaScript, l'ancien (`require`) et le moderne (`import`), et un preload sandboxé n'accepte que l'ancien.
- `docs/concepts/coeur-separe-protocole.md:33` : « bundlé ». Gloser : regroupé en un seul fichier JavaScript au build.
- `docs/concepts/coeur-separe-protocole.md:27` : « dans une transaction ». Gloser : tout est appliqué, ou rien.

Le reste des deux fiches est clair, au bon format (une phrase, le problème, le fonctionnement avec un schéma Mermaid et les chemins des fichiers, les pièges, les liens) et exact par rapport au code.

**S5 — `packages/core/package.json:11-13` : `bin` non demandé.**
Le plan ne prévoit pas de binaire `jam-core` installable. On lance le cœur par `node src/cli.ts` ou `pnpm core:ping`. Le coût est nul, mais c'est du « pour plus tard ».
*Correction proposée* : le retirer, ou le garder et le citer dans la fiche concept. Au choix du coordinateur.

**S6 — `packages/core/src/db/database.ts:15` et `:20` : constante utilisée avant d'être déclarée.**
`BUSY_TIMEOUT_MS` est déclarée sous la fonction qui l'utilise. Le code fonctionne, mais un lecteur doit chercher plus bas.
*Correction proposée* : déplacer la déclaration au-dessus de `openDatabase`, à côté de `IN_MEMORY`.

**S7 — `packages/core/src/paths.ts:10` : chemin par défaut propre à macOS dans un cœur portable (NFR-005).**
Le plan a acté ce choix (étape 8, question 4), donc rien à changer au S1. Mais le jour où le cœur tournera sur Linux (VPS), le chemin par défaut deviendra `~/Library/Application Support/jam`.
*Correction proposée* : une ligne dans `OPEN-QUESTIONS.md`, ou une mention dans Q-019. `JAM_DATA_DIR` couvre déjà le besoin.

**S8 — Durcissement Electron à noter pour plus tard.**
Aucun `session.setPermissionRequestHandler` n'est posé : par défaut, Electron accorde les demandes de permission de la page (caméra, notifications, etc.). Le risque est faible, puisque la page ne charge que son propre code sous CSP. Rien à coder au S1.
*Correction proposée* : ajouter ce point à Q-019 (packaging et durcissement), avec S2.

RELECTURE : OK
