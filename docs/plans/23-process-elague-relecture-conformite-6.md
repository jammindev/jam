# Relecture #23 — axe conformité, tour 6

Relu : tout le travail non commité de la branche (`git status`, `git diff`, et les fichiers non suivis : `process/fiche-projet.md`, `scripts/maintainer_time.py` et ses tests, `docs/methode.md`, `docs/decisions/0018-process-elague.md`, `docs/concepts/veille-et-mesure.md`, `docs/process/README.md`). Références : le plan validé (`docs/plans/23-process-elague.md`, les six points en tête), le brouillon de l'issue K1-2 (`docs/plans/cadrage-kit-issues.md`, l. 91 à 140), les ADR 0009, 0012, 0013, 0015, 0016, 0017 et 0018, les specs, et l'ancien `docs/process/` du worktree principal.

Tests : `python3 -m unittest`, 185 tests, OK (72 s).

## Critère de fin, point par point

| Point | Verdict | Où |
|---|---|---|
| `process/`, `roles/`, `process/fiche-projet.md` existent | OK | renommages `git mv` visibles dans `git status` |
| `docs/process/` ne contient plus qu'un renvoi | OK | `docs/process/README.md` seul, 10 lignes, liens justes |
| Plafond de 4904 mots (process et profils) | OK | `hooks/test_plugin.py`, `MethodTest.test_under_word_cap` vert ; `test_no_file_left_uncounted` empêche un fichier hors du compte |
| Ni `pnpm`, ni chemin du poste, ni nom d'hôte, de personne ou d'un autre projet dans `process/` et `roles/` | OK | `test_generic`, plus une recherche des noms du poste et des projets connus : aucune occurrence (seuls `[jam]` et `JAM_ROLE`, noms du plugin lui-même) |
| Règles du point 3 dans le process **et** dans le profil qui les applique, avec FR ou RET | OK | niveaux (FR-049 : process, coordinateur, planificateur) ; *léger* (FR-052 : process, coordinateur) ; seuil (FR-050 : process, relecteur, orchestrateur, coordinateur) ; plafonds (FR-051 : process, coordinateur, orchestrateur) ; relais et confirmation dans le terminal du coordinateur (FR-053 : process, coordinateur, orchestrateur) ; interface (FR-054 : process, recetteur) ; mesure (FR-055, RET-018 : process, coordinateur, orchestrateur) ; ADR 0017 (lancement par Orca, Q-058, fenêtre d'autorisation : process, coordinateur, orchestrateur) |
| Planificateur : niveau motivé quand une tâche monte | OK | `roles/planificateur.md:16` |
| Règle 6 d'`AGENTS.md` cohérente avec FR-052 et FR-053 | OK | `AGENTS.md:38` |
| `docs/methode.md` au niveau *léger* | OK | `docs/methode.md:5` |
| Q-058 tranchée, cohérente avec le profil de l'orchestrateur et les ADR | OK | `OPEN-QUESTIONS.md` Q-058, `roles/orchestrateur-tache.md:7` et `:19`, process l. 35, ADR 0018 (précise ADR 0013 et ADR 0017, mentions de statut prévues à l'acceptation), glossaire « Note de suivi » |

## Autres points vérifiés

- **NFR-016** : plus aucun « Origine : … » dans `process/` ni `roles/` ; chaque règle nouvelle a sa ligne dans la table « Ce que chaque règle nouvelle remplace ou retire » de l'ADR 0018, et les origines sans trace sont dans « Origines retirées du process ». Les renvois `(ADR 0018)` du process (l. 49, 84, 85, 103) et de l'implémenteur (l. 11) y trouvent leur ligne.
- **Décisions d'ADR acceptées** : rien de perdu sans trace. Comparé à l'ancien process : carte seule (ADR 0015), coordinateur sur `main` et par Orca (ADR 0017), sessions interactives (ADR 0012, 0013), merge sérialisé, publication après `git pull`, PR sans rebase, milestone par son titre exact. La vérification à la main d'une carte `in-progress` (ADR 0013, 0017) est remplacée par la veille, sauf la fenêtre d'autorisation du système, gardée et tracée (ADR 0018). L'écart du planificateur à la table de l'ADR 0009 est écrit dans l'ADR 0018, avec sa mention de statut.
- **Règles propres à jam** : section « Orca », clone de référence (planificateur, implémenteur, licence, vérification par le relecteur de conformité, carte du §0 par le rédacteur), nommage des worktrees, milestones, recette par `--plugin-dir`, effet du merge sur le poste : toutes dans `docs/methode.md` ou `AGENTS.md` (règles 3, 9).
- **Niveau *léger*** : cohérent dans le process (table « Niveaux »), le profil du coordinateur, `AGENTS.md` (Environnement, règles 6, 9, 10), le glossaire et FR-052. La garde du coordinateur laisse `git` ouvert (`hooks/guard_coordinator.py:54`) : le commit au niveau *léger* est faisable.
- **ADR existantes** : 0009, 0012 et 0013 ne changent que par leurs liens ; 0018 « proposée », index à jour ; RET-017 et RET-018 « en application » : conforme au brief.
- **Liens** : aucun lien vers l'ancien `docs/process/` hors `docs/plans/` ; les nouveaux chemins relatifs (`../../roles/`, `../../process/`, `../methode.md`, `decisions/…` depuis `docs/methode.md`) résolvent.
- **Vocabulaire** : « agent en cours », « épisode », « veille des cartes », « moment », « note de suivi », « session libre » entrés au glossaire ; plus d'« agent actif » dans le process.
- **Lisibilité et sur-ingénierie** : docstrings de `maintainer_time.py` et `watch_cards.py` qui disent le *pourquoi* ; options limitées à ce que demande le plan (fenêtre, dossier des transcripts, `--idle-minutes`). Rien hors périmètre.

## Bloquants

Aucun.

## À corriger

Aucun.

## Suggestions

1. **`process/README.md:72`, `process/fiche-projet.md:13`, `AGENTS.md:38`** : « merge d'un projet en production, et tout autre feu vert » exige déjà la forme complète pour tout merge, puisqu'aucune règle n'allège un merge hors production. Le gabarit (« En production, le feu vert merge se relaie sous sa forme complète ») et la règle 6 (« celui de jam compris ») laissent croire qu'un merge hors production pourrait se relayer par un « ok ». Sans conséquence : un `✓` de merge est de toute façon confirmé dans le terminal du coordinateur (l. 74). Correction possible : « le merge, et tout autre feu vert » dans le process, et retirer la phrase du gabarit, ou dire qu'elle ne fait que rappeler la règle.
2. **`process/README.md:35`** (Q-058) : un retour reçu après l'ouverture de la PR (carte `⏸ feu vert merge`) ne peut plus être « committé avec la tâche » sans un nouvel accord, que la garde de sortie exige. La note reste alors non suivie et disparaît avec le worktree après le merge. Le coordinateur en reprend le contenu dans le brief d'un cadrage (`roles/coordinateur.md:21`), donc rien n'est perdu en pratique. Correction possible : ajouter « après l'ouverture de la PR, son contenu passe dans le brief du cadrage qui le traite ».
3. **`process/README.md:102`** : « Les interdits protègent ce que lisent les rôles suivants : `.claude/`, `AGENTS.md`, `CLAUDE.md`, la fiche et `docs/plans/` » se lit comme une règle pour tous les rôles qui écrivent, alors que le rédacteur écrit à bon droit `AGENTS.md`, la fiche et `docs/plans/`. Écrire « Les interdits de l'implémenteur protègent… ».
4. **`docs/specs/01-REQUIREMENTS.md:14`** (FR-045) **et `docs/specs/02-ARCHITECTURE.md:36`** (ligne « Fiche projet ») : ils énumèrent le contenu de la fiche sans « à lire avant toute tâche » ni « règles propres », que le gabarit et le glossaire ajoutent. Aligner les deux énumérations sur le gabarit.
5. **`process/README.md:3`** : le process cite des RET, FR et Q (RET-001, RET-017, FR-049…) sans dire qu'ils sont ceux du repo du plugin ; seules les ADR sont situées. Dans un autre projet, qui a ses propres `RETOURS.md`, « RET-001 » se chercherait au mauvais endroit. Écrire « Les références (ADR, FR, RET, Q) sont celles du repo du plugin ».
6. **`docs/references/orca.md:19`, `:23` et `:34`** : la carte du §0 sert « au planificateur », et le clone est préparé et vérifié par « l'orchestrateur de tâche », alors que jam est au niveau *léger* (ni l'un ni l'autre) et que sa fiche dit « la session qui lance les rôles ». Règle dormante (ADR 0014 historique) : à aligner le jour où une tâche reprend du code d'Orca, ou dès maintenant en écrivant « la session qui lance les rôles ».
7. **`hooks/session_start_recap.py:136`** : le récapitulatif signale encore chaque autre session comme « Autre agent actif », terme que le glossaire marque désormais « sans usage ». L'ancien process expliquait que cet avertissement, reçu par chaque rôle au sujet de l'orchestrateur de tâche, était attendu ; l'explication est partie avec l'élagage. Hors du plan (aucun changement de comportement des hooks hormis la ligne « Méthode ») : à noter avec Q-056, qui reprend Q-036.

RELECTURE : OK
