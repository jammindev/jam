# ADR 0005 — Electron, macOS uniquement

- **Statut** : acceptée
- **Date** : 2026-10-08

## Contexte

Il faut une application desktop. Quatre options étaient sur la table :

- **Electron** : TypeScript partout.
- **Tauri** : backend en Rust.
- **Tauri avec un sidecar Node.**
- **Une app web locale.**

Le mainteneur ne code pas ([ADR 0003](0003-code-ecrit-par-agents.md)). Son niveau sur l'une ou l'autre stack compte donc moins que trois autres critères : la qualité du code que les agents produisent dans la stack, la lisibilité du résultat, et la possibilité de reprendre des briques d'Orca, qui est sous licence MIT et écrit en Electron/TS.

## Décision

- **Electron** pour l'application desktop.
- **macOS uniquement** au MVP. Le cœur reste néanmoins portable : pas d'API propre à macOS en dehors de l'UI et des notifications.

## Conséquences

- (+) Les briques d'Orca peuvent être reprises directement (diff, git, organisation main/renderer), sous réserve de la mention de licence.
- (+) Le SDK Anthropic TS, le SDK MCP TS et l'écosystème Node sont disponibles nativement.
- (+) Le mainteneur découvre Electron, ce qui fait l'objet d'une fiche concept.
- (−) L'application est lourde : environ 150 Mo et une consommation de RAM plus élevée qu'avec Tauri. C'est acceptable pour un outil personnel.
- (−) Linux, et donc un éventuel usage sur le VPS, n'est pas couvert au MVP. Le cœur séparé ([ADR 0006](0006-coeur-separe-ui.md)) garde cette porte ouverte.
