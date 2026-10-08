# Relecture 4 — cadrage `specs-retours-dora`

> Relecteur seul, contexte neuf. Objet : `git diff main` (specs, ADR, process, profils, brouillon d'issues). Les relectures des tours précédents n'ont pas été lues.
> Décisions du mainteneur prises en compte : pas de date d'échéance sur les milestones ; RET-007 validé (instances Claude neuves, diversité de modèles en E2) ; les trois points de C5 sur DORA validés. Faits pris en compte : le hook de démarrage et la garde du coordinateur sont installés sur le poste, hors repo ; la garde n'agit que si `JAM_ROLE=coordinateur`.

## Vérifié sans constat

- **Numéros** : FR-036, FR-037 et FR-038 sont neufs et uniques ; Q-022 à Q-033 suivent Q-021 sans trou ; ADR 0011 et 0012 sont listées dans `docs/decisions/README.md` en « Proposée » ; RET-001 à RET-007 sont tous cités au moins une fois là où leur impact l'annonce.
- **Fidélité aux retours** : chaque modification renvoie à un RET, ou se déclare friction du coordinateur (Q-022 à Q-025, process ligne 121). Je n'ai pas trouvé d'ajout qui ne soit rattaché à rien.
- **Repo public** : aucun secret, aucune adresse, aucun chemin propre à une machine. Les seules mentions personnelles (« Ben » dans le glossaire, la vision, les questions ouvertes) existaient déjà sur `main`. `~/.claude` (Q-024) est un chemin générique.
- **Permissions** : aucun profil n'ouvre commit, push ou `gh` en écriture. L'implémenteur interdit `git commit`, `git push`, `git -C` et `gh`, sous les deux formes ; le relecteur n'a pas `gh` ; sa variante n'a que des formes exactes en lecture, sans joker sur `gh api` ; le rédacteur n'a pas de shell. Les voies restantes (`pnpm exec`, `node -e`, script de test) sont déclarées dans « Ce qu'Orca ne permet pas » et dans Q-025.
- **Brouillon d'issues** : les six issues du S2 sont de petits lots, chacune avec un critère de fin vérifiable par un test ou par un essai nommé. Elles couvrent ensemble le critère du milestone S2.

## Bloquant

Aucun.

## À corriger

1. **`docs/plans/specs-retours-dora-issues.md`, ligne 30 (sort de l'issue #1).** Le texte dit que le lien vers `docs/plans/E0-S1-squelette.md` « fonctionnera dès que le plan sera versé dans `main` avec la PR du S1 ». Or le S1 est déjà mergé (PR #5, commit `194d58f` sur `main`), et le plan est déjà dans `main`. La ligne décrit un état passé, et la proposition « Reste telle quelle » ne dit pas ce qu'il advient de #1 une fois le S1 livré.
   **Correction attendue** : indiquer que le S1 est livré par la PR #5 et que le lien fonctionne. Proposer de fermer #1 en citant la PR #5, si elle ne l'a pas déjà été. Le coordinateur peut le vérifier avec `gh issue view 1` avant publication.

2. **`docs/specs/04-ROADMAP.md`, ligne 46 (critère du S4), à croiser avec l'ADR 0011, ligne 75 (§5).** Le critère demande que l'écran affiche, « pour `house` et pour jam, les cinq métriques DORA et les indicateurs agents ». L'ADR 0011 §5 dit que les indicateurs agents de jam sont perdus tant que son pipeline est déroulé dans Orca. Au S4, jam n'aura sans doute fait passer aucune tâche par son propre pipeline : pour jam, la case des indicateurs agents sera vide. Le recetteur ne saura pas si le critère est rempli. La même phrase se retrouve dans le milestone E0-S4 du brouillon d'issues (ligne 24).
   **Correction attendue** : préciser dans les deux endroits ce qu'on attend pour jam. Par exemple : « pour jam, les cinq métriques ; ses indicateurs agents peuvent rester vides tant que ses tâches passent par Orca (ADR 0011 §5) ».

3. **`docs/specs/04-ROADMAP.md`, ligne 34 (coupe 4, « un rôle « livreur » exécute les commandes `gh` sous feu vert »).** Cette coupe existait déjà, mais la branche l'a renumérotée sans la revoir. Elle contredit maintenant l'ADR 0012, ligne 22 : dans jam, le cœur « tient seul le commit, la publication et le merge ». Elle contredit aussi NFR-012, l'ADR 0009 et la règle 6 d'`AGENTS.md`, mise à jour par cette branche : aucun rôle ne pousse, ne merge ni ne publie sur GitHub.
   **Correction attendue** : reformuler la coupe sans rôle qui publie. Par exemple : « le cœur exécute les commandes `gh` (push, PR, merge) sous feu vert, sans suivi intégré de la CI ». Si un rôle livreur reste voulu, il faut une ADR qui le prévoie, mais ce choix revient au mainteneur.

4. **`docs/decisions/0011-pratiques-et-metriques-dora.md`, ligne 39.** L'ADR 0011 précise une règle de l'ADR 0008, acceptée : sa ligne 45 dit « Boucles automatiques uniquement sur des critères objectifs : tests verts, CI verte ». NFR-010 est réécrite en conséquence. Mais rien n'est prévu pour que l'ADR 0008 signale cette précision. Un agent qui lit l'ADR 0008 seule, avec la consigne « une décision actée ne se contourne pas », jugera la boucle de relecture jusqu'à OK contraire à l'ADR. L'ADR 0012 traite le même cas pour l'ADR 0009 (ligne 31).
   **Correction attendue** : ajouter dans la Décision de l'ADR 0011 une ligne du même modèle : « À l'acceptation de cette ADR, le statut de l'ADR 0008 mentionne cette précision (critère de la boucle de relecture) ». Le rédacteur l'appliquera au feu vert, en même temps que le passage à « acceptée ».

## Suggestions

1. **`docs/specs/RETOURS.md`, ligne 55 (RET-005, analyse).** Le paragraphe dit d'abord que le hook refuse les écritures « hors de sa mémoire et du dossier temporaire », puis qu'il autorise quatre emplacements. Remplacer la première mention par « hors des emplacements autorisés (voir plus bas) », ou par la liste des quatre.

2. **`docs/specs/GLOSSARY.md`, ligne 28 (« Garde-fou »).** La parenthèse omet « en substance », qui figure dans FR-024, le process et RET-006. Sans ces mots, la définition paraît plus stricte. Écrire : « un constat bloquant ou à corriger qui revient, en substance, au tour suivant ».

3. **`docs/specs/GLOSSARY.md`, lignes 48-49 (taux d'échec et taux de reprise).** Les définitions disent « qui ont causé un incident » et « qui corrigent un incident ». L'ADR 0011 (lignes 55-56) donne la règle de calcul : « désignées par une issue `incident` » et « qui ferment une issue `incident` ». Reprendre la forme de l'ADR, qui dit comment on compte.

4. **`docs/process/roles/implementeur.md`, ligne 9.** `Edit(./**)` permet à l'implémenteur de modifier le plan validé au feu vert 1 et les rapports de relecture des tours précédents. Ces rapports ne sont pas suivis par git tant que rien n'est committé, donc une modification ne se voit pas dans le diff. C'est sur eux que le coordinateur juge l'absence de progrès. Le planificateur et le rédacteur sont déjà protégés de ces fichiers. Ajouter `"Edit(docs/plans/**)"` aux interdits de l'implémenteur.

5. **`docs/process/roles/relecteur.md` ligne 9 et `implementeur.md` ligne 9 : `Bash(git diff:*)` et `Bash(git log:*)`.** `git diff --output=<fichier>` et `git log --output=<fichier>` écrivent un fichier n'importe où. Ce n'est ni un commit ni un push, mais cela contourne la limite « écrit seulement son fichier de relecture ». Au choix : l'ajouter à la liste de « Ce qu'Orca ne permet pas », ou interdire les formes `--output` sous les deux écritures.

6. **`docs/decisions/0011-pratiques-et-metriques-dora.md`, ligne 32.** « Rien de ce qui compte ne vit hors de git ou de l'état du cœur. » La garde du coordinateur et le hook de démarrage vivent hors du repo, ce que l'ADR 0012 assume (ligne 38). Ajouter : « sauf, provisoirement, l'outillage du poste du mainteneur (ADR 0012) ».

7. **`docs/decisions/0012-coordinateur-role-garde-fous-hook.md`, ligne 22, et conséquences, lignes 37-39.** L'exception « installation d'un hook déjà relu » ouvre au coordinateur l'emplacement des hooks, celui de sa propre garde comprise. Le hook ne peut pas savoir si un hook a été relu : c'est une consigne, pas du code. Ajouter une conséquence (−) : « l'exception d'installation de hook permet aussi de modifier la garde elle-même ; elle repose sur la relecture préalable, comme les écritures par le shell ».

8. **`docs/specs/04-ROADMAP.md`, ligne 46 (périmètre du S4), et FR-028.** Pour `house`, livrer veut dire déployer (ADR 0011). Le S4 suppose donc que la configuration du repo désigne son workflow de déploiement (FR-028), mais aucun jalon ne le mentionne. L'ajouter au périmètre du S4, ou le noter pour le `cadrage-s4`.

9. **`docs/specs/04-ROADMAP.md`, ligne 45 (S3), et FR-036.** FR-036 horodate aussi chaque feu vert. Les feux verts arrivent au S3, mais la ligne du S3 ne le dit pas. À reprendre au `cadrage-s3`, pour que l'horodatage des feux verts ne soit pas oublié.

10. **`docs/process/README.md`, ligne 120.** « Les profils qui écrivent interdisent donc `Edit(.claude/**)` ». Le recetteur écrit `docs/plans/<tâche>-recette.md`, mais son profil n'a pas encore de commande, donc ni cette interdiction ni les formes `rtk`. Ajouter une ligne dans Q-033 ou une nouvelle Q : « profil du recetteur : commande à écrire, sur le modèle des autres ».

11. **`docs/process/README.md`, ligne 8 (acteur « Coordinateur »).** Le paragraphe mêle la mission, le statut de rôle, la garde et ses quatre exceptions. Pour un mainteneur qui ne code pas, garder la mission et un renvoi : « C'est un rôle lui aussi, protégé par une garde quand il est lancé avec `JAM_ROLE=coordinateur` ([profil](roles/coordinateur.md), ADR 0012) ». Le détail est déjà dans le profil et dans « Garde-fous ».

RELECTURE : CORRECTIONS (4)
