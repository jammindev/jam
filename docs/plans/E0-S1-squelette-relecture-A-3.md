# Relecture A (tour 3) — E0 · S1 « Squelette » — axe JUSTESSE

> Rôle : relecteur, contexte neuf. Axe : bugs et erreurs ignorées, valeur des tests, robustesse du protocole, migrations SQLite et survie au redémarrage, cycle de vie du processus cœur.
> Objet : l'implémentation non commitée du worktree `e0-s1-squelette`.

## Vérifications faites

| Vérification | Résultat |
|---|---|
| `pnpm check` (typecheck + tests + build) | **Vert** : typecheck des 3 paquets, 13 fichiers et **102 tests verts**, build electron-vite (main, preload, renderer) réussi. |
| Les tests sont-ils typecheckés ? | Oui : `test/` est inclus dans les `tsconfig` de `protocol`, `core` et `desktop` (node). Les `expectTypeOf` ont donc un vrai effet, puisque `tsc` échouerait si l'inférence changeait. |
| Le Node embarqué d'Electron 44.7 sait-il exécuter `cli.ts` (type stripping) ? | Indice favorable, mais l'exécution n'a pas été vérifiée : le binaire `Electron Framework` contient `amaro` et `ERR_UNSUPPORTED_NODE_MODULES_TYPE_STRIPPING`. Mes permissions ne permettent pas de lancer Electron, donc la recette manuelle (`pnpm dev`) reste la seule preuve. |
| Résolution de `@jam/core/cli` depuis le main bundlé | Correcte : `createRequire` part de `apps/desktop/out/main`, trouve le lien pnpm et le résout en chemin réel (`packages/core/src/cli.ts`), qui n'est pas sous `node_modules`. Le type stripping ne le refusera donc pas. |

## Ce qui a été contrôlé et tient

- **Cadrage NDJSON** (`ndjson.ts`) : reste partiel conservé, plusieurs messages dans un même morceau, `\r\n` et lignes vides ignorés, dernière ligne sans `\n` livrée par `end()`. Le décodage UTF-8 d'un caractère coupé en deux est prouvé par un test avec octets bruts (`server.test.ts:181`).
- **Corrélation des id** (`client.ts`) : une `Map` par id ; une réponse à un id inconnu est ignorée, une enveloppe cassée qui porte l'id d'un appel fait échouer cet appel, une erreur à `id: null` est journalisée. Le test des réponses concurrentes (`client.test.ts:56`) échouerait si la corrélation se faisait dans l'ordre d'arrivée.
- **Flux fermé** : `end`, `close`, `error` en lecture et `error` en écriture (EPIPE) rejettent les appels en cours et tous les suivants. Chaque cas a son test, et le test EPIPE (`client.test.ts:85`) planterait le processus de test si l'écouteur `error` manquait.
- **Erreurs JSON-RPC** côté serveur : -32700, -32600 (avec l'id renvoyé seulement s'il est lisible et entier), -32601, -32602 (avec les `issues` zod), -32001 et -32603 (sans fuite du message interne). Chaque code est testé.
- **Migrations** (`database.ts`) : `BEGIN IMMEDIATE` puis lecture de `user_version` dans la transaction ; refus d'une base plus récente ; rollback complet si une migration échoue (le test `database.test.ts:61` échouerait sans transaction) ; pas de rejeu à la seconde ouverture (le test échouerait sur `table repos already exists`). `user_version` est bien transactionnel.
- **Survie au redémarrage**, prouvée à trois niveaux : `repos.test.ts:126` (fermer puis rouvrir la base), `cli.e2e.test.ts:54` (deux processus CLI successifs) et `core-process.test.ts:48` (`startCore` → `stop` → `startCore`, comme l'app). Côté app, `productName: "jam"` donne `~/Library/Application Support/jam/jam.db`, le même fichier que le défaut du CLI.
- **Doublons** : la contrainte `UNIQUE` tranche de façon atomique, le code d'erreur étendu 2067 est reconnu (prouvé par les tests de doublon), et `realpathSync.native` fusionne le slash final, les liens symboliques et la casse.
- **Cycle de vie du cœur** : arrêt poli par fermeture de stdin, repli SIGKILL après 2 s, `will-quit` retenu jusqu'à la sortie du cœur puis relancé sans boucle (`core` remis à `undefined`). Un cœur tué donne « connection closed » sans faire planter le main (testé). Si Electron meurt brutalement, le pipe stdin se ferme et le cœur sort de lui-même.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. **`apps/desktop/src/main/core-process.ts:41-55`**, `stopChild` peut attendre indéfiniment si le `spawn` a échoué. Après un événement `error` au lancement (EAGAIN, EMFILE), `exitCode` et `signalCode` restent `null`. Node n'émet pas toujours `exit` dans ce cas, et `kill('SIGKILL')` sur un processus jamais né ne fait rien. La promesse ne se résout alors jamais, et `will-quit`, qui a appelé `preventDefault()`, bloque la fermeture de l'app. Le cas est rare, puisque `process.execPath` existe toujours. *Correction* : résoudre aussi sur `child.once('error', …)`, ou tout de suite si `child.pid === undefined`.

2. **`packages/core/src/server.ts:84-100`**, `serve` ne se termine que sur `end` ou `error`. Un flux d'entrée détruit sans erreur n'émet que `close`, et `serve` ne se résout alors jamais : le CLI ne ferme pas la base et ne rend pas la main. Le cas est improbable avec `process.stdin`, qui émet `end` quand le parent ferme le pipe. *Correction* : brancher aussi `input.on('close', finish)`, avec un test `input.destroy()` sans argument.

3. **`packages/protocol/src/client.ts:47-49` et `58-60`**, une ligne illisible venue du cœur est ignorée en silence (`if (line.ok)`). Par exemple, un `console.log` ajouté par erreur dans le cœur écrirait sur stdout et casserait le protocole sans laisser de trace. *Correction* : passer les lignes `ok: false` à `logError`, comme les erreurs à `id: null`, et adapter le test `client.test.ts:97`.

4. **`packages/core/test/cli.e2e.test.ts:40-41`**, aucun écouteur `error` sur `child.stdin`. Dans les tests où le CLI sort tout de suite (codes 1 et 2) alors qu'on lui écrit une requête, un EPIPE tardif serait une exception non gérée, et le test échouerait sans raison. Le risque reste faible, car l'écriture part avant que l'enfant démarre. *Correction* : `child.stdin.on('error', () => {})`, le code de sortie restant la vraie assertion.

5. **`apps/desktop/src/main/index.ts:41-60`**, si `startCore` lève une exception (par exemple si `require.resolve('@jam/core/cli')` échoue après une installation cassée), la promesse de `whenReady` est rejetée sans être gérée : aucune fenêtre ne s'ouvre, `window-all-closed` ne se déclenche jamais, et l'app reste vivante mais invisible. *Correction* : un `.catch` qui journalise l'erreur puis appelle `app.quit()`, ou qui ouvre quand même la fenêtre pour que l'erreur s'affiche.

6. **`apps/desktop/src/renderer/App.tsx:126` et `145`**, `.parse()` dans le rendu : un résultat invalide lèverait une exception pendant le rendu React et, faute d'error boundary, laisserait une fenêtre blanche. Le cas est inatteignable aujourd'hui, puisque le client du main valide déjà le résultat avant l'IPC. *Correction* : `safeParse` et un affichage d'erreur, ou un commentaire qui dit pourquoi `parse` est sûr ici.

## Restent hors de portée de cette relecture

- **Lancement réel sous Electron** (`ELECTRON_RUN_AS_NODE` et type stripping dans le Node d'Electron 44.7), garde IPC (`event.sender`, `isMethodName`) et séquence `will-quit` : aucun test automatique ne les couvre, comme le plan le prévoit. Le critère de fin repose ici sur la recette manuelle : `pnpm dev`, Cmd+K, ajout d'un repo, quitter, relancer, repo toujours listé.
- **CI verte sur la PR** : elle ne pourra être constatée qu'après l'ouverture de la PR.

RELECTURE : OK
