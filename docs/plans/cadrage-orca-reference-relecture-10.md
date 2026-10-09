# Relecture — cadrage-orca-reference, tour 10 (intégration de `main`)

Relecteur seul, les deux axes, section « Relecture d'un cadrage » du profil. Périmètre court : `git diff HEAD` (résolution des conflits et alignements) et `git diff origin/main` sur `docs/decisions/0009-permissions-par-role.md`, `docs/decisions/README.md`, `docs/process/roles/`, `docs/specs/OPEN-QUESTIONS.md`, `docs/specs/RETOURS.md`, `docs/references/orca.md`. ADR 0013, ADR 0014 et ADR 0015 lus en entier pour la cohérence.

## Vérifications faites, sans constat

- **Marqueurs de conflit** : aucun (`<<<<<<<`, `=======`, `>>>>>>>`, `|||||||`) dans le repo hors `docs/plans/`. Les fichiers résolus sont encore « UU » dans l'index : c'est normal, le `git add` revient à l'orchestrateur de tâche avant le commit.
- **Apports de `main` conservés** : `git diff origin/main` ne retire aucune ligne de `main`. Les 13 lignes « supprimées » sont des lignes de `main` reprises à l'identique et prolongées : statut de l'ADR 0009 (compléments 0012 et 0013 gardés, précision 0014 ajoutée), permissions et paragraphe `Edit(./**)` de l'implémenteur (« l'orchestrateur de tâche juge » gardé ; paragraphe sur `rm` et RET-010 gardé), étape « Étapes » du planificateur (renvoi à la recette gardé, renumérotée en 4), lignes de `orca.md`, règle 9 d'`AGENTS.md`. Statuts 0011 et 0012 « Acceptée » de `main` gardés dans l'index des ADR ; RET-001 à RET-010 et RET-012/013 identiques à `main`.
- **Numérotation** : RET-001 à RET-013 dans l'ordre, RET-011 entre RET-010 et RET-012. Q-035 à Q-043 puis Q-050, Q-051 : Q-040, Q-042, Q-043 à leur place autour de Q-041 (de `main`), aucun doublon. Index des ADR : 0013, 0014, 0015 dans l'ordre. Aucune référence à un numéro inexistant (Q-044 à Q-049, RET-014+, ADR 0016+).
- **Statuts** : ADR 0014 « acceptée » (fichier et index) ; RET-011 « appliqué » ; statut de l'ADR 0009 mentionne la précision de l'ADR 0014, comme l'ADR 0014 le demande ; Q-042 tranchée à l'intégration ; Q-043 confiée à l'orchestrateur de tâche.
- **ADR 0013 et ADR 0015** : plus aucun « signaler au coordinateur » dans l'apport du cadrage. `orca.md` §0 (l. 34) fait remonter une erreur de carte par le commentaire de la carte, avec le feu vert plan, comme les suggestions récurrentes de relecture (profil de l'orchestrateur de tâche, l. 30). Préparation, vérification et remise du clone sont à l'orchestrateur de tâche partout : `orca.md` §0, planificateur, implémenteur (via le brief), glossaire « Clone de référence », RET-011 point 5, profil de l'orchestrateur de tâche (l. 31).
- **Q-042 et le process** : le choix de ne pas retoucher « Lancement d'un rôle » tient. `docs/process/README.md` l. 96 donne le contenu minimal (« toujours ») ; le chemin du clone est un ajout que chaque profil concerné prévoit.
- **Chemins machine** : aucun dans l'apport du cadrage. Le clone n'est désigné que par `<clone-orca>`, les fichiers d'Orca par leur chemin dans son repo.

## Constats

### Bloquant

Aucun.

### À corriger

1. **`docs/process/roles/orchestrateur-tache.md`, l. 31 (règle « Clone de référence ») contre l. 7-8 (permissions du même profil)**. La règle ajoutée à l'intégration confie à l'orchestrateur de tâche la procédure du §0 de `docs/references/orca.md` (l. 23-34). Or cette procédure sort de ses permissions telles que le profil les écrit :
   - **écriture** : le clone vit dans « un dossier temporaire du poste » et « sert à toutes les tâches » (`orca.md` l. 23 et 33), donc à plusieurs sessions. Le profil limite l'écriture aux « dossiers temporaires **de la session** » (l. 8). L'ADR 0013 (table, l. 56) dit seulement « dossiers temporaires » : pas de contradiction avec l'ADR, mais avec le profil. Une fois la garde étendue (Q-036), le même écart pourrait faire refuser la préparation du clone ;
   - **shell** : `chmod -R a-w`, `chmod -R u+w`, `rm -rf` et la suppression du clone ne sont pas dans sa liste (`orca`, `git`, `gh`, l. 7). D'après l'ADR 0013, chacune de ces commandes demande donc l'accord du mainteneur dans le terminal de l'orchestrateur de tâche, où il n'est en général pas. Bloqué sur cette invite, l'orchestrateur ne peut plus mettre à jour sa carte (ADR 0015, table l. 42). Le risque se présente à la première préparation, puis à chaque clone refait parce qu'un dossier temporaire a été purgé (`orca.md` l. 34).

   **Correction attendue** : écrire l'écart dans le profil, sans changer d'ADR.
   - Au point « Écriture de fichiers » (l. 8) : « … et le dossier du clone de référence d'Orca, partagé entre les sessions (RET-011) ».
   - À la règle « Clone de référence » (l. 31) : `chmod` et la suppression du clone sont hors de sa liste et demandent l'accord du mainteneur (ADR 0013). Il prépare ou refait donc le clone avant de lancer le planificateur, et met sa carte en attente du mainteneur tant que l'invite n'a pas de réponse.
   - En une phrase dans Q-036 : l'extension de la garde doit autoriser ce dossier.

   Si le rédacteur juge que ce dossier partagé change la ligne de l'ADR 0013 au lieu de la préciser, il le signale à l'orchestrateur de tâche au lieu de trancher.

### Suggestions

1. **`docs/specs/RETOURS.md`, l. 161** : « (reporté à l'intégration de `main`, Q-042) » décrit un état passé : c'est fait. Proposition : « (ajouté à l'intégration de `main`, Q-042) ».
2. **`docs/specs/RETOURS.md`, RET-011, statut** : « appliqué (feu vert de cadrage du 2026-10-09) ». La règle du profil de l'orchestrateur de tâche a été ajoutée après ce feu vert, à l'intégration. Si le feu vert qui suit cette relecture couvre l'intégration, on peut l'ajouter en fin de statut (« ; intégration de `main` relue au tour 10 »). Pour la traçabilité seulement.

RELECTURE : CORRECTIONS (1)
