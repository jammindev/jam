# Relecture du cadrage `cadrage-kit` — tour 1

Relecteur seul, contexte neuf. Périmètre : la rédaction non commitée du worktree (14 fichiers modifiés, ADR 0016 et 0017, `docs/plans/cadrage-kit-issues.md`). Inventaire des hooks cité par K1-a vérifié sur sa source hors du repo : quatre hooks, événements et matchers conformes, tests présents pour la garde du coordinateur et la reprise de contexte seulement. Conforme.

Vérifié sans constat : numérotation (FR-042 à FR-051, NFR-013, NFR-014, Q-054 à Q-061, ADR 0016 et 0017, RET-014 et RET-015 sans doublon ; le trou Q-044 à Q-049 existait déjà) ; exigences de l'app gardées avec leur état ; sort de chaque ADR dans l'ADR 0016 ; ADR 0017 cohérente avec le process, le profil du coordinateur, le glossaire et l'ADR 0013 (ligne « Lancement ») ; plus aucune règle « terminal flottant » hors historique ; milestone K1 et sort d'E0-S3 et E0-S4 proposés ; repo public : aucun nom de machine, d'hôte, de chemin du poste ni d'autre projet ajouté par ce cadrage (les mentions de `house` et du VPS sont antérieures).

## Bloquant

### B-1 — K1-a ne peut pas être déroulée avec les profils de rôle actuels

- **Fichiers** : `docs/plans/cadrage-kit-issues.md` l. 37, 66, 79 ; `docs/process/roles/implementeur.md` l. 9 ; `docs/process/roles/relecteur.md` l. 9 ; `docs/process/roles/recetteur.md` l. 9.
- **Constat** : K1-a est la première tâche du jalon, en TDD sur des hooks Python testés par `python3 -m unittest`, avec une recette qui installe le plugin (`claude --plugin-dir`). Ses rôles sont lancés avec les profils mergés, qui ne le permettent pas : l'implémenteur n'a que `pnpm`, `npx`, `node` (il ne peut pas lancer ses tests) ; le relecteur n'a que `pnpm test` et `vitest` ; le recetteur n'a que des commandes de l'app (`pnpm dev`, `curl` sur le port 9333, `JAM_DATA_DIR`…). Le process rendu générique n'arrive qu'avec K1-b, après K1-a. En l'état, le premier rôle de K1-a sera refusé, ou l'orchestrateur de tâche improvisera des commandes hors profil (contraire à l'ADR 0009).
- **Correction attendue** : dans ce cadrage, ajouter aux trois profils les formes exactes nécessaires à K1-a (`python3 -m unittest` et ses variantes, formes `rtk` comprises ; pour le recetteur, l'installation du plugin pour sa seule session), comme passage contredit par l'ADR 0016. À défaut, dire explicitement dans K1-a que son plan fixe les commandes des rôles, soumises au feu vert plan, et le tracer (exception à l'ADR 0009). La première voie est plus sûre.

## À corriger

### C-1 — NFR-014 s'applique au repo entier, qui viole déjà sa règle

- **Fichier** : `docs/specs/01-REQUIREMENTS.md` l. 27 (avec `GLOSSARY.md` l. 10 et ADR 0016 l. 24 : « le repo est lui-même le plugin »).
- **Constat** : « Le plugin ne contient ni nom d'un autre projet, ni chemin, ni nom de personne ». Si le repo est le plugin, `docs/` en fait partie, et il contient déjà le nom d'un autre projet (ADR 0011, RETOURS, OPEN-QUESTIONS) et le prénom du mainteneur (glossaire). L'exigence est fausse dès son écriture ; « ni chemin » interdirait aussi les chemins relatifs dont le plugin a besoin.
- **Correction attendue** : restreindre NFR-014 aux dossiers du plugin (`process/`, `roles/`, `hooks/`, `scripts/`, `skills/`, `modeles/`, manifeste), comme le font déjà les critères de fin des issues, et écrire « chemin du poste ».

### C-2 — Plafond du projet : « sa part » du plafond global, ou pas de part ?

- **Fichiers** : ADR 0016 l. 40 et l. 51 ; `01-REQUIREMENTS.md` l. 14 (FR-045) ; `cadrage-kit-issues.md` l. 136.
- **Constat** : l'ADR 0016 crée un plafond global lu par chaque coordinateur « au lieu d'estimer sa part », mais garde un « plafond d'agents » dans la fiche projet ; K1-c le définit comme « sa part du plafond global ». Les deux textes se contredisent sur ce que le planificateur de K1-c devra écrire.
- **Correction attendue** : trancher dans l'ADR 0016 : soit la fiche donne un plafond propre au projet, borne supplémentaire sous le plafond global (et non une part), soit la fiche n'a pas de plafond. Aligner FR-045, le glossaire (« Fiche projet ») et K1-c.

### C-3 — K1-f ne dépend que de K1-a, mais son critère de fin exige K1-b

- **Fichiers** : `cadrage-kit-issues.md` l. 32, 35, 214 ; `04-ROADMAP.md` l. 20.
- **Constat** : critère de K1-f : « aucune doc hors historique ne demande `pnpm` ». Or les profils de `docs/process/roles/` demandent `pnpm` tant que K1-b n'est pas mergée. Lancée en parallèle comme le permet l'ordre conseillé, K1-f ne peut pas atteindre son critère, et si elle est mergée avant K1-b, les rôles gardent des commandes `pnpm` qui ne marchent plus.
- **Correction attendue** : K1-f dépend de K1-a et K1-b (table de la section 2, ordre conseillé, roadmap).

### C-4 — Critère de fin de K1-c non vérifiable à sa clôture

- **Fichier** : `cadrage-kit-issues.md` l. 143.
- **Constat** : « le plan de K1-d fixe son niveau » ne peut être vérifié qu'après le merge de K1-c, au plan d'une autre tâche.
- **Correction attendue** : garder dans le critère ce qui se vérifie dans K1-c (règles écrites, Q-061 tranchée, le profil du planificateur exige un niveau motivé dans le plan) ; reporter le contrôle du niveau dans la recette ou le critère de K1-d.

### C-5 — Aucune fiche concept prévue pour le jalon K1

- **Fichiers** : `04-ROADMAP.md` l. 24 (critère de fin du jalon) ; `cadrage-kit-issues.md` l. 21 (description du milestone) ; `AGENTS.md` règle 3 ; NFR-004, déclarée valable (`01-REQUIREMENTS.md` l. 109).
- **Constat** : « Un jalon livré = une fiche concept » reste une règle de travail, mais ni le critère du jalon ni aucune issue ne produit de fiche (plugin Claude Code, hooks comme garde-fous).
- **Correction attendue** : ajouter la ou les fiches concept à l'issue qui livre la brique (par exemple K1-a pour « plugin et hooks ») et au critère de fin du jalon, ou acter par une ligne que la règle 3 change pour le kit.

### C-6 — K1-b n'est pas un petit lot

- **Fichier** : `cadrage-kit-issues.md` l. 85-118.
- **Constat** : K1-b déplace et réécrit en générique le process et sept profils, intègre l'ADR 0017, tranche Q-058, refait le modèle de permissions des profils (qui écrit `process/`, `roles/`, `modeles/` ; interdits à transposer, sachant que les rôles lisent le plugin installé), modifie un hook avec son test, écrit le gabarit et la fiche de jam, et met à jour `AGENTS.md`. C'est la plus grosse issue du jalon, mélange code et docs (donc deux relecteurs sur tout le diff), et contient une question de conception (permissions) qui peut faire durer la relecture (ADR 0011, petits lots).
- **Correction attendue** : découper, par exemple : K1-b1 « déplacement générique du process et des profils, gabarit et fiche de jam » ; K1-b2 « permissions des profils dans le plugin et hook de reprise ». Ajuster dépendances, roadmap et renvois K1-x.

## Suggestions

- **S-1** — `docs/process/README.md` l. 3, 19, 109, 196-205 : l'introduction (« en attendant que jam sache dérouler son pipeline… alimente E0 »), les jalons « S1, S2… », « dans jam, c'est le cœur qui injectera ce contexte » et « Ce qu'Orca ne permet pas (et que jam fera) » restent sur `main` jusqu'à K1-b. Une ligne d'avertissement en tête (« depuis l'ADR 0016, les mentions de jam, du cœur et d'E0 décrivent l'app abandonnée ; réécriture par K1-b ») évite de les prendre pour des règles, sans rien déplacer.
- **S-2** — `docs/process/README.md` l. 28, `roles/coordinateur.md` l. 27, `roles/orchestrateur-tache.md` l. 27 : l'analyse d'un retour `💬` reste prescrite dans un dossier temporaire, alors que l'ADR 0017 pose « rien d'indispensable en dossier temporaire ». C'est reconnu (Q-058), mais une mention « (provisoire, Q-058) » à ces endroits rendrait l'exception visible.
- **S-3** — `cadrage-kit-issues.md` l. 37 et 79 : après K1-a, la session de recette chargera le plugin installé **et** celui du worktree, sous le même nom. Le plan de K1-a doit dire comment n'en charger qu'un (ou comment lire le double chargement), au-delà du double récapitulatif.
- **S-4** — `cadrage-kit-issues.md` l. 77 : la dernière puce du critère de K1-a (retrait des hooks du poste) n'a lieu qu'après le merge, donc après la clôture de l'issue. La placer plutôt dans les actions du coordinateur après le merge de K1-a.
- **S-5** — `cadrage-kit-issues.md` l. 79 : la garde des écritures distantes laisse passer un `git commit` lancé dans un dossier temporaire de session. Préciser que le repo jetable de la check-list n'est pas dans un tel dossier, sinon le refus attendu n'arrive pas.
- **S-6** — `cadrage-kit-issues.md` l. 170 et 194 : « refuse quand le plafond est atteint » demande d'occuper le plafond par de vrais agents (quota) ; prévoir un plafond abaissé pour le test. « Une issue de test » est une publication sur un repo public : dire qui la crée et la ferme, ou utiliser un worktree sans issue.
- **S-7** — `01-REQUIREMENTS.md` l. 12 : FR-043 « reprend la méthode de FR-021 à FR-026 », alors que FR-022 à FR-026 restent valables et seule FR-021 est remplacée. Écrire « remplace FR-021 ; s'appuie sur FR-022 à FR-026 et FR-040 ».
- **S-8** — `01-REQUIREMENTS.md` l. 48 : FR-029 (plusieurs tâches en parallèle) est « remplacée par FR-051 », qui ne parle que du plafond. Le parallélisme lui-même n'est plus exigé ; dire « valable, bornée par FR-051 » si c'est l'intention.
- **S-9** — ADR 0016 l. 78 : l'ADR 0009 est classée « Valable » alors qu'une partie est déclarée caduque ; « Valable, précisée » ou « Valable en partie », comme pour 0012 et 0008.
- **S-10** — `00-VISION.md`, critère de succès : il omet « le code Electron est retiré », présent dans le critère du jalon (roadmap, milestone). Aligner.

RELECTURE : CORRECTIONS (7)
