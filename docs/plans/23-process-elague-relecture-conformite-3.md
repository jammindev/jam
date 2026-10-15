# Relecture #23, axe conformité, tour 3

Relu : tout le travail non commité de la branche (`git status`, `git diff`, fichiers non suivis), comparé au plan validé, à l'issue (brouillon K1-2 de `docs/plans/cadrage-kit-issues.md`), aux ADR 0009, 0012, 0013, 0015, 0016, 0017 et 0018, et à l'ancien `docs/process/` du worktree principal.

Tests : `python3 -m unittest`, 178 tests, OK (dont `hooks.test_plugin.MethodTest` : plafond de 4904 mots, ni `pnpm` ni `/Users/` ni `/home/` dans `process/` et `roles/`).

## Critère de fin, point par point

| Point | Verdict |
|---|---|
| `process/`, `roles/`, `process/fiche-projet.md` existent ; `docs/process/` réduit à un renvoi | OK (`docs/process/README.md`, 9 lignes, liens justes) |
| Plafond de 4904 mots | OK (test vert) ; les nombres avant et après restent à écrire dans la PR |
| Ni `pnpm`, ni chemin, ni nom d'hôte ou d'autre projet dans `process/` et `roles/` | OK (Grep sur noms de projets, d'hôtes, de personnes et chemins : rien) |
| Règles du point 3 dans le process et dans le profil qui les applique, avec leur référence | OK : niveaux (process, coordinateur, planificateur, FR-049) ; *léger* (process, coordinateur, FR-052) ; seuil (process, relecteur, orchestrateur, coordinateur, FR-050) ; plafonds (process, coordinateur, orchestrateur, FR-051) ; relais (process, coordinateur, orchestrateur, FR-053) ; recette d'interface (process, recetteur, FR-054) ; mesure (process, coordinateur, orchestrateur, FR-055 / RET-018) ; ADR 0017 (lancement par Orca, Q-058, fenêtre d'autorisation : process et coordinateur, orchestrateur pour Q-058) |
| Planificateur : niveau motivé quand une tâche monte | OK (`roles/planificateur.md:16`) |
| Règle 6 d'`AGENTS.md` cohérente avec FR-052 et FR-053 | OK sur le fond (voir suggestion 2 sur la forme) |
| `docs/methode.md` au niveau *léger* | OK |
| Q-058 tranchée, cohérente avec l'orchestrateur de tâche et les ADR | OK : OPEN-QUESTIONS, ADR 0018, process l. 35, `roles/orchestrateur-tache.md:7` et `:18`, mention de statut prévue pour l'ADR 0013 |
| NFR-016 : origines remplacées par un renvoi, règles nouvelles avec ce qu'elles remplacent | OK, sauf le constat 1 et la suggestion 3 |
| ADR existantes : seuls les liens changent | OK (0009, 0012, 0013 : liens ; index : une ligne) |
| Liens vers l'ancien `docs/process/` hors `docs/plans/` | OK, aucun lien cassé |
| Règles propres à jam sorties des profils | OK (section « Orca », clone de référence, `--plugin-dir`, nommage des worktrees : `docs/methode.md`) |

## Bloquant

Aucun.

## À corriger

### 1. Le profil du coordinateur perd l'exception « installation d'un hook relu » de l'ADR 0012, sans trace

- **Fichier** : `roles/coordinateur.md:9`.
- **Constat** : l'ancien profil autorisait l'écriture « pour installer un hook déjà relu » (exception de l'ADR 0012, acceptée). Le nouveau dit : « Écriture de fichiers seulement dans sa mémoire, le plan de la session et les dossiers temporaires : la garde du coordinateur refuse le reste. » Or la garde n'a pas changé (le plan exclut tout changement de comportement des gardes) : elle permet toujours cette installation, et son message de refus la cite encore (`hooks/guard_coordinator.py`, fonction `fail`). L'ADR 0018 ne cite pas ce retrait, ni dans son tableau ni dans « Retirés sans remplacement » (l. 67), qui ne mentionne que la garde de l'orchestrateur de tâche (Q-056).
- **Viole** : NFR-016 (une règle retirée dit ce qu'elle retire, dans une ADR) et le point « aucune décision d'une ADR acceptée perdue sans être actée ».
- **Scénario d'échec** : le mainteneur demande au coordinateur d'installer un correctif de hook déjà relu (copie de `hooks-staging/` vers `~/.claude/hooks/`). Le coordinateur lit son profil, qui dit que la garde refuse tout le reste, et refuse ou lance un rôle pour rien, alors que la garde l'aurait laissé faire. À l'inverse, un relecteur qui compare le profil au message de la garde trouve deux règles contraires, sans ADR pour départager.
- **Correction attendue** (une des deux) : ajouter au profil, l. 9, « et l'installation d'un hook relu (ADR 0012, Q-056) » ; ou ajouter ce retrait à la liste « Retirés sans remplacement » de l'ADR 0018, en renvoyant à Q-056 pour le sort de l'exception dans la garde. La première garde le profil d'accord avec la garde, inchangée.

## Suggestions

1. **Retour `💬` venu d'un cadrage** (`roles/coordinateur.md:21`, `process/README.md:35`). L'ancien process disait : « Si sa tâche est un cadrage, il le transmet au rédacteur ; sinon, le coordinateur le confie à un cadrage. » Le nouveau process a perdu le « sinon », et le profil du coordinateur dit seulement « Un retour signalé par `💬` est confié à un cadrage ». Risque : un retour reçu dans `cadrage-x`, déjà transmis au rédacteur, est confié à un second cadrage, d'où deux RET pour une remarque. Ajouter « sauf s'il vient d'un cadrage, dont le rédacteur l'inscrit ». (L'ancien profil du coordinateur avait déjà ce flou : ce n'est pas un recul introduit par cette tâche, d'où le classement en suggestion.)
2. **Règle 6 d'`AGENTS.md`** (l. 38) : « pour le merge, celui de jam compris (fiche) » se lit comme une règle valable pour le merge de tout projet. FR-053 réserve la forme complète au merge d'un projet en production ; c'est la fiche de jam qui l'exige pour jam. Écrire par exemple « pour le merge (la fiche de jam exige la forme complète, bien que jam ne soit pas en production) ».
3. **ADR 0018, ce qui est retiré** (l. 40 à 67) : trois changements du process n'y figurent pas. (a) Le critère d'arrêt « budget de l'étape dépassé » de la boucle de relecture, que l'ancien process jugeait déjà inapplicable dans Orca ; (b) « pas de nombre de tours fixé (RET-006) », que le plan met hors périmètre ; (c) la règle d'écriture du relecteur, passée de `Edit(docs/plans/*-relecture*.md)` au seul nom exact de son rapport, ce qui ferme la limite « le relecteur peut réécrire les rapports des tours précédents » de l'ancienne section « Ce qu'Orca ne permet pas ». Une ligne dans « Retirés sans remplacement » pour (a) et (b), une ligne du tableau pour (c).
4. **Coordinateur au niveau *léger*** (`roles/coordinateur.md:19`) : il lance lui-même les rôles, mais son profil ne reprend ni « il ferme le terminal d'un rôle dès sa ligne de fin » ni le remplacement de `<tâche>` et `<commande de test>` dans la commande du profil. Le profil de l'orchestrateur de tâche les a (l. 14 et 15) ; le process couvre la fermeture (l. 53). Ajouter les deux à la règle *léger*, pour que le coordinateur n'ait pas à les déduire.
5. **FR-050** (`docs/specs/01-REQUIREMENTS.md:19`) dit encore « ne trouve que du cosmétique ». Le glossaire et l'ADR 0018 définissent désormais le seuil (scénario d'échec ou exigence citée). Ajouter « précisé par l'ADR 0018 » dans la colonne d'origine éviterait qu'un lecteur des exigences reste sur l'ancienne formule.

RELECTURE : CORRECTIONS (1)
