# ADR 0015 : remontée par la carte seule, coordinateur dans le terminal flottant d'Orca

- **Statut** : acceptée
- **Date** : 2026-10-09
- **Tranche** : RET-012, RET-013, Q-037. Précise l'[ADR 0013](0013-orchestration-deux-niveaux.md)

## Contexte

L'ADR 0013 a été éprouvée une première fois sur l'issue #7 (PR #9). Deux points de sa décision n'ont pas tenu à l'usage.

- **Le message court** : pour un événement qui attend le mainteneur, l'orchestrateur de tâche prévenait le coordinateur par `orca terminal send`. Ce texte arrive dans la saisie du terminal du coordinateur, où le mainteneur écrit aussi. Le mainteneur l'a constaté le 2026-10-09 : « je vois des trucs apparaître automatiquement dans le prompt ». Le risque noté dans l'ADR 0013 (Q-037) s'est produit. Le canal a été abandonné le jour même, sur consigne du coordinateur (RET-013).
- **L'emplacement du coordinateur** : lancé dans un terminal du worktree principal, il n'est visible que depuis ce worktree. Pour lui parler pendant une recette, le mainteneur doit changer de worktree. Il a proposé de l'ouvrir dans le workspace flottant d'Orca, accessible depuis tous les worktrees. Proposition validée, testée et appliquée le 2026-10-09 (RET-012).

L'ADR 0013 est acceptée : ces deux changements font l'objet de cette ADR plutôt que d'une retouche de son texte.

## Décision

### Remontée par la carte seule

- L'orchestrateur de tâche **n'écrit plus dans le terminal du coordinateur**. Il tient seulement sa carte Orca : statut et commentaire. Pour un événement qui attend le mainteneur, le commentaire désigne le fichier à lire, dans le worktree de la tâche (chemin du worktree, puis chemin relatif).
- Le coordinateur **surveille les cartes en arrière-plan** et prévient le mainteneur quand l'une l'attend (feu vert, blocage).
- La carte porte aussi ce qui attend le coordinateur lui-même : un feu vert donné dans le worktree pour une de ses actions, un retour du mainteneur reçu dans le worktree. Ces mentions viennent après l'état de la tâche, toujours en tête, qui seul fixe le statut de la carte : le mainteneur lit le début de la carte, le coordinateur cherche ses mentions sur toutes les cartes. Elles se cumulent jusqu'à ce que le coordinateur en accuse réception dans le terminal de l'orchestrateur de tâche. Leur format est dans le process (« Signalement d'attente »).
- Dans l'autre sens, rien ne change : le coordinateur écrit dans le terminal d'un orchestrateur de tâche (`orca terminal send`) pour lui transmettre un feu vert ou une consigne. L'orchestrateur de tâche est un agent : il n'y a pas de saisie du mainteneur à protéger, sauf quand le mainteneur lui parle au même moment.
- **Feu vert relayé** : le format de l'ADR 0013 ne change pas (mots exacts, heure, session ; l'action que le feu vert ouvre, et elle seule). Seul le support change. Un feu vert donné dans le worktree, qui ouvre une action du coordinateur (merge ; publication des issues et des milestones), est cité dans le commentaire de la carte. Un feu vert donné au coordinateur est transmis dans le terminal de l'orchestrateur de tâche.

### Coordinateur dans le terminal flottant

- Le coordinateur est lancé dans le **terminal flottant** d'Orca, que le mainteneur ouvre depuis n'importe quel worktree. Il reste l'interlocuteur unique du mainteneur s'il le souhaite (RET-009).
- RET-008 tient : la session est **lancée depuis le worktree principal**, sur `main`. Le terminal flottant s'ouvre dans le dossier personnel : on se place d'abord dans le worktree principal, puis on lance `JAM_ROLE=coordinateur claude` (avec `--continue` pour reprendre une session).
- La CLI `orca` voit ce terminal (`worktreeId` vaut `global-floating-terminal`, sans chemin de worktree). Il n'a plus besoin d'être joint par les orchestrateurs de tâche, puisqu'ils ne lui écrivent plus.

### Ce que l'ADR 0013 devient

| ADR 0013 | Avec cette ADR |
|---|---|
| Coordinateur lancé dans un terminal Orca du worktree principal | Lancé dans le terminal flottant, depuis le dossier du worktree principal |
| Carte Orca, plus un message court au coordinateur quand le mainteneur est attendu | Carte Orca seule, surveillée par le coordinateur |
| Feu vert donné dans le worktree, remonté par un message court | Cité dans le commentaire de la carte s'il ouvre une action du coordinateur (merge, publication) ; sinon, l'orchestrateur de tâche agit et le segment d'état change |
| Correspondance avec jam : « Carte Orca et message court au coordinateur » | « Carte Orca » |
| Conséquence (+) : le coordinateur ne voit des tâches que les cartes et les messages courts | Il n'en voit que les cartes |
| Conséquence (−) : le message de l'orchestrateur de tâche arrive dans la saisie du mainteneur (Q-037) | Risque réalisé à #7, supprimé par la carte seule |
| Conséquence (−) : bloqué sur une invite, l'orchestrateur de tâche ne peut ni mettre à jour sa carte ni prévenir le coordinateur | Il ne peut plus mettre à jour sa carte |

Le reste de l'ADR 0013 tient, dont la conséquence sur l'expéditeur non authentifié d'un message `orca terminal send`. Cette conséquence s'étend aux commentaires de carte : un commentaire peut être écrit par toute session qui dispose de la CLI `orca`.

À l'acceptation de cette ADR, le statut de l'ADR 0013 mentionne cette précision.

### Correspondance avec jam

Dans jam, l'interlocuteur du niveau projet est joignable de partout, et sa session tourne dans le worktree principal du repo, quel que soit l'écran d'où le mainteneur lui parle. C'est une précision de FR-016 (champ de conversation accessible partout). Elle ne change pas l'étape du coordinateur conversationnel, qui reste celle de FR-040 tant que Q-039 n'est pas tranchée.

La remontée par la carte seule préfigure ce que l'ADR 0013 prévoyait déjà pour jam : les deux niveaux lisent le même état du cœur (FR-027), sans message entre agents.

## Conséquences

- (+) La saisie du mainteneur dans le terminal du coordinateur n'est plus jamais modifiée par un autre agent.
- (+) Un seul endroit à tenir pour l'orchestrateur de tâche : sa carte. Un changement de terminal du coordinateur ne casse plus rien, puisque personne n'a besoin de son handle.
- (+) Le mainteneur parle au coordinateur depuis n'importe quel worktree, pendant une recette par exemple.
- (−) Le coordinateur ne voit un événement qu'à sa prochaine lecture des cartes : la remontée a un délai.
- (−) Un commentaire de carte tient en une ligne : il désigne un fichier, il ne le remplace pas.
- (−) Le mainteneur doit penser au `cd` avant de lancer le coordinateur. Oublié, la session tourne dans le dossier personnel et ne lit ni `AGENTS.md` ni le process. Le hook de démarrage affiche le worktree de la session, ce qui permet de le voir.
- (−) Un message du coordinateur dans le terminal d'un orchestrateur de tâche peut encore croiser la saisie du mainteneur, s'il parle à cet orchestrateur au même moment. Le cas est plus rare : le mainteneur ne va dans un worktree que pour discuter de la tâche.
