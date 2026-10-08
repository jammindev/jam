# jam

> Nom provisoire.

Un cockpit de *loop engineering*. Pour chaque issue GitHub, l'outil ouvre un worktree et y fait travailler des rôles d'agents : plan, TDD, relecture, recette. Il les accompagne jusqu'au merge et n'interrompt l'humain que pour trois feux verts.

Le projet avance en deux boucles :

- **la boucle extérieure** (le pipeline) d'abord, qui fait travailler Claude Code ;
- **la boucle intérieure** ensuite : un harness d'agent maison.

Statut : E0, jalon S1 (squelette). Voir [`docs/specs/`](docs/specs/) et [`docs/decisions/`](docs/decisions/).

## Démarrer

Prérequis : macOS, Node 24.21 (voir `.node-version`) et pnpm.

```sh
pnpm install      # dépendances
pnpm dev          # lance l'app ; Cmd+K ouvre la palette de commandes
pnpm core:ping    # interroge le cœur seul, sans l'app
pnpm check        # typecheck, tests et build, comme la CI
```

Licence : [MIT](LICENSE).
