# ADR 0012 : le coordinateur est un rôle, ses garde-fous sont tenus par un hook

- **Statut** : proposée
- **Date** : 2026-10-08
- **Tranche** : RET-005, complète l'[ADR 0009](0009-permissions-par-role.md)

## Contexte

L'ADR 0009 donne un profil de permissions à chaque rôle du pipeline, transmis par les options de la CLI. Le coordinateur, session conversationnelle dans laquelle parle le mainteneur, n'en avait pas. La règle « le coordinateur ne produit aucun livrable » ne tenait donc qu'à sa mémoire et à son obéissance. Elle est née de cet épisode : il avait créé lui-même les milestones et les issues #1 à #4, ce qui a donné [RET-001](../specs/RETOURS.md).

Le mainteneur demande que le coordinateur ait lui aussi un garde-fou en code (RET-005). Ses options de CLI ne suffisent pas : il lui faut le shell (`orca`, `git`, `gh`) pour orchestrer, committer et publier, mais il ne doit écrire aucun fichier du repo.

Depuis l'ADR 0009, deux autres profils en sortent aussi : le rédacteur, rôle né de RET-001, et une variante du relecteur.

## Décision

- **Le coordinateur est un rôle**, avec son profil dans [`roles/coordinateur.md`](../process/roles/coordinateur.md).
- **Deux exceptions à l'ADR 0009**, propres au coordinateur :
  - il committe, pousse, publie sur GitHub et merge, après le feu vert correspondant et avec l'accord explicite du mainteneur. C'est le rôle que tiendra le cœur dans jam ;
  - il tourne en session interactive, et non en refus sans invite : le mainteneur est présent, et toute commande hors des réglages lui demande son accord.
- Sa session est lancée avec la variable d'environnement **`JAM_ROLE=coordinateur`**, qui permet à un hook de reconnaître le rôle. La variable doit être présente **au lancement** de la session : un `export` fait ensuite depuis le shell de l'agent n'atteint pas les hooks.
- **La garde est un hook personnel du poste du mainteneur, hors du repo.** Appelé avant chaque écriture de fichier, il refuse au coordinateur toute écriture hors de quatre emplacements : sa mémoire, le plan de la session, les dossiers temporaires de la session, et l'installation d'un hook déjà relu. Sans `JAM_ROLE`, il ne fait rien. Elle a été installée le 2026-10-09, après deux tours de relecture ; son état est suivi dans [Q-026](../specs/OPEN-QUESTIONS.md). **Dans jam, c'est le cœur qui jouera ce rôle** : il lance chaque rôle et tient seul le commit, la publication et le merge.
- **Profils hors de la table de l'ADR 0009**, tracés ici :

| Rôle | Fichiers | Shell | Réseau / Git distant |
|---|---|---|---|
| Coordinateur | Lecture ; écriture limitée à sa mémoire, au plan de la session, aux dossiers temporaires et à l'installation d'un hook relu | `orca`, `git`, `gh`. Accord du mainteneur pour le commit, le push, la publication et le merge, et pour toute commande hors des réglages du poste | Lecture : oui. Push, publication, merge : après feu vert |
| Rédacteur | Lecture ; écriture dans `docs/`, `AGENTS.md` et `README.md` | Aucun | Recherche web, en lecture |
| Relecteur, variante « issues publiées » | Comme le relecteur | En plus : `gh issue view`, `gh issue list`, `gh api` sur les milestones, formes exactes | `gh` en lecture seulement |

- À l'acceptation de cette ADR, le statut de l'ADR 0009 mentionne ce complément.

## Conséquences

- (+) RET-001 devient une contrainte, plus une consigne.
- (+) Le même mécanisme (`JAM_ROLE` + hook) pourra servir aux autres rôles quand les options de la CLI ne suffisent pas.
- (−) La garde ne voit pas les écritures faites par le shell (redirection, `gh issue create`). Les publications sur GitHub restent tenues par le feu vert et par l'accord explicite avant commit (AGENTS.md, règle 6).
- (−) La garde vit sur un seul poste et n'est pas versionnée : elle ne protège que là. C'est acceptable tant que jam se construit dans Orca, sur ce poste.
- (−) L'exception « installation d'un hook relu » permet aussi de modifier la garde elle-même. Le hook ne peut pas savoir si un hook a été relu : cette exception repose sur la relecture préalable, comme les écritures par le shell.
- (−) Une session coordinateur lancée sans `JAM_ROLE` n'est pas protégée, et rien ne le signale sinon le hook de démarrage, qui affiche « session libre ».
