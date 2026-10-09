# Brouillons d'issues — cadrage `cadrage-orchestration`

> Rédigés par le rédacteur. Le coordinateur les publie sur `jammindev/jam` après le feu vert de cadrage, une fois la PR du cadrage mergée.
> Une issue = un petit lot ([ADR 0011](../decisions/0011-pratiques-et-metriques-dora.md)).

## `pnpm dev` échoue sur une installation neuve (binaire Electron absent)

- **Publiée : #7**, sortie du lot et publiée sans attendre la fin du cadrage (Q-041). PR fautive : #5.
- **Milestone** : `E0-S1 Squelette` (encore ouvert, vérifié par le coordinateur). Le bug rend faux, sur une installation neuve, le critère du S1 « L'app se lance ».
- **Labels** : `bug`, `incident` (ajouté par le mainteneur)
- **Origine** : recette manuelle du S1 ; RET-010.

**Constat**
Sur le worktree principal, `pnpm install` puis `pnpm dev` échoue aussitôt : `Error: Electron uninstall`. La recette de l'agent du S1 (`docs/plans/E0-S1-squelette-recette.md`) était pourtant passée.

**Cause**
- Electron 44 ne télécharge plus son binaire à l'installation : il le fait au premier `require('electron')` (`node_modules/electron/index.js`). Après un `pnpm install` neuf, le binaire et `path.txt` sont absents.
- electron-vite 5 lit `path.txt` lui-même et échoue s'il manque, sans déclencher le téléchargement. `pnpm dev` ne marche donc jamais sur une installation neuve.
- La recette de l'agent avait lancé l'app par Playwright (`_electron.launch`), qui passe par `require('electron')` et a téléchargé le binaire avant le contrôle de `pnpm dev`.
- La CI ne lance jamais `pnpm dev`.

**Critère de fin**
- Depuis une installation neuve (`node_modules` supprimé, puis `pnpm install`), `pnpm dev` ouvre la fenêtre de l'app sans étape manuelle.
- Depuis la même installation neuve, `pnpm check` et `pnpm core:ping` passent toujours.
- La recette de l'agent le vérifie selon RET-010 : installation neuve, check-list du mainteneur en premier.

**Pistes, non tranchées** (le choix revient au planificateur)
- Déclencher le téléchargement du binaire après l'installation, ou avant `pnpm dev`.
- Vérifier si Electron fournit encore un script d'installation, et si pnpm le bloque.
- Couvrir le cas en CI, sur une installation neuve.

**Hors périmètre** : la règle de recette elle-même (RET-010, déjà dans le process).
