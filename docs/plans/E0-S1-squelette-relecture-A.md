# Relecture A — E0 · S1 « Squelette » (axe justesse)

> Rôle : relecteur, contexte neuf. Axe : bugs et erreurs ignorées, valeur des tests, robustesse du protocole, migrations SQLite, cycle de vie du cœur lancé par Electron. L'axe de l'autre relecteur n'est pas couvert ici.

## Vérification exécutée

`pnpm check` lancé en local : typecheck OK (3 paquets, tests compris), **73 tests verts sur 12 fichiers**, build electron-vite OK.

Non vérifié (mes permissions ne permettent pas de lancer Electron) : `pnpm dev`, la palette Cmd+K, la survie d'un repo au redémarrage **de l'app**, et surtout l'exécution de `packages/core/src/cli.ts` par le Node embarqué d'Electron 44 (`ELECTRON_RUN_AS_NODE=1` + type stripping). Ces points restent à prouver en recette.

## Constats

### Bloquant

Aucun.

### À corriger

**1. Une écriture vers un cœur mort peut faire planter le processus main** — `packages/protocol/src/client.ts:36-49` et `apps/desktop/src/main/core-process.ts:28`

Le client écoute `end` et `close` sur `readable`, mais rien n'écoute `error` sur `writable` (le stdin du cœur). Si le cœur meurt (base illisible au démarrage, plantage) et qu'un appel part avant que la fin de stdout ait été traitée, l'écriture échoue en `EPIPE` : le socket émet `error` sans écouteur, l'exception remonte dans le main d'Electron (boîte « A JavaScript error occurred in the main process »). Le plan prévoit au contraire qu'un cœur planté donne « simplement une erreur affichée ».

Correction attendue : dans `createClient`, ajouter `writable.on('error', close)` (même traitement que la fermeture du flux : rejeter les appels en cours, refuser les suivants), avec un test : un `writable` qui émet `error` rejette l'appel en cours par « connection closed » sans exception non gérée.

**2. Une dernière ligne sans retour à la ligne est ignorée en silence** — `packages/protocol/src/ndjson.ts:19-31`, `packages/core/src/server.ts:66-70`

Le décodeur garde la fin non terminée en attente, et `serve` se termine sur `end` sans jamais la traiter. `printf '{"jsonrpc":"2.0","id":1,"method":"ping"}' | node packages/core/src/cli.ts serve --db :memory:` ne répond rien et sort en code 0. Pour un cœur qu'on doit pouvoir piloter « avec un simple `echo` » au terminal, c'est une erreur avalée sans trace.

Correction attendue : ajouter au décodeur une méthode `end()` qui rend le reste en attente (décodé, ou -32700 si ce n'est pas du JSON), l'appeler dans `serve` sur `end` avant d'attendre les réponses en cours. Tests : décodeur (`push('{"id":1}')` puis `end()` rend le message) et serveur (requête sans `\n` final puis fin du flux : une réponse est écrite).

**3. Le cycle de vie du cœur lancé par l'app n'a aucun test** — `apps/desktop/src/main/core-process.ts:17-47`

`startCore` et `stopChild` sont la seule partie du cycle de vie (démarrage, arrêt poli, arrêt forcé, cœur déjà mort) et ne sont couverts ni par un test ni par une preuve automatisée. Le fichier n'importe pas `electron` : il est testable tel quel sous Vitest (`process.execPath` y vaut Node, `ELECTRON_RUN_AS_NODE` est alors sans effet).

Correction attendue : `apps/desktop/test/core-process.test.ts` avec au moins :
- démarrage sur une base temporaire, `client.call('ping', {})` répond ;
- `stop()` résout et le processus fils est bien sorti ;
- cœur tué (`SIGKILL`) : l'appel en cours est rejeté par « connection closed », un appel suivant aussi, sans exception non gérée (couvre aussi le constat 1) ;
- `stop()` sur un cœur déjà mort résout immédiatement.

(`startCore` devra exposer le `ChildProcess` ou son `pid` pour le test, ou le test tuera le fils via le `pid` renvoyé par `ping`.)

### Suggestions

**S1. Accès concurrent à la base partagée** — `packages/core/src/db/database.ts:13` et `:32-35`

La base par défaut est partagée entre l'app et le CLI (question 4 du plan). Aucun délai d'attente n'est réglé : une écriture pendant qu'un autre processus tient un verrou échoue tout de suite en `SQLITE_BUSY` (visible comme -32603). Et la version du schéma est lue **hors** de la transaction, ouverte en `BEGIN` différé : deux premières ouvertures simultanées jouent toutes deux la migration 1, la seconde échoue (« table repos already exists »). Rare au S1, mais à régler avant que des agents écrivent en parallèle. Correction proposée : `new DatabaseSync(path, { timeout: 5000 })` (option à confirmer dans la doc de Node 24), `BEGIN IMMEDIATE`, puis relire `user_version` à l'intérieur de la transaction. Sinon, noter le point dans `OPEN-QUESTIONS.md`.

**S2. Base plus récente que le code acceptée en silence** — `packages/core/src/db/database.ts:33`

Si `user_version` dépasse `migrations.length`, `migrate` ne dit rien et le cœur tourne sur un schéma qu'il ne connaît pas. Le cas arrivera vite : tous les worktrees du projet lancent `pnpm dev` sur le même `userData/jam.db`, et un worktree qui ajoute la migration 2 rendra la base « trop récente » pour les autres. Correction proposée : lever une erreur explicite (« base en version N, ce code connaît M migrations »), avec un test.

**S3. Message trompeur si la base ne s'ouvre pas** — `packages/core/src/cli.ts:37-42`

Toute exception de `main` (base corrompue, dossier sans droits, migration en échec) affiche aussi l'aide d'usage et sort en code 2, comme une faute de frappe. Correction proposée : n'afficher `USAGE` que pour les erreurs de `parseArgs`, et sortir en code 1 pour les autres.

**S4. Chemins équivalents via un lien symbolique** — `packages/core/src/repos.ts:14`

`resolve` normalise `/x/` et `/x/../x`, mais pas les liens symboliques : sur macOS, `/tmp/house` et `/private/tmp/house` deviennent deux repos distincts. Correction proposée : `realpathSync` après la vérification d'existence, et un test avec un lien.

**S5. Cas limites de tests manquants (faible coût)**
- `packages/core/test/repos.test.ts` : la branche « chemin qui existe mais n'est pas un dossier » (`repos.ts:16`, `isDirectory()` faux) n'est pas testée ; seul le chemin absent l'est.
- `packages/core/test/client.test.ts` : une ligne illisible ou une réponse à un `id` inconnu doit être ignorée sans casser les appels suivants (`client.ts:38-55`).
- `packages/core/test/server.test.ts` : un caractère multi-octet (« é ») coupé entre deux morceaux de `Buffer` ; c'est `setEncoding('utf8')` qui le protège (`server.ts:53`, `client.ts:36`), et rien ne vérifie qu'on ne le retire pas.

**S6. Formulaire qui garde les valeurs d'une autre commande** — `apps/desktop/src/renderer/App.tsx:62-71`

`CommandForm` n'a pas de `key` : si une seconde commande à paramètres est choisie alors qu'un formulaire est ouvert, React réutilise le composant et ses valeurs saisies. Sans effet aujourd'hui (une seule commande a des paramètres). Correction proposée : `key={form.command.id}`.

## Écarts déclarés, jugés sur mon axe

- **Node 25 en local, 24.21 en CI et dans Electron** : la sortie de `pnpm check` montre `ExperimentalWarning: SQLite is an experimental feature`, donc les tests locaux ne tournent pas sur la version épinglée. Sans conséquence pour le protocole (l'avertissement part sur stderr, stdout reste propre), mais seule la CI sur 24.21 prouve le comportement réel : ne pas considérer le jalon fini avant la CI verte.
- **Test du client dans `packages/core`** : justifié. Le test a besoin du vrai serveur, et `protocol` ne doit pas dépendre de `core`.
- **Deux points d'entrée du protocole** (`@jam/protocol` et `@jam/protocol/client`) : justifié et utile. `client.ts` importe `node:stream`, l'entrée principale reste sans Node et peut aller dans le renderer.
- **`renderer/errors.ts`, `test/paths.test.ts`, export `@jam/core/commands`** : corrects et testés ; l'export `commands` ne sert qu'au test de `schema-fields`, ce qui garantit que le formulaire est testé sur le vrai schéma et pas sur une copie.
- pnpm 10.20, `@vitejs/plugin-react` 5.2, `global.d.ts` : hors de mon axe, rien à signaler côté justesse.

## Points solides

- Corrélation par `id`, requêtes concurrentes et rejet des appels en cours à la fermeture du flux : implémentés et réellement testés (les tests échoueraient si l'ordre ou la corrélation étaient faux).
- Codes JSON-RPC conformes : -32700 avec `id: null`, -32600 qui renvoie l'`id` quand il est lisible, -32601, -32602 avec les détails zod, -32603 qui masque le message interne (testé), -32001.
- Résultats revalidés côté client contre le schéma de la méthode (testé).
- Migrations dans une transaction avec retour arrière complet (testé), non rejouées à la réouverture (testé), survie au redémarrage prouvée à deux niveaux : base fermée puis rouverte, et deux exécutions successives du vrai CLI.
- Arrêt du cœur : fermeture de stdin, réponses en cours terminées avant `db.close()`, `SIGKILL` après 2 s ; si le main meurt, le pipe se ferme et le cœur s'arrête seul.

RELECTURE : CORRECTIONS (3)
