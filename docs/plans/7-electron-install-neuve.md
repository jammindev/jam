# Plan : issue #7, `pnpm dev` échoue sur une installation neuve

## 1. Objectif et critère de fin

Après un `pnpm install` neuf, `pnpm dev` doit lancer l'app sans étape manuelle. Aujourd'hui il échoue avec `Error: Electron uninstall`.

**Critère de fin** (repris de l'issue) :
- depuis une installation neuve (`node_modules` supprimé, puis `pnpm install`), `pnpm dev` ouvre la fenêtre de l'app sans étape manuelle ;
- depuis la même installation, `pnpm check` et `pnpm core:ping` passent toujours ;
- la recette le vérifie selon RET-010 : installation neuve, check-list du mainteneur d'abord.

**Cause, vérifiée dans le code publié** :
- `electron@44.7.0` n'a plus de script `postinstall` : son `package.json` n'a aucun champ `scripts`. Le binaire est téléchargé par `index.js` au premier `require('electron')`. Le téléchargeur reste disponible sous la commande `install-electron` (`install.js`). Elle est idempotente : si `dist/version`, `path.txt` et l'exécutable sont déjà en place, elle sort tout de suite avec le code 0.
- `electron-vite@5.0.0` (`getElectronPath`) lit directement `node_modules/electron/path.txt` sans passer par `require('electron')`. Si le fichier manque, il lève `Electron uninstall`. Seule `ELECTRON_EXEC_PATH` permet de court-circuiter cette lecture.
- `onlyBuiltDependencies: [electron]` dans `pnpm-workspace.yaml` n'a donc plus d'effet : pnpm ne bloque rien, il n'y a simplement plus de script à lancer.
- `ELECTRON_SKIP_BINARY_DOWNLOAD` dans la CI n'a plus d'effet non plus : aucun `postinstall` n'existe, et `install.js` ne lit pas cette variable.

## 2. Choix techniques

- **Télécharger le binaire juste avant `pnpm dev`, pas après l'installation.** Le script `dev` de `apps/desktop` appelle d'abord `install-electron`. C'est la commande fournie par Electron lui-même, et le modèle « à la demande » d'Electron 44 est ainsi respecté. Ni `pnpm install` ni la CI ne téléchargent environ 100 Mo pour un typecheck. Une fois le binaire présent, l'appel coûte quelques millisecondes.
- **Écarté : un `postinstall` à la racine.** Il téléchargerait le binaire à chaque installation, CI comprise, alors que seul `dev` en a besoin.
- **Écarté : les scripts `predev`.** On n'en dépend pas, car pnpm ne lance pas toujours les scripts `pre`/`post` selon sa configuration. Un `&&` explicite est lisible et sûr.
- **Un script nommé `electron:install`**, que `dev` appelle et que la CI peut appeler. La CI exerce ainsi exactement l'étape dont dépend `pnpm dev`.
- **Couvrir le cas en CI, sur Linux, sans lancer l'app.** Après `pnpm install --frozen-lockfile`, la CI lance `electron:install`, puis vérifie `path.txt` et l'exécutable **comme les lit electron-vite**. Elle ne passe pas par `require('electron')`, qui masquerait le défaut : c'est ce qui l'a masqué pendant la recette par Playwright. Lancer la fenêtre en CI (xvfb, macOS) serait de la sur-ingénierie pour ce lot. L'ouverture de la fenêtre reste vérifiée par la recette.
- **Nettoyer les réglages devenus faux** : supprimer `ELECTRON_SKIP_BINARY_DOWNLOAD` de la CI. Si `@electron/get` la lisait, elle empêcherait la nouvelle vérification. Retirer aussi `electron` de `onlyBuiltDependencies` et corriger le commentaire.
- **Aucune contradiction avec une ADR.** Petit lot (ADR 0011). macOS reste la cible (ADR 0005). La CI sous Linux ne vérifie que le mécanisme de téléchargement, ce qui est portable.
- La PR ferme l'issue `incident` #7 (`Closes #7`), ce qui alimente le taux de reprise (ADR 0011).

## 3. Étapes (TDD)

1. **Test d'abord, en CI** : dans `.github/workflows/ci.yml`, après `pnpm install --frozen-lockfile`, ajouter une étape qui lance `pnpm --filter @jam/desktop electron:install`, puis vérifie `apps/desktop/node_modules/electron/path.txt` et l'exécutable `dist/<contenu de path.txt>` (`test -f` / `test -x`). Supprimer `ELECTRON_SKIP_BINARY_DOWNLOAD` et son commentaire.
   *Preuve d'échec* : en local, sur une installation neuve, la même commande échoue, car le script `electron:install` n'existe pas, et `path.txt` est absent.
2. **Code** : dans `apps/desktop/package.json`, ajouter `"electron:install": "install-electron"` et passer `dev` à `"pnpm run electron:install && electron-vite dev"`, avec un commentaire sur le *pourquoi* placé dans le README ou dans la fiche concept, puisque le JSON n'accepte pas de commentaire.
   *Preuve* : les commandes de l'étape 1 passent sur une installation neuve.
3. **Nettoyage** : retirer `electron` de `onlyBuiltDependencies` dans `pnpm-workspace.yaml` et corriger le commentaire, qui ne garde qu'esbuild.
   *Preuve* : `pnpm install` neuf ne signale aucun build ignoré et `pnpm check` passe.
4. **Vérification locale complète** (implémenteur, sur macOS) : `rm -rf node_modules apps/*/node_modules packages/*/node_modules`, `pnpm install`, `pnpm dev` (la fenêtre s'ouvre, Cmd+K ouvre la palette), `pnpm check`, `pnpm core:ping`. Ne jamais lancer `require('electron')` ni Playwright avant `pnpm dev`.
5. **Docs** : dans `README.md`, une ligne sous `pnpm dev` : « au premier lancement, télécharge le binaire Electron (réseau requis) ». Puis la fiche concept (section 7).

## 4. Fichiers créés ou modifiés

- `apps/desktop/package.json` : scripts `electron:install` et `dev`.
- `.github/workflows/ci.yml` : nouvelle étape de vérification, variable supprimée.
- `pnpm-workspace.yaml` : `onlyBuiltDependencies` et son commentaire.
- `README.md` : une ligne.
- `docs/concepts/processus-electron.md` : un paragraphe.

## 5. Hors périmètre

- La règle de recette RET-010 elle-même.
- Lancer réellement la fenêtre en CI (xvfb ou runner macOS).
- L'empaquetage et la distribution de l'app (electron-builder, signature).
- Toute montée de version d'Electron ou d'electron-vite.

## 6. Questions au mainteneur

1. **Télécharger avant `pnpm dev` plutôt qu'après `pnpm install` ?** Recommandation : avant `pnpm dev`. Le téléchargement n'a lieu qu'au moment où l'on en a besoin, et la CI reste légère.
2. **Ajouter la vérification en CI ?** Elle coûte un téléchargement d'environ 100 Mo par exécution, soit quelques secondes. Recommandation : oui. C'est un incident, et la CI est par construction une installation neuve : elle empêche la régression.
3. **Retirer `electron` de `onlyBuiltDependencies` ?** Recommandation : oui. L'entrée n'a plus d'effet et son commentaire induit en erreur.

## 7. Concepts

Pas de nouvelle fiche, car c'est un correctif et non un jalon. On ajoute à `docs/concepts/processus-electron.md` un court paragraphe, « Le binaire Electron, téléchargé à la demande » : Electron 44 n'a plus de `postinstall` (la version exacte du retrait reste à vérifier dans les notes de version) ; `require('electron')` télécharge le binaire, mais electron-vite lit `path.txt` sans le déclencher ; d'où l'appel à `install-electron` avant `dev`, et le piège d'une recette qui charge Electron avant de tester `pnpm dev`.
