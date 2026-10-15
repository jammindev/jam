# Relecture — #23 Process élagué, axe conformité, tour 10

Relecteur B, axe conformité. Relu : tout le travail non commité de la branche (`git diff`, fichiers non suivis : `process/fiche-projet.md`, `scripts/maintainer_time.py`, `docs/methode.md`, l'ADR 0018, `docs/concepts/veille-et-mesure.md`, `docs/process/README.md`), comparé au `docs/process/` du worktree principal. `python3 -m unittest` : **186 tests, OK** (dont le plafond de 4904 mots et l'absence de `pnpm`, `/Users/`, `/home/` dans `process/` et `roles/`).

Note d'indépendance : une recherche Grep sur `docs/plans/23-process-elague*.md` (noms interdits) a affiché au passage quelques lignes de rapports de relecture précédents. Je ne les ai pas ouverts et n'en ai rien repris.

## Changements depuis le tour 9, vérifiés d'abord

- **Numéro d'issue « (#23) » avec dièse** : process l. 61, profil du coordinateur l. 21, ADR 0018 l. 73, RET-019. La mesure le lit (`#23\b`, `maintainer_time.py` l. 216-218). Cohérent.
- **Retour reçu dans un worktree au niveau *léger*** : remonte au coordinateur (process l. 37, ADR 0018 l. 30 et l. 58, glossaire « Note de suivi »). Cohérent.
- **Conflit avec `main`** : process l. 33, orchestrateur de tâche l. 21, ADR 0018 l. 63 ; règle d'avant précisée (décision du coordinateur avec le mainteneur ; résolution par l'implémenteur ou le rédacteur). Cohérent.
- **Limite de la mesure** (recette et feux verts tapés dans le worktree de la tâche non comptés) : process l. 112, ADR 0018 l. 44 (Q-065), RET-018, Q-065, fiche concept l. 43, docstring et sortie du script (l. 30-31, l. 256-257). Cohérent.
- **`at_work`** : un agent `waiting` n'est plus au travail (`watch_cards.py` l. 127-132), et le réveil se nomme « agent en attente d'une autorisation depuis N min » ; profil du coordinateur l. 20 et fiche concept l. 32 alignés.
- **Relais** : forme complète pour tout feu vert autre que plan et recette, merge compris : process l. 74-79, `AGENTS.md` règle 6, fiche de jam (« Merge »), ADR 0018 l. 53. Conforme à FR-053 (forme complète pour « tout feu vert qu'aucune règle n'allège ») et à l'ADR 0016 (allègement pour le plan et la recette seulement). Le gabarit de la fiche ne parle plus du relais, ce qui ne contredit rien.
- **Coupes** (description du récapitulatif, liste d'ADR de l'intro) : rien de perdu, la ligne « Méthode » reste décrite (l. 51) et l'intro renvoie aux ADR du plugin et à l'ADR 0018.

## Critère de fin, point par point

| Point | Constat |
|---|---|
| `process/`, `roles/`, `process/fiche-projet.md` ; `docs/process/` réduit à un renvoi | OK. `docs/process/` ne contient que `README.md`, renvoi vers `process/`, `roles/`, le gabarit et la fiche de jam. |
| Plafond de 4904 mots | OK (`hooks/test_plugin.py`, `MethodTest.test_under_word_cap`, liste fermée des pages). |
| Ni `pnpm`, ni chemin, ni hôte, ni autre projet dans `process/` et `roles/` | OK (test, et Grep sans casse sur des noms d'hôte et de projets du poste : rien). `hooks/` et `scripts/` : seuls des chemins de test inventés. |
| Chaque règle du point 3 dans le process et dans le profil qui l'applique, avec RET ou FR | OK. Niveaux (FR-049 : process, coordinateur, planificateur) ; *léger* (FR-052 : process, coordinateur) ; seuil (FR-050 : process, relecteur, orchestrateur, coordinateur) ; plafonds (FR-051 : process, coordinateur, orchestrateur) ; relais et confirmation dans le terminal du coordinateur (FR-053 : process, coordinateur, orchestrateur) ; recette d'interface (FR-054 : process, recetteur) ; mesure (FR-055, RET-018 : process, coordinateur, orchestrateur) ; ADR 0017 (lancement par Orca, NFR-013, Q-058, fenêtre d'autorisation, Q-059 : process, coordinateur). |
| Planificateur : niveau motivé | OK (`roles/planificateur.md` l. 16). |
| Règle 6 d'`AGENTS.md` cohérente avec FR-052 et FR-053 | OK. |
| `docs/methode.md` au niveau *léger* ; Q-058 tranchée | OK. Q-058 tranchée dans `OPEN-QUESTIONS.md`, l'ADR 0018, le process et le profil de l'orchestrateur de tâche ; l'ADR 0018 précise l'ADR 0013 (mention de statut prévue à l'acceptation). |

## Autres vérifications

- **NFR-016** : plus aucun « Origine : … » dans `process/` ni `roles/` ; les règles nouvelles ont leur ligne dans la table de l'ADR 0018 (dont les ajouts du tour 9) ; les origines sans trace sont dans son second tableau. Les règles qui semblaient nouvelles (« non reproduit », carte sans segment d'état en `in-review`, fermeture des terminaux au nettoyage, relecteurs par zones) existaient dans `docs/process/` de `main`.
- **Décisions des ADR acceptées** : rien de perdu sans acte. Mesure à la main (ADR 0016) : remplacée, actée (ADR 0018 l. 57, RET-018, mention « précisée (0018) » prévue). Vérification à la main d'une carte (ADR 0013, 0017) : remplacée sauf fenêtre d'autorisation, actée. Profil du planificateur (ADR 0009) : écart acté. Repérage des refus par le cœur (ADR 0009) : déjà caduc par l'ADR 0016.
- **ADR existantes** : 0009, 0012 et 0013 ne changent que par leurs liens ; 0016 et 0017 intactes ; ADR 0018 « proposée », RET-017 à RET-019 « en application », index à « Proposée » : conforme au profil du rédacteur.
- **Règles propres à jam** : sorties des profils (section « Orca », clone de référence, `--plugin-dir`, convention de nom du worktree) et écrites dans `docs/methode.md` et `AGENTS.md` (règles 3 et 9).
- **Niveau *léger*** cohérent dans le process, le profil du coordinateur, l'implémenteur et le rédacteur (check-list en fin de travail, interdits `Edit` de l'implémenteur ciblés sur le plan et les rapports de relecture), le relecteur (seul, deux axes), le glossaire, FR-052, `AGENTS.md`.
- **Liens** : aucun lien vers l'ancien `docs/process/` hors `docs/plans/` ; les liens relatifs de `roles/`, `docs/methode.md`, `docs/decisions/`, `RETOURS.md`, `references/orca.md` et de la fiche concept visent des fichiers présents.
- **Friction 18** : même explication dans le process (l. 105), `roles/recetteur.md` (l. 11), l'ADR 0018 (l. 65, qui garde l'ancrage par `/` pour la raison de la ligne 64) et `docs/methode.md` (« Recette ») ; Q-064 ouverte pour la suite.
- **Règle « Messages au mainteneur »** : deux phrases, fidèle au retour (se lit seul, projet et tâche en mots, références internes remplacées), RET-019 citée.
- **Écart à l'issue sur la mesure** : acté dans RET-018, l'ADR 0018 (l. 44) et Q-065 ; FR-055, FR-046, FR-056, `00-VISION.md`, `02-ARCHITECTURE.md` et `04-ROADMAP.md` alignés ; « le mainteneur valide le chiffre » n'apparaît plus nulle part.
- **Vocabulaire** : « agent en cours », « épisode », « moment », « note de suivi » employés comme le glossaire les définit.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. **`process/README.md` l. 61 et `roles/coordinateur.md` l. 21** : la forme du numéro est donnée par le numéro de jam, `(#23)`, dans un process générique. Correction proposée : `(#<n>)`, comme dans « Mesure » (l. 112).
2. **`process/README.md` l. 61** : un cadrage n'a pas d'issue (l. 35), et la règle demande pourtant « la tâche suivie de son numéro d'issue ». Pour une règle nouvelle, question à ouvrir : un message sur un cadrage nomme-t-il seulement son worktree `cadrage-<slug>`, que la mesure lit aussi ?
3. **`process/README.md` l. 33** : « `main` est fusionné sans rebase » ne dit pas qui fusionne. L'orchestrateur de tâche au niveau *standard*, le coordinateur au niveau *léger* : préciser par « par la session qui conduit la tâche » si les mots le permettent sous le plafond.
4. **`process/README.md` l. 105** : « Même repli si une autre écriture permise est refusée » se lit comme valant pour tout rôle, alors que seul le recetteur a un dossier de recette. Correction proposée : « Même repli pour le recetteur si une autre écriture permise est refusée », ou renvoyer au profil du recetteur, qui le dit déjà (l. 11).
5. **`scripts/maintainer_time.py` l. 13 et l. 31** : deux lignes de la docstring ne sont plus coupées (près de 120 caractères), après les retouches. Lisibilité seulement : recouper le paragraphe.
6. **`docs/specs/OPEN-QUESTIONS.md` l. 64 et l. 65** : Q-064 et Q-065 portent « Ben » dans la colonne Porteur. C'est la convention de toute la table, antérieure à la tâche, et c'est le mainteneur. Je le signale seulement parce que le brief demande de relever tout nom de personne (NFR-002).

RELECTURE : OK
