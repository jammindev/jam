# Relecture — cadrage `cadrage-orchestration`, tour 6

Relecteur seul, relecture d'un cadrage. Périmètre : toutes les modifications non commitées du worktree (12 fichiers modifiés, plus `docs/decisions/0013-orchestration-deux-niveaux.md`, `docs/process/roles/orchestrateur-tache.md` et `docs/plans/cadrage-orchestration-issues.md`), confrontées aux trois briefs du rédacteur et aux décisions ajoutées depuis (format de tout feu vert relayé ; accord limité à l'action que le feu vert ouvre ; milestone `E0-S1 Squelette` encore ouvert).

## Ce qui a été vérifié et tient

- **Fidélité aux retours.** RET-008, RET-009 (les huit propositions, leur validation du 2026-10-09, les compléments, la question Q-039 non tranchée, l'exception unique de ce cadrage décrite seulement dans l'ADR 0013) et RET-010 reprennent les briefs sans écart. La proposition du rédacteur (feu vert merge d'un cadrage) est bien présentée comme proposition.
- **Feu vert relayé.** Le format (mots exacts, heure, session) vaut pour tout feu vert relayé, et l'accord ne vaut que pour l'action ouverte. C'est écrit de la même façon dans `AGENTS.md` (règle 6), le process (« Format de tout feu vert relayé »), l'ADR 0013, RET-009 et les deux profils qui orchestrent.
- **ADR acceptées.** L'ADR 0008 est respectée : dans jam, c'est le code qui orchestre, et l'ADR 0013 explique pourquoi le dispositif ne rouvre pas l'« équipe » écartée. Les écarts à l'ADR 0009 (commit par un rôle, session interactive) sont tracés comme exceptions, sur le modèle de l'ADR 0012. FR-021, FR-027, FR-029, FR-034, FR-038 et FR-040 restent cohérents avec la correspondance Orca → jam.
- **Glossaire.** « Orchestrateur de tâche », « Agent actif », « Lead », « Coordinateur » et « Rôle » sont définis et utilisés de façon constante ; la distinction lead / orchestrateur de tâche est expliquée.
- **Brouillon d'issue.** Un seul bug, un critère de fin vérifiable par le mainteneur (`node_modules` supprimé, `pnpm install`, `pnpm dev` ouvre la fenêtre), des scripts `pnpm check` et `pnpm core:ping` qui existent bien dans `package.json`, un milestone justifié et vérifié ouvert, une solution laissée au planificateur. C'est un petit lot (ADR 0011). La cause est cohérente avec `E0-S1-squelette-recette.md` (Playwright d'abord, `pnpm dev` au contrôle « 3 bis »).

## Bloquant

Aucun.

## À corriger

### 1. La liste « si la proposition est refusée » oublie trois endroits qui imposent un feu vert merge à toute PR

- **Fichier** : `docs/process/README.md`, ligne 31 (étape 4 « Feu vert cadrage »).
- **Constat** : si le mainteneur refuse le feu vert merge d'un cadrage, le rédacteur doit écrire que le feu vert de cadrage ouvre aussi le merge, mais seulement « ici, dans « Format de tout feu vert relayé », dans l'ADR 0013 [...] et dans RET-009 ». Trois autres textes resteraient alors faux pour un cadrage :
  - `AGENTS.md`, règle 6 : « seul le coordinateur merge, après le feu vert merge » ;
  - `docs/process/roles/coordinateur.md`, ligne 27 : « **Seul à merger** : après le feu vert merge, il merge la PR » ;
  - `docs/process/roles/orchestrateur-tache.md`, ligne 30 (« Fin ») : « la carte indique « ⏸ feu vert merge » ».

  Ces modifications seraient faites après le feu vert, sans nouvelle relecture : la consigne, telle qu'elle est écrite, conduirait à des docs contradictoires.
- **Correction attendue** : ajouter ces trois endroits à la liste du cas de refus (règle 6 d'`AGENTS.md`, « Seul à merger » du profil du coordinateur, « Fin » du profil de l'orchestrateur de tâche), ou formuler ces trois passages pour qu'ils restent justes dans les deux cas (par exemple « après le feu vert qui ouvre le merge, voir le process »).

### 2. Le lien du brouillon d'issue sera cassé une fois l'issue publiée

- **Fichier** : `docs/plans/cadrage-orchestration-issues.md`, ligne 13.
- **Constat** : le corps de l'issue contient le lien relatif `[`E0-S1-squelette-recette.md`](E0-S1-squelette-recette.md)`. Il fonctionne dans le fichier du repo, mais dans une issue GitHub, il se résout sous `github.com/jammindev/jam/issues/` et mène à une page introuvable. Le process insiste pourtant pour que les liens des issues vers les docs fonctionnent (publication après le merge, étape 4).
- **Correction attendue** : un lien absolu vers `main` (`https://github.com/jammindev/jam/blob/main/docs/plans/E0-S1-squelette-recette.md`) ou, comme dans `specs-retours-dora-issues.md`, le chemin en clair `docs/plans/E0-S1-squelette-recette.md`.

## Suggestions

### S1. Dire que la réinstallation des dépendances fait partie de la recette, réseau compris

- **Fichiers** : `docs/specs/RETOURS.md` (RET-010, « Règle »), `docs/specs/OPEN-QUESTIONS.md` (Q-033).
- **Constat** : RET-010 justifie la réinstallation au regard de la colonne « Fichiers » de l'ADR 0009 (lecture seule sur les fichiers suivis). Mais la table de l'ADR 0009 donne aussi au recetteur, pour le shell, « commande ou skill de recette du repo », et pour le réseau, « selon la recette (navigateur local) ». Or `pnpm install` depuis zéro accède au registre de paquets, et le binaire d'Electron se télécharge depuis le réseau.
- **Proposition** : une phrase dans RET-010 ou Q-033 : la réinstallation est une étape de la recette (couverte par « commande de recette » et « réseau selon la recette » de l'ADR 0009), et la commande du recetteur à écrire devra autoriser l'accès réseau qu'elle demande.

### S2. Préciser où s'arrête l'« installation neuve »

- **Fichier** : `docs/process/roles/recetteur.md`, ligne 9.
- **Constat** : le profil dit « sans binaire ni cache préparé par un autre contrôle », sans préciser où. Le process (ligne 138) dit « dans le worktree ». Un recetteur pourrait croire devoir vider les caches du poste (magasin pnpm, cache d'Electron dans le dossier utilisateur), qui sont hors du worktree et de ses permissions.
- **Proposition** : reprendre « dans le worktree » dans le profil.

### S3. Aligner l'ordre de la recette entre le process et le profil

- **Fichiers** : `docs/process/README.md`, lignes 137 à 140 ; `docs/process/roles/recetteur.md`, lignes 7 à 11.
- **Constat** : le profil commence par « écrire d'abord la check-list du mainteneur », étape que la section « Recette » du process ne mentionne pas. Le lecteur du seul process peut se demander d'où vient la check-list à dérouler « d'abord ».
- **Proposition** : ajouter cette étape (ou un renvoi au profil) dans la section « Recette » du process.

### S4. Statut des ADR 0011 et 0012

- **Fichiers** : `docs/decisions/README.md`, lignes 17 et 18 ; ADR 0013, ligne 59.
- **Constat** (hors du diff, mais il touche ce cadrage) : les ADR 0011 et 0012 sont encore « proposées », alors que le cadrage qui les a produites est mergé (PR #6). L'ADR 0013 « précise » l'ADR 0012, et `AGENTS.md` (règle 6) les cite toutes les deux. À l'acceptation de l'ADR 0013, la mention à reporter irait dans le statut d'une ADR encore proposée.
- **Proposition** : signaler au mainteneur, au feu vert de ce cadrage, qu'il faut décider du statut de l'ADR 0012 (et de l'ADR 0011) en même temps que celui de l'ADR 0013.

RELECTURE : CORRECTIONS (2)
