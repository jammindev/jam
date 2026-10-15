# Relecture #23 — axe conformité, tour 5

Relu : tout le travail non commité de la branche (`git status`, `git diff`, fichiers non suivis), comparé à `docs/process/` du worktree principal. Référence : plan validé `docs/plans/23-process-elague.md`, issue K1-2 (`docs/plans/cadrage-kit-issues.md`), ADR 0009, 0012, 0013, 0015, 0016, 0017, 0018, specs.

Tests : `python3 -m unittest` : 184 tests, OK (le test de taille et de généricité de `hooks/test_plugin.py` compris).

## Critère de fin, point par point

| Point | Verdict |
|---|---|
| `process/`, `roles/`, `process/fiche-projet.md` existent ; `docs/process/` ne contient plus qu'un renvoi | OK (`docs/process/README.md` seul, renvoi) |
| Plafond de 4904 mots pour `process/` et `roles/` | OK (`MethodTest.test_under_word_cap` vert, fiche comprise ; aucun fichier hors compte) |
| Ni `pnpm`, ni chemin, ni nom d'hôte ou d'autre projet dans `process/` et `roles/` | OK (recherche faite : rien) |
| Chaque règle du point 3 dans le process et dans le profil du rôle qui l'applique, avec sa référence | OK, sauf le relais reçu par l'orchestrateur de tâche (constat 1) |
| Profil du planificateur : niveau motivé quand une tâche monte | OK (`roles/planificateur.md:16`, FR-049) |
| Règle 6 d'`AGENTS.md` cohérente avec FR-052 et FR-053 | OK |
| `docs/methode.md` au niveau *léger* | OK |
| Q-058 tranchée, cohérente avec le profil de l'orchestrateur de tâche et les ADR | OK (ADR 0018 précise 0013 et 0017, mentions de statut prévues) |
| Liens vers l'ancien `docs/process/` (hors `docs/plans/`) | OK : aucun lien cassé |
| NFR-016, « Origine : … » | OK : plus aucune « Origine » dans `process/` et `roles/` ; tableau des origines dans l'ADR 0018 |
| Règles propres à jam sorties des profils | OK (`docs/methode.md`, « Règles propres » ; `AGENTS.md`, règle 9) |
| Niveau *léger* cohérent | OK (process, coordinateur, implémenteur, `AGENTS.md`, glossaire, FR-052) |

## Bloquant

Aucun.

## À corriger

### 1. `roles/orchestrateur-tache.md:17` : le profil ne dit pas comment l'orchestrateur de tâche reçoit un feu vert relayé (FR-053)

L'ancien profil portait la règle côté réception (« Un feu vert relayé ne vaut que s'il respecte le format […]. Sinon, il demande la confirmation au mainteneur »). Le nouveau ne garde que le sens montant (segment `✓`). Le relais allégé (point 3 de l'issue) n'y figure donc que pour ce qu'il envoie, pas pour ce qu'il reçoit, alors que c'est lui qui agit sur un feu vert relayé par le coordinateur (commit, push et PR). Le critère de fin demande la règle « dans le profil du rôle qui l'applique ».

**Scénario d'échec** : cadrage au niveau *standard*. Le coordinateur transmet le feu vert de cadrage par un simple « ok » dans le terminal de l'orchestrateur de tâche. Son profil dit seulement « commit, push et PR seulement après le feu vert qui les ouvre » : il committe, pousse et ouvre la PR. La garde de sortie lit cet « ok » comme le dernier message du mainteneur et laisse passer. Or, d'après FR-053 et le process (« Relais d'un feu vert »), un feu vert de cadrage relayé exige les mots exacts, l'heure et la session ; sinon il ne vaut qu'information.

**Correction attendue** : ajouter à la règle de la ligne 17 (ou juste après) une phrase du type : « Un feu vert relayé par le coordinateur : un « ok » suffit pour le plan et la recette ; pour tout autre feu vert, les mots exacts, l'heure et la session, sinon il demande confirmation au mainteneur (FR-053). »

### 2. `docs/decisions/0018-process-elague.md:5`, `:30-32` et `:95` : Q-027 s'écarte de l'ADR 0009, acceptée, sans le dire

La table de l'ADR 0009 (`docs/decisions/0009-permissions-par-role.md:18`) donne au planificateur la « commande de tests » en shell et « Réseau : Non ». L'ADR 0018 tranche Q-027 à l'inverse sur les deux points : le planificateur garde `WebSearch` et `WebFetch`, et ne reçoit pas la commande de test. Q-027 nomme pourtant l'ADR 0009 (`docs/specs/OPEN-QUESTIONS.md`, Q-027 : « Profil du planificateur et ADR 0009 »). L'ADR 0018 ne cite l'ADR 0009 ni dans sa ligne « Tranche », ni dans la section Q-027, ni dans les mentions de statut à poser à l'acceptation (ligne 95). C'est contraire à `AGENTS.md` (« Une décision actée ne se contourne pas ») et au point de cette relecture « aucune décision d'une ADR acceptée perdue sans être actée ».

**Scénario d'échec** : un relecteur de conformité d'une tâche future compare `roles/planificateur.md` à l'ADR 0009, que l'ADR 0016 garde « valable en partie » pour les profils. Il trouve la recherche web et l'absence de commande de test en contradiction avec la table, sans mention dans le statut de 0009. Il en fait un constat, ou un rédacteur « corrige » le profil vers l'ADR 0009 : la décision de Q-027 est perdue.

**Correction attendue** : dans l'ADR 0018, ligne 5, ajouter « précise l'ADR 0009 (profil du planificateur) » ; dans la section Q-027, dire qu'elle s'écarte de la table de l'ADR 0009 (recherche web en lecture, pas de commande de test) ; à la ligne 95, ajouter la mention de statut de l'ADR 0009 (par exemple « précisée (0018) : profil du planificateur »). Le texte de l'ADR 0009 ne change pas.

## Suggestions

### 3. `process/README.md:49` : « en chemins absolus » ne vaut que pour le process et les profils

Le hook affiche la fiche en chemin relatif (`` fiche `docs/methode.md` ``, `hooks/session_start_recap.py:175`), et seulement le process et les profils en chemins absolus. Écrire : « une ligne « Méthode » avec la fiche du repo, puis ce process et les profils en chemins absolus ».

### 4. `roles/relecteur.md:9` et `docs/decisions/0018-process-elague.md:56` : le resserrement de l'écriture du relecteur n'est pas tracé

L'ancienne règle `Edit(docs/plans/*-relecture*.md)` laissait un relecteur réécrire les rapports des tours précédents (limite écrite dans l'ancienne section « Ce qu'Orca ne permet pas »). La nouvelle, `Edit(/docs/plans/<rapport>)`, ferme cette voie, mais la ligne 56 de l'ADR 0018 ne parle que de l'ancrage par `/`. Pour NFR-016, compléter cette ligne : « le relecteur n'écrit plus que le rapport nommé dans son brief (retire la limite : il pouvait réécrire les rapports des tours précédents) ».

RELECTURE : CORRECTIONS (2)
