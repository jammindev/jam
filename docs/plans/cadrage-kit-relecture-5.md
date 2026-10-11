# Relecture du cadrage `cadrage-kit` — tour 5

Relecteur seul, contexte neuf. Objet : la rédaction non commitée du worktree (ADR 0016 et 0017, specs 00 à 04, glossaire, questions ouvertes, retours RET-014 à RET-016, process et profils, `AGENTS.md`, `README.md`, brouillons `cadrage-kit-issues.md`). Inventaire des hooks vérifié en lecture seule sur le dossier des hooks du poste de travail et ses réglages ; rien n'en est repris ici qui désigne le poste.

Vérifié sans constat : sort de chaque ADR (0001 à 0015) cohérent avec `AGENTS.md` (ADR caduques 0002, 0004 à 0007, 0010) ; exigences de l'app gardées avec leur état, aucun numéro réutilisé ni supprimé ; nouvelles questions à partir de Q-054 ; liste du `git rm` du profil de l'implémenteur conforme aux fichiers de l'app à la racine ; sept profils comptés ; passages du process contredits par l'ADR 0017 (acteurs, correspondance, lancement du coordinateur) mis à jour, profil du coordinateur aussi ; aucun chemin du poste, nom d'hôte, nom de machine ou nom d'un autre projet ajouté par ce cadrage.

## Bloquant

Aucun.

## À corriger

### C-1 — Renvoi « (section 2) » dans des corps d'issue publiés

- **Fichier** : `docs/plans/cadrage-kit-issues.md`, lignes 72 et 83 (corps de K1-1).
- **Constat** : la ligne 6 dit que le corps publié va de « **Exigences** » à la fin de la section de l'issue. La section 2 du fichier (commandes des rôles, liste de ce que le recetteur note « non reproduit », `--add-dir` des hooks du poste) n'est donc pas publiée. Sur GitHub, « (section 2) » ne désigne rien : le planificateur et le recetteur de K1-1 perdent la liste des points « non reproduits ».
- **Correction attendue** : remplacer chaque « (section 2) » par un lien vers la section du fichier sur `main` (`docs/plans/cadrage-kit-issues.md`, « 2. Ordre, niveaux et recette »), ou reprendre dans le corps la liste des points « non reproduits » (session lancée avec `JAM_ROLE`, `git commit`, carte Orca, lancement d'un script ou d'une session `claude`).

### C-2 — K1-2 : les rôles lancés après l'implémenteur liraient des profils qu'il vient de déplacer et réécrire

- **Fichiers** : `docs/plans/cadrage-kit-issues.md`, lignes 106 et 121 ; `docs/process/README.md`, ligne 82.
- **Constat** : le process dit que les rôles d'une tâche lisent le process et les profils **dans le worktree**. Dans K1-2, l'implémenteur déplace `docs/process/` vers `process/` et `roles/`, puis réécrit ces fichiers (ligne 106). Les relecteurs et le recetteur lancés ensuite liraient donc des profils écrits par l'implémenteur qu'ils doivent relire, ce que le profil de l'implémenteur cherche justement à empêcher (exclusion de `docs/process/`). Les chemins de profil des briefs (`docs/process/roles/…`) n'existent plus dans le worktree après le déplacement. La ligne 121 suppose que « les rôles lisent les profils du plugin installé », mais pendant K1-2 le plugin installé est celui de K1-1, qui n'a pas encore de `roles/`.
- **Correction attendue** : dans le corps de K1-2, dire que pour cette tâche l'orchestrateur de tâche lit le process et fait lire aux rôles les profils du worktree principal (`main`), par leur chemin absolu donné dans le brief, et pas ceux du worktree de la tâche. Formuler la phrase de la ligne 121 en hypothèse que le plan vérifie, pour les tâches qui suivront K1-2.

### C-3 — ADR 0016 : l'entrée en vigueur se contredit sur la confirmation d'un feu vert remonté par la carte

- **Fichiers** : `docs/decisions/0016-kit-de-methode.md`, ligne 68 ; `docs/process/README.md`, ligne 134.
- **Constat** : la ligne 68 applique la confirmation dans le terminal du coordinateur « dès que la garde de sortie du plugin est installée » (après le merge de K1-1), puis dit « Jusque-là [le merge de K1-2], `docs/process/README.md` et la règle 6 s'appliquent tels quels ». Or le process (ligne 134) dit qu'un feu vert relayé avec mots exacts, heure et session « vaut […] accord explicite » pour le merge. Entre l'installation du plugin et le merge de K1-2, le process sur `main` dit qu'un segment `✓` suffit, et la garde le refuse. Même ambiguïté pour le seuil « assez bon » et la mesure, applicables dès l'acceptation.
- **Correction attendue** : écrire « Pour le reste, jusqu'au merge de cette issue, `docs/process/README.md` et la règle 6 s'appliquent tels quels », ou ajouter au process, ligne 134, une phrase qui renvoie à la confirmation dans le terminal du coordinateur une fois la garde de sortie du plugin installée.

### C-4 — Plafond d'agents global : seul le coordinateur compte, alors que l'orchestrateur de tâche lance aussi des agents

- **Fichiers** : `docs/specs/01-REQUIREMENTS.md`, ligne 20 (FR-051) ; `docs/decisions/0016-kit-de-methode.md`, ligne 63 ; `docs/specs/GLOSSARY.md`, ligne 16.
- **Constat** : « Chaque coordinateur les compte avant d'en lancer un ». Au niveau *standard*, c'est l'orchestrateur de tâche qui lance les rôles (planificateur, implémenteur, deux relecteurs ou plus, recetteur). Appliquée à la lettre, la règle ne borne pas ces lancements : le plafond global est dépassé alors que chaque coordinateur la respecte. Le process actuel (ligne 80, « le nombre d'agents qu'il peut lancer à la fois ») répondait à ce cas par une part fixée par le coordinateur ; l'exigence du kit ne dit plus rien.
- **Correction attendue** : écrire que **toute session qui lance un agent** (coordinateur, ou orchestrateur de tâche au niveau *standard*) compte les agents en cours avant de le lancer, par exemple par le script de lancement de K1-1, qui refuse au plafond. Reporter la même formulation dans l'ADR 0016 et le glossaire.

## Suggestions

- **S-1 — Inventaire des gardes de sortie** (`docs/decisions/0016-kit-de-methode.md` l. 15 ; `docs/plans/cadrage-kit-issues.md` l. 48). Sur le poste de travail, les réglages ne câblent qu'**une** garde de sortie, qui ne couvre que `git commit` et `git push` : ni `gh pr merge`, ni écriture `gh`. La garde du coordinateur laisse volontairement ouverts les effets de `git`, `gh` et `orca`. « Trois gardes s'y recouvrent » vaut peut-être pour un autre poste, mais ne se vérifie pas sur celui que le plan inventorie. Surtout, la garde de sortie unique est en grande partie un **comportement nouveau** (merge et écritures `gh`), pas seulement une fusion. Le dire dans le « But » de K1-1 aide à estimer la taille du lot.
- **S-2 — Formulation du relais allégé** (FR-053, `01-REQUIREMENTS.md` l. 22 ; ADR 0016 l. 64 ; glossaire l. 40). « La forme complète reste obligatoire pour le merge d'un projet en production » laisse croire que le merge d'un projet hors production est allégé. Or seuls le feu vert plan et le feu vert recette le sont. Plus simple : « forme complète pour tout feu vert, sauf le feu vert plan et le feu vert recette ».
- **S-3 — Check-list de K1-1, refus d'un `git commit`** (`cadrage-kit-issues.md` l. 83). La garde actuelle laisse passer toute sortie lancée depuis le dossier temporaire de la session. Préciser que le repo jetable est créé hors de ce dossier, ou que le plan dit si la garde du plugin garde cette exception. Sans cela, le point de la check-list peut échouer pour une raison étrangère à la garde.
- **S-4 — Quatrième hook non vérifié** (`cadrage-kit-issues.md` l. 79). Le critère de fin dit que le plugin « câble les quatre hooks », mais ne vérifie que trois d'entre eux : ajouter la ligne d'état git à chaque message. Dire aussi si cette ligne porte la marque du plugin. Si oui, la garde de sortie doit continuer de l'ignorer quand elle lit le dernier message du mainteneur (la garde actuelle la reconnaît à son texte exact).
- **S-5 — Manifeste et nom de personne** (NFR-014, `01-REQUIREMENTS.md` l. 32). Le manifeste d'un plugin a d'ordinaire un champ `author`. Dire si le manifeste nomme le mainteneur (déjà nommé dans le glossaire) ou omet ce champ, pour que le critère de fin de K1-1 (l. 80) se vérifie sans débat.
- **S-6 — Description du milestone K1** (`cadrage-kit-issues.md` l. 17 et 20). Elle cite « K1-1 et K1-2 », mais l'action 4 ne remplace ces repères que dans les corps d'issue. Écrire « les deux premières issues du jalon », ou ajouter la description du milestone à la seconde passe.
- **S-7 — Plafond de NFR-015** (`01-REQUIREMENTS.md` l. 33 ; `cadrage-kit-issues.md` l. 109). Préciser si le gabarit `process/fiche-projet.md` compte dans le nombre de mots « après ».
- **S-8 — Taille de K1-1.** C'est de loin le plus gros lot (retrait de l'app, CI, quatre hooks dont une garde en grande partie nouvelle, deux scripts avec des sorties d'Orca simulées, manifeste, installation, passages du rédacteur, fiche concept). Le plan peut l'estimer et, si besoin, laisser la fiche concept à K1-3, qui est au niveau *léger* et ne touche qu'à la doc.
- **S-9 — Introduction du process** (`docs/process/README.md` l. 3). « En attendant que jam sache dérouler son pipeline » reste sur `main` jusqu'au merge de K1-2, alors que l'ADR 0016 abandonne ce but. Ce n'est pas une règle, et le brief limite les retouches du process à l'ADR 0017 : une ligne de renvoi à l'ADR 0016 suffirait, si le mainteneur le veut.
- **S-10 — Q-030** (`OPEN-QUESTIONS.md` l. 36). Le décideur est « Ben, avec les métriques », et la question renvoie aux indicateurs agents, que l'ADR 0016 ne calcule plus. Ajuster la colonne « Qui ou quoi tranche » (par exemple « Ben, à l'usage »).
- **S-11 — Comptage des « agents en cours »** (FR-051). `orca terminal list` liste des terminaux, pas forcément des sessions d'agent : un shell ouvert sans agent compterait. Le plan de K1-1 (script de lancement) dit comment il les distingue.
- **S-12 — Noms d'un autre projet déjà sur `main`** (`RETOURS.md` l. 27 et 155 ; `OPEN-QUESTIONS.md` l. 41). Ces lignes ne viennent pas de ce cadrage. Avec la décision 7 de RET-016 (« rien de propre à un autre projet ») et la page publique à venir, un nettoyage pourrait suivre, hors de ce cadrage.

RELECTURE : CORRECTIONS (4)
