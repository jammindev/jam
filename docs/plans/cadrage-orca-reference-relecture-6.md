# Relecture du cadrage `cadrage-orca-reference`, tour 6 (relecteur seul, deux axes)

Objet relu : la rédaction non commitée (`git diff`, 8 fichiers), au regard de RET-011, de la vision, des exigences, des ADR, du glossaire et du process.

Points vérifiés sans constat :
- les cinq points de RET-011 sont tous appliqués (planificateur §« Avant de commencer » et §3 du plan, `orca.md` §0, `AGENTS.md` règle 9) ; la portée (jam seulement, pas l'issue #7) est dans RET-011 ;
- les renvois aux ADR sont justes : ADR 0001 (référence de lecture, mention de licence), ADR 0005 (reprise de briques comme critère), ADR 0002 l. 25 et ADR 0004 l. 11 et 13 (PTY, TUI, Agent SDK), vision l. 49 (« On n'élague pas le code d'Orca ») ;
- les renvois de sections de la carte (§1 à §6, §9) pointent vers les bonnes parties de la note ;
- aucun chemin propre au poste, secret ni donnée personnelle dans les ajouts : le clone est toujours désigné par `<clone-orca>`, et les fichiers d'Orca par leur chemin dans le repo d'Orca ;
- numérotation libre et sans collision avec l'autre cadrage : RET-011, Q-040, Q-042, Q-043 ;
- le format de RET-011 suit celui des autres retours ; le terme nouveau « Clone de référence » est ajouté au glossaire ;
- le placement de `--add-dir` en fin de commande est correct : il arrête la liste variadique de `--disallowedTools`.

## Bloquant

Aucun.

## À corriger

### 1. L'accès de l'implémenteur au clone sort de la lettre de l'ADR 0009 sans trace dans une ADR

- **Fichiers** : `docs/specs/RETOURS.md` l. 98 et l. 102 ; `docs/decisions/0009-permissions-par-role.md` l. 19 (référence).
- **Constat** : le complément proposé reconnaît lui-même aller « au-delà de la lettre de l'ADR 0009 (« lecture et écriture dans le worktree ») ». La procédure prévue au feu vert de cadrage (l. 102) ne règle que le glossaire et le profil du planificateur. Si le mainteneur valide le complément, le tableau de l'ADR 0009 ne décrira plus la pratique, et rien ne le signalera dans les ADR. Or `AGENTS.md` dit qu'une décision actée ne se contourne pas : on propose une nouvelle ADR. Le repo l'a déjà fait pour un cas de même nature : la variante `gh` du relecteur est « tracée dans l'ADR 0012 » (`relecteur.md` l. 13). La remarque ne vise que la façon de tracer le complément, pas son existence.
- **Correction attendue** : rédiger une ADR 0014 « proposée », courte, qui précise l'ADR 0009 : l'implémenteur lit aussi le clone de référence quand le plan prévoit une reprise, sans aucune écriture hors du worktree. Au feu vert, elle est acceptée avec le complément (mention reportée au statut de l'ADR 0009, comme le prévoit le process) ou retirée s'il est refusé. Ajouter ce cas aux deux branches de la l. 102, et l'ADR 0014 à l'« Impact » de RET-011. À défaut d'ADR, la l. 102 doit au moins dire comment le statut de l'ADR 0009 portera la précision si le complément est validé.

### 2. « La carte couvre les briques d'E0 » est inexact : la fin de vie du worktree manque

- **Fichier** : `docs/references/orca.md` l. 37 (affirmation) et tableau l. 39-48.
- **Constat** : le jalon S4 (`04-ROADMAP.md` l. 46) comprend « suppression du worktree et des branches ». Orca possède cette brique (§3 « Fin de vie » : archivage, `scripts.archive` bloquant, branches non mergées gardées), que le §9 classe même « à reprendre » (« Hook d'archive bloquant », « `orca.yaml` setup/archive »). Le tableau n'a qu'une ligne « Création et nommage des worktrees », dont le point d'entrée (`worktree-add.ts`) ne couvre pas la suppression. Comme la l. 37 affirme que la carte couvre E0, la règle « le cadrage d'un jalon qui touche une autre brique la complète d'abord » ne se déclenchera pas pour le S4. Le planificateur d'une tâche de nettoyage lira alors un fichier de création, ou conclura sur une carte incomplète. Même remarque, moins grave puisque le S1 est livré, pour la configuration par repo (§3 « Préparation », `orca.yaml`).
- **Correction attendue** : au choix,
  - ajouter une ligne « Fin de vie d'un worktree (suppression, archivage) », avec un point d'entrée relevé au tag `v1.4.218` (le chemin doit être vérifié sur l'arbre du tag, comme ceux du tableau) ;
  - ou restreindre la l. 37 à ce qui est réellement couvert, par exemple « La carte couvre les briques des jalons S2 et S3. Le cadrage du S4 la complète pour la fin de vie du worktree ; celui d'un jalon qui touche une autre brique d'Orca (le diff en E3, par exemple) la complète d'abord ».

## Suggestions

### 3. Vérification du clone : exiger que la commande réussisse, pas seulement une sortie vide

- **Fichier** : `docs/references/orca.md` l. 33.
- **Constat** : `git status --porcelain` sur un dépôt abîmé (purge partielle de `.git/`) écrit son erreur sur la sortie d'erreur et rien sur la sortie standard : la condition « doit être vide » est alors remplie à tort. Le contrôle `describe` rattrape la plupart des cas, mais pas forcément tous. Par ailleurs, la suppression d'un éventuel `.claude/` (l. 29) ne figure pas dans le bloc de commandes l. 24-27, alors que c'est ce bloc que l'orchestrateur exécutera.
- **Correction proposée** : écrire « doit réussir et ne rien afficher ». Dans le bloc de commandes, ajouter une ligne commentée `rm -rf <clone-orca>/.claude  # si présent (absent au tag v1.4.218)` avant le `chmod`.

### 4. Le profil de l'implémenteur ne dit pas comment il reçoit le clone

- **Fichiers** : `docs/process/roles/implementeur.md` l. 7-11 et l. 18 ; `docs/specs/RETOURS.md` l. 102.
- **Constat** : le planificateur (l. 11) dit que sa commande se termine par `--add-dir <clone-orca>`. L'implémenteur ne parle que du chemin donné dans le brief, alors que le complément prévoit aussi `--add-dir`. C'est encore le coordinateur qui lance les rôles avec la commande du profil : il ne saura pas qu'il faut ajouter l'option.
- **Correction proposée** : dans la branche « complément validé » de la l. 102, prévoir d'ajouter au profil de l'implémenteur, sous sa commande, une phrase symétrique à celle du planificateur : « Si le plan marque un morceau repris, la commande se termine par `--add-dir <clone-orca>` ».

### 5. Glossaire : une définition, pas une réserve de procédure

- **Fichier** : `docs/specs/GLOSSARY.md` l. 35.
- **Constat** : la réserve « Ce n'est sans doute pas un contrôle d'accès… (à vérifier, Q-043) » figure déjà dans le profil du planificateur et dans RET-011. Dans une définition, elle alourdit l'entrée sans rien définir.
- **Correction proposée** : arrêter l'entrée à « … chemin dans le brief et `--add-dir` », et laisser la réserve au profil et à Q-043.

RELECTURE : CORRECTIONS (2)
