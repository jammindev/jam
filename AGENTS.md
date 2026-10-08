# AGENTS.md

Instructions pour tout agent de code qui travaille sur ce repo.

## Le projet

Un cockpit de *loop engineering*. Pour chaque issue GitHub, un pipeline codé dans le cœur fait travailler des rôles d'agents dans un worktree dédié (plan, TDD, relecture, recette) jusqu'au merge. Le mainteneur n'intervient que pour trois feux verts.

**À lire avant toute tâche** :
- `docs/specs/00-VISION.md` : pourquoi, principes, non-objectifs ;
- `docs/specs/01-REQUIREMENTS.md` : exigences numérotées (FR / NFR) ;
- `docs/specs/02-ARCHITECTURE.md` : composants et stack ;
- `docs/specs/04-ROADMAP.md` : étape et jalon en cours ;
- `docs/decisions/` : ADR. **Une décision actée ne se contourne pas.** En cas de désaccord, proposer une nouvelle ADR.
- `docs/specs/GLOSSARY.md` : vocabulaire à respecter dans le code.

## Stack

- Electron (macOS uniquement), UI en React + TypeScript.
- Le cœur tourne dans un **processus séparé**, exposé par un protocole typé (ADR 0006).
- TypeScript `strict` partout. Données externes validées avec zod.
- Claude Code piloté en headless `stream-json` (ADR 0004). Persistance SQLite (ADR 0010).
- Chaque action d'UI passe par le **registre de commandes** (ADR 0007).

## Règles de travail

1. **Le mainteneur ne code pas** (ADR 0003). Le code doit donc être lisible et expliqué : noms explicites, commentaires sur le *pourquoi*, pas sur le *quoi*.
2. **TDD** : on écrit d'abord le test qui échoue, puis le code.
3. **Un jalon livré = une fiche concept** dans `docs/concepts/` (format décrit dans le README de ce dossier).
4. **Pas de sur-ingénierie.** On construit ce que demande le jalon, rien de plus. Tout ce qui vient « pour plus tard » est noté dans `docs/specs/OPEN-QUESTIONS.md`.
5. **Aucune mention d'auteur IA**, nulle part : pas de trailer `Co-Authored-By`, pas de signature dans les PR, aucune référence à un assistant dans le code ou les docs.
6. **Commit, push et PR uniquement avec l'accord explicite du mainteneur.** Les rôles du pipeline (`docs/process/roles/`) ne committent jamais. Seul le coordinateur committe, et seulement après un feu vert.
7. **Repo public** : jamais de secret, de donnée personnelle ou de tiers, ni de chemin propre à une machine.
8. **Langues** : docs, ADR et messages de commit en français. Code (identifiants, commentaires) en anglais.
9. **Code repris d'Orca** (MIT) : conserver la mention de copyright et de licence, et l'ajouter dans `THIRD_PARTY_NOTICES.md`.
10. **Méthode** : chaque tâche suit le pipeline décrit dans `docs/process/README.md`. Si tu as été lancé avec un rôle, lis d'abord ton profil dans `docs/process/roles/`.
