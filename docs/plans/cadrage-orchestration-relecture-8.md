# Relecture du cadrage `cadrage-orchestration` — tour 8 (relecteur seul)

Périmètre : toutes les modifications non commitées (`git status`, `git diff`, fichiers nouveaux), avec l'accent sur la passe qui suit le feu vert de cadrage (profil du rédacteur, « Une fois le feu vert de cadrage donné… »).

## Vérifications faites

- **ADR 0011, 0012, 0013** : statut « acceptée » dans les trois fichiers et dans l'index `docs/decisions/README.md` (0013 ajoutée à l'index).
- **Reports de mentions prévues par les ADR** :
  - ADR 0011 (l. 39) prévoit une mention dans le statut de l'ADR 0008 : faite (`0008-boucle-exterieure-pipeline.md:3`), fidèle au §1 de l'ADR 0011.
  - ADR 0012 (l. 31) prévoit une mention dans le statut de l'ADR 0009 : faite (`0009-permissions-par-role.md:3`), fidèle aux profils et exceptions tracés dans l'ADR 0012.
  - ADR 0013 (l. 59) prévoit une mention dans le statut de l'ADR 0012 et de l'ADR 0009 : faites (`0012-coordinateur-role-garde-fous-hook.md:3`, `0009-permissions-par-role.md:3`), fidèles à la « Précision de l'ADR 0012 » (l. 50) et au profil de l'orchestrateur de tâche.
  - L'ADR 0013 ne prévoit aucune mention dans l'ADR 0008 (elle dit ne pas la rouvrir) : aucune ajoutée, c'est juste.
- **RET-001 à RET-010** : tous « appliqué ». RET-009 (l. 272) date l'acceptation de l'ADR 0013 au feu vert de cadrage formel, cohérent avec le statut.
- **Q-041** : présente, au format de la table (origine, question, porteur, statut « Ouvert »). Q-040 absent, comme annoncé.
- **Publication après le merge** : formulation identique dans `GLOSSARY.md:15` (« Brouillon d'issue »), `roles/redacteur.md:5`, `roles/coordinateur.md:28`, `process/README.md:32`, en tête de `cadrage-orchestration-issues.md:3` et dans l'ADR 0013 (§ Cadrages).
- **Issue #7** : `cadrage-orchestration-issues.md:8` porte « Publiée : #7 », renvoie à Q-041 et désigne la PR fautive (#5), comme l'exige l'ADR 0011 pour une issue `incident` ; labels `bug`, `incident` (l. 10). L'écart avec la règle de publication après le merge est expliqué par Q-041, pas passé sous silence.
- Aucune autre mention « proposée » ou « en application » ne subsiste pour ces ADR et retours. Le reste du diff (process, profils, `AGENTS.md`, glossaire, roadmap) ne contredit pas la passe.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. **`docs/specs/RETOURS.md:67`** (RET-006) : « À l'acceptation de l'ADR 0011, le statut de l'ADR 0008 **mentionnera** cette précision. » C'est fait. Correction proposée : « Le statut de l'ADR 0008 mentionne cette précision depuis l'acceptation de l'ADR 0011. »
2. **`docs/specs/RETOURS.md:16`** (RET-001) : « Les corrections […] **seront publiées** par le coordinateur après le feu vert. » Le retour est désormais « appliqué » ; si ces corrections ont été publiées (PR #6 mergée), passer au passé ; sinon, le signaler comme reste à faire. Je n'ai pas pu vérifier sur GitHub (pas d'accès `gh` dans ce profil).
3. **`docs/specs/RETOURS.md:301`** (RET-010, Impact) : le brouillon d'issue du bug est cité sans son numéro. Ajouter « publiée : #7 » pour qu'un lecteur ne cherche pas une issue encore à publier.
4. **`docs/specs/OPEN-QUESTIONS.md:44`** (Q-041) : préciser que la publication de #7 avant le merge est un écart à la règle de l'ADR 0013 (§ Cadrages), pour que la question ne se lise pas comme une pratique admise. Par exemple : « …publiée à part, avant le merge du cadrage, par exception à l'ADR 0013. »

RELECTURE : OK
