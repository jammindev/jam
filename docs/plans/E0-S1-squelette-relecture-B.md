# Relecture B — E0 · S1 « Squelette » (axe conformité)

> Rôle : relecteur, contexte neuf. Axe B : conformité au plan, au critère de fin et aux ADR, écarts déclarés, sur-ingénierie, lisibilité, repo public, sécurité Electron, CI, fiches concept. Les bugs et la qualité des tests relèvent de la relecture A.
>
> Vérifié : `pnpm test` passe (12 fichiers, 73 tests). Tests sur Node 25 local, d'où les `ExperimentalWarning` SQLite dans la sortie.
>
> Je n'ai pas pu lire l'issue #1 (`gh` n'est pas autorisé pour ce rôle). J'ai donc pris comme référence le critère de fin du plan et la ligne S1 de `04-ROADMAP.md`.

## Synthèse

L'implémentation suit le plan de près. Les quatre méthodes, le registre de commandes dérivé de zod, la base SQLite avec migrations par `user_version`, le CLI, le client typé, l'app Electron, la CI et les deux fiches concept sont tous là. Chaque preuve demandée par le plan a son test. Les ADR 0005, 0006, 0007 et 0010 sont respectées, et l'ADR 0009 ne s'applique pas encore. Le code est très lisible : les noms sont explicites et les commentaires expliquent le *pourquoi*. Je n'ai trouvé ni secret, ni donnée personnelle, ni code repris d'Orca : `THIRD_PARTY_NOTICES` n'est donc pas nécessaire, et `LICENSE` (MIT) est présent. La configuration de sécurité Electron est correcte, et le preload compilé tient en 4 lignes.

Il y a un seul point à corriger, et il ne touche que la documentation : une contrainte cachée sur le futur packaging de l'app.

## Bloquant

Aucun.

## À corriger

**C1. Le packaging futur est contraint par deux choix du S1, et rien ne le dit** : `docs/specs/OPEN-QUESTIONS.md` (après la ligne 22, Q-018)

Le plan range « packaging, signature et icône » hors périmètre et prévoit que les éléments repoussés soient notés dans `OPEN-QUESTIONS.md` (section 5). Rien n'y figure sur le packaging. Or deux choix faits maintenant le compliquent :
- `apps/desktop/src/main/core-process.ts:18-20` lance le cœur avec `ELECTRON_RUN_AS_NODE`. Une app empaquetée et signée devra donc garder le *fuse* Electron `RunAsNode` activé. Electron recommande pourtant de le désactiver, parce qu'il permet d'utiliser le binaire signé de l'app comme un Node quelconque.
- Le cœur s'exécute sans étape de build, en TypeScript dans `packages/core/src` (plan, section 2). Dans une app empaquetée, ces sources se retrouveraient dans `node_modules` ou dans `app.asar`, deux endroits où Node refuse le type stripping (la fiche `coeur-separe-protocole.md:33` le mentionne déjà). Le packaging imposera donc de compiler le cœur.

Le mainteneur ne peut pas découvrir ces points seul.

*Correction attendue* : ajouter une entrée, par exemple « Q-019 — Packaging, signature et icône : il faudra compiler le cœur (pas de type stripping dans `node_modules`/asar) et garder le fuse `RunAsNode` (lancement par `ELECTRON_RUN_AS_NODE`), ou passer à un autre mode de lancement. Ouvert, hors E0 S1 ». Aucun changement de code.

## Suggestions

**S1. Node : `engines` laisse passer Node 25** : `package.json:8`
Le plan veut Node 24.21 « épinglé (`.node-version`, `engines`) ». Or `">=24.21.0"` accepte Node 25, la version qui tourne en local. Les tests locaux s'exécutent donc sur un Node différent de celui de la CI et d'Electron : les `ExperimentalWarning` SQLite qui s'affichent en local n'existent pas en 24.21. Correction proposée : `"^24.21.0"`, et installer Node 24.21 en local avec un gestionnaire de versions qui lit `.node-version` (fnm, volta, mise).

**S2. CI : droits du jeton et versions des actions** : `.github/workflows/ci.yml:8` et `:16-19`
Le repo est public. Il vaut mieux ajouter `permissions: { contents: read }` au niveau du workflow, puisque le job n'écrit rien. On peut aussi épingler les actions par SHA plutôt que par tag (`@v5`, `@v4`), ce qui les protège contre un tag déplacé. Deux lignes, aucun effet sur le résultat.

**S3. Sécurité Electron : navigation et origine des appels IPC** : `apps/desktop/src/main/index.ts:9-19` et `:36`
L'essentiel est en place : `contextIsolation`, `sandbox`, pas de `nodeIntegration`, une CSP dans `index.html` et un preload minimal. La checklist Electron recommande aussi :
- d'interdire la navigation et l'ouverture de fenêtres (`window.webContents.setWindowOpenHandler(() => ({ action: 'deny' }))` et `will-navigate` → `preventDefault`) ;
- de vérifier dans `ipcMain.handle` que l'appel vient bien de la fenêtre de l'app (`event.senderFrame`).

Le risque est faible tant que la page n'affiche que du contenu local. C'est à poser avant que la page n'affiche du contenu externe (issues, diffs, Markdown) au S2.

**S4. Fiche Electron : la CSP n'est pas expliquée** : `docs/concepts/processus-electron.md:24`
La fiche liste les réglages de sécurité de la fenêtre mais oublie la `Content-Security-Policy` d'`apps/desktop/src/renderer/index.html:6-9`. Ajouter une puce, par exemple : « CSP : la page ne charge que ses propres scripts ; même une donnée piégée affichée dans la page ne peut pas exécuter de code venu d'ailleurs ».

**S5. Fiche cœur : un piège trop technique pour un non-codeur** : `docs/concepts/coeur-separe-protocole.md:32`
« Syntaxe effaçable seulement : ni `enum`, ni propriétés de paramètre… » ne dit pas pourquoi cela compte pour le mainteneur. Il suffit d'une demi-phrase : « Node retire les types sans rien compiler, il ne sait donc pas traduire ces constructions. Si un agent en écrit une, le cœur ne démarre plus. »

**S6. Fixtures de test : chemin qui ressemble à celui d'une machine** : `packages/core/test/paths.test.ts:6`, `:10`, `:14-15`
`'/Users/ben'` est un faux dossier personnel, mais il ressemble à un vrai chemin du mainteneur. Or l'AGENTS.md, règle 7, interdit les chemins propres à une machine. Proposition : `'/Users/someone'`.

**S7. Messages d'erreur en anglais dans une UI en français** : `packages/core/src/repos.ts:17`, `:21`, `:24` ; `packages/protocol/src/client.ts:85`
L'utilisateur voit par exemple « Erreur : /x is not a git repository ». C'est acceptable au S1, puisqu'aucun design n'est demandé. À trancher plus tard : soit les messages du cœur passent en français, soit l'UI traduit à partir du code d'erreur. Dans les deux cas, il vaudrait la peine d'en faire une ligne dans `OPEN-QUESTIONS.md`.

**S8. Une ligne dense dans le serveur** : `packages/core/src/server.ts:57`
Le ternaire, `.then` et `.finally` sont enchaînés sur une seule ligne. On peut le découper avec une variable intermédiaire (`const response = line.ok ? … : …`) pour qu'un non-codeur suive le trajet d'une requête.

## Jugement des écarts déclarés

| Écart | Jugement |
|---|---|
| pnpm 10.20 au lieu de 12 (Q-018) | **Accepté.** Il est tracé dans `OPEN-QUESTIONS.md`, la clé `onlyBuiltDependencies` est bien celle de pnpm 10, et la CI installe la version épinglée dans `packageManager`. |
| Node 25 en local, 24.21 en CI et dans Electron | **Accepté**, puisque la CI et l'app tournent sur la version cible. Voir S1 pour aligner l'environnement local. |
| `@vitejs/plugin-react` 5.2 | **Accepté.** Le plan ne fixait pas de version, et celle-ci est compatible avec Vite 7. J'ai vérifié que son script inline de dev (préambule React Refresh) est injecté avant la balise CSP, donc pas bloqué en `pnpm dev`. |
| Test du client dans `packages/core` | **Accepté.** Le test a besoin du vrai serveur, et `protocol` ne doit pas dépendre de `core` (sinon, dépendance circulaire). |
| Deux points d'entrée (`@jam/protocol` et `@jam/protocol/client`) | **Accepté et justifié.** Le renderer importe le protocole et ne doit pas tirer `node:stream`. C'est expliqué dans `packages/protocol/src/index.ts:1-2`. |
| `renderer/errors.ts` (+ test) | **Accepté.** Le plan demande qu'une erreur s'affiche en texte, et sans ce fichier l'utilisateur verrait le préfixe IPC d'Electron. |
| `renderer/global.d.ts` | **Accepté.** C'est le minimum pour typer `window.jam`. |
| `test/paths.test.ts` | **Accepté.** Il prouve la règle `--db` / `$JAM_DATA_DIR` / dossier par défaut de l'étape 8 du plan. |
| Export `@jam/core/commands` | **Accepté.** Il ne sert qu'au test de l'app, mais il permet de tester `fieldsFromSchema` sur le vrai schéma de `repo.add`, comme le demande l'étape 11. |

Écart non déclaré : `bin: { "jam-core": … }` dans `packages/core/package.json:11-13` n'est pas dans le plan. C'est inoffensif et cohérent avec le nom utilisé dans les commentaires, donc rien à faire.

## Points de conformité vérifiés

- **Critère de fin** : le protocole (`ping`, `repos.list`, `repos.add`, `commands.list`), `pnpm core:ping` (base `:memory:`, qui ne touche pas la vraie base), la survie au redémarrage prouvée en CLI (`cli.e2e.test.ts:53`), `pnpm check` = typecheck + tests + build, et la CI identique sont tous conformes. Les deux fiches sont écrites et référencées dans `docs/concepts/README.md`.
- **ADR 0006** : un seul processus local, sans authentification ni négociation de version.
- **ADR 0007** : le registre unique vit dans le cœur, `paramsSchema` est dérivé par `z.toJSONSchema` sans double déclaration, et la palette n'a aucune commande codée en dur.
- **ADR 0010** : `node:sqlite`, migrations numérotées dans une transaction, version suivie par `PRAGMA user_version`.
- **ADR 0005** : le cœur n'utilise aucune API macOS. Seul le chemin par défaut de la base suit la convention macOS, et `--db` ou `JAM_DATA_DIR` le remplacent.
- **Documents** : `02-ARCHITECTURE.md` (Persistance) et `OPEN-QUESTIONS.md` (Q-013 tranchée, Q-014 à Q-018) sont à jour, et `.gitignore` est complété.
- **Repo public** : aucune mention d'IA, aucun secret, aucune adresse. `out/` et `*.db` sont ignorés.

## À confirmer avant le feu vert (hors décompte)

Je ne peux lancer ni Electron ni la CI. Trois points du critère de fin reposent donc sur la preuve manuelle de l'étape 12 et sur la CI de la PR, et je n'ai trouvé aucune trace de cette preuve dans le worktree :
- `pnpm dev` ouvre l'app, et Cmd+K liste et exécute les deux commandes ;
- un repo est toujours listé après avoir quitté puis relancé **l'app** ;
- la CI est verte sur la PR.

Le coordinateur doit s'assurer que la recette les couvre.

RELECTURE : CORRECTIONS (1)
