# Relecture du cadrage `cadrage-orca-reference`, tour 9

Relecteur seul, les deux axes. Objet : la rédaction non commitée (`AGENTS.md`, `docs/decisions/0014-*.md`, `docs/decisions/README.md`, profils du planificateur, de l'implémenteur, du rédacteur et du relecteur, `docs/references/orca.md`, `GLOSSARY.md`, `OPEN-QUESTIONS.md`, `RETOURS.md`), relue contre RET-011 et les décisions du mainteneur du 2026-10-09.

## Vérifications faites

- **Les cinq points de RET-011** sont appliqués et tracés :
  1. regard ciblé : profil du planificateur, l. 15, et `orca.md`, §0, l. 19 et 36 (points d'entrée, quelques fichiers) ;
  2. section « Orca » du plan : profil du planificateur, l. 20, avec la ligne unique quand aucune brique n'est touchée ; `AGENTS.md`, règle 9 ;
  3. s'inspirer par défaut, copier par exception : planificateur, l. 21 ; implémenteur (mention de licence, `THIRD_PARTY_NOTICES.md`) ; `AGENTS.md`, règle 9 ;
  4. liste noire : planificateur, l. 22, et `orca.md`, l. 51, avec renvoi aux ADR 0002 et 0004, qui disent bien que le PTY et la détection d'état d'une TUI sont la partie fragile (ADR 0002, l. 25 ; ADR 0004, l. 11) ;
  5. clone en lecture seule, version fixée, hors du repo, `--add-dir` : planificateur, l. 11 et 13 ; `orca.md`, l. 23 à 34. Aucun chemin propre au poste dans les docs : le clone est toujours `<clone-orca>`, et les fichiers d'Orca sont cités par leur chemin dans le repo d'Orca.
- **Portée** : tâches de jam seulement, pas l'issue #7 (RET-011, « Portée »). Les profils le disent (« pour les tâches de jam seulement »).
- **Décision (1) du mainteneur** : l'ADR 0014 est « proposée », précise l'ADR 0009 sans la contredire (aucune écriture ajoutée), suit le format de l'ADR 0012 (table de profil, mention à reporter dans le statut de l'ADR 0009 à l'acceptation, conforme au process, l. 28). Le profil de l'implémenteur la reflète (permissions, `--add-dir` seulement en cas de reprise, `BLOQUÉ : clone de référence absent` si le chemin manque). L'index des ADR est à jour ; l'absence de 0013 est attendue.
- **Décision (2) du mainteneur** : `orca.md`, l. 38, dit que la carte ne couvre que les briques relevées, et le profil du rédacteur, l. 24, lui fait compléter la carte au cadrage de chaque jalon, au tag de référence.
- **Cohérence avec la vision et les ADR** : « on n'élague pas Orca » est bien dans `00-VISION.md`, l. 49 ; l'ADR 0005 parle bien de la reprise des briques d'Orca (l. 15 et 24), comme le dit l'analyse de RET-011 ; R-03 existe dans la roadmap ; Q-012 existe.
- **Vocabulaire** : « Clone de référence » ajouté au glossaire, statut « Provisoire ». « Orchestrateur de tâche » n'est pas défini ici, ce qui est attendu (autre cadrage) ; Q-042 trace la fusion.
- **Numérotation** : RET-011, Q-040, Q-042, Q-043 et ADR 0014 sont dans la plage réservée à ce cadrage.
- **Vérifiabilité** : chaque règle se contrôle sur un livrable (section « Orca » du plan, en-tête de licence, entrée dans `THIRD_PARTY_NOTICES.md`, `--add-dir` dans la commande, état du clone vérifié par `git status` et `git describe`). Les limites connues (règle `"Read"` non restreinte par chemin, droits de fichiers contournables par `node -e`) sont dites dans l'ADR 0014 et suivies dans Q-043 et R-03.
- **Repo public** : aucun secret, donnée personnelle ou chemin machine dans le diff.
- **Sur-ingénierie** : rien au-delà de RET-011 et des deux compléments validés ; la configuration d'une « référence de lecture » dans jam est renvoyée à Q-040.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestion

1. **`docs/references/orca.md`, l. 26 et 30** : la note dit avoir vérifié l'absence de `.claude/` « ni à la racine ni en profondeur », puis que, dans une version future, « il est supprimé avant le `chmod` ». Or la commande en commentaire (`rm -rf <clone-orca>/.claude`) et l'exclusion de la vérification (`':!.claude'`, l. 34) ne visent que la racine. Un `.claude/` imbriqué dans une version future resterait, alors que Claude Code peut y découvrir des skills. Le risque est futur et une montée de version oblige à relire la note (Q-040). Correction proposée, au choix : écrire « s'il en a un **à la racine** », ou ajouter à la l. 30 « un `.claude/` en profondeur se traite au moment de la montée de version (Q-040) ».

2. **`docs/references/orca.md`, l. 34**, dernière phrase : « Un fichier absent d'un clone vérifié est donc un vrai écart de version. » Elle ne dit pas avec quoi on compare. Pour un fichier cité aux §1 à §9 (relevés sur `main` en 1.4.214), c'est bien un écart de version ; pour un fichier de la carte, relevé au tag, ce serait une erreur de la carte. Correction proposée : « Un fichier cité aux §1 à §9 et absent d'un clone vérifié est donc un vrai écart de version, à signaler dans le plan ; un fichier de la carte absent est une erreur de la carte, à signaler au coordinateur. »

RELECTURE : OK
