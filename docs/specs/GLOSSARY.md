# Glossaire

> « Provisoire » = pas encore validé. « App (abandonné) » = terme de l'app Electron, sans usage depuis l'ADR 0016 ; gardé pour lire l'historique.

## Le kit (ADR 0016)

| Terme | Définition | Statut |
|---|---|---|
| Kit | jam depuis le 2026-10-11 : la méthode de travail du mainteneur, outillée et versionnée, sous la forme d'un plugin Claude Code (ADR 0016). | Provisoire (RET-014) |
| Plugin | Paquet de Claude Code installé sur le poste de travail : process, profils de rôle, hooks et scripts. Le repo jam est lui-même le plugin. | Provisoire (RET-014, RET-016) |
| Gel du kit | Une fois le jalon K1 livré, le kit ne change que sur une friction vécue dans un projet ; toute nouvelle règle dit laquelle elle remplace ou retire (ADR 0016). | Provisoire (RET-016) |
| Garde de sortie | Hook du plugin qui refuse, à toute session, commit, push, merge et écritures `gh` sans accord explicite du mainteneur. Il remplace les gardes qui se recouvraient sur le poste. Distinct de la garde du coordinateur, qui garde ses écritures de fichiers. | Provisoire (RET-016) |
| Fiche projet | `docs/methode.md` d'un projet qui suit la méthode : niveau par défaut, ce qu'il faut lire avant une tâche, commande de test, grille de relecture, recette, sens d'un merge (mise en production ou non), plafond d'agents du projet (borne propre au projet, en plus du plafond global), règles propres. Seule trace de la méthode dans le projet ; gabarit dans `process/fiche-projet.md`. | Provisoire (RET-014, RET-016) |
| Niveau de tâche | Régime d'une tâche. Par défaut, celui de son projet, fixé par sa fiche selon le risque : *standard* (déroulé complet, avec orchestrateur de tâche) pour un projet en production qui touche à l'argent ou à des données de personnes ; *léger* partout ailleurs (ni orchestrateur de tâche ni planificateur : le coordinateur lance l'implémenteur, puis un relecteur ; pas de recette par un agent). Une tâche peut monter d'un niveau, motivé ; au-dessus de *standard*, *renforcé*, sans contenu fixé (Q-061). | Provisoire (RET-014, RET-016) |
| Seuil « assez bon » | Règle d'arrêt de la relecture : un tour qui ne trouve que des suggestions clôt la boucle. Un constat n'est « à corriger » que s'il écrit un scénario d'échec (entrée, mauvais résultat) ou cite l'exigence, l'ADR ou le critère de fin qu'il viole ; sinon c'est une suggestion (ADR 0018). | Provisoire (RET-014) |
| Plafond d'agents global | Nombre maximal d'agents en cours sur le poste de travail, tous projets confondus : les sessions d'agent que liste `orca terminal list`, qu'elles travaillent ou attendent. Toute session qui lance un agent (coordinateur, ou orchestrateur de tâche au niveau *standard*) compte les agents en cours avant de le lancer ; le plafond de la fiche projet s'y ajoute comme borne propre au projet, sans en être une part. | Provisoire (RET-014) |
| Poste de travail | Machine dédiée où tournent Orca, Claude Code et les agents. Le mainteneur la pilote à distance par le serveur Orca distant (ADR 0017). | Provisoire (RET-015) |
| Agent en cours | Session d'agent que liste `orca terminal list`, qu'elle travaille ou attende. Les plafonds d'agents portent sur eux (FR-051) ; un terminal de rôle resté ouvert après sa ligne de fin en est un. | Provisoire (RET-014, ADR 0018) |
| Veille des cartes | Script du plugin (`watch_cards.py`) que le coordinateur garde en arrière-plan : il rend la main quand une carte de son projet attend le mainteneur ou le coordinateur, ou qu'une carte `▶` n'est plus tenue (agent bloqué, ou aucun agent au travail depuis N minutes). | Provisoire (RET-017) |
| Épisode | Pour la veille : la période pendant laquelle une même situation dure sur une carte (un agent bloqué, ou une carte inactive). La veille ne se réveille qu'une fois par épisode, sur la transition qui l'ouvre. | Provisoire (RET-017) |
| Moment | Pour la mesure du temps du mainteneur : une suite de ses messages à moins de 10 min l'un de l'autre. Il vaut sa durée plus 3 min de lecture (FR-055). | Provisoire (RET-018) |
| Note de suivi | Analyse d'un retour reçu dans un worktree, écrite par l'orchestrateur de tâche dans `docs/plans/<tâche>-retours.md` et committée avec la tâche. Ce n'est pas un livrable : elle n'est pas relue (ADR 0018). Au niveau *léger*, il n'y en a pas : le retour remonte au coordinateur. | Provisoire (Q-058) |
| Session libre | Session d'agent lancée sans `JAM_ROLE` : elle n'a pas de rôle, et la garde du coordinateur ne la protège pas. Le récapitulatif de démarrage l'affiche ainsi (ADR 0017). | Provisoire (RET-015) |

## Méthode

| Terme | Définition | Statut |
|---|---|---|
| Boucle intérieure | La boucle d'un agent : modèle → outils → modèle, jusqu'à la fin de sa tâche. C'est le **harness**. | Validé |
| Boucle extérieure | Le système qui trouve le travail, le confie à des agents, fait vérifier et attend les feux verts. C'est le **pipeline** (ADR 0008). | Validé |
| Loop engineering | Pratique (2026) qui consiste à construire la boucle extérieure plutôt que de prompter un agent tour par tour. | Validé |
| Pipeline | La séquence d'étapes de la méthode : plan → TDD → relecture → recette → PR + CI → merge. Tenue par l'orchestrateur de tâche ; l'app devait la coder dans son cœur (ADR 0008, ADR 0016). | Provisoire (redéfini, ADR 0016) |
| Étape | Un maillon du pipeline, exécuté par un rôle ou par un feu vert. | Validé |
| Rôle | Profil d'agent (prompt, outils, permissions). Les rôles du pipeline et du cadrage (planificateur, implémenteur, relecteur, recetteur, rédacteur) sont instanciés à la demande avec un contexte neuf. Les deux rôles qui orchestrent sont des sessions conversationnelles qui durent : le coordinateur pour le projet, l'orchestrateur de tâche pour une tâche. L'« équipe », c'est l'ensemble des rôles. | Provisoire (définition élargie, RET-001, RET-005 et RET-009) |
| Rédacteur | Rôle qui rédige specs, ADR, docs de process et brouillons d'issues. Il écrit dans `docs/`, `AGENTS.md` et `README.md`, et ne touche jamais au code. | Provisoire |
| Brouillon d'issue | Issue rédigée sous forme de fichier par le rédacteur, publiée sur GitHub par le coordinateur après le feu vert de cadrage, une fois la PR du cadrage mergée. | Provisoire |
| Coordinateur | Agent conversationnel au niveau d'un projet : il orchestre le cadrage et les tâches, et arbitre. Interlocuteur unique du mainteneur s'il le souhaite. Il ne produit aucun livrable (RET-001). C'est un rôle, avec son profil et sa garde, active quand la session est lancée avec `JAM_ROLE=coordinateur` (ADR 0012). Une session Orca dans un terminal du worktree principal (`main`) de son projet, sur le poste de travail : un coordinateur par projet (ADR 0017). Il lance un orchestrateur de tâche par tâche de niveau *standard* et merge (ADR 0013) ; au niveau *léger*, il conduit lui-même la tâche, commit et PR compris (ADR 0016). | Provisoire (emplacement revu, RET-015 ; niveau léger, RET-016) |
| Orchestrateur de tâche | Agent conversationnel au niveau d'une tâche, dans son worktree ; il conduit aussi un cadrage, dans `cadrage-<slug>` : il lance les rôles de la tâche, tient ses boucles et ses garde-fous, committe, pousse et ouvre la PR après les feux verts, et remonte l'avancement au coordinateur par sa seule carte Orca (ADR 0015). Le mainteneur peut lui parler de la tâche en détail. Il ne produit aucun livrable. C'est un rôle (`JAM_ROLE=orchestrateur-tache`, ADR 0013). Il tient à la main ce que l'app aurait tenu en code. Absent au niveau *léger* (ADR 0016). | Provisoire (RET-009, RET-016) |
| Agent actif | Agent en train de travailler. Un agent qui attend une réponse, un feu vert ou la fin d'un autre agent n'est pas actif. Le plafond de l'ADR 0013 portait sur eux ; le plafond d'agents global porte sur les agents en cours, actifs ou non, qu'un script sait compter (ADR 0016). | Sans usage dans le process (ADR 0018) : voir « Agent en cours » |
| Cadrage | Travail qui produit ou modifie specs, ADR et issues avant qu'une tâche n'entre dans le pipeline : rédacteur → relecteur → feu vert de cadrage → PR → feu vert merge. Il n'a pas d'issue ; son worktree s'appelle `cadrage-<slug>`. | Provisoire (feu vert merge ajouté, RET-009) |
| Code applicatif | Dans le kit : hooks et scripts du plugin, tests compris. Son changement exige au moins deux relecteurs au niveau *standard* (RET-007) ; un seul au niveau *léger* (RET-016). Hors docs, CI et outillage. Avant l'ADR 0016 : les fichiers de l'app et du cœur (`apps/`, `packages/`). | Provisoire (redéfini, ADR 0016) |
| Livrable | Tout ce qu'une tâche ou un cadrage produit : code, spec, ADR, doc, issue. Il passe toujours par production par un rôle, relecture indépendante, puis feu vert. | Provisoire |
| Retour | Remarque ou suggestion du mainteneur, consignée dans `RETOURS.md` (RET-NNN) et appliquée par un rôle. | Provisoire |
| Tour de relecture | Une relecture complète par des relecteurs neufs, suivie des corrections. Les tours s'enchaînent jusqu'à ce que tous les relecteurs disent OK (RET-006), ou jusqu'au seuil « assez bon ». | Provisoire |
| Axe de relecture | Partie d'une relecture confiée à un relecteur : **justesse** (bugs, tests, cas limites) ou **conformité** (plan, ADR, lisibilité, sur-ingénierie, sécurité du repo public) (RET-007). | Provisoire |
| Feu vert | Validation humaine explicite. Le pipeline d'une tâche en compte trois : plan, recette, merge ; deux au niveau *léger*, sans plan. En amont, un cadrage en compte deux : le feu vert de cadrage valide les specs, les ADR et les issues (FR-040), puis le feu vert merge ouvre le merge de sa PR (RET-009). Relayé d'une session à l'autre, il cite les mots exacts, l'heure et la session, sauf, à partir du merge de K1-2, le feu vert plan et le feu vert recette, pour lesquels un « ok » transmis suffit (RET-016). | Provisoire (feu vert de cadrage, feu vert merge d'un cadrage, relais allégé ajoutés) |
| File « À toi » | Liste de ce qui attend le mainteneur : feux verts, questions, blocages, recettes. Dans le kit : les cartes Orca `in-review` marquées `⏸` ou `⛔`. | Validé |
| Tâche | Une issue GitHub qui traverse le pipeline dans son worktree. | Validé |
| Worktree | Checkout git isolé (`git worktree`), un par tâche. | Validé |
| Garde-fou | Plafond d'itérations ou de budget par étape, ou détection d'absence de progrès en relecture (un constat bloquant ou à corriger qui revient, en substance, au tour suivant). Son déclenchement fait passer la tâche à l'état « bloqué ». | Provisoire (absence de progrès ajoutée, RET-006) |
| Agent | Une instance de rôle en cours d'exécution : une session Claude Code. | Provisoire (redéfini, ADR 0016) |
| Tour (turn) | Un aller-retour modèle → éventuels appels d'outils. | Provisoire |
| Outil (tool) | Capacité exposée au modèle, décrite par un schéma. | Provisoire |
| Mainteneur | Ben. Il décide, donne les feux verts, recette. Il n'écrit pas le code. | Validé |

## Termes de l'app (abandonnés)

| Terme | Définition | Statut |
|---|---|---|
| Harness | Programme qui exécute la boucle intérieure : appels au modèle, outils, permissions, contexte. | App (abandonné) : plus de harness maison |
| Lead | La session principale d'un worktree, à laquelle le mainteneur parle de sa tâche (ADR 0008, FR-034). Dans jam, c'était l'interlocuteur du niveau tâche : il n'orchestrait pas, le cœur enchaînait les étapes (ADR 0013). | App (abandonné) : l'orchestrateur de tâche en tient lieu |
| Backend d'agent | Ce qui exécute réellement un agent : Claude Code headless (E0) ou le harness maison (E2). | App (abandonné) |
| Headless / stream-json | Mode non interactif de Claude Code (`-p`), qui émet un événement JSON par ligne. | App (abandonné) ; reste un mode de Claude Code (Q-054) |
| Commande d'UI | Action nommée et typée de l'interface, partagée par la palette et l'agent (ADR 0007). | App (abandonné) |
| Clone de référence | Clone d'Orca à la version de référence fixée dans `docs/references/orca.md`, en lecture seule, hors du repo, donné au planificateur et à l'implémenteur d'une tâche de jam (RET-011, ADR 0014). | Sans usage (ADR 0014 historique) |
| Terminal flottant | Terminal du workspace flottant d'Orca, joignable depuis tous les worktrees, sans worktree propre : il s'ouvre dans le dossier personnel. Le coordinateur y a tourné du 2026-10-09 au 2026-10-10 (ADR 0015). Une session qui y tourne n'a pas de rôle (ADR 0017). Propre à Orca. | Provisoire (plus d'usage pour le coordinateur, RET-015) |

## Mesure (ADR 0011)

> Définitions gardées : les pratiques de l'ADR 0011 restent. Plus aucun écran ne les calcule depuis l'ADR 0016 : une seule mesure reste, le temps du mainteneur par issue, estimé par un script, présenté comme une estimation (Q-057, FR-055, RET-018).

| Terme | Définition | Statut |
|---|---|---|
| DORA | Programme de recherche sur la performance de livraison logicielle ([dora.dev](https://dora.dev)). | Provisoire |
| Petit lot | Changement assez petit pour être relu, testé et mergé en quelques jours. Une tâche est un petit lot. | Provisoire |
| Livraison | Par défaut, merge dans `main`. Pour un repo dont `main` est déployé, déploiement réussi. La fiche projet dit lequel. | Provisoire |
| Incident | Défaut constaté après une livraison et qui exige une correction immédiate. Signalé par une issue étiquetée `incident`. | Provisoire |
| Délai de changement (*change lead time*) | Du premier commit de la branche à la livraison. | Provisoire |
| Fréquence de livraison (*deployment frequency*) | Nombre de livraisons par semaine. | Provisoire |
| Temps de rétablissement (*failed deployment recovery time*) | De la livraison fautive à la livraison de son correctif. | Provisoire |
| Taux d'échec des changements (*change fail rate*) | Part des livraisons désignées par une issue `incident`. | Provisoire |
| Taux de reprise (*deployment rework rate*) | Part des livraisons qui ferment une issue `incident`. | Provisoire |
| Indicateurs agents | Par tâche : itérations, tours de relecture, coût, durée de tâche. | Provisoire |
| Durée de tâche | De la création du worktree au merge, dont le temps d'attente des feux verts. | Provisoire |
