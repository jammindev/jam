# Relecture — cadrage `cadrage-kit`, tour 7 (relecture courte)

Périmètre : le dernier passage du rédacteur, c'est-à-dire le passage des statuts et les corrections demandées au feu vert de cadrage (décisions 2 et 3). Relecteur seul.

## 1. Passage des statuts

- **ADR 0016 et 0017** : « acceptée (feu vert de cadrage du 2026-10-11) ». Conforme.
- **ADR 0001 à 0015** : `git diff --stat` montre une seule ligne modifiée par ADR, la ligne de statut, ce qui laisse le fond intact. Chaque statut reporte le sort du tableau de l'ADR 0016 : historique (0001, 0014), caduque (0002, 0004 à 0007, 0010), valable (0003), valable en partie (0008, 0009, 0011, 0015), précisée (0012, 0013). Le statut de l'ADR 0015 mentionne le remplacement de sa partie « Coordinateur dans le terminal flottant » par l'ADR 0017, une section qui existe bien sous ce titre. Le statut de l'ADR 0013 ne parle plus du terminal flottant. Ces deux points répondent à l'ADR 0017, l. 46.
- **Index** `docs/decisions/README.md` : cohérent avec les statuts et le tableau. La définition de « caduque » et d'« historique » y est ajoutée.
- **RETOURS** : RET-014, RET-015 et RET-016 passent à « appliqué ».

## 2. Corrections du feu vert

| Correction | Où | État |
|---|---|---|
| ADR 0009 « Valable en partie » | ADR 0016, l. 94 | Appliquée |
| Ligne « Licence » hors de la section de l'app | `README.md`, l. 9 | Appliquée |
| « à partir du merge de K1-2 » | `GLOSSARY.md`, l. 40 (« Feu vert ») | Appliquée |
| Principe des niveaux aligné sur « en production » | `00-VISION.md`, l. 7 et 45 | Appliquée |
| Bloc « Après le merge de K1-2 » déplacé dans K1-2 | `cadrage-kit-issues.md`, l. 138, absent de K1-1 | Appliquée |
| Garde de sortie pour tout le poste, voulue, sans contredire « le kit ne s'étend à aucun autre projet » | ADR 0016, l. 37 ; K1-1, point 4 (l. 69), rattaché à Q-055, avec la recette | Appliquée |
| K1-1 découpée par le plan en étapes vérifiables | `cadrage-kit-issues.md`, l. 72 | Appliquée |

Rien d'autre n'a été ajouté. Pas de contradiction trouvée : l'ADR 0016, l. 37, et l. 45 se distinguent bien, l'une vise la garde installée, l'autre la méthode et la fiche. Aucun chemin du poste, nom d'hôte ou de machine, ni nom d'un autre projet dans les fichiers touchés. La seule occurrence trouvée, `~/.local/share/jam` dans Q-021, existait déjà et désigne une convention générique.

## Constats

### Bloquant
Aucun.

### À corriger
Aucun.

### Suggestion
1. **`docs/decisions/0011-pratiques-et-metriques-dora.md:3`** : le statut dit « le §1 et les définitions restent ». Or le tableau de l'ADR 0016 (l. 96) ajoute que l'exception « outillage du poste » du §1 disparaît. Ajouter « sauf l'exception "outillage du poste", les hooks entrant dans le plugin », pour qu'un lecteur de l'ADR 0011 seule ne la croie pas encore en vigueur. Cosmétique : le statut renvoie à l'ADR 0016, qui fait foi.

RELECTURE : OK
