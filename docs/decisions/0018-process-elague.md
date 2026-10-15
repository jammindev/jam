# ADR 0018 : process élagué

- **Statut** : acceptée (feu vert recette du 2026-10-15)
- **Date** : 2026-10-13
- **Tranche** : issue #23 (K1-2), RET-017, RET-018, RET-019, Q-027, Q-058. Précise l'[ADR 0016](0016-kit-de-methode.md) (mesure, valeur du plafond), l'[ADR 0013](0013-orchestration-deux-niveaux.md) (écriture de la note de suivi par l'orchestrateur de tâche, veille), l'[ADR 0017](0017-coordinateur-main-poste-de-travail.md) (analyse d'un retour, carte restée `in-progress`) et l'[ADR 0009](0009-permissions-par-role.md) (profil du planificateur)

## Contexte

L'ADR 0016 fait de jam un plugin qui porte la méthode, sous un plafond de taille (NFR-015) : au plus 4904 mots pour le process et les profils, la moitié des 9808 mots de `docs/process/` sur `main` au départ de #23. Elle demande aussi que l'historique d'une règle (« Origine : … ») quitte le process pour une ADR, et que toute nouvelle règle dise laquelle elle remplace ou retire (NFR-016).

L'issue #23 déplace la méthode dans `process/` et `roles/`, la rend générique et y écrit les règles de RET-014 à RET-016. Trois constats s'y ajoutent :
- sur un autre projet du poste, un relais de feu vert envoyé par `orca terminal send` a été avalé, et la veille des cartes attendait à vide une carte que plus personne ne tenait (RET-017) ;
- le temps du mainteneur, seule mesure de la méthode (FR-055), ne lui est plus demandé : un script l'estime (RET-018) ;
- l'essai de #22 a laissé 24 frictions, dont la plupart trouvent une règle ici (plan de #23, annexe C).

Cette ADR est la trace que le process ne porte plus.

## Décision

### Où vit la méthode

- Le déroulé est dans `process/README.md`, les sept profils dans `roles/`, le gabarit de la fiche dans `process/fiche-projet.md`. `docs/process/README.md` n'est plus qu'un renvoi.
- Un agent lit le process et les profils **du plugin installé**, désignés par la ligne « Méthode » du récapitulatif de démarrage, jamais les copies d'un worktree. Celles d'un worktree de jam restent donc inertes jusqu'au merge.
- Ce qui est propre à jam (section « Orca » du plan, clone de référence, recette avec `--plugin-dir`) sort des profils pour la fiche de jam, [`docs/methode.md`](../methode.md).

### Q-058 : l'analyse d'un retour

L'orchestrateur de tâche écrit l'analyse d'un retour reçu dans son worktree dans `docs/plans/<tâche>-retours.md`, et la commite avec la tâche. C'est une note de suivi, pas un livrable : elle n'est pas relue. C'est la seule exception à son interdit d'écrire un livrable. Elle remplace le fichier d'un dossier temporaire de sa session, qu'un redémarrage du poste pouvait vider (NFR-013).

Au niveau *léger*, aucune session ne conduit la tâche dans le worktree, et le coordinateur n'écrit rien dans le repo : un retour reçu dans le worktree remonte au coordinateur, qui le traite comme s'il l'avait reçu lui-même, par le brief d'un cadrage. Il n'y a donc pas de note de suivi à ce niveau.

### Q-027 : le planificateur

Il garde `WebSearch` et `WebFetch` : ils ont servi à chercher la cause de la friction 18 de #22 (écriture refusée malgré la règle `Edit`). Il gagne `git diff`, pas la commande de test : il ne lance rien. Il n'écrit que son plan, par une seule règle `Edit`, sans liste d'interdits.

C'est un écart à la table de l'[ADR 0009](0009-permissions-par-role.md), qui donnait au planificateur la commande de tests et aucun accès réseau : il garde la recherche web, en lecture seule, et n'a pas la commande de test.

### Valeurs fixées au feu vert plan

- **Seuil « assez bon »** (FR-050) : un constat n'est « à corriger » que s'il écrit un scénario d'échec (entrée, mauvais résultat) ou cite l'exigence, l'ADR ou le critère de fin qu'il viole ; sinon c'est une suggestion.
- **Plafonds** (FR-051) : 6 agents en cours sur le poste, valeur écrite dans le process ; le plafond de chaque projet est dans sa fiche (3 pour jam).
- **Mesure** (FR-055) : des messages à moins de 10 min l'un de l'autre forment un moment, qui vaut sa durée plus 3 min de lecture.

Précisé après la recette de #23, sur décision du mainteneur : le script ne lit que les sessions du coordinateur, sur le worktree principal. Dans le worktree de #22, tout message venait d'agents, et le script en comptait les relais comme des messages du mainteneur. Limite : la recette du mainteneur, faite dans une session du worktree de la tâche, n'est pas comptée, ni un feu vert tapé là (Q-065). Un transcript illisible est ignoré. C'est un écart à l'issue #23, qui nommait aussi les sessions de la tâche (RET-018).

### Ce que chaque règle nouvelle remplace ou retire

| Règle du process ou d'un profil | Remplace ou retire | Trace |
|---|---|---|
| Niveaux *léger*, *standard*, *renforcé* ; *léger* conduit par le coordinateur, un seul relecteur | Le déroulé unique, avec orchestrateur de tâche pour toute tâche | FR-049, FR-052, ADR 0016 |
| Seuil « assez bon » ; une suggestion reclassée sans nouveau scénario reste une suggestion | « La boucle s'arrête quand tous disent OK », seul critère d'arrêt | FR-050, frictions 12 et 13 de #22 |
| 6 agents en cours au poste, plus le plafond de la fiche ; un agent en cours est une session que liste `orca terminal list` | Environ 3 agents actifs, fixés par le coordinateur | FR-051, RET-009 |
| Relais allégé : « ok » pour le plan et la recette ; forme complète pour tout autre feu vert, merge compris | Les mots exacts, l'heure et la session pour tout feu vert relayé | FR-053, ADR 0016 |
| Feu vert remonté par la carte pour un merge ou une publication : le mainteneur le confirme dans le terminal du coordinateur | Le segment `✓` valait accord pour le coordinateur | FR-053, garde de sortie (#22) |
| Relais dans un terminal court et sans négation, puis `orca terminal read` 30 s après | Rien : ajout | RET-017, friction 24 de #22 |
| Veille : réveil sur un agent bloqué ou sur une carte `▶` sans agent au travail depuis 10 min, une fois par épisode ; le coordinateur relance ou passe la carte en `⛔` | La vérification à la main d'une carte longtemps `in-progress` (ADR 0013, ADR 0017), **sauf** pour une fenêtre d'autorisation du système : elle laisse l'agent au travail, et la veille ne la voit pas. Pour ce cas, la règle reste : une carte `▶` dont le commentaire ne change plus alors que son agent travaille fait prévenir le mainteneur (ADR 0017, Q-059) | RET-017, FR-046 |
| Temps du mainteneur estimé par `maintainer_time.py` d'après les seules sessions du coordinateur, sur le worktree principal, présenté comme une estimation | Le temps noté à la main, donné par le mainteneur au feu vert merge | RET-018, FR-055 |
| Analyse d'un retour dans `docs/plans/<tâche>-retours.md` ; au niveau *léger*, retour remonté au coordinateur, traité par le brief d'un cadrage | Le fichier d'un dossier temporaire | Q-058, ci-dessus |
| Une ADR née dans une tâche, hors cadrage, passe à « acceptée » après le feu vert recette de cette tâche, avant le commit : le rédacteur reporte les mentions de statut qu'elle prévoit et passe les retours concernés à « appliqué » | Le passage à « acceptée » après le seul feu vert de cadrage | Relecture de #23 (cette ADR, née dans la tâche) |
| Process et profils lus dans le plugin installé | « La tâche suit le process et les profils mergés, lus dans le worktree » ; l'interdit `Edit(docs/process/**)` de l'implémenteur | Plan de #23, §2 |
| Interdits de l'implémenteur : `.claude/`, `AGENTS.md`, `CLAUDE.md`, la fiche, le plan de la tâche et les rapports de relecture | `.claude/`, `AGENTS.md`, `docs/process/`, tout `docs/plans/`, qui l'empêchait d'écrire la check-list du mainteneur au niveau *léger* | Plan de #23, §2 ; relevé du coordinateur pendant la tâche |
| Niveau *léger* : le coordinateur conduit aussi les cadrages ; l'implémenteur ou le rédacteur écrit en fin de travail la check-list du mainteneur | Rien : comblent un trou | Relevé du coordinateur pendant la tâche |
| Conflit avec `main` : la tâche passe en `⛔` et le coordinateur décide avec le mainteneur ; les fichiers en conflit sont résolus par l'implémenteur, ou le rédacteur pour des docs, relancé avec le conflit dans son brief ; puis les tests sont relancés, et la branche n'est poussée qu'après un nouveau feu vert | Précise « En conflit, ⛔ et décision du coordinateur avec le mainteneur » (profil de l'orchestrateur de tâche), qui ne disait pas qui résout : ni l'orchestrateur de tâche ni le coordinateur n'écrivent un livrable | Relecture de #23 |
| Règles `Edit` des profils ancrées par `/`, résolues depuis le dossier de lancement de la session et non depuis son dossier courant, qui suit ses `cd` ; le relecteur n'écrit que le rapport que nomme son brief, donc sans interdit `.claude/` | Les règles relatives, sans ancrage ; `Edit(docs/plans/*-relecture*.md)` et l'interdit `Edit(.claude/**)` du relecteur, qui lui laissaient réécrire les rapports des tours précédents | Plan de #23, §2 et annexe A |
| Une session lancée avec `--plugin-dir <dossier>` ne peut écrire dans ce dossier, quelle que soit la forme de la règle `Edit` (relative, ancrée par `/`, absolue par `//`) : le recetteur lancé avec `--plugin-dir <worktree>` écrit d'emblée son rapport dans son dossier de recette, et un rédacteur le recopie tel quel | Le rapport du recetteur écrit dans `docs/plans/` du worktree ; le diagnostic « règle `Edit` relative » de la friction 18, faux : l'ancrage par `/` ne lève pas ce refus, mais reste la forme des profils pour la raison de la ligne précédente | Friction 18 de #22, sonde de la recette de #23 (Q-064) |
| Commande de test et recette prises dans la fiche | Les commandes `pnpm`, `node`, `npx`, `curl`, `screencapture`, `pgrep`, le `rm -rf` des `node_modules` et `JAM_DATA_DIR` | ADR 0016, friction 14 de #22 |
| Plan de deux pages au plus, sinon refait | Rien : ajout | Friction 3 de #22 |
| Un brief ne contredit pas un profil : le profil prime | Rien : ajout | Friction 23 de #22 |
| Un rôle ne lit rien hors du worktree et des chemins de son brief, transcripts compris | Rien : ajout | Friction 10 de #22 |
| Terminal d'un rôle fermé dès sa ligne de fin | Rien : ajout | Friction 21 de #22 |
| Check-list du mainteneur faite de demandes à une session, faisables depuis un téléphone ; phrases d'accord ou de refus vérifiées contre la garde de sortie | Reformule « Une check-list de 5 étapes au plus », dont elle garde le plafond de cinq points | Frictions 19, 20 et 22 de #22 |
| Recette d'une interface par captures ou enregistrement | Rien : ajout | FR-054 |
| Messages au mainteneur : tout message qui lui est adressé se lit seul, projet et tâche en mots, la tâche suivie de son numéro d'issue entre parenthèses, avec son dièse (« (#23) »), que lit la mesure du temps, autres références internes remplacées par ce qu'elles désignent | Rien : ajout | RET-019 |
| Brief par fichier, lu par le script de lancement | Brief tapé par `orca terminal send --text` | Friction 1 de #22 |
| Hooks du plugin, messages préfixés `[jam]` ; la reprise désigne la fiche et le process du plugin, au démarrage, après `/clear` et à la reprise d'une session | Hook de démarrage et garde du coordinateur du poste ; le chemin du process du repo ; un récapitulatif absent à la reprise d'une session | FR-044, ADR 0016 |

Retirés sans remplacement, parce qu'ils décrivaient l'app ou le développement de jam : l'introduction « en attendant que jam sache dérouler son pipeline », la table « Correspondance entre le pipeline cible et Orca », la section « Ce qu'Orca ne permet pas (et que jam fera) » (ses limites encore vraies restent dans « Permissions »), les renvois au cœur, les passages « Kit » des profils, les commandes de l'app, la mention de la garde de l'orchestrateur de tâche (Q-056).

### Origines retirées du process

Le process ne dit plus pourquoi une règle existe. Les origines qu'il portait sont ici ; celles qui n'avaient de trace ni dans une ADR ni dans un retour sont marquées « ici seulement ».

| Règle | Origine | Trace |
|---|---|---|
| Une tâche suit le process mergé (devenu : le process du plugin installé) | Au premier essai (#7), le profil de l'orchestrateur de tâche et les règles de recette n'existaient que sur la branche d'un cadrage non mergé ; le recetteur a dû les lire dans un autre worktree | Ici seulement |
| Une suggestion qui revient est remontée avec le feu vert suivant | Au premier essai (#7), la même suggestion est revenue au tour 2, sans règle pour en décider | Ici seulement |
| Rapport de relecture toujours dans un fichier | Des rapports rendus seulement dans le terminal ont été perdus : le terminal ne garde que l'écran | Ici seulement (Q-023) |
| Chaque règle `Bash` doublée de sa forme `rtk`, aussi étroite | Des rôles refusés après la réécriture des commandes par le hook RTK du poste ; une règle `rtk` large ouvre trop | Ici seulement (Q-022) |
| Interdits `Edit(.claude/**)` et `git -C` | Ajoutés par précaution, à la relecture d'un cadrage | Ici seulement |
| Ni suppression ni arrêt de processus pour l'implémenteur ; une installation neuve va à la recette | Au premier essai (#7), le plan demandait à l'implémenteur de supprimer les `node_modules` et de lancer `pnpm dev`, ce que sa liste ne permettait pas | Ici seulement |
| Plafond d'agents | Limite d'usage atteinte avec 5 agents actifs dans la nuit du 8 au 9 octobre | RET-009 |
| La recette part d'une installation neuve et déroule d'abord la check-list du mainteneur | À la recette du S1, Playwright avait téléchargé le binaire d'Electron avant que `pnpm dev` soit vérifié | RET-010 |
| La carte est le seul canal vers le coordinateur | Un `orca terminal send` s'insère dans la saisie du mainteneur (2026-10-09) | RET-013, ADR 0015 |
| Le coordinateur ne produit aucun livrable | Il avait créé lui-même milestones et issues | RET-001 |

## Conséquences

- (+) La méthode tient sous son plafond, et chaque règle a une trace : ici, dans une autre ADR, un retour ou une exigence.
- (+) Les rôles d'une tâche qui modifie `process/` ou `roles/` ne lisent pas les règles en cours d'écriture.
- (+) Une carte que personne ne tient réveille le coordinateur ; le temps du mainteneur n'est plus demandé.
- (−) Le process ne dit plus pourquoi : pour comprendre une règle, il faut lire cette ADR.
- (−) Le temps du mainteneur est une estimation, avec des limites écrites (`docs/concepts/veille-et-mesure.md`).
- (−) L'analyse d'un retour n'est pas relue : seule la reformulation par le rédacteur d'un cadrage passe en relecture.

À l'acceptation de cette ADR, le statut de l'ADR 0016 mentionne « précisée (0018) », celui de l'ADR 0017 « précisée (0018) », et celui de l'ADR 0013 « précisée (0018) : l'orchestrateur de tâche écrit la note de suivi d'un retour ; la veille remplace la vérification à la main d'une carte, sauf pour une fenêtre d'autorisation du système », et celui de l'ADR 0009 « précisée (0018) : profil du planificateur, avec la recherche web en lecture et sans la commande de test ».
