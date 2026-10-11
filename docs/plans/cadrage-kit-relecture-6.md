# Relecture du cadrage `cadrage-kit` — tour 6

Relecteur seul, contexte neuf. Périmètre : la rédaction non commitée du worktree (17 fichiers modifiés, ADR 0016 et 0017, brouillons d'issues). Seuil « assez bon » : « à corriger » réservé aux erreurs, aux contradictions et aux règles trompeuses.

## Vérifications faites

- **ADR 0016 / 0017, specs, process, issues** : cohérents entre eux sur les points structurants.
  - Contenu du plugin et gel : ADR 0016, FR-042 à FR-048, NFR-016, 02, 04 et README.
  - Niveaux *standard* / *léger* / *renforcé* : ADR 0016, FR-049, FR-052, glossaire, Q-061.
  - Plafond global en agents en cours : ADR 0016, FR-051, glossaire, Q-038.
  - Relais allégé et confirmation dans le terminal du coordinateur : ADR 0016, FR-053, K1-1, K1-2.
  - Mesure unique : FR-055, Q-057, K1-1 à K1-3.
  - Entrée en vigueur au merge de K1-2 : ADR 0016, et l'ordre des issues dans le brouillon (§2).
- **Process** : seuls les passages contredits par l'ADR 0017 ont changé : acteurs, correspondance, lancement du coordinateur et profil du coordinateur. Plus aucune mention du terminal flottant comme emplacement du coordinateur. La ligne « Lancement » de l'ADR 0013 citée par l'ADR 0017 existe bien.
- **Exigences** : aucun numéro supprimé ni réutilisé (vérifié sur le diff). Chaque FR et NFR de l'app a un état. FR-021, FR-028, FR-029, FR-036, FR-037 et FR-038 renvoient à l'exigence du kit qui les remplace, et ces renvois sont réciproques. La liste « restent valables » (NFR-001 à 004, NFR-009 à 012) correspond aux états.
- **ADR** : le sort de chaque ADR (0001 à 0015) est donné, et `AGENTS.md` cite les mêmes ADR caduques (0002, 0004 à 0007, 0010). Le tag `app-electron` existe.
- **Issues** : trois au plus, ordre strict, niveaux justifiés.
  - Chaque issue a des exigences, un critère de fin vérifiable, une recette adaptée à l'absence d'app (RET-010) et une ligne « Orca ».
  - Toutes les nouvelles FR et NFR sont couvertes.
  - Les milestones E0-S3 et E0-S4 ont chacun un sort proposé, et K1 sa description.
- **Profils** : les passages « Kit » ajoutés sont cohérents avec le brouillon.
  - Python `unittest` pour les trois profils.
  - `git rm` pour l'implémenteur : sa liste exacte correspond aux fichiers présents à la racine, sans fichier caché oublié.
  - `git mv` pour l'implémenteur : l'ordre est correct.
  - `--plugin-dir` pour le recetteur.
- **Inventaire des hooks du poste** :
  - quatre hooks : garde du coordinateur (Edit, Write, NotebookEdit, Bash), garde des sorties (commit, push), reprise de contexte et état git ;
  - deux sans tests ;
  - la garde du coordinateur ne garde pas les sorties.

  C'est cohérent avec la formulation prudente de K1-1 : le plan inventorie, et retire « si » la garde du coordinateur traite les sorties. Les hooks ne contiennent aucun nom de machine.
- **Repo public** : aucun chemin du poste, nom d'hôte, nom de machine ni nom d'un autre projet dans le texte ajouté. Les seules occurrences (`house`, `VPS`, chemins `~/` génériques) sont antérieures à ce cadrage. RET-014 remplace le nom de la machine par un repère entre crochets.

## Bloquant

Aucun.

## À corriger

Aucun.

## Suggestions

1. **`docs/plans/cadrage-kit-issues.md:79` et `:130`** : les critères de fin vérifient moins que NFR-014, que les deux issues citent. K1-1 ne vérifie ni nom d'hôte ni nom de machine ; K1-2 ne vérifie ni nom de personne ni nom de machine. Reprendre la liste exacte de NFR-014 dans les deux critères. Le risque est faible : les hooks du poste ne contiennent aucun nom de machine, et `docs/process/` aucun nom de personne.
2. **`docs/plans/cadrage-kit-issues.md:85`** : le bloc « Après le merge de K1-2 » se trouve dans le corps de K1-1, qui sera fermée à ce moment-là. Il contient l'installation du plugin sur le poste et le retrait des hooks en double. Or c'est le merge de K1-2 qui déclenche ces actions (ADR 0016, « Entrée en vigueur »), et K1-3, conduite en *léger*, suppose le plugin installé. Déplacer ce bloc dans le corps de K1-2, ou l'y répéter.
3. **`docs/plans/cadrage-kit-issues.md:79`** : « le plugin câble les quatre hooks », mais seuls trois sont vérifiés. Ajouter : à chaque message, une ligne d'état git marquée du plugin.
4. **`docs/plans/cadrage-kit-issues.md:95`** : K1-2 cite Q-027 dans ses exigences, mais ni « À faire » ni le critère de fin n'en parlent. Écrire « trancher Q-027 au plan (profil du planificateur) », ou retirer Q-027 de la liste.
5. **`docs/plans/cadrage-kit-issues.md:109` et `:129`** : le comptage `wc -w` n'est dans aucune commande de rôle. Dire qui compte et reporte les nombres de mots dans la PR (l'orchestrateur de tâche, par exemple), ou ajouter la forme exacte au profil de l'implémenteur pour K1-2.
6. **`docs/plans/cadrage-kit-issues.md:106`** : le déplacement de `docs/process/roles/` casse les liens que posent les ADR, `RETOURS.md` et les specs vers `../process/roles/<rôle>.md`. Or le texte d'une ADR ne change pas. Dire si ces liens sont corrigés (liens seuls) ou laissés, puisque le renvoi de `docs/process/README.md` ne couvre pas les profils. La check-list cite « liens des docs déplacées » sans dire la règle.
7. **`docs/process/roles/planificateur.md:11` et `docs/process/roles/orchestrateur-tache.md:31`** : ces deux profils exigent encore le clone de référence pour une tâche de jam, alors que l'ADR 0016 rend l'ADR 0014 historique. Les corps d'issue lèvent la contradiction (« malgré son profil, que K1-2 réécrit »), ce qui suffit au seuil. Pour éviter qu'un orchestrateur de tâche bloque sa carte sur « accord attendu pour le clone de référence », un passage « Kit » d'une ligne, comme dans les trois autres profils, serait plus sûr. C'est hors de la lettre du brief : à l'orchestrateur de tâche de juger.
8. **`docs/process/roles/implementeur.md:13`** : les formes `git mv` servent à K1-2, alors que le brief limite les ajouts à la première issue. L'écart est justifié par le brouillon (`cadrage-kit-issues.md:32` : K1-2 tourne avec les profils de `main`) ; à signaler au mainteneur au feu vert de cadrage.
9. **`docs/specs/GLOSSARY.md:40`** (« Feu vert ») : l'allègement du relais est écrit au présent. Or la règle 6 d'`AGENTS.md` et le process gardent la forme complète jusqu'au merge de K1-2 (ADR 0016, « Entrée en vigueur »). Ajouter « à partir du merge de K1-2 ». Sans conséquence grave : un « ok » seul serait traité comme une simple information, ce qui est sans danger.
10. **`docs/specs/00-VISION.md:45`** : le principe « un projet sans enjeu d'argent ni de données de personnes passe en léger » omet la condition « en production » de FR-049 et du pitch de la même page (ligne 7). Aligner la formulation, par exemple : « *standard* pour un projet en production qui touche à l'argent ou à des données de personnes, *léger* ailleurs ».
11. **`docs/decisions/0016-kit-de-methode.md:93`** : l'ADR 0009 est classée « Valable » alors qu'elle a une partie caduque. Or la règle de la ligne 101 ne vise que les ADR « valables en partie ou précisées ». La classer « Valable en partie », pour que la mise à jour de son statut à l'acceptation ne soit pas oubliée.
12. **`README.md:21`** : la ligne « Licence » est sous la section « L'app (en cours de retrait) », que K1-1 fait retirer. La remonter au-dessus de cette section, pour que le retrait ne l'emporte pas (NFR-002 : licence explicite).
13. **`docs/plans/cadrage-kit-issues.md:57` à `:70`** : K1-1 est lourde pour un petit lot (ADR 0011) : retrait de l'app, quatre hooks rendus génériques, une garde unifiée, deux scripts, la CI et l'installation. Le découpage en trois issues vient du mainteneur (RET-016), il n'y a donc rien à changer ici. Le plan gagnerait à prévoir des étapes séparément vérifiables. Point pratique : sans `__init__.py`, `python3 -m unittest` sans argument ne découvre pas les tests de `hooks/` ni de `scripts/`. La commande de la CI et celle des profils (`python3 -m unittest *`) doivent donc nommer leur dossier, ce que le plan fixe.

RELECTURE : OK
