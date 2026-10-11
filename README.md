# jam

Le kit d'une méthode de *loop engineering*. Pour chaque issue GitHub, des rôles d'agents travaillent dans un worktree dédié : plan, TDD, relecture, recette. Ils vont jusqu'au merge, et l'humain n'intervient que pour les feux verts. La méthode tourne dans [Orca](https://github.com/stablyai/orca), avec Claude Code.

jam est un **plugin Claude Code** minimal : le process, les profils de rôle, les hooks qui tiennent les garde-fous et deux scripts. Chaque projet qui suit la méthode n'a qu'une fiche, `docs/methode.md`.

Statut : jalon K1, kit en construction, gelé une fois livré ; cette page deviendra la page publique de la méthode. jam visait d'abord une app Electron, abandonnée le 2026-10-11 ([ADR 0016](docs/decisions/0016-kit-de-methode.md)) ; son dernier état est au tag `app-electron`, et son code est en cours de retrait. Voir [`docs/specs/`](docs/specs/) et [`docs/decisions/`](docs/decisions/).

Licence : [MIT](LICENSE).

## L'app (en cours de retrait)

Tant que son code est dans le repo, l'app se lance ainsi. Prérequis : macOS, Node 24.21 (voir `.node-version`) et pnpm.

```sh
pnpm install      # dépendances
pnpm dev          # lance l'app ; Cmd+K ouvre la palette de commandes
                  # au premier lancement, télécharge le binaire Electron (réseau requis)
pnpm core:ping    # interroge le cœur seul, sans l'app
pnpm check        # typecheck, tests et build, comme la CI
```
