# Relecture du cadrage `specs-retours-dora`, tour 7

> Relecteur seul, contexte neuf. Objet : `git diff main` (specs, process, profils de rôle, ADR 0011 et 0012, `RETOURS.md`, `OPEN-QUESTIONS.md`) et le brouillon `docs/plans/specs-retours-dora-issues.md`.
> Les relectures des tours précédents n'ont pas été lues. Une recherche de chemins machine sur `docs/**/*.md` a affiché au passage trois lignes de ces rapports, sans effet sur les constats ci-dessous.
> Faits pris tels que donnés par le coordinateur : S1 mergé (PR #5), issue #1 fermée, hook de démarrage et garde du coordinateur installés hors du repo, garde active seulement avec `JAM_ROLE=coordinateur`. Décisions du mainteneur prises en compte : pas d'échéance sur les milestones, RET-007 validé, trois points de C5 sur DORA validés.

## Vérifications faites

1. **Cohérence entre fichiers.**
   - Numéros : FR-036, FR-037 et FR-038 sont nouveaux et uniques ; Q-022 à Q-035 se suivent ; RET-001 à RET-007 ; ADR 0011 et 0012 inscrites « proposée » dans `decisions/README.md`.
   - La relecture par axes, la boucle jusqu'à OK et l'absence de progrès sont dites de la même façon dans RET-006 et RET-007, FR-022 à FR-024, NFR-010, la roadmap (S3, R-02), le glossaire (« Garde-fou », « Tour de relecture », « Axe de relecture »), le process et le profil du relecteur.
   - La précision de l'ADR 0011 §1 sur l'ADR 0008 (critère de la boucle de relecture) est annoncée dans RET-006 et prévue à l'acceptation (process, étape 4 du cadrage ; règle du rédacteur).
   - La coupe 1 (écran des métriques), FR-037 en **S** et le critère du S4 concordent, et la clause « se limite à `house` » renvoie bien à la coupe 3 (multi-repo).
   - Le glossaire, le profil, l'ADR 0012 et le process disent la même chose de la garde du coordinateur (quatre emplacements autorisés, `JAM_ROLE` au lancement, « session libre »).
   - `apps/` et `packages/`, cités dans la définition de « Code applicatif », existent.
2. **Fidélité aux retours.** Chaque modification se rattache à un RET, ou bien elle est signalée comme friction du coordinateur (section RTK, Q-022 à Q-025, ligne 122 du process). RET-002 reprend les trois compléments validés. RET-007 reprend la décision « instances Claude neuves, diversité de modèles en E2 » (Q-034). Le brouillon ne pose aucune échéance de milestone.
3. **Repo public.** Pas de secret, pas d'adresse, pas de chemin propre à une machine. `~/.claude` (Q-024) est un chemin générique de l'outil. « Ben » figurait déjà sur `main`.
4. **Permissions.** Aucun profil n'ouvre le commit, le push ou `gh` en écriture :
   - le rédacteur n'a aucun shell ;
   - le relecteur et sa variante n'ont que des formes exactes de `gh` en lecture, sans joker sur `gh api` ;
   - l'implémenteur interdit `git commit`, `git push`, `git -C` et `gh`, sous leurs deux formes, simple et `rtk` ;
   - le coordinateur relève de l'exception tracée dans l'ADR 0012.
   Les voies `node`, `npx`, `pnpm` et script de test restent ouvertes, mais le process les reconnaît (Q-025, R-03).
5. **Brouillon d'issues.** Chaque point du critère du S2 de la roadmap est couvert par une issue :
   - S2-a : lister les issues ;
   - S2-b : worktree, et fiche « worktree » ;
   - S2-c : horodatage, et fiche « stream-json » ;
   - S2-d : profil ;
   - S2-e : brief et process ;
   - S2-f : plan affiché, fil résumé, redémarrage.
   Chaque issue a un critère de fin vérifiable et un hors-périmètre. Le sort des issues #1 à #4 est cohérent avec les faits donnés.

## Bloquant

Aucun.

## À corriger

Aucun.

## Suggestions

1. **`docs/process/roles/coordinateur.md:22`** : la règle cite le « budget » parmi les garde-fous que tient le coordinateur. Or le process (`docs/process/README.md:111`) dit que rien ne mesure ce budget dans Orca. Écrire plutôt : « tours de relecture, comparaison des constats (absence de progrès) ; le budget n'est pas mesuré dans Orca, seule compte l'alerte de quota que voit le mainteneur ».

2. **`docs/plans/specs-retours-dora-issues.md:81-83` (S2-c)** : la ligne 39 justifie l'ordre S2-b → S2-c par « S2-b comme S2-c ajoutent une migration ». Le périmètre de S2-c ne dit pourtant pas qu'il crée la table des étapes. Ajouter : « La table des étapes arrive par une nouvelle migration numérotée (ADR 0010). »

3. **`docs/plans/specs-retours-dora-issues.md:97-99, 114 et 129` (S2-d, S2-e, S2-f)** : deux points restent sans issue.
   - **La consigne du planificateur.** FR-022 définit le profil comme « prompt, outils, permissions ». S2-d ne construit que la ligne de commande, et S2-e parle de la consigne « en plus » du contexte. Préciser dans S2-d que le profil contient aussi la consigne du rôle.
   - **L'endroit où le plan est lu pour être affiché** : un fichier du worktree de `house`, ou le résultat du flux. Préciser dans S2-f : « l'endroit où le plan est écrit et lu est fixé dans le plan de l'issue ».

4. **`docs/plans/specs-retours-dora-issues.md:4`** : « son worktree et ses fichiers gardent leur nom ». Seul le premier rapport (`…-relecture.md`) n'est pas numéroté ; les suivants le sont (`…-relecture-2.md` à `-7.md`). Écrire : « son worktree garde son nom, et son premier rapport de relecture n'est pas numéroté ».

5. **`docs/plans/specs-retours-dora-issues.md`, section 1 (ligne 12)** : deux actions de publication sont absentes du brouillon.
   - **Le milestone `E0-S1`.** Son unique issue est fermée, et GitHub ne ferme pas un milestone tout seul. Proposer de le fermer, ou dire pourquoi il reste ouvert.
   - **Le label `incident`.** L'ADR 0011 (§2, `docs/decisions/0011-pratiques-et-metriques-dora.md:47`, et §5) mesure jam dès la période Orca à partir des issues `incident`. Proposer de créer ce label sur `jammindev/jam` à la publication, pour qu'un incident puisse être signalé dès maintenant.

6. **`docs/process/roles/redacteur.md:9` et `docs/process/roles/planificateur.md:9`** : ces deux rôles ont `Read` sans restriction de chemin et `WebFetch`. Une page web ou une issue piégée pourrait faire lire un fichier du poste (hors worktree) puis l'envoyer dans une URL. Ce n'est ni un commit ni un push. L'ADR 0009 (contexte) dit pourtant qu'un worktree ne protège pas `$HOME`. Ajouter une ligne dans « Ce qu'Orca ne permet pas » (`docs/process/README.md`), ou étendre Q-027 au rédacteur.

7. **`docs/process/roles/redacteur.md:9`** : `Edit(docs/**)` laisse le rédacteur modifier un plan validé (`docs/plans/<tâche>.md`) ou un rapport de recette. Pour s'aligner sur le planificateur, ajouter aux interdits `"Edit(docs/plans/*-recette.md)"`. On peut aussi écrire dans le profil que le rédacteur ne touche, dans `docs/plans/`, qu'aux brouillons d'issues.

8. **`docs/specs/GLOSSARY.md:19`** : « Code applicatif » exclut la CI. Or un changement de `.github/workflows/ci.yml` touche à ce qui s'exécute avec les secrets du repo, et n'aurait qu'un seul relecteur. Faire confirmer cette exclusion par le mainteneur, ou y inclure la CI.

9. **`docs/process/README.md:94`** : le premier tour n'a pas de nom de fichier explicite (`-1`, ou pas de suffixe). Préciser : « `<tour>` commence à 1 ».

10. **`docs/specs/OPEN-QUESTIONS.md:16` (Q-012)** : ajouter « à trancher dans le plan de S2-d », pour que la question renvoie à l'issue qui la tranchera.

11. **`docs/process/roles/planificateur.md:9`** : ce cadrage modifie la commande du planificateur, mais garde `WebSearch` et `WebFetch`, alors que l'ADR 0009 (acceptée) donne « Réseau : Non » à ce rôle. L'écart existait déjà et Q-027 le reporte « au prochain cadrage ». Aucune correction ici, mais le mainteneur peut vouloir le trancher dans ce cadrage, puisque le profil est déjà ouvert.

RELECTURE : OK
