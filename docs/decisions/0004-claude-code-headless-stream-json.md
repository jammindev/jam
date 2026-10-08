# ADR 0004 — Intégrer Claude Code en mode headless `stream-json`

- **Statut** : acceptée
- **Date** : 2026-10-08
- **Tranche** : Q-003

## Contexte

En E0, l'outil orchestre Claude Code ([ADR 0002](0002-orchestrer-claude-code-avant-harness.md)). Trois modes d'intégration étaient possibles :

1. **L'interface interactive (TUI) dans un terminal intégré**, comme Orca. Il faut alors déduire l'état de l'agent à partir de l'écran ou de hooks, ce qui est fragile, et un prompt peut se perdre pendant le démarrage.
2. **Le mode headless `stream-json`.**
3. **L'Agent SDK.** Il embarque le même binaire, et l'authentification par abonnement n'y est pas garantie.

## Décision

On lance Claude Code en headless, via `claude -p --output-format stream-json` (avec `--input-format stream-json` si besoin), et on reprend une session avec `--resume`. L'outil lit les événements structurés et les affiche lui-même.

## Conséquences

- (+) Le début et la fin de chaque tour sont connus, ainsi que les outils appelés et le coût. Pas de terminal à émuler, pas de détection d'inactivité.
- (+) Le format d'événements et le fil d'activité seront réutilisés tels quels par le harness maison. C'est ce qui donne corps à l'interface « backend d'agent » (FR-011).
- (+) Claude Code fonctionne avec l'abonnement existant, donc sans coût API en E0.
- (−) On perd l'interface interactive de Claude Code (slash commands, etc.).
- (−) Il faut implémenter l'approbation des permissions depuis l'UI, probablement via `--permission-prompt-tool`. **À vérifier** au moment de l'implémentation.
- (−) Le format `stream-json` peut changer d'une version de Claude Code à l'autre. On fixe la version testée.
