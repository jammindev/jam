# Relecture du cadrage `cadrage-orca-reference`, tour 5

Relecteur seul, les deux axes. Objet : la rédaction non commitée (8 fichiers) qui applique RET-011.

Vérifié sans constat :
- les cinq points validés par le mainteneur se retrouvent dans le profil du planificateur, la carte (§0 de `docs/references/orca.md`), `AGENTS.md` (règle 9) et RET-011 ;
- c'est cohérent avec l'ADR 0001 (référence de lecture, licence), les ADR 0002 et 0004 (liste noire), l'ADR 0009 pour le planificateur (aucune écriture ajoutée) et le principe « partir du minimum » ;
- portée : jam seulement, pas l'issue #7 ;
- repo public : aucun chemin propre au poste, le clone est toujours désigné par `<clone-orca>` ;
- numérotation : RET-011, Q-040, Q-042 et Q-043, sans collision avec l'autre cadrage ;
- glossaire : « Clone de référence » est défini et employé partout de la même façon ;
- la procédure du clone tient : `git status` fonctionne sur un dépôt en lecture seule, et `describe --exact-match` fonctionne sur un clone superficiel pris au tag.

## Bloquant

Aucun.

## À corriger

### 1. `docs/process/roles/planificateur.md`, ligne 22 : la mention de licence se rattache à « inspiré »

La phrase enchaîne « Ne marquer **repris** qu'un petit morceau… ; sinon, le marquer **inspiré** et décrire ce qu'il faut réécrire ; l'implémenteur y ajoute la mention de licence (…), et `THIRD_PARTY_NOTICES.md` figure alors dans les fichiers créés ou modifiés ». Dans cet ordre, « y » et « alors » renvoient au cas **inspiré**. Un planificateur peut donc demander une mention de licence et une entrée dans `THIRD_PARTY_NOTICES.md` pour du code réécrit. Cela contredit le profil de l'implémenteur (ligne 19 : seulement pour un morceau repris) et le point 3 de RET-011 (« sinon, on réécrit »).

**Correction attendue** : placer la clause de licence juste après le cas repris, et dire que le cas inspiré n'en a pas. Par exemple : « Ne marquer **repris** qu'un petit morceau autonome, en citant son fichier source, et seulement si l'implémenteur reçoit le clone (complément proposé, RET-011). Pour un morceau repris, l'implémenteur ajoute la mention de licence (`AGENTS.md`, règle 9), et `THIRD_PARTY_NOTICES.md` figure dans les fichiers créés ou modifiés. Sinon, le marquer **inspiré** et décrire ce qu'il faut réécrire : pas de mention de licence. »

### 2. `docs/references/orca.md`, lignes 37 et 46 : la carte ne couvre pas toutes les briques d'E0

La ligne 37 dit : « La carte couvre les briques d'E0 ». Or la brique 5 d'E0, « File « À toi » et notifications filtrées » (`04-ROADMAP.md`, ligne 23, jalon S3), n'a pas de point d'entrée. La ligne 46 l'écarte : « pas les notifications, sans point d'entrée relevé ». Pourtant Orca la possède : le §4.5 décrit ses notifications, l'état `isUnread` et le kanban « Needs You ». RET-011 (ligne 90) cite d'ailleurs les notifications parmi ce qu'Orca a déjà résolu.

Pour une tâche du S3 sur les notifications, le planificateur se retrouve coincé. Soit il écrit « aucune brique d'Orca » d'après la carte, ce qui est faux. Soit il explore hors de la carte, ce que son profil interdit (ligne 16). La règle de complément de la ligne 37 ne vise que les briques d'**autres** jalons (« une autre brique d'Orca (le diff en E3…) »). Elle ne couvre donc pas ce cas.

**Correction attendue**, au choix :
- ajouter une ligne « File « À toi », notifications » au tableau, avec un point d'entrée relevé au tag ;
- ou écrire à la ligne 37 que la carte couvre les briques d'E0 **sauf** la file « À toi » et les notifications (brique 5), et que le cadrage du S3 la complète d'abord, puis aligner la ligne 46.

## Suggestions

### 3. `docs/process/roles/implementeur.md`, ligne 18 : laisser un seul comportement quand le clone manque

« Ne rien reprendre, et signaler l'écart avant de réécrire, ou s'arrêter sur `BLOQUÉ : clone de référence absent` » laisse le choix à l'agent, sans critère. De plus, en `dontAsk`, « signaler avant de réécrire » n'a pas de canal : l'implémenteur ne peut signaler que dans sa sortie finale, donc après coup.

Proposition : un seul comportement, `BLOQUÉ : clone de référence absent`. Le plan validé prévoit une copie : la remplacer par une réécriture serait un écart non validé. Et la cause est une erreur de lancement, vite corrigée par l'orchestrateur de tâche.

### 4. `docs/process/roles/implementeur.md`, lignes 7 à 11 : la commande ne mentionne pas `--add-dir`

Le planificateur le mentionne sous sa commande (ligne 11), comme le glossaire (ligne 35 : « chemin dans le brief et `--add-dir` ») et RET-011 (ligne 98). Le profil de l'implémenteur n'en parle pas. Le mainteneur, qui lit les profils pour savoir ce que chaque rôle reçoit, ne voit donc pas cet accès.

Proposition : ajouter sous la commande « Si le plan marque un morceau repris, l'orchestrateur de tâche ajoute `--add-dir <clone-orca>` (complément proposé, RET-011) ». Ajouter aussi cette ligne à la liste de ce que le rédacteur retire si le complément est refusé (RETOURS, ligne 102).

### 5. `docs/process/roles/planificateur.md`, ligne 11 : phrase en double et mal placée

La phrase insérée sépare le bloc de commande de la phrase suivante (« Chaque commande shell figure aussi sous sa forme `rtk …` »), qui se rapporte à ce bloc. Elle répète en outre le paragraphe « Clone de référence d'Orca » (ligne 14). Proposition : la supprimer, ou la placer après la ligne 12.

### 6. `docs/specs/RETOURS.md`, ligne 98 : dire franchement l'écart avec la lettre de l'ADR 0009

« Il lit hors du worktree sans y écrire, ce qui reste dans l'esprit de l'ADR 0009. » Or le tableau de l'ADR 0009 (ligne 19) donne à l'implémenteur « Lecture et écriture dans le worktree ». Le complément dépasse donc la lettre de l'ADR pour la lecture.

Proposition : l'écrire tel quel, pour que le mainteneur tranche en connaissance de cause. Si le complément est validé, prévoir au feu vert une mention dans le statut de l'ADR 0009. L'étape 4 du cadrage le permet (`docs/process/README.md`, ligne 28).

### 7. `docs/specs/RETOURS.md`, ligne 102 : branche « refusé » incomplète

Si le complément est refusé, seuls le glossaire et le profil du planificateur sont ajustés. Plusieurs textes resteraient alors sans objet : la règle 9 d'`AGENTS.md` (« on ne copie qu'un petit morceau autonome »), les deux règles de reprise de l'implémenteur (lignes 18 et 19) et le point 5 du relecteur. Ils ne seraient pas faux, mais inertes.

Proposition : dire explicitement, dans cette branche, s'ils restent en l'état (par exemple, en attente d'une voie de reprise) ou s'ils sont allégés.

RELECTURE : CORRECTIONS (2)
