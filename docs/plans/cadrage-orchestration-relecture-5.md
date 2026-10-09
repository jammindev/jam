# Relecture — cadrage `cadrage-orchestration`, tour 5

> Relecteur seul, relecture d'un cadrage. Périmètre : toutes les modifications non commitées du worktree (12 fichiers modifiés, plus l'ADR 0013, le profil `orchestrateur-tache.md` et le brouillon `cadrage-orchestration-issues.md`). Références : les trois briefs du rédacteur, et les décisions ajoutées depuis (format du feu vert relayé étendu à tout feu vert relayé ; un feu vert relayé ne vaut accord que pour l'action qu'il ouvre). Fait vérifié par le coordinateur : le milestone « E0-S1 Squelette » est encore ouvert.

## Vérifié sans constat

- **Fidélité à RET-008** : coordinateur sur `main`, lancé depuis un terminal Orca du worktree principal, `git pull` après chaque merge (process, profil du coordinateur, ADR 0013, `AGENTS.md`).
- **Fidélité à RET-009** : les huit propositions sont présentées comme validées, les formules « à trancher » ont disparu. L'ADR 0013 reste « proposée », RET-008, RET-009 et RET-010 restent « en application ». Les compléments (mise en place immédiate, « dans jam, c'est le code qui orchestre », Q-039 non tranchée) sont repris dans RET-009, l'ADR 0013 (« Correspondance avec jam »), la table de correspondance du process et le glossaire (« Lead », « Orchestrateur de tâche », « Coordinateur »).
- **Décisions ajoutées depuis** : le format (mots exacts, heure, session) vaut pour tout feu vert relayé, et la portée est limitée à l'action ouverte, dans le process (« Format de tout feu vert relayé »), l'ADR 0013 (« Feu vert relayé »), RET-009, et par renvoi dans les deux profils d'orchestration. La limite (expéditeur non authentifié) est dans les conséquences (−) de l'ADR 0013.
- **Exception de ce cadrage** : décrite seulement dans l'ADR 0013, comme arbitré.
- **ADR acceptées** : l'ADR 0008 tient (le cœur orchestre dans jam ; l'objection « équipe d'agents permanents » est traitée dans le contexte de l'ADR 0013). L'ADR 0009 est complétée par deux exceptions tracées, avec mention prévue dans son statut à l'acceptation. Aucune exigence n'est modifiée, ce qui est cohérent avec FR-021, FR-027, FR-029, FR-034 et FR-040.
- **RET-010** : règle sobre, sans mécanisme nouveau, reprise dans le profil du recetteur, la section « Recette » du process et Q-033. Le recetteur reste en lecture seule sur les fichiers suivis par git.
- **Brouillon d'issue** : un seul bug, un petit lot (ADR 0011). Le critère de fin est vérifiable (`node_modules` supprimé, `pnpm install`, `pnpm dev` ouvre la fenêtre). Les scripts cités existent (`dev`, `check`, `core:ping` dans `package.json`), et le rapport de recette cité existe. Le choix technique est laissé au planificateur.
- **Glossaire** : les termes nouveaux (« Orchestrateur de tâche », « Agent actif ») sont définis et employés de façon constante.
- **Repo public** : ni secret, ni donnée personnelle, ni chemin propre à une machine (les chemins sont génériques : `<chemin du worktree>`).

## Bloquant

Aucun.

## À corriger

1. **`AGENTS.md`, ligne 40 (règle 6) : la portée d'un feu vert relayé manque, et « après un feu vert » est trop large.**
   La règle 6 est celle qui définit l'« accord explicite ». Elle dit « Après un feu vert, l'orchestrateur de tâche committe, pousse sa branche et ouvre la PR », puis « Un feu vert relayé […] ne vaut que s'il cite les mots exacts […] ». Lue seule, elle laisse entendre qu'un feu vert quelconque, y compris le feu vert plan, ouvre le commit, et qu'un feu vert relayé au bon format vaut accord sans restriction. Or la décision du mainteneur, reprise dans le process et l'ADR 0013, limite l'accord à l'action que ce feu vert ouvre, et le feu vert plan n'en ouvre aucune. La règle d'entrée du repo contredit donc, par omission, la décision.
   **Correction attendue** : préciser le feu vert et la portée, par exemple : « Après le feu vert recette (ou de cadrage), l'orchestrateur de tâche committe, pousse sa branche et ouvre la PR ; seul le coordinateur merge, après le feu vert merge (ADR 0012, ADR 0013). Un feu vert relayé entre le coordinateur et l'orchestrateur de tâche ne vaut que s'il cite les mots exacts du mainteneur, l'heure et la session où il l'a donné, et seulement pour l'action que ce feu vert ouvre (voir « Remontée vers le coordinateur » dans `docs/process/README.md`). »

## Suggestions

1. **`docs/plans/cadrage-orchestration-issues.md`, ligne 8 : trancher le milestone.** Le coordinateur a vérifié que « E0-S1 Squelette » est encore ouvert. La condition « s'il est encore ouvert, sinon S2 » et la phrase « le coordinateur le vérifie à la publication » peuvent laisser place à : « **Milestone** : `E0-S1 Squelette` (encore ouvert). Le bug rend faux, sur une installation neuve, le critère du S1 « L'app se lance ». » Le coordinateur n'aura plus de choix à faire à la publication.

2. **`docs/specs/04-ROADMAP.md`, ligne 39 : « Seul le S1 fait exception : une seule issue ».** Si l'issue du bug est rattachée au S1, cette phrase devient inexacte. On peut la préciser, par exemple : « Seul le S1 fait exception : une seule issue de départ, dont le plan était déjà validé, plus le correctif né de sa recette (RET-010). »

3. **`docs/process/README.md`, ligne 31 : cas où le feu vert merge d'un cadrage est refusé.** La consigne « Si la proposition est refusée, il retire la phrase » ne suffit pas : la liste de « Format de tout feu vert relayé » (ligne 119, « merge après le feu vert merge ») et la table de l'ADR 0013 ne prévoiraient alors aucun feu vert qui ouvre le merge d'une PR de cadrage. On peut ajouter que, en cas de refus, le feu vert de cadrage ouvre aussi le merge de sa PR, et l'écrire au même endroit que les autres actions.

4. **`docs/process/README.md`, ligne 31 : ordre publication / merge d'un cadrage.** Le coordinateur publie les issues après le feu vert de cadrage, donc avant le merge de la PR. Une issue publiée peut alors renvoyer à des docs (RET, ADR, process) qui ne sont pas encore sur `main`. Si c'est voulu, une demi-phrase suffit ; sinon, publier après le merge.

RELECTURE : CORRECTIONS (1)
