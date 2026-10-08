# Recette — E0 · S1 « Squelette »

> Rôle : recetteur. Cible : l'implémentation non commitée de la branche `e0-s1-squelette`, après trois tours de relecture. Date : 2026-10-09.

## 1. Vérifications automatisées

L'app a été pilotée par un script Playwright pour Electron (`playwright-core`, `_electron.launch` sur le build de `apps/desktop`). Le script, ses journaux et ses captures sont dans le dossier de travail de la recette, **hors du repo** (`recette-s1/`). Aucun fichier du repo n'a été modifié, à part ce rapport.

**Environnement** : macOS (Darwin 25.5), Node 25.2.1 (le Node 24.21 épinglé n'est pas installé sur la machine ; `engines: >=24.21.0` est respecté), pnpm 10.20.0, Electron 44.7.0.

**Données** : le scénario principal (critères 3 à 5) a tourné avec un `userData` temporaire (`--user-data-dir`). Le script a vérifié `app.getPath('userData')` avant toute action et se serait arrêté s'il ne pointait pas vers ce dossier. Le repo ajouté se trouve uniquement dans cette base temporaire.

| # | Critère | Commande / action | Résultat | Verdict | Captures |
|---|---|---|---|---|---|
| 1 | `pnpm check` passe | `pnpm check` | Code de sortie 0. Typecheck OK ; 13 fichiers de tests, **102 tests passés** ; build electron-vite OK (main, preload, renderer). | OK | journal `recette-s1/pnpm-check.log` |
| 2 | `pnpm core:ping` répond | `pnpm core:ping` | `{"jsonrpc":"2.0","id":1,"result":{"pong":true,"pid":26785}}` sur la sortie standard, code 0. | OK | — |
| 3 | L'app se lance ; Cmd+K ouvre la palette avec les deux commandes | `node recette-s1/recette.mjs` : lancement du build, `Meta+K` | Fenêtre « jam » affichée. Palette ouverte, éléments lus dans le DOM : `["Ajouter un repo","Lister les repos"]`. « Lister les repos » sur base neuve : « Aucun repo. » | OK | `captures/01-lancement.png`, `02-palette-cmdk.png`, `03-liste-vide.png` |
| 4 | « Ajouter un repo » fonctionne depuis la palette | Palette → « Ajouter un repo » ; formulaire `path`, `testCommand`, `acceptanceCommand` ; chemin = clone principal du repo jam, tests = `pnpm test` ; « Exécuter » | Message « Repo ajouté : <chemin> », aucune erreur affichée. « Lister les repos » affiche `<chemin> — tests : pnpm test`. | OK | `captures/04-formulaire-ajout.png`, `05-repo-ajoute.png`, `06-liste-apres-ajout.png` |
| 5 | Le repo survit au redémarrage | Fermeture de l'app (`app.quit()`, donc le vrai chemin `will-quit`), puis relance sur le même `userData` | À la fermeture, le cœur s'arrête proprement : `[core] exited (code 0, signal null)`, en 162 ms. `jam.db` présent dans le `userData`. Après relance, « Lister les repos » affiche toujours `<chemin> — tests : pnpm test`. Contrôle direct en SQLite : 1 ligne dans `repos`. | OK | `captures/07-relance.png`, `08-liste-apres-relance.png` |
| 3 bis | `pnpm dev` lance l'app (critère du plan) | `pnpm dev --remoteDebuggingPort 9333`, puis connexion CDP | Serveur Vite démarré, fenêtre chargée depuis `http://localhost:5173/`. Palette : `["Ajouter un repo","Lister les repos"]`. « Lister les repos » : « Aucun repo. » (base différente, voir ci-dessous). Fermeture de la fenêtre : l'app quitte et le cœur sort avec le code 0. | OK | `captures/09-dev-lancement.png`, `10-dev-palette.png`, `11-dev-liste.png` |

### Observations

1. **Base réelle de l'app touchée par le contrôle `pnpm dev`.** Cela vient de mon script, pas de l'app : electron-vite écrase la variable `ELECTRON_CLI_ARGS`, donc le `--user-data-dir` n'a pas été transmis. Le dossier `~/Library/Application Support/jam/` n'existait pas avant la recette. Il contient maintenant une `jam.db` au schéma v1, **sans aucun repo** (rien n'a été ajouté pendant ce contrôle), et les caches Chromium. Je l'ai laissé en place : il est inoffensif, et ta recette manuelle l'aurait créé de toute façon.
2. **Cmd+K a été simulé** par Playwright dans le renderer (protocole CDP), sans passer par le clavier ni par les menus de macOS. Un raccourci système qui capterait Cmd+K avant la page ne serait pas détecté. La check-list ci-dessous le vérifie au vrai clavier.
3. **Écart de versions par rapport au plan.** Le plan prévoit pnpm 12 ; `packageManager` déclare `pnpm@10.20.0`. Sous Node 25, `node:sqlite` affiche un `ExperimentalWarning` sur la sortie d'erreur, alors que le plan l'annonce absent en 24.21. Sans effet sur le résultat : la réponse de `core:ping` reste seule sur la sortie standard, et le cœur lancé par Electron (Node 24 embarqué) n'affiche pas ce warning.
4. **Détail d'affichage, non bloquant.** Quand le formulaire « Ajouter un repo » est ouvert, le résultat de la commande précédente (« Aucun repo. ») reste affiché sous le formulaire (`captures/04-formulaire-ajout.png`).
5. **Hors de ma vérification.** La CI verte sur la PR (la PR n'existe pas encore). Les deux fiches concept sont présentes (`docs/concepts/processus-electron.md`, `docs/concepts/coeur-separe-protocole.md`) ; je n'ai pas relu leur contenu.

## 2. Recette manuelle (mainteneur)

1. **`pnpm check`** à la racine du worktree. *Attendu* : se termine sans erreur, avec « 102 passed ».
2. **`pnpm core:ping`**. *Attendu* : une ligne `{"jsonrpc":"2.0","id":1,"result":{"pong":true,"pid":…}}`.
3. **`pnpm dev`**, puis **Cmd+K au clavier** dans la fenêtre. *Attendu* : la palette s'ouvre et liste « Ajouter un repo » et « Lister les repos ».
4. **« Ajouter un repo »** : chemin absolu d'un repo git local, commande de tests `pnpm test`, recette vide, puis « Exécuter ». *Attendu* : « Repo ajouté : <chemin> ».
5. **Quitter avec Cmd+Q**, relancer `pnpm dev`, puis Cmd+K → « Lister les repos ». *Attendu* : le repo est listé avec `tests : pnpm test`.

RECETTE AGENT : OK
