# Relecture du cadrage `cadrage-orca-reference`, tour 4

Relecteur seul, les deux axes, en mode « relecture d'un cadrage ». Objet : la rédaction non commitée (8 fichiers) qui applique RET-011.

## Vérifié, sans constat

- Les cinq points de la règle validée par le mainteneur sont tous repris : regard ciblé à partir de la carte (`planificateur.md:15`, `orca.md:19`, `orca.md:35`), section « Orca » avec repris / inspiré / écarté et une ligne si aucune brique n'est touchée (`planificateur.md:20`), inspiration par défaut et copie d'un petit morceau autonome avec licence (`planificateur.md:21`, `AGENTS.md:42`), liste noire PTY et TUI (`planificateur.md:22`, `orca.md:49`), clone en lecture seule à version fixée, hors du repo, ouvert par `--add-dir` (`planificateur.md:13`, `orca.md:23-33`).
- La portée est respectée : tâches de jam seulement, pas l'issue #7, dès la tâche suivante (`RETOURS.md:101`).
- Cohérence avec les ADR : ADR 0001 (référence de lecture, licence, pas d'élagage d'Orca, repris aussi par la vision, `00-VISION.md:49`), ADR 0002 et 0004 (liste noire, Agent SDK écarté dans la carte, `orca.md:44`), ADR 0005 (reprise de briques), ADR 0009 (aucune écriture ajoutée au planificateur). L'absence de nouvelle ADR est justifiée (`RETOURS.md:97`).
- Repo public : aucun chemin propre au poste. Le clone est désigné par `<clone-orca>`, et les profils imposent de citer les fichiers d'Orca par leur chemin dans le repo d'Orca (`planificateur.md:13`, `implementeur.md:18`).
- L'affirmation « rien n'a été repris jusqu'ici » (`RETOURS.md:88`) est exacte : hors `docs/`, seuls `AGENTS.md` et `LICENSE` mentionnent Orca ou un copyright, et `THIRD_PARTY_NOTICES.md` n'existe pas.
- La renumérotation de la structure du plan (3 à 8) ne casse aucun renvoi dans `docs/specs/`, `docs/process/` ou `docs/decisions/`.
- La brique « Persistance SQLite (`node:sqlite`) » de la carte est conforme à l'ADR 0010 et à `02-ARCHITECTURE.md:55`.
- Questions ouvertes : Q-040, Q-042, Q-043 ont un thème, un responsable et un statut ; l'étape « E0 S2 » de Q-040 se justifie (S2 lance le planificateur avec son profil).
- Vocabulaire : « Clone de référence » ajouté au glossaire en « Provisoire ». L'absence de « orchestrateur de tâche » est attendue (autre cadrage, Q-042).

## Constats

### Bloquant

Aucun.

### À corriger

**C1. Le cas « l'implémenteur n'a pas le clone » n'est traité que du côté de l'implémenteur, et sa consigne contredit le plan.**
- Fichiers : `docs/process/roles/planificateur.md:21` et `docs/process/roles/implementeur.md:18`.
- Problème : le planificateur peut marquer **repris** un morceau d'Orca sans savoir si l'implémenteur aura accès au clone. Si le complément est refusé, le profil de l'implémenteur dit « il ne reprend rien et s'en tient à ce que le plan décrit ». Mais le plan décrit justement une reprise. L'implémenteur ne peut donc ni suivre le plan, ni appliquer la règle de son profil « Tout écart est signalé et justifié » (`implementeur.md:14`), puisque rien ne lui dit qu'il s'agit d'un écart. Le résultat serait une reprise abandonnée en silence, ou une réécriture de mémoire présentée comme conforme au plan.
- Correction attendue :
  - dans `planificateur.md:21`, ajouter qu'un morceau ne se marque **repris** que si l'implémenteur reçoit le clone (complément proposé, RET-011). Sinon, il se marque **inspiré**, et le plan décrit ce qu'il faut réécrire ;
  - dans `implementeur.md:18`, remplacer « il ne reprend rien et s'en tient à ce que le plan décrit » par : si le plan marque un morceau **repris** et que le brief ne donne pas le chemin du clone, l'implémenteur ne reprend rien, et il signale l'écart avant de réécrire ou s'arrête sur `BLOQUÉ : clone de référence absent`.

**C2. La consigne de l'implémenteur dépend d'une décision qu'il ne peut pas connaître, et rien ne prévoit de la nettoyer au feu vert.**
- Fichiers : `docs/process/roles/implementeur.md:18`, `docs/specs/GLOSSARY.md:35`, `docs/specs/RETOURS.md:98`.
- Problème : le profil dit « complément proposé dans RET-011, à valider au feu vert de cadrage » et « Si ce complément est refusé… ». Un implémenteur lancé plus tard n'a aucun moyen de savoir si le complément a été validé ou refusé. Le seul fait qu'il observe, c'est le brief, qui contient ou non le chemin du clone. Par ailleurs, l'étape 4 du cadrage (`docs/process/README.md:28`) fait passer les ADR à « acceptée » et les retours à « appliqué », mais ne prévoit pas de retirer une mention « à valider » d'un profil ou du glossaire. Elle risque donc de rester après la décision.
- Correction attendue :
  - formuler la règle de l'implémenteur sur le fait observable : « Si le brief donne le chemin du clone de référence… ; sinon… » (voir C1). Garder la référence à RET-011, sans la formule « si ce complément est refusé » ;
  - dans `RETOURS.md` (complément proposé), dire en une ligne ce que le rédacteur change au feu vert de cadrage. Si le complément est validé : retirer les mentions « complément proposé / à valider » de `implementeur.md` et de `GLOSSARY.md`. S'il est refusé : retirer de ces deux fichiers l'accès de l'implémenteur au clone, et appliquer la variante de C1 où le planificateur ne marque jamais « repris ».

### Suggestions

**S1. Le `--add-dir` n'apparaît que dans la prose, pas dans les blocs de commande.**
`planificateur.md:9`, et `implementeur.md:9` si le complément est validé. Le coordinateur (et, plus tard, l'orchestrateur de tâche) lance un rôle en recopiant la commande du profil (`docs/process/README.md:53`). Ajouter dans le bloc, ou juste sous lui, la forme complète pour les tâches de jam, par exemple `… --add-dir <clone-orca>`. Le risque d'un oubli au lancement disparaît. Q-042 couvre la fusion, mais pas le bloc de commande lui-même.

**S2. « En tête du fichier repris » colle mal à « un petit morceau autonome ».**
`implementeur.md:18`. La règle du planificateur (`planificateur.md:21`) vise un petit morceau, qui atterrira souvent dans un fichier de jam plutôt que de former un fichier entier. Écrire « en tête du fichier de jam qui contient le morceau repris (mention de copyright d'Orca, licence MIT, fichier source et version) ». Faire de même pour « la liste des fichiers repris » de `THIRD_PARTY_NOTICES.md` : « la liste des morceaux repris, avec le fichier de jam qui les contient, leur fichier source et la version de référence ».

**S3. La règle 9 d'`AGENTS.md` ne mentionne pas la ligne « aucune brique d'Orca ».**
`AGENTS.md:42`. La règle dit « Quand une tâche touche une brique qu'Orca possède, le plan dit… ». Le profil, lui, exige une section « Orca » pour toute tâche de jam, réduite à une ligne si aucune brique n'est touchée (`planificateur.md:20`, RET-011 point 2). Un agent qui ne lit qu'`AGENTS.md` pourrait omettre la section. Écrire par exemple : « Le plan de chaque tâche de jam a une section « Orca » : ce qu'on reprend, ce dont on s'inspire, ce qu'on écarte, ou une ligne si la tâche ne touche aucune brique d'Orca ».

**S4. La ligne « Notifications » de la carte n'a pas de point d'entrée pour les notifications.**
`docs/references/orca.md:46`. Le seul point d'entrée est `src/shared/agent-status-types.ts` (« modèle à 4 états seulement »), c'est-à-dire le statut, pas le déclenchement d'une notification (passage working → idle, son, badge, `isUnread`, §4.5). Or les notifications filtrées sont une brique d'E0 (roadmap, brique 5). Deux options : ajouter au tag `v1.4.218` le fichier qui émet la notification système, ou renommer la brique « Statut par worktree » pour que la carte ne promette pas plus qu'elle ne pointe. Je n'ai pas pu vérifier l'arbre d'Orca : le chemin est à relever par l'orchestrateur.

**S5. « Il le supprime et le refait » : la suppression d'un clone sans droit d'écriture demande d'abord de les remettre.**
`docs/references/orca.md:33`. Le point précédent (`orca.md:32`) le dit pour un changement de version (`chmod -R u+w`, puis suppression), mais pas ici. Écrire « il le supprime (comme ci-dessus) et le refait ».

**S6. La section « Incertitudes » ne tient pas compte du §0.**
`docs/references/orca.md:473`. « Écart de version entre `main` (1.4.214) et l'app installée (1.4.218) » : le §0 relève désormais la carte au tag et donne un exemple d'écart (`SCHEMA_VERSION` 42 contre 43, règles d'écran absentes au tag). Préciser que cet écart ne concerne plus que les §1 à §9, la carte du §0 étant relevée au tag.

RELECTURE : CORRECTIONS (2)
