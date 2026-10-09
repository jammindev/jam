# Relecture — cadrage-orchestration, tour 2

Relecteur seul, relecture d'un cadrage. Périmètre : toutes les modifications non commitées du worktree (`AGENTS.md`, `docs/decisions/README.md`, `docs/process/README.md`, profils `coordinateur`, `implementeur`, `redacteur`, `relecteur`, `04-ROADMAP.md`, `GLOSSARY.md`, `OPEN-QUESTIONS.md`, `RETOURS.md`) et les fichiers nouveaux `docs/decisions/0013-orchestration-deux-niveaux.md` et `docs/process/roles/orchestrateur-tache.md`.

Références lues : brief du rédacteur et son complément 1 (qui prime), `00-VISION`, FR-021 à FR-040 de `01-REQUIREMENTS.md`, ADR 0008, 0009 (acceptées), ADR 0012 (proposée), glossaire, process et profils.

## Fidélité aux retours et décisions du mainteneur

- **RET-008** : remarque, analyse et lancement (`JAM_ROLE=coordinateur claude` depuis le worktree principal, `git pull` après chaque merge) sont fidèlement rendus dans `RETOURS.md`, le process, le profil du coordinateur, `AGENTS.md` et l'ADR 0013.
- **RET-009** : la remarque est transcrite sans déformation. Les huit propositions sont notées comme validées le 2026-10-09 (« ça me semble OK »), et les formulations « à trancher » ont disparu du process, des profils et d'`AGENTS.md`. L'ADR 0013 et les retours restent « proposée » / « en application », comme demandé.
- **Complément 2 et 3** (mise en place immédiate, « dans jam, c'est le code qui orchestre ») : rendus dans RET-009, l'ADR 0013 (section « Correspondance avec jam »), la table de correspondance du process et le glossaire (« Lead », « Orchestrateur de tâche »). Cohérent avec l'ADR 0008, FR-021, FR-027 et FR-034 ; aucune exigence n'a été modifiée. Rien ne contredit FR-038.
- **Complément 4** : Q-039 posée, marquée non tranchée, avec la mention qu'il faudrait une nouvelle ADR.
- **Arbitrages** : feu vert relayé (option a) rendu dans `AGENTS.md`, le process, les deux profils et les conséquences de l'ADR 0013, limite de l'authentification comprise ; exception de ce cadrage décrite seulement dans l'ADR 0013 (RET-009 se contente de la mentionner) ; feu vert merge d'un cadrage présenté comme proposition dans RET-009 (voir toutefois S1).
- **Choix d'une nouvelle ADR plutôt qu'un amendement de l'ADR 0012** : justifié (ADR 0013, l. 19), et le lien avec l'ADR 0008, qui écarte une « équipe » d'agents qui dialoguent, est traité (l. 21).

## Constats

### Bloquant

Aucun.

### À corriger

**1. L'ADR 0013 étend à l'orchestrateur de tâche la session interactive, une exception à l'ADR 0009 acceptée, sans la nommer.**
- Fichiers : `docs/decisions/0013-orchestration-deux-niveaux.md`, l. 45-54 ; `docs/process/roles/orchestrateur-tache.md`, l. 10-14.
- Constat : l'ADR 0009 (acceptée) impose que toute demande hors profil soit « refusée automatiquement, sans invite ». L'ADR 0012 trace **deux** exceptions pour le coordinateur, dont la session interactive, justifiée par « le mainteneur est présent ». L'ADR 0013 ne liste qu'**une** exception pour l'orchestrateur de tâche (commit, push, PR, l. 47). La session interactive n'apparaît qu'en creux, dans la table (l. 54, « accord du mainteneur… pour toute commande hors des réglages du poste ») et dans le profil (`JAM_ROLE=orchestrateur-tache claude`, sans `--permission-mode`). Or la justification de l'ADR 0012 ne vaut pas ici : le mainteneur n'est en général pas devant le terminal d'un orchestrateur de tâche, c'est même pourquoi les conséquences (l. 87) et le process (l. 97) décrivent l'orchestrateur bloqué sur une invite que personne ne voit. Une décision actée ne se contourne pas : la dérogation doit être écrite.
- Correction attendue : dans « Exceptions et profils » de l'ADR 0013, ajouter une seconde exception à l'ADR 0009, sur le modèle de l'ADR 0012 : l'orchestrateur de tâche tourne en session interactive, avec sa propre justification (le mainteneur peut lui parler de la tâche, ce qu'une session `dontAsk` ne permet pas) et un renvoi à la conséquence (−) de la l. 87. Dans le profil, l. 14, remplacer « Comme pour le coordinateur » par un renvoi à cette exception.

### Suggestions

**S1. Le feu vert merge d'un cadrage est écrit comme une règle dans le process, alors qu'il reste une proposition ailleurs.**
- Fichiers : `docs/process/README.md`, l. 31 ; à comparer avec `docs/decisions/0013-orchestration-deux-niveaux.md`, l. 42, et `docs/specs/RETOURS.md`, l. 410.
- Le process dit « que le mainteneur donne aussi pour un cadrage (RET-009) », sans réserve ; l'ADR et RET-009 disent « proposition du rédacteur, à valider au feu vert de ce cadrage ». Ajouter la même réserve dans le process, ou prévoir explicitement que le rédacteur la retire au feu vert. Si la proposition est validée, compléter aussi « Feu vert » dans `GLOSSARY.md` (l. 26), qui ne cite que le feu vert de cadrage en amont du pipeline.

**S2. Les deux sections sur les hooks du poste se retrouvent sous « Remontée vers le coordinateur ».**
- Fichier : `docs/process/README.md`, l. 91, 99 et 107.
- La nouvelle section `## Remontée vers le coordinateur` a été insérée avant `### Hook de démarrage du poste du mainteneur` et `### Hook RTK du poste du mainteneur`, qui en deviennent des sous-sections sans rapport. Déplacer la section « Remontée » après les deux hooks (avant « Relecture »), ou rattacher les hooks à une section à eux. Au passage, ajouter une ligne vide entre la l. 75 et le titre de la l. 76.

**S3. L'avertissement « autre agent actif dans le même worktree » du hook de démarrage va se déclencher pour chaque rôle.**
- Fichier : `docs/process/README.md`, l. 103 ; `docs/specs/OPEN-QUESTIONS.md`, Q-036.
- Avec un orchestrateur de tâche qui vit dans le worktree, chaque rôle lancé verra désormais cet avertissement (constaté au démarrage de cette relecture). Il devient du bruit, ou pousse un rôle à croire qu'un autre écrit en même temps que lui. Noter ce point dans Q-036 (le hook peut reconnaître `JAM_ROLE=orchestrateur-tache` et ne pas le signaler) ou dans une nouvelle question ouverte, et en attendant indiquer dans le process que l'orchestrateur de tâche du worktree est attendu.

**S4. « Orchestrateur de tâche » couvre aussi un cadrage, que le glossaire n'appelle pas « tâche ».**
- Fichiers : `docs/specs/GLOSSARY.md`, l. 18 et l. 28 ; `docs/process/roles/orchestrateur-tache.md`, l. 3.
- Le glossaire définit une tâche comme une issue GitHub ; le profil dit « une tâche (une issue, ou un cadrage) ». Ajouter dans l'entrée « Orchestrateur de tâche » qu'il conduit aussi un cadrage, dans `cadrage-<slug>`.

**S5. Vocabulaire dans la règle 6 d'`AGENTS.md`.**
- Fichier : `AGENTS.md`, l. 40.
- « Un feu vert relayé d'un orchestrateur à l'autre » emploie « orchestrateur » pour le coordinateur, ce que le glossaire ne fait pas. Écrire « entre le coordinateur et l'orchestrateur de tâche ».

**S6. Portée de la règle du feu vert relayé.**
- Fichiers : `docs/process/README.md`, l. 96 ; `docs/process/roles/orchestrateur-tache.md`, l. 26.
- Les trois éléments (mots exacts, heure, session) ne sont exigés que pour le commit, le push, la PR et le merge. Rien ne dit si un feu vert plan ou recette relayé sans eux permet de passer à l'étape suivante. Comme les deux profils transmettent de toute façon chaque feu vert avec ces trois éléments (profil de l'orchestrateur, l. 25 ; profil du coordinateur, l. 25), il est plus simple d'exiger le format pour tout feu vert relayé.

RELECTURE : CORRECTIONS (1)
