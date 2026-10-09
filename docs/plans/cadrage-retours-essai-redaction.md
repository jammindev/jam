# Rapport de rédaction : cadrage-retours-essai

J'ai modifié les docs (process, profils, specs) et ajouté l'ADR 0015 au statut « proposée ». J'ai inscrit RET-012 et RET-013 au statut « en application ». Il n'y a pas de brouillon d'issue, aucune correction de code ne s'imposant.

## Fichiers touchés

- `docs/decisions/0015-remontee-carte-seule-coordinateur-flottant.md` (nouveau) et `docs/decisions/README.md`
- `docs/process/README.md`
- `docs/process/roles/orchestrateur-tache.md`, `coordinateur.md`, `recetteur.md`, `implementeur.md`, `planificateur.md`
- `docs/specs/RETOURS.md` (RET-012, RET-013)
- `docs/specs/OPEN-QUESTIONS.md` (Q-033 et Q-037 tranchées, Q-036 complétée, Q-050 ajoutée ; Q-051 ajoutée au tour 1)
- `docs/specs/01-REQUIREMENTS.md` (FR-016), `docs/specs/02-ARCHITECTURE.md` (composant « Coordinateur »)
- `docs/specs/GLOSSARY.md` (« Coordinateur », « Orchestrateur de tâche », nouveau terme « Terminal flottant »)
- `docs/plans/cadrage-retours-essai-redaction.md` (ce rapport)

## Les 14 frictions

1. **Recetteur sans commande, Q-033 confiée à l'orchestrateur de tâche** : corrigé. La commande est écrite dans le profil du recetteur, et Q-033 désigne désormais le rédacteur.
2. **Profil d'orchestrateur sur une branche non mergée** : corrigé dans le process et le profil du coordinateur. Une tâche suit le process et les profils mergés, et un cadrage qui les change est mergé avant les tâches qui doivent l'appliquer.
3. **Le hook de démarrage ne reconnaît pas l'orchestrateur** : déjà suivi par Q-036. J'y ai seulement ajouté que #7 l'a confirmé.
4. **Un relais ne se distingue pas d'une saisie du mainteneur** : corrigé par l'ADR 0015 et RET-013 (la carte seule vers le coordinateur).
5. **L'implémenteur n'a ni `rm` ni arrêt de processus** : corrigé sans élargir sa liste. L'installation neuve et le lancement de l'app relèvent de la recette, une étape de CI se vérifie sur la PR, et le planificateur ne les met plus dans les étapes de l'implémenteur.
6. **Une suggestion revient d'un tour de relecture à l'autre** : corrigé dans le process (section « Relecture »). Une suggestion ne bloque pas et ne compte pas comme absence de progrès. Celles qui reviennent sont citées au mainteneur avec le feu vert suivant, et il décide.
7. **Commande du recetteur composée à la volée** : corrigé. Je l'ai généralisée en `<tâche>`, `<dossier de recette>` et `<chemin du worktree>`, avec les formes `rtk`, l'interdit `Edit(.claude/**)` et ni commit, ni push, ni `gh`. J'ai retiré le `--add-dir` vers le cadrage, devenu inutile (voir 2).
8. **`orca terminal read` ne rend que l'écran** : corrigé dans le process (section « Lancement d'un rôle »). Il sert à lire la ligne de fin d'un rôle ; le contenu se lit dans son fichier.
9. **Deux instances de jam partagent `jam.db`** : nouvelle question Q-050. L'app passe le chemin au cœur par `--db`, donc `JAM_DATA_DIR` ne la déplace pas. Le recetteur arrête désormais l'app en arrêtant sa propre tâche de fond, et ne garde aucun `pkill` (voir les points tranchés).
10. **Cmd+K non simulé** : tranché, le clavier reste au mainteneur. Le rapport de recette note « non reproduite ». Le contrôle outillé viendra avec le test e2e de l'app (Q-017).
11. **`--milestone` veut le titre exact** : corrigé dans le profil de l'orchestrateur de tâche (titre lu sur l'issue) et dans la ligne « PR + CI » de la table de correspondance du process.
12. **Le coordinateur change de terminal** : réglé par l'ADR 0015. Personne n'a plus besoin de son handle, qui a disparu du brief de l'orchestrateur de tâche.
13. **Rebaser sur `main` avant la PR** : corrigé dans le profil de l'orchestrateur de tâche. Pas de rebase si la PR est mergeable sans conflit, puisque la CI d'une PR tourne sur sa fusion avec `main`. En cas de conflit, la tâche passe en « ⛔ bloqué » et le coordinateur décide avec le mainteneur.
14. **Canal `orca terminal send` abandonné** : corrigé partout. Profils, process (acteurs, cadrage, correspondance, lancements, remontée, table « Signalement d'attente » sans sa colonne « Message au coordinateur », « Ce qu'Orca ne permet pas »), Q-037 tranchée et glossaire.

## Points tranchés

- **Nouvelle ADR plutôt que retouche de l'ADR 0013**, puisqu'elle est acceptée. L'ADR 0015 précise l'ADR 0013 sur deux points : la carte seule et le terminal flottant. Le statut de l'ADR 0013 la mentionnera à l'acceptation.
- **RET-013 séparé de RET-012** : ce sont deux décisions distinctes, même si l'ADR 0015 couvre les deux.
- **Remarque du mainteneur pour jam** : je l'ai traduite en précision de FR-016 (champ de conversation accessible partout, avec une session dans le worktree principal) plutôt qu'en nouvelle exigence. Cela évite un numéro FR qui pourrait entrer en conflit avec le cadrage parallèle et ne change pas l'étape (Q-039).
- **Feu vert donné dans le worktree** : il est cité dans le commentaire de carte seulement s'il ouvre une action du coordinateur (merge, publication). Le commentaire garde la citation tant que le coordinateur n'a pas agi. J'ai ajouté une ligne pour ce cas à la table « Signalement d'attente ».
- **Aucun `pkill` dans la commande du recetteur.** L'arrêt de sa propre tâche de fond a suffi à #7, et un `pkill` reste une commande large. Il ne garde que `pgrep` pour vérifier, et liste les processus restants sans les arrêter ; c'est le mainteneur qui les arrête. Ma première justification (un `pkill -f <chemin du worktree>/` tuerait la session du recetteur, dont la ligne de commande contient ce chemin) n'est pas confirmée par #7, où `pgrep` sur le nom du worktree n'a rien trouvé : je ne m'appuie plus dessus (S1 du tour 1).
- **`rm -rf` en forme exacte**, sans joker. La commande est à mettre à jour quand un paquet s'ajoute à `apps/` ou `packages/`.
- **Q-033, déduction** : je n'ai trouvé aucun refus d'écriture de l'implémenteur dans les docs de #7. J'en conclus que `Edit(./**)` a été vérifié, puisque les cinq fichiers du correctif ont été écrits. C'est déduit, pas constaté dans un journal.
- **Une conséquence (−) ajoutée à l'ADR 0015** : un message du coordinateur dans le terminal d'un orchestrateur de tâche peut encore croiser une saisie du mainteneur, s'il parle à cet orchestrateur au même moment.

## Corrections du tour 1

Rapport : `docs/plans/cadrage-retours-essai-relecture-1.md`, `RELECTURE : CORRECTIONS (3)`, aucun bloquant.

### À corriger

- **C1, retour reçu par l'orchestrateur de tâche sans forme sur la carte** : corrigé.
  - Nouvelle ligne de la table « Signalement d'attente » : statut `in-review`, commentaire `💬 retour : <une ligne> · <chemin absolu du fichier de l'analyse>`.
  - L'orchestrateur de tâche écrit la reformulation et l'analyse dans un dossier temporaire de sa session, le seul endroit où il peut écrire (process, « Cadrage » étape 1 ; profil de l'orchestrateur de tâche).
  - Le segment reste sur la carte jusqu'à l'accusé de réception du coordinateur, donné dans le terminal de l'orchestrateur de tâche, même si l'état de la tâche change entre-temps.
  - Le coordinateur traite lui-même les segments `✓` et `💬` : profil du coordinateur, process (« Surveillance »), ADR 0015.
  - L'emplacement du fichier d'analyse est précisé dans le profil du coordinateur.
- **C2, suggestions récurrentes sans canal** : corrigé (process, « Relecture » ; profil de l'orchestrateur de tâche).
  - Le commentaire du feu vert suivant désigne aussi le dernier rapport où chaque suggestion revient, par exemple `· suggestion récurrente : <chemin du worktree>/docs/plans/<tâche>-relecture-<axe>-<tour>.md`.
  - Le coordinateur les présente au mainteneur avec le feu vert.
- **C3, deux citations de feu vert sur la carte d'un cadrage** : corrigé (process, « Remontée vers le coordinateur » et table ; profil de l'orchestrateur de tâche).
  - Le préfixe est fixé : `✓` pour une citation qui attend une action du coordinateur, `⏸` pour une attente du mainteneur.
  - Les segments se séparent par ` · ` et se cumulent jusqu'à l'accusé de réception.
  - Deux exemples couvrent le cadrage : après l'ouverture de la PR, puis après le feu vert merge donné dans le worktree.

### Suggestions

- **S1, qui arrête les processus restants** : appliquée. C'est le mainteneur (profil du recetteur), puisque l'orchestrateur de tâche n'a pas d'arrêt de processus. J'ai aussi retiré du rapport la justification non confirmée par #7 (voir « Points tranchés »).
- **S2, `<tâche>` n'est pas un chemin** : appliquée (profil du recetteur).
- **S3, ADR 0015** : appliquée.
  - La conséquence de l'ADR 0013 sur l'expéditeur non authentifié est citée telle quelle, puis « s'étend aux commentaires de carte ».
  - La mention « À l'acceptation… » passe sous « Ce que l'ADR 0013 devient ».
- **S4, plusieurs repos** : appliquée par une question ouverte, Q-051 (un coordinateur par repo ou un seul ?), plutôt que par une décision. Le multi-repo et le coordinateur conversationnel viennent tous deux plus tard (Q-039). FR-016 et RET-012 renvoient à Q-051.
- **S5, `jam.db` dans « Ce qu'Orca ne permet pas »** : appliquée. La puce est retirée du process ; le point reste dans le profil du recetteur et dans Q-050.
- **S6, `in-review` pour un cas qui attend le coordinateur** : appliquée avec C1 et C3, sans nouveau statut (Orca n'en a que quatre).
  - Le préfixe du commentaire dit qui est attendu : `⏸` ou `⛔` pour le mainteneur, `✓` ou `💬` pour le coordinateur.
  - Le mainteneur ne regarde que les cartes `⏸` et `⛔` : process, table et « Ce qu'Orca ne permet pas ».
- **S7, CI non relancée quand `main` avance** : appliquée. Au merge, le coordinateur vérifie que la PR est toujours mergeable sans conflit (profil du coordinateur), et le profil de l'orchestrateur de tâche le rappelle dans la règle de rebase.

### Fichiers touchés au tour 1

`docs/process/README.md`, `docs/process/roles/orchestrateur-tache.md`, `coordinateur.md`, `recetteur.md`, `docs/decisions/0015-remontee-carte-seule-coordinateur-flottant.md`, `docs/specs/OPEN-QUESTIONS.md` (Q-051), `docs/specs/01-REQUIREMENTS.md` (FR-016), `docs/specs/RETOURS.md` (impact de RET-012), ce rapport.

## Corrections du tour 2

Rapport : `docs/plans/cadrage-retours-essai-relecture-2.md`, `RELECTURE : CORRECTIONS (1)`, aucun bloquant. Consigne : le format de la carte doit rester lisible d'un coup d'oeil par le mainteneur.

### À corriger

- **C1, ordre des segments et statut de la carte** : corrigé, en simplifiant la section « Signalement d'attente » du process.
  - **Ordre fixe** : en tête, un seul **segment d'état** (`▶`, `⏸`, `⛔`, ou `✓ mergé`), puis les segments qui attendent le coordinateur (`✓` feu vert, `💬` retour). La table est coupée en deux, une par sorte de segment, avec un exemple (`▶ implémenteur en cours · 💬 retour : …`).
  - **Statut** : seul le segment d'état le fixe. Les segments `✓` et `💬` ne le changent pas. Une carte sans segment d'état (par exemple après un feu vert merge donné dans le worktree) passe en `in-review`.
  - **Qui regarde quoi** : le mainteneur ne lit que le début des cartes `in-review` (`⏸` ou `⛔`). Le coordinateur cherche les `✓` et `💬` sur toutes les cartes, quel que soit le statut.
  - Pour garder ` · ` comme seul séparateur de segments : le fichier d'un `💬` suit une virgule (`💬 retour : <une ligne>, <chemin>`), et une suggestion récurrente se met entre parenthèses dans le segment du feu vert. Les formats cités dans la section « Corrections du tour 1 » ci-dessus sont donc remplacés.
  - Mêmes règles reportées dans la remontée (« Surveillance », « Feux verts » et l'exemple du cadrage), les profils de l'orchestrateur de tâche et du coordinateur, et l'ADR 0015.

### Suggestions

- **S1, « le reste de l'ADR 0013 tient »** : appliquée. Trois lignes ajoutées au tableau « Ce que l'ADR 0013 devient », une par conséquence qui change : contexte léger (cartes seules), risque Q-037 (réalisé, supprimé), invite de permission (ne peut plus mettre à jour sa carte).
- **S2, joker `curl …/json*`** : appliquée. Formes exactes `curl -s http://localhost:9333/json` et `…/json/list`, avec leurs formes `rtk`. `/json/close` et `/json/activate` ne sont plus permis.
- **S3, analyse d'un retour dans un dossier temporaire** : appliquée (profil du coordinateur). Ce dossier disparaît au nettoyage du worktree : le coordinateur reprend son contenu dans le brief du cadrage, au lieu d'y renvoyer par le chemin.

### Fichiers touchés au tour 2

`docs/process/README.md`, `docs/process/roles/orchestrateur-tache.md`, `coordinateur.md`, `recetteur.md`, `docs/decisions/0015-remontee-carte-seule-coordinateur-flottant.md`, ce rapport.

## Passe des statuts

Feu vert de cadrage du mainteneur : « ok pour tout », 20:34, 2026-10-09, session du coordinateur. Tour 3 : `docs/plans/cadrage-retours-essai-relecture-3.md`, `RELECTURE : OK`, trois suggestions.

### Statuts

- **ADR 0015** : « acceptée », dans le fichier et dans l'index `docs/decisions/README.md`. La phrase « À l'acceptation de cette ADR, le statut de l'ADR 0013 mentionne cette précision » est gardée telle quelle, comme dans les ADR 0011, 0012 et 0013.
- **ADR 0013** : son statut mentionne la précision, sur le modèle des ADR 0008 et 0012 : remontée par la carte seule, sans message court, et coordinateur dans le terminal flottant, lancé depuis le worktree principal.
- **RET-012 et RET-013** : « appliqué ».

### Suggestions du tour 3

- **S1, publication avant le nettoyage** : appliquée (profil du coordinateur). Pour un cadrage, il publie les issues et les milestones juste après le `git pull`, avant de passer la carte à « ✓ mergé » et de nettoyer le worktree. Le segment `✓ feu vert de cadrage` reste ainsi sur la carte jusqu'à la publication qu'il autorise.
- **S2, ligne de table de l'ADR 0015** : appliquée. Le feu vert donné dans le worktree n'est cité sur la carte que s'il ouvre une action du coordinateur (merge, publication) ; sinon, l'orchestrateur de tâche agit et le segment d'état change.
- **S3, sujet de phrase** : appliquée (profil de l'implémenteur). « …ni arrêt de processus, et l'implémenteur ne les obtient pas par détour (`node -e`) ».

### Fichiers touchés à la passe des statuts

`docs/decisions/0013-orchestration-deux-niveaux.md`, `docs/decisions/0015-remontee-carte-seule-coordinateur-flottant.md`, `docs/decisions/README.md`, `docs/specs/RETOURS.md`, `docs/process/roles/coordinateur.md`, `docs/process/roles/implementeur.md`, ce rapport.

RÉDACTION PRÊTE
