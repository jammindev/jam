# Glossaire

> « Provisoire » = pas encore validé.

| Terme | Définition | Statut |
|---|---|---|
| Boucle intérieure | La boucle d'un agent : modèle → outils → modèle, jusqu'à la fin de sa tâche. C'est le **harness**. | Validé |
| Boucle extérieure | Le système qui trouve le travail, le confie à des agents, fait vérifier et attend les feux verts. C'est le **pipeline** (ADR 0008). | Validé |
| Loop engineering | Pratique (2026) qui consiste à construire la boucle extérieure plutôt que de prompter un agent tour par tour. | Validé |
| Harness | Programme qui exécute la boucle intérieure : appels au modèle, outils, permissions, contexte. | Validé |
| Pipeline | La séquence d'étapes codée en dur du mainteneur : plan → TDD → relecture → recette → PR + CI → merge. | Validé |
| Étape | Un maillon du pipeline, exécuté par un rôle ou par un feu vert. | Validé |
| Rôle | Profil d'agent (prompt, outils, permissions). Les rôles du pipeline et du cadrage (planificateur, implémenteur, relecteur, recetteur, rédacteur) sont instanciés à la demande avec un contexte neuf. Les deux rôles qui orchestrent sont des sessions conversationnelles qui durent : le coordinateur pour le projet, l'orchestrateur de tâche pour une tâche. L'« équipe », c'est l'ensemble des rôles. | Provisoire (définition élargie, RET-001, RET-005 et RET-009) |
| Rédacteur | Rôle qui rédige specs, ADR, docs de process et brouillons d'issues. Il écrit dans `docs/`, `AGENTS.md` et `README.md`, et ne touche jamais au code. | Provisoire |
| Brouillon d'issue | Issue rédigée sous forme de fichier par le rédacteur, publiée sur GitHub par le coordinateur après le feu vert de cadrage, une fois la PR du cadrage mergée. | Provisoire |
| Lead | La session principale d'un worktree, à laquelle le mainteneur parle de sa tâche (ADR 0008, FR-034). Dans jam, c'est l'interlocuteur du niveau tâche : il n'orchestre pas, le cœur enchaîne les étapes, et il lit le même état du cœur que le niveau projet (ADR 0013). Dans Orca, l'orchestrateur de tâche tient cette place. | Provisoire |
| Coordinateur | Agent conversationnel au niveau du projet : il orchestre le cadrage et les tâches, et arbitre. Interlocuteur unique du mainteneur s'il le souhaite. Il ne produit aucun livrable (RET-001). C'est un rôle, avec son profil et sa garde, active quand la session est lancée avec `JAM_ROLE=coordinateur` (ADR 0012). Aujourd'hui une session dans Orca, sur le worktree principal (`main`) ; il lance un orchestrateur de tâche par tâche et merge (ADR 0013). Dans jam, l'orchestration, le commit et le merge sont tenus par le cœur dès E0 ; le coordinateur conversationnel (cadrage, FR-040), interlocuteur du niveau projet avec le cockpit, arrive après E0 (Q-039). | Provisoire |
| Orchestrateur de tâche | Agent conversationnel au niveau d'une tâche, dans son worktree ; il conduit aussi un cadrage, dans `cadrage-<slug>` : il lance les rôles de la tâche, tient ses boucles et ses garde-fous, committe, pousse et ouvre la PR après les feux verts, et remonte l'avancement au coordinateur. Le mainteneur peut lui parler de la tâche en détail. Il ne produit aucun livrable. C'est un rôle (`JAM_ROLE=orchestrateur-tache`, ADR 0013). Propre à Orca, où il tient à la main, faute de cœur, ce que jam fera en code : dans jam, l'orchestration d'une tâche est tenue par le cœur (ADR 0008), et la discussion de la tâche passe par le lead, interlocuteur du niveau tâche. On ne l'appelle pas « lead » pour cette raison : dans jam, le lead n'orchestre pas. | Provisoire (RET-009) |
| Agent actif | Agent en train de travailler. Un agent qui attend une réponse, un feu vert ou la fin d'un autre agent n'est pas actif. Dans Orca, on vise environ 3 agents actifs en même temps, tous niveaux confondus (ADR 0013). | Provisoire (RET-009) |
| Cadrage | Travail qui produit ou modifie specs, ADR et issues avant qu'une tâche n'entre dans le pipeline : rédacteur → relecteur → feu vert de cadrage → PR → feu vert merge. Il n'a pas d'issue ; son worktree s'appelle `cadrage-<slug>`. | Provisoire (feu vert merge ajouté, RET-009) |
| Code applicatif | Tout fichier de l'app et du cœur (`apps/`, `packages/`), tests compris. Son changement exige au moins deux relecteurs (RET-007). Hors docs, CI et outillage du process. | Provisoire |
| Livrable | Tout ce qu'une tâche ou un cadrage produit : code, spec, ADR, doc, issue. Il passe toujours par production par un rôle, relecture indépendante, puis feu vert. | Provisoire |
| Retour | Remarque ou suggestion du mainteneur, consignée dans `RETOURS.md` (RET-NNN) et appliquée par un rôle. | Provisoire |
| Tour de relecture | Une relecture complète par des relecteurs neufs, suivie des corrections. Les tours s'enchaînent jusqu'à ce que tous les relecteurs disent OK (RET-006). | Provisoire |
| Axe de relecture | Partie d'une relecture confiée à un relecteur : **justesse** (bugs, tests, cas limites) ou **conformité** (plan, ADR, lisibilité, sur-ingénierie, sécurité du repo public) (RET-007). | Provisoire |
| Feu vert | Validation humaine explicite. Le pipeline d'une tâche en compte trois : plan, recette, merge. En amont, un cadrage en compte deux : le feu vert de cadrage valide les specs, les ADR et les issues (FR-040), puis le feu vert merge ouvre le merge de sa PR (RET-009). | Provisoire (feu vert de cadrage, puis feu vert merge d'un cadrage ajoutés) |
| File « À toi » | Liste de ce qui attend le mainteneur : feux verts, questions, blocages, recettes. | Validé |
| Tâche | Une issue GitHub qui traverse le pipeline dans son worktree. | Validé |
| Worktree | Checkout git isolé (`git worktree`), un par tâche. | Validé |
| Garde-fou | Plafond d'itérations ou de budget par étape, ou détection d'absence de progrès en relecture (un constat bloquant ou à corriger qui revient, en substance, au tour suivant). Son déclenchement fait passer la tâche à l'état « bloqué ». | Provisoire (absence de progrès ajoutée, RET-006) |
| Agent | Une instance de rôle en cours d'exécution, via un backend d'agent. | Provisoire |
| Backend d'agent | Ce qui exécute réellement un agent : Claude Code headless (E0) ou le harness maison (E2). | Validé |
| Headless / stream-json | Mode non interactif de Claude Code (`-p`), qui émet un événement JSON par ligne. | Validé |
| Tour (turn) | Un aller-retour modèle → éventuels appels d'outils. | Provisoire |
| Outil (tool) | Capacité exposée au modèle, décrite par un schéma. | Provisoire |
| Commande d'UI | Action nommée et typée de l'interface, partagée par la palette et l'agent (ADR 0007). | Validé |
| Mainteneur | Ben. Il décide, donne les feux verts, recette. Il n'écrit pas le code. | Validé |

## Mesure (ADR 0011)

| Terme | Définition | Statut |
|---|---|---|
| DORA | Programme de recherche sur la performance de livraison logicielle ([dora.dev](https://dora.dev)). | Provisoire |
| Petit lot | Changement assez petit pour être relu, testé et mergé en quelques jours. Une tâche est un petit lot. | Provisoire |
| Livraison | Par défaut, merge dans `main`. Pour un repo dont `main` est déployé, déploiement réussi. | Provisoire |
| Incident | Défaut constaté après une livraison et qui exige une correction immédiate. Signalé par une issue étiquetée `incident`. | Provisoire |
| Délai de changement (*change lead time*) | Du premier commit de la branche à la livraison. | Provisoire |
| Fréquence de livraison (*deployment frequency*) | Nombre de livraisons par semaine. | Provisoire |
| Temps de rétablissement (*failed deployment recovery time*) | De la livraison fautive à la livraison de son correctif. | Provisoire |
| Taux d'échec des changements (*change fail rate*) | Part des livraisons désignées par une issue `incident`. | Provisoire |
| Taux de reprise (*deployment rework rate*) | Part des livraisons qui ferment une issue `incident`. | Provisoire |
| Indicateurs agents | Par tâche : itérations, tours de relecture, coût, durée de tâche. | Provisoire |
| Durée de tâche | De la création du worktree au merge, dont le temps d'attente des feux verts. | Provisoire |
