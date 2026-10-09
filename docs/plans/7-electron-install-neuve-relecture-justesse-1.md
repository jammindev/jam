# Relecture A, justesse, tour 1 : issue #7

Objet : le diff non commité du worktree (`git diff`), 5 fichiers : `apps/desktop/package.json`, `.github/workflows/ci.yml`, `pnpm-workspace.yaml`, `README.md`, `docs/concepts/processus-electron.md`.

## Vérifications faites dans `node_modules` (sans charger Electron)

- `electron@44.7.0/package.json` : aucun champ `scripts`, donc aucun `postinstall`. `bin.install-electron` pointe vers `install.js`, et `apps/desktop/node_modules/.bin/install-electron` existe. Le script `electron:install` résout donc bien sa commande.
- `electron/install.js` : `isInstalled()` exige `dist/version` égal à la version du paquet, `path.txt` égal au chemin de la plateforme et l'exécutable présent. Sinon, il télécharge, extrait, puis écrit `path.txt` en dernier. En cas d'échec, il affiche la pile et sort avec le code 1, ce que le `&&` du script `dev` propage. Hors ligne avec un binaire déjà là, il sort avec 0 avant tout accès réseau. Une extraction interrompue, sans `path.txt` ou sans exécutable, relance le téléchargement. Le comportement « idempotent » annoncé est exact.
- `electron/index.js` : `require('electron')` télécharge bien le binaire s'il manque. Le piège décrit dans la fiche concept est donc réel.
- `electron-vite@5.0.0` (`dist/chunks/lib-q6ns0vZr.js:141-159`) : `getElectronPath()` lit `ELECTRON_EXEC_PATH`, sinon `path.txt` à côté du paquet `electron` résolu depuis electron-vite, et lève `Electron uninstall` s'il est absent ou vide. Une seule version d'electron (`44.7.0`) est présente dans le store pnpm. Le `path.txt` que vérifie la CI (`apps/desktop/node_modules/electron`) est donc le même fichier que celui que lit electron-vite.
- `getElectronPath()` n'est appelé que par `startElectron` (dev, preview) et par la compilation en bytecode. Celle-ci n'est pas utilisée dans `apps/desktop`, et il n'existe pas de script `preview`. `electron-vite build`, donc `pnpm check`, n'a pas besoin du binaire.
- `ELECTRON_SKIP_BINARY_DOWNLOAD` n'est lu nulle part dans `node_modules/.pnpm`. Sa suppression ne change rien au comportement.
- `@electron-internal/extract-zip@1.0.5`, le binding natif chargé par `install.js`, n'a aucun script d'installation et embarque ses binaires précompilés, dont `index.linux-x64-gnu.node` pour `ubuntu-latest`. Retirer `electron` de `onlyBuiltDependencies` ne bloque donc aucun build, et la CI peut extraire le zip.
- `pnpm-lock.yaml` : l'entrée `electron@44.7.0` n'a pas `requiresBuild`, et la section `settings` n'enregistre pas `onlyBuiltDependencies`. `pnpm install --frozen-lockfile` n'est pas affecté.
- Avant le correctif, `pnpm --filter @jam/desktop electron:install` échoue faute de script (pnpm sort en erreur si aucun paquet sélectionné n'a le script). L'étape de CI échoue donc bien sans le code : le test d'abord est valide.
- Les arguments passés à `pnpm dev` sont ajoutés en fin de commande, donc à `electron-vite dev`, et non à `install-electron`. Correct.
- Aucun test vitest n'importe `electron` : seuls `src/main/index.ts` et `src/preload/index.ts` le font, et ils sont compilés, pas exécutés. `pnpm check` en CI ne télécharge donc rien en passant, et ne masque rien.

Tests : aucun code couvert par vitest n'est modifié. Je n'ai pas lancé `pnpm test`, et ni `pnpm dev` ni rien qui charge Electron, comme demandé.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestion

1. **Le test de CI ne prouve pas que `dev` appelle `electron:install`** (`.github/workflows/ci.yml:31-36`, `apps/desktop/package.json:10`). L'étape lance `electron:install` directement. Si un futur changement retire `pnpm run electron:install &&` du script `dev`, la CI reste verte et le défaut de l'issue revient, sans être vu avant la recette. Ce choix est conforme au plan validé : l'ouverture de la fenêtre reste vérifiée par la recette. Correction possible, peu coûteuse : dans la même étape de CI, vérifier que le script `dev` commence par l'appel, par exemple `node -e "process.exit(require('./apps/desktop/package.json').scripts.dev.startsWith('pnpm run electron:install && ') ? 0 : 1)"`. Sinon, l'accepter et le noter.
2. **`test -x` réussit si `path.txt` est vide** (`.github/workflows/ci.yml:35-36`). Avec un `path.txt` vide, la commande devient `test -x ".../dist/"`, qui est vraie pour un dossier, alors qu'electron-vite lèverait `Electron uninstall` (chaîne vide, donc fausse). `install.js` n'écrit jamais de chaîne vide, le risque est donc faible. Correction attendue : `test -s "$electron_dir/path.txt"` à la place de `test -f`, et ajouter `test -f` sur l'exécutable avant `test -x`. La vérification suit alors exactement ce que lit electron-vite.

RELECTURE : OK
