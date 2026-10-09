# Relecture, axe B (conformité), tour 2 : issue #7

Périmètre : le diff non commité du worktree (`git diff`), soit 5 fichiers : `apps/desktop/package.json`, `.github/workflows/ci.yml`, `pnpm-workspace.yaml`, `README.md`, `docs/concepts/processus-electron.md`. Référence : `docs/plans/7-electron-install-neuve.md` (questions 1, 2 et 3 validées).

**Écart au profil, à signaler** : j'ai ouvert par erreur les deux relectures du tour 1 (`-conformite-1`, `-justesse-1`) en début de session, avant d'avoir appliqué la règle d'indépendance du profil. Les constats ci-dessous reposent sur ma propre lecture du diff et de `node_modules`, mais le coordinateur doit savoir que ce tour n'est pas strictement « neuf ».

## Vérifications faites dans le code publié (sans charger Electron)

- `electron@44.7.0/package.json` : aucun champ `scripts`, donc aucun `postinstall`. `bin.install-electron` pointe vers `install.js`.
- `electron/install.js` : `isInstalled()` vérifie `dist/version`, `path.txt` et l'exécutable, puis sort avec le code 0. Sinon il télécharge, extrait, et écrit `path.txt` en dernier ; en cas d'échec, il sort avec le code 1, que le `&&` du script `dev` propage. L'appel avant chaque `pnpm dev` est donc bien idempotent et sans effet une fois le binaire présent.
- `electron-vite@5.0.0` (`dist/chunks/lib-q6ns0vZr.js:142-155`) : lit `ELECTRON_EXEC_PATH`, sinon `path.txt` du paquet `electron`, et lève `Error('Electron uninstall')` s'il manque. La cause décrite dans le plan et la fiche est exacte.
- `package.json` racine : `pnpm dev` délègue à `pnpm --filter @jam/desktop dev`, donc au nouveau script. Aucun changement nécessaire à la racine.
- Recherche hors `node_modules` et hors `docs/plans/` : `ELECTRON_SKIP_BINARY_DOWNLOAD`, `onlyBuiltDependencies` et `postinstall` n'apparaissent plus nulle part ailleurs que dans le diff. Aucune doc restée fausse (les plans `E0-S1-*` sont des archives).

## Conformité au plan

| Étape du plan | Constat |
|---|---|
| 1. CI : `electron:install`, puis vérification de `path.txt` et de l'exécutable sans `require('electron')` ; suppression de `ELECTRON_SKIP_BINARY_DOWNLOAD` | Conforme (`ci.yml:27-38`). La vérification est un peu plus stricte que le plan (`test -s` sur `path.txt`, `test -f` puis `test -x` sur l'exécutable), ce qui colle mieux à ce que lit electron-vite. Ce n'est pas de la sur-ingénierie : trois lignes, même étape. Le bloc `env` est supprimé avec son commentaire. |
| 2. `"electron:install": "install-electron"`, `"dev": "pnpm run electron:install && electron-vite dev"` | Conforme à la lettre (`apps/desktop/package.json:10-11`). Le *pourquoi* est dans la fiche concept, comme prévu, le JSON n'acceptant pas de commentaire. |
| 3. `onlyBuiltDependencies` : esbuild seul, commentaire corrigé | Conforme (`pnpm-workspace.yaml:5-10`). Le commentaire dit pourquoi Electron n'y est plus et renvoie au script `electron:install`. |
| 5. README : une ligne sous `pnpm dev` | Conforme, texte identique au plan (`README.md:21`). |
| 7. Fiche concept : un court paragraphe sur le binaire téléchargé à la demande | Conforme sur le fond (`processus-electron.md:36-37`), placé dans « Les pièges », ce qui respecte les cinq sections fixées par `docs/concepts/README.md`. La parenthèse « version exacte du retrait à vérifier » prévue par le plan n'y figure pas : la fiche dit seulement « Electron 44 n'a pas de script `postinstall` », ce qui est vérifié et ne laisse aucune question ouverte. |
| 4. Vérification locale complète sur installation neuve | Ne se voit pas dans un diff : relève du rapport de l'implémenteur et de la recette (RET-010). |
| Hors périmètre | Respecté : pas de fenêtre lancée en CI, pas de montée de version, RET-010 non modifiée, pas d'empaquetage. |

Le `Closes #7` prévu par le plan relève de la PR, pas du diff : à ne pas oublier par le coordinateur.

**ADR** : aucune contradiction. Petit lot (ADR 0011) ; macOS reste la cible (ADR 0005) ; la CI Linux ne vérifie que le téléchargement, et le commentaire existant `ci.yml:14` (« the app is only built, not launched ») reste vrai. Aucune action d'UI touchée (ADR 0007), aucun changement du cœur (ADR 0006).

**Lisibilité** : noms explicites (`electron:install`, étape CI « Electron binary is ready for pnpm dev », variables `electron_dir` / `electron_exe`). Les commentaires de la CI et de `pnpm-workspace.yaml` disent le *pourquoi*, y compris pourquoi ne pas passer par `require('electron')`. La fiche explique le mécanisme avec des mots simples (« le paquet ne contient pas l'app, seulement de quoi la télécharger »). Code et commentaires en anglais, docs en français.

**Sur-ingénierie** : rien en trop. Le script `electron:install` séparé est prévu par le plan et sert à `dev` comme à la CI.

**Repo public** : aucun secret, aucune donnée personnelle, aucun chemin propre à une machine (seuls des chemins relatifs au repo ; `~/Library/Application Support/jam` est antérieur au diff et générique). Aucune mention d'auteur IA.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. **`docs/concepts/processus-electron.md:36`** : le point « Le binaire Electron est téléchargé à la demande » est long (une dizaine de phrases) pour une fiche limitée à une page, et il répète en partie la ligne suivante et le commentaire de la CI. Correction proposée, facultative : le resserrer à quatre ou cinq phrases (pas de `postinstall` ; electron-vite lit `path.txt` sans `require` ; d'où `electron:install` avant `dev` ; sans effet si le binaire est là).

RELECTURE : OK
