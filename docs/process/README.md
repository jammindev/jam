# Développer jam avec Orca, en appliquant notre propre pipeline

> En attendant que jam sache dérouler son pipeline ([ADR 0008](../decisions/0008-boucle-exterieure-pipeline.md)), on le **déroule à la main dans Orca**. Deux bénéfices : jam est construit selon sa propre méthode, et on éprouve le pipeline sur papier avant de le coder. Chaque friction rencontrée est notée dans `OPEN-QUESTIONS.md` et alimente E0.

## Acteurs

- **Mainteneur** : donne les trois feux verts et fait la recette.
- **Coordinateur** : une session d'agent conversationnelle, dans laquelle le mainteneur parle. Il crée les worktrees, lance les rôles, lit leurs sorties, tient le mainteneur informé, committe et merge **après** les feux verts. Il ne code pas.
- **Rôles** : planificateur, implémenteur, relecteur, recetteur. Chacun est une session d'agent **neuve**, lancée dans le worktree avec son profil ([`roles/`](roles/)) et ses permissions ([ADR 0009](../decisions/0009-permissions-par-role.md)).

## Correspondance entre le pipeline cible et Orca

| Étape | Cible (jam E0) | Aujourd'hui, dans Orca |
|---|---|---|
| Tâche | Issue GitHub | Issue GitHub si le repo distant existe, sinon un jalon de `04-ROADMAP.md` |
| Worktree | Créé par le cœur | `orca worktree create --name <tâche> --no-parent`, nommé `e0-s1-squelette`, etc. |
| Plan | Rôle planificateur | Terminal dans le worktree, agent en `dontAsk` + lecture seule, écrit uniquement `docs/plans/<tâche>.md` |
| **Feu vert 1** | File « À toi » | Statut du worktree `in-review`, commentaire « ⏸ feu vert plan ». Le mainteneur répond au coordinateur |
| Implémentation TDD | Rôle implémenteur, boucle jusqu'au vert | Nouveau terminal, agent en `acceptEdits` + liste blanche shell. Ni commit ni push |
| Relecture | Rôle relecteur, contexte neuf | Nouveau terminal, lecture seule, écrit `docs/plans/<tâche>-relecture.md`. Les corrections repartent vers l'implémenteur |
| Recette | Rôle recetteur, puis mainteneur | Contrôles automatisables par l'agent, puis test manuel du mainteneur |
| **Feu vert 2** | File « À toi » | Statut `in-review`, commentaire « ⏸ feu vert recette ». Le coordinateur committe une fois le feu vert donné |
| PR + CI | Le cœur via `gh` | `gh pr create` + CI, **si le repo distant existe**. Sinon, l'étape est sautée |
| **Feu vert 3** | File « À toi » | Commentaire « ⏸ feu vert merge » |
| Merge | `gh pr merge` | `gh pr merge`, ou merge local dans `main` tant qu'il n'y a pas de remote |
| Nettoyage | Le cœur | `orca worktree rm` + suppression de la branche |

## Lancement d'un rôle (coordinateur)

```sh
# 1. Worktree de la tâche
orca worktree create --repo id:<repoId> --name <tâche> --no-parent --json
# 2. Terminal du rôle (profil de permissions dans roles/<rôle>.md)
orca terminal create --worktree id:<repoId>::<chemin> --title <rôle> --command '<commande du rôle>' --json
# 3. Attendre que l'agent soit prêt, puis envoyer le brief
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 60000 --json
orca terminal send --terminal <handle> --text "<brief>" --enter --json
# 4. Suivre
orca terminal wait --terminal <handle> --for tui-idle --timeout-ms 1800000 --json
orca terminal read --terminal <handle> --json
```

Le brief d'un rôle contient toujours : le chemin du profil de rôle à lire, la tâche (jalon ou issue), les livrables attendus et le critère de fin.

## Signalement d'attente (file « À toi » provisoire)

| Situation | Statut Orca | Commentaire de la carte |
|---|---|---|
| Un rôle travaille | `in-progress` | `▶ <rôle> en cours` |
| Feu vert attendu | `in-review` | `⏸ feu vert <plan / recette / merge>` |
| Bloqué (garde-fou, refus de permission) | `in-review` | `⛔ bloqué : <raison>` |
| Terminé | `completed` | `✓ mergé` |

Le mainteneur n'a qu'une chose à regarder : les cartes en `in-review`.

## Garde-fous

- Implémentation : **8 itérations au plus** (cycles test-correction). Au-delà, la tâche passe en « bloqué ».
- Relecture → implémentation : **2 allers-retours au plus**. Au-delà, la décision revient au mainteneur.
- Aucun rôle ne committe, ne pousse ni ne merge.

## Ce qu'Orca ne permet pas (et que jam fera)

- Les permissions par rôle ne s'appliquent qu'aux options passées à la CLI de l'agent : on ne peut rien imposer de plus fin.
- La « file » se réduit aux cartes `in-review` : il n'y a pas de vue dédiée.
- Les boucles et les garde-fous sont tenus par le coordinateur, donc par un agent, et non par du code.
- L'état d'avancement vit dans les commentaires de cartes et dans `docs/plans/`, pas dans une base.
