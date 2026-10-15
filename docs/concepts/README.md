# Concepts

Une fiche courte par concept, écrite **au moment où la brique qui le met en œuvre est livrée** ([ADR 0003](../decisions/0003-code-ecrit-par-agents.md), NFR-004). On n'écrit pas de fiche à l'avance.

## Format d'une fiche (≤ 1 page)

1. **En une phrase** : ce que c'est.
2. **Le problème** qu'il résout.
3. **Comment ça marche** : un schéma Mermaid si utile, et le chemin des fichiers du repo qui l'implémentent.
4. **Les pièges** rencontrés ou connus.
5. **Pour aller plus loin** : liens.

## Fiches

Les fiches de l'app Electron sont **historiques** ([ADR 0016](../decisions/0016-kit-de-methode.md)) : elles décrivent du code retiré, lisible au tag `app-electron`. Les fiches qu'elle prévoyait sans les avoir écrites sont sans objet.

| Concept | Brique | Fiche |
|---|---|---|
| Plugin Claude Code et hooks | Kit (K1, #22) | [plugin-et-hooks.md](plugin-et-hooks.md) |
| Veille sur transitions et mesure du temps du mainteneur | Kit (K1, #23) | [veille-et-mesure.md](veille-et-mesure.md) |
| Processus Electron (main, renderer, preload) et IPC | App : squelette | [processus-electron.md](processus-electron.md), historique |
| Cœur séparé et protocole typé | App : squelette | [coeur-separe-protocole.md](coeur-separe-protocole.md), historique |
| Git worktree | App : Git | Sans objet |
| Claude Code headless et `stream-json` | App : Agent | Sans objet |
| Interface « backend d'agent » | App : Agent | Sans objet |
| Boucle d'agent (tool use) | App : Harness | Sans objet |
| Permissions et approbation | App : Harness | Sans objet |
| Contexte, cache et compaction | App : Harness | Sans objet |
