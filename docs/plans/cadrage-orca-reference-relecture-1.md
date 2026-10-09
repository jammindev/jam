# Relecture du cadrage `cadrage-orca-reference`, tour 1

Relecteur seul, deux axes. Objet : la rédaction non commitée qui applique RET-011 (8 fichiers : `AGENTS.md`, profils de l'implémenteur, du planificateur et du relecteur, `docs/references/orca.md`, glossaire, `OPEN-QUESTIONS.md`, `RETOURS.md`).

Vérifié sans constat :
- les cinq points de la règle validée sont reportés dans le profil du planificateur et dans RET-011 ;
- l'ADR 0001 n'est ni contournée ni modifiée : pas de fork, Orca reste une référence de lecture, et la licence est encadrée. L'absence de nouvelle ADR est justifiée ;
- la liste noire est conforme aux ADR 0002 et 0004 ;
- les citations de l'ADR 0005 et de la vision (« on n'élague pas le code d'Orca ») sont exactes ;
- aucun chemin propre à une machine : le chemin du clone reste dans le brief, et le plan cite les fichiers d'Orca par leur chemin dans le repo d'Orca ;
- les renvois de section de la carte (§1 à §9) pointent vers les bonnes sections ;
- RET-011 suit le format des entrées précédentes ;
- la numérotation (RET-011, Q-040) respecte le partage avec l'autre cadrage, et la mention non définie de « l'orchestrateur de tâche » est attendue.

## Bloquant

Aucun.

## À corriger

### 1. La section « Orca » devient obligatoire dans tout plan, y compris ceux que jam produira pour `house`

- **Fichiers** : `docs/process/roles/planificateur.md`, lignes 13, 15 et 20 ; `docs/specs/OPEN-QUESTIONS.md`, ligne 40.
- **Constat** : selon l'ADR 0009, les profils de rôle sont décrits dans `docs/process/roles/`. Le jalon S2 (`04-ROADMAP.md`, ligne 44) fait tourner ce même rôle planificateur, « avec son profil », sur des issues de `house`. Tel qu'il est rédigé, le profil impose à tout plan une section « Orca » (au minimum une ligne « aucune brique ») et un clone d'Orca ouvert par `--add-dir`. Or RET-011 porte sur la construction de jam : Orca n'est une référence que pour ce repo. Pour `house`, la section serait du bruit et le clone serait inutile. La seconde moitié de Q-040 (« le cœur fournira-t-il lui-même ce clone au planificateur ? ») hérite de la même ambiguïté.
- **Correction attendue** :
  - limiter explicitement la règle aux tâches du repo jam, par exemple : « Pour les tâches de jam (RET-011) : … » en tête du paragraphe « Clone de référence », de la lecture de la carte et de la section 3 du plan ;
  - reformuler la seconde moitié de Q-040 : dans jam, une « référence de lecture » sera-t-elle une donnée de la configuration du repo (pour jam : Orca), ou une règle propre au développement de jam ?

### 2. L'ouverture du clone à l'implémenteur n'est pas couverte par la règle validée

- **Fichiers** : `docs/process/roles/implementeur.md`, ligne 18 ; `docs/specs/GLOSSARY.md`, ligne 35 ; `docs/specs/RETOURS.md`, lignes 95 et 101.
- **Constat** : le point 5 validé par le mainteneur ouvre le clone **au planificateur**. La rédaction l'ouvre aussi à l'implémenteur quand le plan prévoit une reprise (profil de l'implémenteur, glossaire). L'ajout se défend : copier un fichier et le texte de la licence demande d'y accéder. Mais RET-011 ne le mentionne ni dans la règle ni dans son impact, où l'implémenteur n'apparaît que pour « reprise et licence ». Le mainteneur validerait donc au feu vert de cadrage une extension que le journal ne trace pas.
- **Correction attendue** : dans RET-011, ajouter après la règle une phrase signalée comme un complément du rédacteur, à valider au feu vert de cadrage, sur le modèle des « compléments validés » de RET-002. Par exemple : « pour une reprise prévue par le plan, l'orchestrateur ouvre aussi le clone à l'implémenteur ». Compléter l'impact en conséquence.

### 3. Personne ne sait comment le clone est produit ni rendu non modifiable

- **Fichiers** : `docs/process/roles/planificateur.md`, ligne 13 ; `docs/references/orca.md`, ligne 20 ; `docs/specs/OPEN-QUESTIONS.md`, ligne 40.
- **Constat** : la rédaction confie le clone à l'orchestrateur de tâche (« sans droit d'écriture », « dans un dossier temporaire »), mais aucun document ne dit comment le faire. Restent sans réponse : la commande de clone au tag, la façon de le rendre non modifiable, la réutilisation d'un même clone entre tâches ou sa suppression. Or l'interdiction d'écrire n'est pas tenue par les seules règles `Edit` : l'implémenteur, qui y a accès (constat 2), dispose de `Bash(node *)` et peut écrire partout, ce que le process reconnaît déjà (« Ce qu'Orca ne permet pas »). Sans droits du système de fichiers, « lecture seule » n'est qu'une consigne. Enfin, le profil de l'orchestrateur de tâche vit dans l'autre cadrage : rien ne garantit qu'il reprendra ce devoir au moment de la fusion.
- **Correction attendue** :
  - décrire la procédure en quelques lignes, de préférence dans la section 0 de `orca.md` à côté de la version de référence : clone superficiel au tag, retrait des droits d'écriture, réutilisation tant que la version ne change pas ;
  - tracer la dépendance dans une question ouverte (Q-042) ou dans Q-040 : à la fusion avec le cadrage de l'orchestrateur, son profil doit inclure la fourniture du clone et le `--add-dir` (planificateur, et implémenteur en cas de reprise).

### 4. La carte contredit sa propre liste noire

- **Fichier** : `docs/references/orca.md`, lignes 376 à 379 (§9, « À reprendre ou à imiter », rubrique « Terminaux »).
- **Constat** : la nouvelle section 0 (ligne 32) écarte toujours le terminal interactif (PTY, `src/main/daemon/`). Pourtant, le §9, auquel la carte renvoie (lignes 27 et 32), range toujours parmi les éléments « à reprendre ou à imiter » le « daemon propriétaire des PTY, séparé de l'UI » et « `xterm/headless` côté serveur pour `read` et `wait` ». Un planificateur qui suit la carte tombe sur deux consignes opposées.
- **Correction attendue** : dans le §9, retirer la rubrique « Terminaux », ou la marquer « écartée : liste noire, voir §0 (ADR 0002, 0004) ».

## Suggestions

### 5. La carte envoie vers l'Agent SDK, que l'ADR 0004 a écarté

- **Fichier** : `docs/references/orca.md`, ligne 27.
- **Constat** : `src/main/native-chat/agent-session-wire/` pilote Claude via l'Agent SDK (§9, ligne 447). L'ADR 0004 a écarté ce mode d'intégration (option 3).
- **Proposition** : préciser dans la cellule « (format des événements seulement ; l'Agent SDK est écarté, ADR 0004) ».

### 6. `THIRD_PARTY_NOTICES.md` absent de la liste des fichiers du plan

- **Fichier** : `docs/process/roles/planificateur.md`, lignes 21 et 25.
- **Constat** : l'implémenteur suit le plan et signale tout écart. Une reprise l'oblige à créer ou modifier `THIRD_PARTY_NOTICES.md`, mais le profil ne dit pas que ce fichier doit figurer dans « Fichiers créés ou modifiés ».
- **Proposition** : ajouter « toute reprise ajoute `THIRD_PARTY_NOTICES.md` aux fichiers créés ou modifiés ».

### 7. Le relecteur ne peut pas distinguer une copie d'une inspiration

- **Fichier** : `docs/process/roles/relecteur.md`, ligne 28.
- **Constat** : le point 5 de l'axe B vérifie que les reprises prévues portent bien leur licence. Mais sans accès au clone, le relecteur ne peut pas repérer un fichier marqué « inspiré » qui serait en réalité copié, donc sans mention de licence.
- **Proposition** : noter la limite dans Q-040, ou ouvrir aussi le clone au relecteur de conformité quand le plan contient une section « Orca » non vide.

### 8. La table du process ne mentionne pas le clone

- **Fichier** : `docs/process/README.md`, ligne 36 (ligne « Plan » de la table de correspondance).
- **Constat** : la commande décrite pour le planificateur est complétée par `--add-dir <clone>` pour les tâches de jam, mais la table du process n'en dit rien.
- **Proposition** : ajouter « + clone de référence d'Orca en lecture (RET-011) ».

RELECTURE : CORRECTIONS (4)
