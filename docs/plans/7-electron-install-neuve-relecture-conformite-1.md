# Relecture, axe B (conformité), tour 1 : issue #7

Périmètre : le diff non commité du worktree, soit 5 fichiers (`apps/desktop/package.json`, `.github/workflows/ci.yml`, `pnpm-workspace.yaml`, `README.md`, `docs/concepts/processus-electron.md`). Référence : `docs/plans/7-electron-install-neuve.md` (questions 1, 2 et 3 validées).

## Vérifications faites dans le code publié (node_modules)

- `electron@44.7.0/package.json` : aucun champ `scripts`, donc plus de `postinstall`. La commande `install-electron` existe (`bin` → `install.js`) et elle est bien liée dans `apps/desktop/node_modules/.bin/`.
- `install.js` : `isInstalled()` vérifie `dist/version`, `path.txt` et l'exécutable, puis sort avec le code 0. L'appel avant chaque `pnpm dev` est donc idempotent, comme l'affirment le plan et la fiche.
- `index.js` : `require('electron')` lance `install.js` si `path.txt` ou l'exécutable manque. Le piège noté pour la recette est exact.
- `electron-vite@5.0.0` (`dist/chunks/lib-*.js`, `getElectronPath`) : il lit `path.txt` à côté du module résolu, puis lève `Error('Electron uninstall')` s'il manque. Seule `ELECTRON_EXEC_PATH` court-circuite cette lecture. La cause décrite est exacte.
- `@electron/get@5.1.0` : aucune lecture de `ELECTRON_SKIP_BINARY_DOWNLOAD`. Sa suppression de la CI ne change que de la configuration morte.
- `@electron-internal/extract-zip@1.0.5` (binding natif utilisé par `install.js`) : binaires précompilés, aucun script d'installation. Retirer `electron` de `onlyBuiltDependencies` ne bloque donc rien.
- `pnpm-lock.yaml` n'enregistre pas `onlyBuiltDependencies` : `--frozen-lockfile` n'est pas touché.

## Conformité au plan

| Étape du plan | Constat |
|---|---|
| 1. CI : `electron:install` puis `test -f` / `test -x` sans `require('electron')`, suppression de `ELECTRON_SKIP_BINARY_DOWNLOAD` | Conforme (`ci.yml:27-36`). Le shell par défaut des `run` sous Linux est `bash -e`, donc chaque `test` qui échoue fait échouer l'étape. Le commentaire explique le *pourquoi*, y compris l'interdiction de passer par `require('electron')`. |
| 2. `electron:install` = `install-electron`, `dev` = `pnpm run electron:install && electron-vite dev` | Conforme (`apps/desktop/package.json:10-11`). Le *pourquoi* est dans la fiche concept, comme prévu, puisque le JSON n'accepte pas de commentaire. |
| 3. `onlyBuiltDependencies` : esbuild seul, commentaire corrigé | Conforme (`pnpm-workspace.yaml:5-10`). Le commentaire renvoie au script `electron:install`. |
| 5. README : une ligne sous `pnpm dev` | Conforme, texte identique au plan (`README.md:21`). |
| 7. Fiche concept : un paragraphe « Le binaire Electron, téléchargé à la demande » | Contenu conforme et exact. La forme est traitée au constat 1. |
| Hors périmètre | Respecté : pas de lancement de fenêtre en CI, pas de montée de version, RET-010 non modifiée. |

L'étape 4 (vérification locale sur installation neuve) et la preuve d'échec de l'étape 1 ne se voient pas dans un diff : elles relèvent du rapport de l'implémenteur et de la recette.

**ADR** : aucune contradiction. Petit lot (ADR 0011) ; macOS reste la cible (ADR 0005) ; la CI Linux ne vérifie que le téléchargement, et le commentaire existant (`ci.yml:14`, « the app is only built, not launched ») reste vrai.

**Sur-ingénierie** : rien en trop. Le script séparé `electron:install` est prévu par le plan, et il sert à la fois à `dev` et à la CI.

**Lisibilité** : les noms sont clairs (`electron:install`, nom d'étape CI explicite), et les commentaires disent le *pourquoi*. Le code et les commentaires sont en anglais, la doc en français.

**Repo public** : aucun secret, aucune donnée personnelle, aucun chemin propre à une machine. Les seuls chemins cités sont relatifs au repo. Aucune mention d'auteur IA.

**Docs devenues fausses ailleurs** : `ELECTRON_SKIP_BINARY_DOWNLOAD` et `onlyBuiltDependencies` ne figurent plus que dans des plans et relectures passés (`E0-S1-*`), qui sont des archives. Rien à corriger.

## Constats

### Bloquant

Aucun.

### À corriger

1. **`docs/concepts/processus-electron.md:37-43`** : la nouvelle section `## Le binaire Electron, téléchargé à la demande` est insérée entre « Les pièges » et « Pour aller plus loin ». Elle ajoute ainsi un sixième titre au format fixé par `docs/concepts/README.md` (cinq sections : En une phrase, Le problème, Comment ça marche, Les pièges, Pour aller plus loin ; une page au plus). Or son contenu est justement un piège connu.
   *Correction attendue* : placer ce contenu dans « Les pièges ». Par exemple, un point « **Le binaire Electron est téléchargé à la demande.** … », ou un sous-titre `### Le binaire Electron, téléchargé à la demande` sous `## Les pièges`. Garder le texte, et resserrer si besoin pour tenir sur une page.

### Suggestions

2. **`docs/concepts/processus-electron.md:39`** : la parenthèse « (la version exacte du retrait reste à vérifier dans les notes de version) » laisse une question ouverte dans une fiche publiée. Le plan (section 7) la demandait telle quelle, d'où le classement en suggestion. Mais AGENTS.md (règle 4) range ce qui reste « pour plus tard » dans `docs/specs/OPEN-QUESTIONS.md`.
   *Correction proposée* : soit vérifier la version dans les notes de version d'Electron et l'écrire, soit retirer la parenthèse et noter la question dans `OPEN-QUESTIONS.md`.

RELECTURE : CORRECTIONS (1)
