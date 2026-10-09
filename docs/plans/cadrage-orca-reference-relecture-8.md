# Relecture du cadrage `cadrage-orca-reference`, tour 8 (relecteur seul)

Objet : rédaction non commitée (`git diff`) qui applique RET-011, avec l'ADR 0014 et les deux compléments validés par le mainteneur (« ok pour tout », 2026-10-09).

Vérifié sans constat :
- Les cinq points de RET-011 se retrouvent dans les profils, dans la note Orca et dans `AGENTS.md`. Le regard ciblé est au planificateur (l. 15). La section « Orca » du plan (l. 20-23) a sa ligne pour une tâche qui ne touche aucune brique. On s'inspire par défaut et on ne copie que par exception. La liste noire figure dans le plan et au §0. Le clone est en lecture seule, à `v1.4.218`, et ouvert par `--add-dir`. La portée (jam seulement, pas l'issue #7) est dans RET-011 l. 101.
- Décision (1) : l'implémenteur lit le clone seulement en cas de reprise, sans écrire hors du worktree. C'est cohérent entre `implementeur.md` (l. 5, 11, 18), l'ADR 0014 (l. 15-16, tableau), RET-011 (l. 99) et le glossaire. L'ADR 0014 « précise » l'ADR 0009 et prévoit la mention dans son statut, sur le modèle de l'ADR 0012 et de l'étape 4 du process. L'absence de 0013 est attendue.
- Décision (2) : la carte « ne couvre que les briques relevées » (`orca.md` l. 38), et `redacteur.md` (l. 24) la fait compléter au cadrage de chaque jalon.
- La licence est cohérente avec l'ADR 0001 et la règle 9 : mention dans le fichier et dans `THIRD_PARTY_NOTICES.md`, plus stricte que le « ou » de l'ADR, sans contradiction. Le fichier source se cite par son chemin dans Orca, jamais par le chemin du clone.
- La diff ne contient aucun chemin propre au poste (`<clone-orca>` partout), ni secret ni mention d'auteur IA. Les liens relatifs ajoutés pointent tous vers des fichiers existants.
- Le §0 est cohérent avec l'ADR 0004 : l'Agent SDK est écarté, seul le format des événements est regardé. Les renvois de section (§1 à §6, §9) correspondent au contenu de la note.

## Bloquant

Aucun.

## À corriger

1. **`docs/specs/RETOURS.md`, l. 102-107 (Impact de RET-011)** : le profil du rédacteur est modifié (`docs/process/roles/redacteur.md`, l. 24 : compléter la carte au cadrage de chaque jalon), mais l'Impact ne le cite pas. Il cite pourtant les trois autres profils touchés. La traçabilité d'un retour vers ses effets est la raison d'être du journal (RET-003).
   **Correction attendue** : ajouter une ligne, par exemple « profil du [rédacteur](../process/roles/redacteur.md) : compléter la carte au cadrage d'un jalon (complément 2) ».

2. **`docs/process/roles/redacteur.md`, l. 24, et `docs/references/orca.md`, l. 21** : la règle ne dit pas d'où le rédacteur relève les fichiers qu'il ajoute à la carte. Or le §0 tient sur une promesse : « les fichiers du tableau ont été relevés à ce tag » (`v1.4.218`). Le rédacteur ne reçoit pas le clone : ni son profil, ni Q-042, ni le glossaire ne le prévoient. Il n'a pas de shell. La seule source qu'il a sous la main est le reste de la note, §1 à §9, qui décrit `main` en 1.4.214. Le §0 signale lui-même que cette source s'écarte du tag : `agent-state-rules/` est absent du tag, et `SCHEMA_VERSION` diffère. Un cadrage de jalon peut donc ajouter à la carte des chemins pris dans `main`, sous l'étiquette « relevés au tag ». Le planificateur ne s'en apercevrait qu'en cours de plan, et le relecteur du cadrage, sans clone ni réseau, ne peut pas le vérifier.
   **Correction attendue** : dans `redacteur.md` l. 24, préciser la source, à savoir les fichiers relevés à la version de référence, dans le clone dont le brief donne le chemin ou sur GitHub au tag, jamais d'après les §1 à §9. Si c'est le clone, l'ajouter aussi à la liste de Q-042 (`OPEN-QUESTIONS.md`, l. 41) et au glossaire (« Clone de référence », l. 35). Dans `orca.md` l. 21, dater chaque ajout, ou dire que chaque ligne ajoutée est relevée au même tag.

## Suggestions

3. **`docs/process/roles/planificateur.md`, l. 21** : « Le reste est **inspiré** » peut se lire comme « tout ce qui n'est pas repris est inspiré », ce qui fait disparaître la troisième catégorie, « écarté », posée deux lignes plus haut. Proposition : « Ce qui n'est ni repris ni écarté est **inspiré** ».

4. **`docs/references/orca.md`, l. 26, 30 et 34** : la suppression et l'exclusion de `.claude/` ne visent que la racine du clone. Claude Code découvre aussi des skills dans des dossiers `.claude/skills/` imbriqués quand on travaille sur des fichiers d'un sous-dossier. Il faut vérifier si cela vaut pour un dossier ouvert par `--add-dir`. Proposition : dire qu'au tag `v1.4.218` aucun `.claude/` n'existe non plus en profondeur (à vérifier par l'orchestrateur), ou en faire une sous-question de Q-043.

5. **`docs/specs/OPEN-QUESTIONS.md`, l. 40 (Q-040)** : la seconde question (une « référence de lecture » comme donnée de configuration du repo) rejoint Q-012 (l. 16), selon laquelle les profils de rôle sont « en Markdown générique ». Or le profil du planificateur contient désormais une branche propre à jam. Proposition : citer Q-012 dans Q-040, pour que le cadrage S2 traite les deux ensemble.

RELECTURE : CORRECTIONS (2)
