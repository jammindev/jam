# Relecture B (tour 3) — E0 · S1 « Squelette »

> Rôle : relecteur, contexte neuf. Axe **B, conformité** : plan, critère de fin, ADR 0005/0006/0007/0009/0010, sur-ingénierie, lisibilité pour un mainteneur qui ne code pas, repo public, sécurité Electron, CI, README, fiches concept.
> Objet : l'implémentation non commitée du worktree `e0-s1-squelette`. Les relectures précédentes (`*-relecture-*`) n'ont pas été lues.
> Écarts déjà acceptés et non remontés : pnpm 10.20 (Q-018), Node 25 en local / 24.21 en CI et dans Electron, `@vitejs/plugin-react` 5.2, TypeScript 7.

## Ce qui a été vérifié

| Point | Résultat |
|---|---|
| `pnpm test` | 13 fichiers, **102 tests verts** (Node 25 local : `ExperimentalWarning` de `node:sqlite` sur stderr, attendu et documenté dans la fiche). |
| `pnpm typecheck` | Vert sur les 3 paquets. |
| `pnpm build`, `pnpm dev`, Cmd+K, redémarrage de l'app | **Non lancés** : hors des permissions du relecteur (écriture dans `out/`, interface graphique). À couvrir par la recette. |
| CI verte sur la PR | Non vérifiable avant l'ouverture de la PR (prévu par le plan, étape 12). |
| Fichiers du plan (§ 4) | Tous présents. Ajouts hors liste, petits et justifiés : `renderer/errors.ts` (retire le préfixe d'erreur IPC), `renderer/global.d.ts` (type de `window.jam`), `test/core-process.test.ts` et `test/errors.test.ts`. |
| Tests demandés par le plan (étapes 2 à 9 et 11) | Tous présents, dont : message coupé en deux, deux messages dans un morceau, -32700 ; chemin relatif et `testCommand` vide refusés ; `expectTypeOf` ; base neuve en version 1 sans rejeu ; doublon, dossier sans `.git`, **survie à la fermeture/réouverture** ; `required` de `repo.add` ; -32601/-32602/-32001 et requêtes concurrentes ; CLI e2e avec arrêt et relance ; `fieldsFromSchema` sur `repo.add`. Le test « l'app quitte puis relance » existe aussi côté app (`core-process.test.ts:48`). |
| ADR 0006 | Cœur en processus séparé (`spawn` + `ELECTRON_RUN_AS_NODE`), protocole typé, un seul processus local, ni authentification ni version. Conforme. |
| ADR 0007 | Un seul registre (`packages/core/src/commands.ts`), paramètres validés par zod, `paramsSchema` dérivé par `z.toJSONSchema` sans double déclaration, palette alimentée par `commands.list`. Conforme. |
| ADR 0010 | `node:sqlite`, un fichier dans `userData`, migrations numérotées via `PRAGMA user_version` dans une transaction. Conforme. |
| ADR 0005 | Le cœur n'utilise aucune API propre à macOS ; seul le chemin par défaut l'est, et Q-021 le note. Conforme. |
| ADR 0009 | Ne s'applique pas encore (aucun agent). La CI n'a que `contents: read`. |
| Sécurité Electron | `contextIsolation`, `sandbox`, pas de `nodeIntegration` ; preload qui n'expose que `jam.call` ; CSP `default-src 'self'` ; pop-ups refusées, navigation bloquée ; `core:call` refusé hors de la fenêtre de l'app ; `ELECTRON_RENDERER_URL` ignoré une fois l'app packagée ; le main vérifie le nom de méthode, le cœur valide les paramètres. Durcissements de packaging reportés dans Q-019. Conforme au plan. |
| Repo public | Aucun secret, aucune donnée personnelle, aucun chemin machine (recherche sur le code, les docs et `pnpm-lock.yaml`). Les tests utilisent des dossiers temporaires et des chemins fictifs (`/Users/someone`). `LICENSE` MIT présent, `"license": "MIT"` dans les 4 `package.json`. Aucun code repris d'Orca, donc pas de `THIRD_PARTY_NOTICES.md` à compléter. |
| Docs | `docs/concepts/README.md`, ligne « Persistance » de `02-ARCHITECTURE.md`, Q-013 tranchée et points repoussés (Q-014 à Q-021) dans `OPEN-QUESTIONS.md` : faits. Docs en français, code et commentaires en anglais. Aucune mention d'assistant IA. |
| Sur-ingénierie | Rien de hors périmètre. Les protections un peu poussées (doublon par chemin réel, `BEGIN IMMEDIATE`, délai d'attente de verrou SQLite) découlent directement de la question 4 du plan : l'app et le CLI partagent le même fichier. Chacune est commentée et testée. |
| Lisibilité | Noms explicites, commentaires qui expliquent le *pourquoi* (ex. `repos.ts:27`, `database.ts:41`, `server.ts:131`, `main/index.ts:23-33`). Les deux transtypages (`as`) sont justifiés en commentaire. |

## Bloquant

Aucun.

## À corriger

Aucun.

## Suggestions

1. **La commande `jam-core` n'existe pas.** `packages/core/src/cli.ts:13` (`Usage: jam-core serve …`), `cli.ts:2` et `packages/core/src/paths.ts:6` parlent de `jam-core`, mais `packages/core/package.json` ne déclare pas de `bin`. Un mainteneur qui tape `jam-core` d'après le message d'aide aura « command not found ».
   *Correction attendue* : écrire `Usage: node packages/core/src/cli.ts serve [--db <path>]` dans `USAGE` et dans le commentaire de `paths.ts`, plutôt que d'ajouter un `bin` (pas demandé au S1).

2. **README : prérequis et données incomplets pour un non-codeur.** `README.md`, section « Démarrer ».
   *Correction attendue* :
   - préciser « pnpm 10.20 (fixé par `packageManager` ; `corepack enable` l'installe) » au lieu de « pnpm » ;
   - ajouter une ligne : « Les repos sont enregistrés dans `~/Library/Application Support/jam/jam.db` (ou `$JAM_DATA_DIR/jam.db`) » ;
   - ajouter une commande pour lister les repos de l'app sans l'ouvrir, utile pour vérifier le critère « un repo survit au redémarrage » :
     `echo '{"jsonrpc":"2.0","id":1,"method":"repos.list"}' | node packages/core/src/cli.ts serve` ;
   - préciser que `pnpm core:ping` utilise une base en mémoire et ne touche pas aux données de l'app ;
   - renvoyer vers `docs/concepts/` pour comprendre l'architecture.

3. **Fiche `processus-electron.md` : trois termes non expliqués.** Ligne 23 : « IPC » (jamais développé) et « renvoie une promesse » ; ligne 21 : `contextBridge`.
   *Correction attendue* : une glose courte pour chacun, par exemple « IPC (*inter-process communication*, la messagerie entre processus) », « une promesse, c'est-à-dire une réponse qui arrivera plus tard », « `contextBridge`, l'API d'Electron qui fait passer un objet du preload vers la page sans lui donner le reste ».

4. **Contrôle de l'expéditeur IPC au niveau du cadre.** `apps/desktop/src/main/index.ts:49` compare `event.sender` à la fenêtre ; la liste de sécurité d'Electron recommande de vérifier aussi `event.senderFrame` (cadre principal, URL attendue). La CSP `default-src 'self'` empêche déjà tout cadre étranger, donc le risque actuel est nul.
   *Correction attendue* : rien au S1 ; ajouter cette vérification à la liste de durcissement de Q-019.

5. **Actions GitHub épinglées par étiquette.** `.github/workflows/ci.yml:22-25` utilise `@v5` / `@v4`. Sur un repo public, l'épinglage par empreinte de commit (SHA) protège contre une étiquette déplacée.
   *Correction attendue* : rien au S1 ; noter dans `OPEN-QUESTIONS.md` « épingler les actions par SHA, avec Dependabot pour les mettre à jour ».

RELECTURE : OK
