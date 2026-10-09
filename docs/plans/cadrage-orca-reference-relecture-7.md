# Relecture du cadrage `cadrage-orca-reference`, tour 7

Relecteur seul, les deux axes. Objet : la rédaction non commitée (`git diff`), qui applique RET-011 et ses deux compléments validés le 2026-10-09 : AGENTS.md, ADR 0014 et index des ADR, profils du planificateur, de l'implémenteur et du relecteur, `docs/references/orca.md`, glossaire, questions ouvertes, retours.

Vérifié sans constat :
- les cinq points de RET-011 sont tous appliqués. Regard ciblé : planificateur l. 15, orca.md §0 l. 19 et 36. Section « Orca » du plan : planificateur l. 20, AGENTS.md règle 9. Inspiration par défaut : planificateur l. 21, AGENTS.md règle 9. Liste noire : planificateur l. 22, orca.md l. 51. Clone en lecture seule, à version fixée, hors du repo, `--add-dir` : planificateur l. 11 et 13, orca.md l. 21 à 34 ;
- portée « tâches de jam seulement » et exclusion de l'issue #7 : RETOURS l. 101. Les règles de l'implémenteur et du relecteur ne se déclenchent que sur un morceau marqué « repris », donc sans effet sur #7 ;
- complément 1 (ADR 0014) : la formulation colle à la décision (lecture du clone seulement si le plan prévoit une reprise, aucune écriture hors du worktree). L'ADR « précise » la 0009 et prévoit la mention dans son statut, comme l'ADR 0012. Index des ADR à jour. Pas de contradiction avec la table de l'ADR 0009 ;
- complément 2 : formulé dans orca.md l. 38 et RETOURS l. 100 (voir le constat 1 sur son point d'application) ;
- cohérence avec les ADR 0001 (référence de lecture, licence), 0002 et 0004 (PTY, TUI, Agent SDK écarté), 0005 (reprise de briques), la vision (« partir du minimum », « on n'élague pas Orca ») ;
- repo public : aucun chemin propre au poste. Le clone est partout `<clone-orca>`, et les fichiers d'Orca se citent par leur chemin dans le repo d'Orca (planificateur l. 13, implémenteur l. 19) ;
- numérotation de la structure du plan (3 → 8) : aucun autre document ne renvoie à ces numéros ;
- glossaire : « Clone de référence » ajouté. Q-040, Q-042 et Q-043 sont référencés par RET-011 et par les profils qui les citent. Les absences attendues (orchestrateur de tâche, ADR 0013, Q-036 à Q-039, Q-041) ne sont pas signalées.

## Bloquant

Aucun.

## À corriger

1. **Le complément 2 n'a pas de point d'application dans le process.** `docs/references/orca.md` l. 38 (et RETOURS l. 100) : « Le cadrage de chaque jalon la complète pour ses briques avant sa première tâche. » Cette obligation ne figure que dans la note sur Orca, que ni le rédacteur ni le relecteur d'un cadrage de jalon n'ont à lire : `docs/process/roles/redacteur.md` l. 13 (« Avant de commencer, lire ») ne la cite pas, et la section « Cadrage et retours du mainteneur » de `docs/process/README.md` (l. 21 à 28) ne parle pas de la carte. RETOURS.md est bien lu par le rédacteur, mais c'est un journal, pas une procédure : au `cadrage-s2` ou au `cadrage-s4`, rien ne garantit que la carte sera complétée (par exemple, la fin de vie du worktree au S4), et le relecteur du cadrage n'a rien pour le vérifier.
   **Correction attendue** : une ligne là où le cadrage d'un jalon est décrit. Par exemple, dans les règles du rédacteur (`redacteur.md`, après l. 23) : « Cadrage d'un jalon de jam : compléter la carte de `docs/references/orca.md` (§0) pour les briques du jalon qu'Orca possède, ou dire en une ligne qu'aucune ne manque (RET-011). » Autre emplacement possible : l'étape 2 « Rédaction » de `docs/process/README.md` l. 26, si le rédacteur préfère ne pas attendre la fusion prévue par Q-042.

## Suggestions

1. `docs/process/roles/implementeur.md` l. 5 : la ligne « Permissions : lecture et écriture dans le worktree » n'a pas suivi l'ADR 0014. Le détail est plus bas (l. 11 et 18), mais un lecteur qui s'arrête à cette ligne ne voit pas la variante. Ajouter par exemple : « En cas de reprise d'Orca prévue par le plan, lecture du clone de référence ([ADR 0014](../../decisions/0014-lecture-clone-orca-implementeur.md)). »
2. `docs/references/orca.md` l. 21 : « `SCHEMA_VERSION` vaut 42 au tag, contre 43 au §2 ». Le tag (1.4.218) est plus récent que `main` en 1.4.214, mais son schéma est plus ancien. C'est cohérent avec la note de la l. 51 (des règles présentes sur `main` et absentes du tag), mais un lecteur peut y voir une coquille. Quelques mots suffiraient pour expliquer que le tag ne descend pas de ce `main`, si c'est bien le cas (à vérifier sur le dépôt d'Orca, je n'ai pas pu le faire depuis ce rôle).

RELECTURE : CORRECTIONS (1)
