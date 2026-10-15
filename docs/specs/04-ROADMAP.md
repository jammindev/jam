# 04 — Roadmap

> Statut : réécrite le 2026-10-11 pour le kit ([ADR 0016](../decisions/0016-kit-de-methode.md), RET-016). L'ancien découpage de l'app (E0 à E3) est abandonné et résumé en fin de page.

## Jalon en cours : K1 — Kit de la méthode

Milestone GitHub `K1 Kit de la méthode`. Trois issues, deux à trois jours de travail, découpées par le cadrage `cadrage-kit` ([brouillons](../plans/cadrage-kit-issues.md)).

| Issue | Contenu | Dépend de |
|---|---|---|
| K1-1 | Le repo devient le kit : retrait du code Electron, hooks rapatriés (garde de sortie unique), scripts de veille et de lancement, fiche concept | — |
| K1-2 | Process élagué : process et profils génériques sous plafond de taille, niveaux, fiche projet (gabarit et fiche de jam), relais allégé, recette d'interface, mesure du temps du mainteneur estimée par script (RET-018), veille des cartes non tenues (RET-017) | K1-1 |
| K1-3 | Page publique : le `README.md` de jam | K1-2 |

**Critère de fin du jalon** : le repo ne contient plus le code de l'app ; le plugin s'installe sur le poste depuis le repo, et ses hooks et scripts passent leurs tests en CI ; le process et les profils sont génériques et tiennent sous leur plafond de taille (NFR-015) ; jam a sa fiche ; le `README.md` est la page publique, avec le temps du mainteneur sur K1-1 et K1-2, estimé par le script de FR-055 ; la fiche concept du jalon (plugin Claude Code et hooks comme garde-fous, `AGENTS.md` règle 3) est écrite.

## Ensuite

Le kit est gelé (NFR-016). Il ne change que sur une friction vécue dans un projet. Chaque autre projet du mainteneur adopte sa fiche quand il en a besoin, sans tâche dédiée dans jam. Ce qui a été retiré du jalon est dans [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md) (Q-062, Q-063).

## Risques principaux

- **R-01** — Rester bloqué à E0 sans jamais écrire le harness. _Sans objet (ADR 0016)._
- **R-02** — Les agents consomment le quota de l'abonnement, dont les limites ont déjà été atteintes. **Mitigation** : plafond d'agents global au poste (FR-051) ; seuil « assez bon » (FR-050) ; niveau *léger* par défaut, sans orchestrateur de tâche (FR-049, FR-052).
- **R-03** — Permissions des agents qui tournent sans surveillance. **Mitigation** : profils par rôle, mode sans permission interdit (ADR 0009), gardes en hooks versionnés (ADR 0012, FR-044). L'orchestrateur de tâche n'a pas encore de garde propre (Q-056). Le sandbox système viendra plus tard.
- **R-04** — Le format `stream-json` change. _Sans objet (ADR 0016)._
- **R-05** — Le format des plugins et des hooks de Claude Code, ou la sortie JSON de la CLI Orca, change. **Mitigation** : tests des hooks et des scripts en CI, avec des sorties d'Orca simulées ; une seule lecture de chaque format, dans le plugin.
- **R-06** — Le poste de travail redémarre ou bloque un agent sur une fenêtre du système. **Mitigation** : rien d'indispensable en dossier temporaire (NFR-013) ; lancement par Orca ; vérification des cartes figées (ADR 0017).
- **R-07** — Le kit devient un chantier sans fin, au détriment des livraisons des projets. C'est le premier risque du jalon. **Mitigation** : trois issues au plus, puis gel (NFR-016) ; toute nouvelle règle dit laquelle elle remplace ou retire ; plafond de taille du process (NFR-015).

## Historique : l'app (abandonnée)

De sa création au 2026-10-11, jam visait une app Electron en quatre étapes : **E0** boucle extérieure sur Claude Code headless (≤ 1 mois), **E0.5** coordinateur conversationnel, **E1** harness maison en CLI, **E2** harness branché dans l'app, **E3** confort. Abandonnée par l'ADR 0016 ; dernier état au tag `app-electron`.

| Jalon d'E0 | Milestone | Sort |
|---|---|---|
| S1 Squelette | #1 | Livré (app Electron, cœur séparé, palette) ; fermé |
| S2 Issue → worktree → un rôle | #2 | Découpé en huit issues (#13 à #20), fermées « not planned » ; milestone fermé |
| S3 Pipeline jusqu'à la PR | #3 | Jamais commencé ; fermeture proposée ([brouillons](../plans/cadrage-kit-issues.md)) |
| S4 Merge, nettoyage, parallélisme, métriques | #4 | Jamais commencé ; fermeture proposée ([brouillons](../plans/cadrage-kit-issues.md)) |
