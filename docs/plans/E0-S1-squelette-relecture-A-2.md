# Relecture A (2ᵉ tour) — E0 · S1 « Squelette » — axe justesse

> Rôle : relecteur, contexte neuf. Axe : bugs et erreurs ignorées, valeur des tests, robustesse du protocole, migrations SQLite et survie au redémarrage, cycle de vie du processus cœur.
> Objet : l'implémentation non commitée du worktree `e0-s1-squelette`, relue contre `docs/plans/E0-S1-squelette.md`.
> Écarts déjà acceptés et non relevés : pnpm 10.20, Node 25 en local (24.21 en CI et dans Electron), `@vitejs/plugin-react` 5.2, TypeScript 7.

## Vérification lancée

`pnpm check` : **vert**. Typecheck des 3 paquets OK ; Vitest : 13 fichiers, 89 tests passés ; `electron-vite build` OK (main 8,2 kB, preload `index.cjs`, renderer).

Remarques sur la sortie, sans constat :
- les processus enfants (tests e2e du CLI et de `startCore`) affichent `ExperimentalWarning: SQLite is an experimental feature` sur stderr. C'est le Node 25 local ; sous Node 24.21 (CI, Electron), le plan annonce l'absence d'avertissement. Sans effet sur le protocole, puisque stdout reste propre ;
- le relecteur ne peut pas vérifier que le Node embarqué d'Electron 44 exécute `cli.ts` par *type stripping* sous `ELECTRON_RUN_AS_NODE=1` : `core-process.test.ts` le lance avec le Node de Vitest. Le lancement manuel de l'étape 12 est la seule preuve. Le chemin résolu (`require.resolve('@jam/core/cli')`) est bien le chemin réel `packages/core/src/cli.ts`, hors de `node_modules` ; Node accepte donc d'en retirer les types.

Points vérifiés sans défaut : le cadrage NDJSON (coupure en plein message, plusieurs messages dans un morceau, `\r\n`, lignes vides, fin de flux sans retour à la ligne, caractère multi-octet coupé entre deux morceaux de bytes) ; la corrélation par `id` avec des requêtes concurrentes ; les codes -32700, -32600 (avec écho de l'`id` lisible), -32601, -32602, -32603 (détail masqué) et -32001 ; le rejet des appels en cours et suivants quand le flux se ferme ou que l'écriture échoue (EPIPE) ; les migrations en `BEGIN IMMEDIATE` avec lecture de `user_version` dans la transaction, l'annulation complète si une migration échoue et le refus d'une base plus récente ; la survie des repos à la fermeture et à la réouverture de la base, et à deux exécutions du CLI ; l'arrêt poli du cœur (fermeture de stdin) avec `SIGKILL` au bout de 2 s ; l'attente de cet arrêt dans `will-quit`, sans boucle (le second `will-quit` passe).

## Bloquant

Aucun.

## À corriger

### A1. Le test « stops the core cleanly » passe même si l'arrêt poli ne marche pas

- **Fichiers** : `apps/desktop/test/core-process.test.ts:38-45`, `apps/desktop/src/main/core-process.ts:35-47`.
- **Constat** : le test vérifie seulement qu'après `stop()` le processus n'existe plus. Or `stopChild` envoie `SIGKILL` au bout de `STOP_TIMEOUT_MS` (2 s), et le délai par défaut de Vitest est de 5 s. Si la fermeture de stdin n'arrêtait plus le cœur (régression de `serve`, ou base jamais fermée), le cœur serait tué au bout de 2 s et le test resterait vert. Ce qui doit être prouvé, c'est le comportement promis par le commentaire de `will-quit` (« Hold the exit until the core has closed its database cleanly »), et ce test ne le prouve pas. Le critère de fin « un repo ajouté est toujours listé après avoir quitté puis relancé l'app » n'est d'ailleurs testé qu'au niveau du CLI, jamais par le chemin `startCore` → `stop` → `startCore` que prend l'app.
- **Correction attendue** :
  1. faire résoudre `stop()` avec la sortie du processus (`{ code, signal }`), puis vérifier dans le test `code === 0` et `signal === null`. Un cœur tué par le `SIGKILL` de secours ferait alors échouer le test ;
  2. ajouter un test qui fait `startCore(db)`, `repos.add`, `stop()`, un nouveau `startCore(db)` sur le même fichier, puis vérifie que `repos.list` renvoie le repo. C'est le parcours « quitter puis relancer l'app » sans Electron.

### A2. Doublon possible sur le disque insensible à la casse de macOS

- **Fichier** : `packages/core/src/repos.ts:19`.
- **Constat** : `realpathSync` (version JavaScript de Node) résout les liens symboliques mais garde la casse tapée. Sur APFS, le système de fichiers par défaut de macOS (insensible à la casse), `/Users/x/Code/House` et `/Users/x/code/house` désignent le même dossier mais donnent deux chaînes différentes : la contrainte `UNIQUE` et le `SELECT` de doublon laissent passer le même repo deux fois. Au S1, le chemin est tapé à la main dans le formulaire (pas de sélecteur natif), donc ce cas est plausible. Le pipeline des jalons suivants travaillerait alors deux fois sur le même checkout.
- **Correction attendue** : utiliser `realpathSync.native(given)`. Il appelle `realpath(3)` du système, qui sur macOS renvoie la casse enregistrée sur le disque (à confirmer par le test). Ajouter dans `repos.test.ts` un test « refuses the same repo written with another case » : créer `House/.git`, ajouter `house`, puis vérifier que le chemin stocké est `…/House` et que l'ajout de `House` est refusé. Le test est sauté (`it.skipIf`) si `existsSync(join(dir, 'house'))` est faux, c'est-à-dire sur le disque sensible à la casse de la CI Linux.

## Suggestions

### S1. Une réponse malformée pour un appel en cours le laisse en attente pour toujours

- **Fichier** : `packages/protocol/src/client.ts:59-64`.
- **Constat** : si `responseSchema` refuse un message dont l'`id` correspond pourtant à un appel en cours (par exemple `error.code` non entier), le message est jeté et l'appel n'aboutit jamais, faute de délai. De même, une erreur -32700 ou -32600 renvoyée avec `id: null` (le cœur n'a pas su lire une de nos requêtes) n'est jamais remontée. C'est incohérent avec le commentaire de la ligne 70 : le cœur est un autre processus, ses données sont externes. Un *résultat* invalide est bien rejeté, mais une *enveloppe* invalide donne une attente silencieuse.
- **Correction proposée** : quand l'`id` du message brut est lisible et correspond à un appel en cours, rejeter cet appel avec `invalid response`. Journaliser (`console.error`) les erreurs reçues avec `id: null`. Ajouter un test pour chaque cas.

### S2. Flux sans écouteur `'error'` côté serveur et côté lecture du client

- **Fichiers** : `packages/core/src/server.ts:54` et `:63` ; `packages/protocol/src/client.ts:36-57`.
- **Constat** : le client écoute `'error'` sur le flux d'écriture, mais pas sur le flux de lecture. `serve` n'écoute `'error'` ni sur `input` ni sur `output`. Dans le cœur, si l'app meurt brutalement pendant qu'une réponse part, l'écriture sur `process.stdout` échoue en EPIPE. L'erreur n'est pas captée : le cœur plante avec une trace de pile, et le `finally` qui ferme la base ne s'exécute pas (SQLite le supporte, mais l'arrêt n'est pas propre). De plus, `serve` ne se résout que sur `'end'` : un flux d'entrée fermé sur erreur ne le résout jamais.
- **Correction proposée** : dans `serve`, traiter `output.on('error')` et `input.on('error')` comme une fin (résoudre la promesse après les réponses en cours, sans écrire plus) ; dans le client, ajouter `readable.on('error', close)`. Ajouter un test serveur qui détruit `output` avec une erreur et vérifie que `serve` se résout.

### S3. L'appel est enregistré avant que la requête soit encodée

- **Fichier** : `packages/protocol/src/client.ts:83-87`.
- **Constat** : `pending.set` vient avant `encodeMessage`. Si `JSON.stringify` lève une exception (un `BigInt` dans les paramètres passe le clonage IPC d'Electron, mais pas la sérialisation JSON), la promesse est bien rejetée, mais l'entrée reste dans `pending` jusqu'à la fermeture du flux.
- **Correction proposée** : encoder d'abord (`const line = encodeMessage(...)`), puis appeler `pending.set` et `write`.

### S4. Un `ROLLBACK` qui échoue masque l'erreur de migration d'origine

- **Fichier** : `packages/core/src/db/database.ts:56-58` (et `:15-16`).
- **Constat** : pour certaines erreurs (`SQLITE_FULL`, `SQLITE_IOERR`…), SQLite annule déjà la transaction de lui-même. Le `ROLLBACK` explicite lève alors « no transaction is active », et c'est cette erreur qui remonte, à la place de la vraie cause. Par ailleurs, `openDatabase` ne ferme pas la base quand `migrate` lève une exception. C'est sans effet dans le CLI, qui s'arrête aussitôt, mais un appelant qui réessaie garde un handle ouvert.
- **Correction proposée** : `if (db.isTransaction) db.exec('ROLLBACK');`, puis dans `openDatabase`, encadrer `migrate` d'un `try { … } catch (e) { db.close(); throw e; }`.

### S5. Course entre le contrôle de doublon et l'insertion

- **Fichier** : `packages/core/src/repos.ts:24-34`.
- **Constat** : si le CLI et l'app ajoutent le même repo au même moment, les deux `SELECT` peuvent passer avant les `INSERT`. Le second `INSERT` viole alors `UNIQUE` et remonte en -32603 « Internal error », au lieu de -32001 « already registered ».
- **Correction proposée** : intercepter l'erreur de contrainte de l'`INSERT` (`errcode` 2067, `SQLITE_CONSTRAINT_UNIQUE`) et la transformer en `RepoInvalidError`. Le `SELECT` préalable peut alors disparaître.

### S6. `--db ""` ouvre une base temporaire sans rien dire

- **Fichier** : `packages/core/src/cli.ts:32`.
- **Constat** : `values.db ?? defaultDatabasePath()` garde une chaîne vide. `new DatabaseSync('')` ouvre alors une base temporaire privée que SQLite efface à la fermeture : les repos ajoutés sont perdus sans message.
- **Correction proposée** : refuser `--db` vide avec le message d'usage (code 2), et ajouter le cas dans `cli.e2e.test.ts`.

### S7. Cas limites non testés

- `packages/protocol/test/ndjson.test.ts` : `encodeMessage` d'une valeur dont une chaîne contient `\n` doit donner une seule ligne. C'est l'invariant du cadrage annoncé en commentaire dans `ndjson.ts:9`.
- `packages/core/test/client.test.ts` : une réponse écrite sans retour à la ligne final, juste avant `end()`, doit résoudre l'appel et non le rejeter en « connection closed ». C'est le chemin de `client.ts:48-53`.
- `packages/core/test/server.test.ts` : une requête avec `params: null` (traitée comme `{}`) et une enveloppe invalide avec un `id` décimal (`1.5`, écho attendu : `null`).

RELECTURE : CORRECTIONS (2)
