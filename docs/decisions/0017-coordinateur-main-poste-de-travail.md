# ADR 0017 : le coordinateur vit dans le `main` du projet, sur le poste de travail

- **Statut** : acceptée (feu vert de cadrage du 2026-10-11)
- **Date** : 2026-10-11
- **Tranche** : RET-015. Remplace la partie « Coordinateur dans le terminal flottant » de l'[ADR 0015](0015-remontee-carte-seule-coordinateur-flottant.md)

## Contexte

L'ADR 0015 a placé le coordinateur dans le terminal flottant d'Orca, joignable depuis tous les worktrees, et lancé depuis le worktree principal après un `cd` (RET-012). Deux choses ont changé.

- **Plusieurs projets.** La méthode tourne sur trois projets, chacun avec son coordinateur. Le terminal flottant est unique pour tout Orca : il ne peut pas porter un coordinateur par projet. Le mainteneur a décidé le 2026-10-10 que le coordinateur d'un projet tourne dans le worktree `main` de ce projet, et qu'une session du terminal flottant n'a plus de rôle (RET-015).
- **Un poste de travail dédié** (2026-10-11). Les agents tournent désormais sur une machine dédiée, le poste de travail. Orca y tourne, et le mainteneur le pilote depuis un autre poste par le serveur Orca distant. Trois constats en découlent :
  - une session d'agent lancée par SSH n'a pas les identifiants de la session graphique (Claude Code, `gh`) ;
  - le poste peut redémarrer, et ses dossiers temporaires sont alors vidés ;
  - une fenêtre d'autorisation du système (accès à un dossier, au trousseau…) s'affiche sur l'écran du poste et bloque l'agent qui l'a provoquée.

## Décision

### Emplacement du coordinateur

- Le coordinateur d'un projet tourne dans **un terminal Orca du worktree principal (`main`) de ce projet**, lancé par `JAM_ROLE=coordinateur claude` (avec `--continue` pour reprendre une session). Il n'y a pas de `cd` à faire : le terminal s'ouvre dans le worktree.
- **Un coordinateur par projet.** Chacun suit les cartes de son projet.
- **Une session du terminal flottant n'a pas de rôle** : c'est une session libre, qui sait seulement où elle est.

### Poste de travail

- **Les agents se lancent par Orca**, sur le poste de travail : terminal Orca ouvert par le mainteneur, ou `orca terminal create` par un coordinateur ou un orchestrateur de tâche. Jamais par une session SSH.
- **Rien d'indispensable ne vit dans un dossier temporaire.** Ce qui doit survivre à un redémarrage vit dans un dépôt (le plugin, ou le repo du projet) ou, pour ce qui est propre au poste, dans un dossier durable du poste. Les cas connus et leur sort :
  - outil de veille des cartes : dans le plugin (`scripts/`), par la première issue du jalon K1 ; schéma de la CLI Orca : versionné dans le plugin s'il est indispensable aux scripts, ce que dit le plan de cette issue ;
  - notes de frictions des essais : relues par ce cadrage ; celles qui restent à trancher sont des questions ouvertes (Q-060) ;
  - clone de référence d'Orca : sans objet tant que l'ADR 0014 est historique ([ADR 0016](0016-kit-de-methode.md)) ;
  - analyse d'un retour reçu dans un worktree (segment `💬` de la carte), écrite aujourd'hui dans un dossier temporaire de l'orchestrateur de tâche : emplacement durable à fixer ([Q-058](../specs/OPEN-QUESTIONS.md)).
- **Fenêtre d'autorisation du système** : seul le mainteneur la valide, sur l'écran du poste. Quand une carte reste `in-progress` sans changer, le coordinateur envisage ce cas comme une invite de permission, et prévient le mainteneur.

### Ce que l'ADR 0015 devient

| ADR 0015 | Avec cette ADR |
|---|---|
| Coordinateur lancé dans le terminal flottant, depuis le dossier du worktree principal | Lancé dans un terminal Orca du worktree principal du projet |
| Il parle au coordinateur depuis n'importe quel worktree | Il va dans le worktree principal du projet pour lui parler |
| Conséquence (−) : le `cd` à ne pas oublier | Supprimée |
| Remontée par la carte seule | Inchangée |

Le reste de l'ADR 0015 tient. L'ADR 0013 retrouve sa ligne « Lancement : dans un terminal Orca du worktree principal ».

À l'acceptation de cette ADR, le statut de l'ADR 0015 mentionne ce remplacement, et le statut de l'ADR 0013 ne parle plus du terminal flottant.

## Conséquences

- (+) Chaque projet a son coordinateur, au bon endroit, qui lit `AGENTS.md` et le process du projet dès le démarrage.
- (+) Le hook de démarrage montre au coordinateur la carte du worktree principal, comme à tout agent.
- (+) Ce qui fait tourner la méthode survit à un redémarrage du poste.
- (−) Le mainteneur ne parle plus au coordinateur depuis n'importe quel worktree : pendant une recette, il change de worktree ou parle à l'orchestrateur de tâche.
- (−) Une fenêtre d'autorisation du système reste invisible à distance tant que le mainteneur ne regarde pas l'écran du poste ([Q-059](../specs/OPEN-QUESTIONS.md)).
- (−) Le plafond d'agents est partagé par plusieurs coordinateurs : chacun doit le lire avant de lancer un agent (ADR 0016).
