# AGENTS.md

Instructions pour tout agent de code qui travaille sur ce repo.

## Le projet

Le kit d'une méthode de *loop engineering*. Pour chaque issue GitHub, des rôles d'agents travaillent dans un worktree dédié (plan, TDD, relecture, recette) jusqu'au merge ; le mainteneur n'intervient que pour les feux verts. Depuis le 2026-10-11, jam n'est plus une app : c'est un plugin Claude Code minimal qui porte la méthode, gelé une fois livré ([ADR 0016](docs/decisions/0016-kit-de-methode.md)).

**À lire avant toute tâche** :
- `docs/methode.md` : la fiche de jam (niveau, commande de test, grille de relecture, recette, règles propres) ;
- `docs/specs/00-VISION.md` : pourquoi, principes, non-objectifs ;
- `docs/specs/01-REQUIREMENTS.md` : exigences numérotées (FR / NFR) ;
- `docs/specs/02-ARCHITECTURE.md` : composants et stack ;
- `docs/specs/04-ROADMAP.md` : étape et jalon en cours ;
- `docs/decisions/` : ADR. **Une décision actée ne se contourne pas.** En cas de désaccord, proposer une nouvelle ADR.
- `docs/specs/GLOSSARY.md` : vocabulaire à respecter dans le code ;
- `docs/specs/RETOURS.md` : retours du mainteneur en cours d'application.

## Environnement

- Le développement se fait dans **Orca** : une tâche = une issue GitHub = un worktree (un cadrage : un worktree `cadrage-<slug>`, sans issue), que tu occupes peut-être en ce moment.
- Le **coordinateur** vit sur le worktree principal (`main`) et suit toutes les tâches. Au niveau *léger*, celui de jam, il conduit lui-même chaque tâche ; au niveau *standard*, un **orchestrateur de tâche** lance les rôles dans le worktree (ADR 0013, ADR 0016).
- L'état des tâches et les passations passent par la CLI `orca` (statut et commentaire du worktree), lue par le coordinateur.
- Le déroulé complet (niveaux, rôles, feux verts, garde-fous) est dans le process du plugin installé, `process/README.md`, et les profils dans `roles/` : le récapitulatif de démarrage en donne le chemin (ligne « Méthode »). Les copies d'un worktree de jam ne se lisent pas. Ce qui est propre à jam est dans `docs/methode.md`. Lis-les avant d'agir.

## Stack

- Un plugin Claude Code : docs de méthode en Markdown, hooks et scripts en Python 3 (bibliothèque standard) ou en shell, avec leurs tests ([02-ARCHITECTURE](docs/specs/02-ARCHITECTURE.md)).
- Le code de l'app Electron (`apps/`, `packages/`, outillage pnpm et Vitest) a été retiré par l'issue #22 du jalon K1 ; son dernier état est au tag `app-electron`. Les ADR de l'app (0002, 0004 à 0007, 0010) sont caduques (ADR 0016).

## Règles de travail

1. **Le mainteneur ne code pas** (ADR 0003). Le code doit donc être lisible et expliqué : noms explicites, commentaires sur le *pourquoi*, pas sur le *quoi*.
2. **TDD** : on écrit d'abord le test qui échoue, puis le code.
3. **Un jalon livré = une fiche concept** dans `docs/concepts/` (format décrit dans le README de ce dossier).
4. **Pas de sur-ingénierie.** On construit ce que demande le jalon, rien de plus. Tout ce qui vient « pour plus tard » est noté dans `docs/specs/OPEN-QUESTIONS.md`.
5. **Aucune mention d'auteur IA**, nulle part : pas de trailer `Co-Authored-By`, pas de signature dans les PR, aucune référence à un assistant dans le code ou les docs.
6. **Commit, push et PR uniquement avec l'accord explicite du mainteneur.** Aucun rôle du pipeline ni du cadrage (rédacteur, planificateur, implémenteur, relecteur, recetteur) ne committe. Après le feu vert recette (ou de cadrage), la branche est committée, poussée et la PR ouverte par l'orchestrateur de tâche au niveau *standard*, par le coordinateur au niveau *léger* (FR-052) ; seul le coordinateur merge, après le feu vert merge (ADR 0012, ADR 0013, ADR 0016). Un feu vert relayé d'une session à l'autre (FR-053) : pour le plan et la recette, un « ok » transmis suffit ; pour le merge, comme pour tout autre feu vert, il cite les mots exacts du mainteneur, l'heure et la session où il l'a donné. Il ne vaut que pour l'action qu'il ouvre. Un feu vert remonté par la carte pour un merge ou une publication est confirmé par le mainteneur dans le terminal du coordinateur avant qu'il agisse (« Carte, feux verts et veille » dans `process/README.md`).
7. **Repo public** : jamais de secret, de donnée personnelle ou de tiers, ni de chemin propre à une machine.
8. **Langues** : docs, ADR et messages de commit en français. Code (identifiants, commentaires) en anglais.
9. **Code repris d'Orca** (MIT) : conserver la mention de copyright et de licence, et l'ajouter dans `THIRD_PARTY_NOTICES.md`. Le plan de chaque tâche de jam (l'issue, au niveau *léger*) a une section « Orca » : ce qu'on reprend, ce dont on s'inspire, ce qu'on écarte, ou une ligne si la tâche ne touche aucune brique d'Orca (RET-011, `docs/methode.md`). On s'inspire par défaut ; on ne copie qu'un petit morceau autonome.
10. **Méthode** : chaque tâche suit le process du plugin installé (`process/README.md`), au niveau que fixe la fiche `docs/methode.md`. Si tu as été lancé avec un rôle, lis d'abord ton profil dans `roles/` du plugin installé, au chemin que donne la ligne « Méthode » du récapitulatif de démarrage, jamais dans un worktree.
