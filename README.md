# jam

Le kit d'une méthode de *loop engineering*. Pour chaque issue GitHub, des rôles d'agents travaillent dans un worktree dédié : plan, TDD, relecture, recette. Ils vont jusqu'au merge, et l'humain n'intervient que pour les feux verts. La méthode tourne dans [Orca](https://github.com/stablyai/orca), avec Claude Code.

jam est un **plugin Claude Code** minimal : le process, les profils de rôle, les hooks qui tiennent les garde-fous et trois scripts (lancement d'une tâche, veille des cartes, estimation du temps du mainteneur). Chaque projet qui suit la méthode n'a qu'une fiche, `docs/methode.md`.

Statut : jalon K1, kit en construction, gelé une fois livré ; cette page deviendra la page publique de la méthode. jam visait d'abord une app Electron, abandonnée le 2026-10-11 ([ADR 0016](docs/decisions/0016-kit-de-methode.md)) ; son code a été retiré du repo, et son dernier état est au tag `app-electron`. Voir [`docs/specs/`](docs/specs/) et [`docs/decisions/`](docs/decisions/).

Licence : [MIT](LICENSE).

## Installation

Prérequis : Claude Code, Orca, `python3`, `git` et `gh`.

Le repo est à la fois le plugin et sa marketplace locale. On l'installe une fois, pour tout le poste de travail, depuis le clone de jam, qui reste sur `main` :

```sh
claude plugin marketplace add <chemin du clone de jam>
claude plugin install jam@jam --scope user
```

- **Mise à jour** : un `git pull` de `main` dans le clone suffit. Le plugin est lu en place, sans copie : la nouvelle version vaut dès la session suivante, ou après `/reload-plugins`.
- **Essai d'une branche** : `claude --plugin-dir <chemin du worktree>` charge la version du worktree pour cette seule session, à la place du plugin installé.
- **CLI Orca** : hooks et scripts la cherchent dans `JAM_ORCA_BIN`, sinon dans le `PATH`, sinon à l'emplacement d'installation standard de l'app Orca sur macOS ; poser `JAM_ORCA_BIN` (bloc `env` des réglages utilisateur de Claude Code) ne sert que si Orca n'est ni dans le `PATH` ni à cet emplacement.

Installé ainsi, le plugin vaut pour tous les projets du poste, y compris ceux qui ne suivent pas la méthode : la garde de sortie y refuse aussi commit, push, merge et écritures `gh` sans accord du mainteneur. C'est voulu ([ADR 0016](docs/decisions/0016-kit-de-methode.md)).

Tests des hooks et des scripts, depuis la racine du repo : `python3 -m unittest`.
