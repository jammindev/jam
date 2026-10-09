# Relecture — cadrage-retours-essai, tour 4 (relecture courte)

Relecteur seul, docs. Périmètre limité au brief : passe des statuts et trois retouches.

## Points vérifiés

1. **ADR 0015 acceptée** : `docs/decisions/0015-remontee-carte-seule-coordinateur-flottant.md:3` porte « acceptée » ; l'index `docs/decisions/README.md` ajoute la ligne 0015 « Acceptée », titre conforme à celui de l'ADR. OK.
2. **Statut de l'ADR 0013** (`docs/decisions/0013-orchestration-deux-niveaux.md:3`) : « acceptée. Précisée par l'[ADR 0015](…) : … ». Même forme que 0008 et 0012 (lien relatif, deux-points, résumé en une phrase). Le résumé couvre les deux volets de 0015 (carte seule, terminal flottant lancé depuis le worktree principal). Répond à la phrase « À l'acceptation de cette ADR, le statut de l'ADR 0013 mentionne cette précision » (0015, l. 46). OK.
3. **RET-012 et RET-013** : nouvelles entrées en fin de `docs/specs/RETOURS.md`, au statut « appliqué ». Le diff ne montre que des ajouts après RET-011 : aucun autre retour modifié. OK.
4. **Retouches** :
   - `docs/process/roles/coordinateur.md:31` : publication juste après le `git pull`, avant « ✓ mergé » et le nettoyage, avec la raison (le segment `✓ feu vert de cadrage` reste sur la carte jusqu'à la publication). Cohérent avec `docs/process/README.md:32` (« Le coordinateur merge, puis publie ») et avec les segments cumulés de `docs/process/README.md:128-130`. OK.
   - ADR 0015, table, l. 38 : « Cité dans le commentaire de la carte s'il ouvre une action du coordinateur (merge, publication) ; sinon, l'orchestrateur de tâche agit et le segment d'état change ». Cohérent avec la Décision (l. 24) et avec `docs/process/README.md:128` et `:178`. OK.
   - `docs/process/roles/implementeur.md:13` : sujet explicite (« La liste ne contient ni `rm` ni arrêt de processus, et l'implémenteur ne les obtient pas par détour ») ; phrase correcte, renvoi à RET-010 juste. OK.
5. **Cohérence et repo public** : aucun chemin propre au poste dans les diffs relus (`<chemin du worktree principal>` reste un gabarit). Aucun secret ni donnée personnelle.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

- `docs/specs/RETOURS.md`, RET-013, ligne **Analyse** : « Un feu vert donné dans le worktree remonte par le commentaire de la carte » ne reprend pas la restriction ajoutée dans l'ADR 0015 (seulement s'il ouvre une action du coordinateur). L'analyse date du retour et la règle appliquée est bien dans l'ADR et le process ; si l'on veut que le retour se lise sans contradiction, ajouter « s'il ouvre une action du coordinateur (merge, publication) ».
- `docs/process/roles/coordinateur.md:30` : la règle « Seul à merger » énumère merge → `git pull` → « ✓ mergé » → nettoyage, et la ligne 31 intercale la publication pour un cadrage. Lisible tel quel ; on peut ajouter en fin de ligne 30 « (pour un cadrage, publication avant « ✓ mergé », voir ci-dessous) » pour qu'une lecture rapide de la ligne 30 seule ne fasse pas sauter l'étape.
- Pour information : l'index saute de 0013 à 0015 et aucun fichier 0014 n'existe sur cette branche. Si le numéro est réservé par un autre cadrage en cours, rien à faire ; sinon, vérifier la numérotation avant le commit.

RELECTURE : OK
