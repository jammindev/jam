# Référence — Construire un harness : API Claude, Agent SDK, MCP, Codex, OpenCode

> Note de recherche du 2026-10-08, rédigée par un sous-agent. Sources citées inline. Plusieurs points sont en bêta ou changent vite (voir « Incertain »). **Revérifier avant d'implémenter.**

## TL;DR

- La boucle tient sur un seul endpoint, `POST /v1/messages` : tant que `stop_reason == "tool_use"`, exécuter les outils et renvoyer tous les `tool_result` dans un seul message `user`. Modèle par défaut actuel : `claude-opus-5-5` (4 $ / 20 $ par MTok).
- Trois points récents qui contraignent un harness :
  - l'historique doit être en ajout seul (le *preserved thinking* interdit de réécrire les tours passés) ;
  - `tool_choice` forcé est interdit sur les modèles 5.x ;
  - on ne peut pas désactiver le thinking sur Opus 5.5.
- L'Agent SDK embarque le binaire Claude Code : gain de temps énorme, mais aucun apprentissage de la boucle et aucun contrôle sur le cœur.
- MCP : la spécification a été refondue le 2026-07-28 (protocole sans état).
- Codex CLI : le sandbox Linux par défaut est désormais bubblewrap, plus Landlock.

## 1. API Messages et tool use

### Définition d'un outil

- Un outil se définit par `name`, `description` et `input_schema` (JSON Schema `object`).
- `strict: true` (à la racine de l'outil) garantit une entrée conforme au schéma. Il exige `additionalProperties: false` et la liste `required`.
- `tool_choice` accepte `auto | any | tool | none`. **Sur Opus 5.5, Sonnet 5.5 et Fable 5.1, `any` et `tool` renvoient une erreur 400** : utiliser `auto` et l'instruction dans le prompt.
- Doc : https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview

### La boucle

1. Envoyer `messages`, `tools` et `system`.
2. Si `stop_reason == "tool_use"`, ajouter **tout** `response.content` comme message `assistant` (blocs `thinking`, texte et `tool_use` compris).
3. Exécuter chaque `tool_use` et renvoyer un message `user` qui contient un `tool_result` par appel, avec le bon `tool_use_id`. En cas d'erreur, `is_error: true`.
4. Recommencer jusqu'à `end_turn`.

Autres `stop_reason` à gérer :

| Valeur | Conduite |
|---|---|
| `max_tokens` | Réponse tronquée. Ne jamais exécuter un `tool_use` incomplet. |
| `refusal` | Ne rien exécuter, lire `stop_details`. |
| `pause_turn` | Un outil serveur a été interrompu. Renvoyer la conversation telle quelle, sans ajouter « continue ». |
| `compaction` | Uniquement si la compaction est configurée avec pause. |

### Appels d'outils parallèles

- Activés par défaut : plusieurs `tool_use` peuvent arriver dans un même message `assistant`.
- Tous les `tool_result` doivent repartir dans **un seul** message `user`. Les répartir sur plusieurs messages déapprend le parallélisme au modèle.
- `disable_parallel_tool_use` force un seul appel par tour.

### Streaming (SSE)

- Séquence : `message_start`, puis pour chaque bloc `content_block_start` → `content_block_delta`* → `content_block_stop`, puis `message_delta` (porte `stop_reason` et `usage`), puis `message_stop`.
- Événements possibles en plus : `ping` et `error` (ex. `overloaded_error`, équivalent du 529).
- Types de delta : `text_delta`, `input_json_delta` (JSON partiel des entrées d'outil), `thinking_delta`, `signature_delta`.
- `eager_input_streaming: true` sur un outil client : les entrées arrivent sans buffering, mais le JSON peut être incomplet et doit être validé.
- Doc : https://platform.claude.com/docs/en/build-with-claude/streaming

### Tool runner du SDK

- `client.beta.messages.toolRunner(...)` en TS (avec `betaZodTool`), `client.beta.messages.tool_runner(...)` en Python (avec `@beta_tool`).
- Il fait tourner la boucle sur **vos** outils : hooks par tour (approbation, interception), streaming et compaction. Pas d'outils intégrés.
- Ne reprend pas automatiquement après `pause_turn` (au moins jusqu'à `@anthropic-ai/sdk` 0.110 et `anthropic` 0.116).

### Outils client et outils serveur

**Outils client** (définis par Anthropic, exécutés chez soi, sans `input_schema`) :

| Outil | Déclaration | Détails |
|---|---|---|
| Bash | `{"type":"bash_20250124","name":"bash"}` | Entrée `command` ou `restart`. Coûte environ 244 à 325 tokens d'entrée. |
| Éditeur de texte | `{"type":"text_editor_20250728","name":"str_replace_based_edit_tool"}` | Commandes `view`, `create`, `str_replace` (une seule occurrence exacte, sinon erreur), `insert`. |
| Mémoire | `memory_20250818` | Dossier `/memories`. Commandes `view`, `create`, `str_replace`, `insert`, `delete`, `rename`. |

**Outils serveur** (exécutés par Anthropic) :

| Outil | Déclaration | Coût |
|---|---|---|
| Recherche web | `web_search_20260209` | 10 $ / 1 000 recherches |
| Récupération de page | `web_fetch_20260209` | Tokens seulement |
| Exécution de code | `code_execution_20260521` | 1 550 h/mois/org gratuites, puis 0,05 $/h. Gratuit avec web search/fetch. |
| Recherche d'outils | `tool_search_tool_regex`, `tool_search_tool_bm25` | Pour les gros catalogues d'outils |

### Prompt caching (levier de coût n° 1)

- Ordre du préfixe : `tools` → `system` → `messages`. Un seul octet modifié invalide tout ce qui suit. Maximum 4 breakpoints.

| Opération | Coût relatif à l'entrée normale |
|---|---|
| Écriture, TTL 5 min | 1,25× |
| Écriture, TTL 1 h | 2× |
| Lecture (cas général) | 0,1× |
| Lecture sur Opus 5.5 et Sonnet 5.5 | 0,05× |
| Lecture sur Fable 5.1 | 0,025× |

- Le cache automatique se déclare avec `cache_control` au niveau de la requête.
- Schéma recommandé pour un agent : un breakpoint explicite en fin de system figé, plus le cache automatique pour la queue de conversation.
- Dans une boucle saine, chaque requête lit tout l'historique en cache et n'écrit que le dernier tour. Vérifier avec `usage.cache_read_input_tokens`.
- Ce qui casse le cache sans prévenir : une date dans le system, un JSON non trié, un jeu d'outils qui change, un changement de modèle ou d'effort.
- Doc : https://platform.claude.com/docs/en/build-with-claude/prompt-caching

### Comptage des tokens

- `POST /v1/messages/count_tokens` (`client.messages.countTokens`). Le résultat dépend du modèle. Ne pas utiliser tiktoken.
- Le tokenizer de Claude 4.7+ produit environ 30 % de tokens en plus que celui de Sonnet 4.6 et des modèles antérieurs.

### Gestion du contexte côté serveur (bêta)

**Context editing**
- Header : `context-management-2025-06-27`.
- Stratégies : `clear_tool_uses_20250919` et `clear_thinking_20251015`. Elles effacent les anciens résultats d'outils, sans les résumer.

**Compaction à seuil**
- Header : `compact-2026-01-12`. Type : `compact_20260112`.
- Déclencheur par défaut à 150k tokens d'entrée (minimum 50k).
- Options : `pause_after_compaction` et `instructions`.
- Renvoyer `response.content` en entier, bloc `compaction` compris. Coût réel visible dans `usage.iterations`.

**Compaction à la demande**
- Header : `compact-2026-09-04`. Paramètre : `compaction`.
- Recommandée quand elle est disponible : elle peut garder les derniers tours tels quels et tourner en arrière-plan.
- Doc : https://platform.claude.com/docs/en/build-with-claude/compaction

### Thinking

- Sur les modèles 4.6+ : `thinking: {type: "adaptive"}`. `budget_tokens` renvoie une erreur 400 sur Opus 4.7+ et sur les 5.x.
- La profondeur se règle avec `output_config.effort` (`low` → `max`). Sur Opus 5.5, la valeur par défaut est `medium` et le thinking ne peut pas être désactivé.
- Par défaut le contenu n'est pas renvoyé (`display: "omitted"`). Pour l'afficher dans une UI : `display: "summarized"`.
- **Preserved thinking, critique pour un harness.** Les blocs `thinking` sont liés au modèle et à la conversation. Modifier un tour passé les invalide, et les comptes créés après le 2026-08-31 reçoivent une erreur 400. Le harness doit donc fonctionner en **ajout seul**.
- Pour injecter une consigne en cours de conversation sans casser le cache : ajouter un message `{"role":"system"}` dans `messages`.

### Modèles et prix

Source : https://platform.claude.com/docs/en/about-claude/pricing, vérifiée le 2026-10-08. Prix en $ par MTok.

| Modèle | Entrée | Sortie | Lecture cache | Contexte |
|---|---|---|---|---|
| `claude-fable-5-1` (le plus capable) | 10 | 50 | 0,25 | 1M |
| `claude-opus-5-5` (défaut recommandé) | 4 | 20 | 0,20 | 1M |
| `claude-sonnet-5-5` | 2 | 10 | 0,10 | 1M |
| `claude-haiku-4-5` | 1 | 5 | 0,10 | 200k |
| Claude Haiku 5.5 (prompts ≤ 100k) | 0,10 | 0,50 | 0,01 | à vérifier |

- Batch : −50 %. Fast mode Opus 5.5 : 8 $ / 40 $.
- Capacités en direct : `GET /v1/models/{id}`, champs `max_input_tokens` et `capabilities`.

## 2. Claude Agent SDK (TS et Python)

**Paquets.** `@anthropic-ai/claude-agent-sdk` et `claude-agent-sdk` (ex-« Claude Code SDK »).
- Doc : https://code.claude.com/docs/en/agent-sdk/overview
- Repos : https://github.com/anthropics/claude-agent-sdk-typescript et https://github.com/anthropics/claude-agent-sdk-python

### Ce qu'il fournit

**Boucle**
- `query()`, plus `ClaudeSDKClient` en Python (bidirectionnel).
- Messages : `SystemMessage` (init, compact_boundary…), `AssistantMessage`, `UserMessage`, `StreamEvent`, `ResultMessage`.
- `ResultMessage` porte le coût, l'usage et le `session_id`, avec les sous-types `error_max_turns` et `error_max_budget_usd`.
- Limites : `maxTurns` et `maxBudgetUsd`.

**Outils intégrés**
- Fichiers : Read, Edit, Write. Recherche : Glob, Grep. Exécution : Bash. Web : WebSearch, WebFetch.
- Orchestration : ToolSearch, Agent, Skill, AskUserQuestion, TaskCreate, TaskUpdate.
- Les outils en lecture seule tournent en parallèle, les mutations en série.

**Permissions**
- Ordre d'évaluation : hooks → règles deny → règles ask → mode → règles allow → callback `canUseTool`.
- Modes : `default`, `acceptEdits`, `plan`, `dontAsk`, le mode qui contourne les permissions, et `auto` (décision par un classifieur).
- Règles de la forme `Bash(npm *)` ou `Edit(//secrets/**)`.
- **Attention** : depuis le SDK TS v0.3.286, si `permissionMode` n'est pas précisé, le démarrage peut se faire en `auto`. Passer `default` explicitement si on en dépend.
- Doc : https://code.claude.com/docs/en/agent-sdk/permissions

**Autres fonctions**
- Hooks (dans le process) : PreToolUse, PostToolUse, UserPromptSubmit, Stop, SubagentStart/Stop, PreCompact.
- Sous-agents via `AgentDefinition`.
- Sessions reprenables et forkables, `sessionStore` pour une persistance externe.
- MCP : stdio, HTTP, et serveurs « SDK » dans le même process pour les outils maison.
- Chargement de CLAUDE.md, des skills et de `settings.json` via `settingSources`.
- Compaction automatique, plus `/compact`.

### Dépendance au binaire

Les deux SDK embarquent le binaire natif Claude Code et le lancent en sous-process (`cli_path` en Python pour en changer). Le cœur de la boucle n'est donc **pas dans le repo** : c'est le binaire Claude Code, fermé.

### Licence et conditions

- Usage régi par les Commercial Terms d'Anthropic, y compris pour un produit distribué à des tiers.
- Repo TS : « © Anthropic PBC. All rights reserved ». Repo Python : wrapper sous MIT, mais le binaire embarqué reste sous les Commercial Terms.
- **Pas de login claude.ai (abonnement) dans un produit tiers sans approbation : il faut une clé API.**
- Marque : interdit d'appeler un produit « Claude Code ». « Claude Agent » et « X Powered by Claude » sont autorisés.
- Le SDK collecte de la télémétrie.

### Ce qu'on perd par rapport à une boucle écrite à la main

- La visibilité sur le prompt système réel, l'assemblage de l'historique et le cache.
- Le choix de la compaction et de la troncature, imposées.
- La forme des outils intégrés, dont les schémas sont figés.
- L'indépendance de version : on dépend du binaire et de son format de session.
- La possibilité de changer de fournisseur de modèle.
- L'apprentissage de la boucle, du cache et de la gestion du contexte.

En échange, on a tout de suite un agent de niveau production.

## 3. MCP côté client

### Spécification du 2026-07-28

Source : https://modelcontextprotocol.io/specification/2026-07-28/basic/transports

**stdio** : JSON-RPC délimité par des retours ligne, dans un sous-process lancé par le client. Annulation via `notifications/cancelled`.

**Streamable HTTP**
- Un seul endpoint, un POST par message. La réponse est un JSON ou un flux SSE propre à la requête.
- En-têtes obligatoires : `MCP-Protocol-Version`, `Mcp-Method` et `Mcp-Name`. Gérer aussi `x-mcp-header`.

**Supprimés dans cette révision**
- `Mcp-Session-Id`, le flux GET, la reprise via `Last-Event-ID` et les requêtes envoyées par le serveur.
- Le handshake `initialize` : version et capacités voyagent dans le `_meta` de chaque requête.

**Remplacements**
- Sampling et elicitation serveur → client passent par MRTR (`InputRequiredResult`).
- Notifications : `subscriptions/listen`.

**Rétrocompatibilité**
- Le client tente une requête moderne, puis se rabat sur `initialize` (2025-11-25).
- L'ancien HTTP+SSE (2024-11-05) est déprécié.

### SDK officiels

Source : https://modelcontextprotocol.io/docs/sdk

- Tier 1 : TypeScript, Python, C#, Go, Rust, Ruby.
- Tier 2 : Java.
- Tier 3 : Swift, PHP, Kotlin.
- *Incertain* : support de la révision 2026-07-28 par SDK non vérifié. La plupart des serveurs parlent encore 2025-06-18 ou 2025-11-25, il faut donc gérer les deux époques.

### Travail côté harness

1. Spawner les serveurs (stdio) ou s'y connecter (HTTP).
2. Appeler `tools/list`.
3. Traduire `inputSchema` vers `input_schema` en préfixant le nom (ex. `mcp__serveur__outil`).
4. Relayer `tools/call`.

Alternative côté API : le MCP connector (bêta `mcp-client-2025-11-20`) fait appeler les serveurs MCP distants par Anthropic. Pas de stdio.

## 4. Harness open source de référence

### Codex CLI (OpenAI)

https://github.com/openai/codex : Apache-2.0, cœur en Rust (`codex-rs/`).

**Outils** (`core/src/tools/handlers`)
- `shell` et `unified_exec`.
- `apply_patch`, l'édition par patch dans un format maison : `*** Begin Patch` / `*** Update File:` / `@@` / `*** End Patch`. Pas de str_replace.
- `update_plan` (`plan.rs`), `view_image`, MCP, multi-agents, `request_user_input`, `tool_search`, `get_context_remaining`.

**Sandbox et approbations**
- Modes : `read-only`, `workspace-write`, `danger-full-access`.
- Approbations : `untrusted`, `on-request`, `on-failure`, `never`.
- macOS : Seatbelt, via `/usr/bin/sandbox-exec` uniquement (protection contre un binaire piégé dans le PATH) et `seatbelt_base_policy.sbpl`.
- Linux, **bubblewrap par défaut** :
  - `--ro-bind / /`, puis `--bind` sur les racines inscriptibles ;
  - `.git` et `.codex` remontés en lecture seule ;
  - seccomp pour couper le réseau ;
  - Landlock devient un mode legacy (`features.use_legacy_landlock`).
- Moteur de règles d'exécution : `execpolicy`.

**Compaction** : résumé local avec un `SUMMARIZATION_PROMPT` surchargeable, plus une variante distante (`compact_remote*`).

**Sessions et config**
- Sessions : fichiers « rollout » JSONL dans `$CODEX_HOME/sessions` et `archived_sessions`, avec un index SQLite (`state_db`).
- Config : `config.toml`. Instructions projet : `AGENTS.md`.
- La doc a migré vers https://learn.chatgpt.com/docs/security.

### OpenCode

`sst/opencode` est devenu https://github.com/anomalyco/opencode : MIT, TypeScript sur Bun.

**Architecture** : client/serveur. `opencode serve` expose un serveur HTTP, et le TUI, le web et le desktop en sont les clients. Un SDK est disponible.

**Outils** (`packages/opencode/src/tool`) : `bash`, `read`, `write`, `edit` (remplacement exact), `apply_patch`, `grep`, `glob`, `lsp` (expérimental), `task` (sous-agent), `todowrite`, `webfetch`, `websearch`, `skill`, `question`.

**À retenir** : `registry.ts` donne `apply_patch` aux modèles `gpt-*` et leur masque `edit` et `write`. Les autres modèles reçoivent `edit` et `write`. Chaque famille obtient ainsi le format d'édition sur lequel elle a été entraînée.

**Agents** : `build` (accès complet), `plan` (lecture seule, demande avant bash), `general` (sous-agent).

**Permissions** : `allow`, `ask` ou `deny` par outil, dans `opencode.json`, avec wildcards.

**Fournisseurs** : Vercel AI SDK et models.dev, plus de 75 fournisseurs dont des modèles locaux (Ollama, LM Studio). Clés dans `~/.local/share/opencode/auth.json`.

**Compaction** : `auto` (activée par défaut) et `prune`, qui efface les vieilles sorties d'outils (`PRUNE_PROTECT` = 40k tokens).

**Sessions** : historiquement en JSON dans `storage/session/{info,message,part}`. Des migrations SQL apparaissent en 2026 : stockage en transition, *à vérifier*.

Docs : https://opencode.ai/docs/tools/ et https://opencode.ai/docs/config/

## 5. Recommandations factuelles pour un harness minimal (read, write, shell, search)

### 1. Langage

TypeScript avec `@anthropic-ai/sdk`, cohérent avec un desktop Electron ou Tauri à frontend web. Python avec `anthropic` convient aussi. Écrire la boucle à la main d'abord (objectif d'apprentissage). Le tool runner pourra servir plus tard.

### 2. Outils

Schémas maison :
- `read_file(path, offset?, limit?)` : contenu avec numéros de ligne, tronqué au besoin ;
- `write_file(path, content)` ;
- `run_shell(command, timeout_ms)` ;
- `search(pattern, path?, glob?)` : s'appuie sur ripgrep.

Ajouter vite un 5e outil, `edit(path, old_str, new_str)`, qui exige une occurrence unique (erreur sinon). Avec `write` seul, le modèle réécrit des fichiers entiers : coûteux et fragile.

Alternative : l'outil Anthropic `text_editor_20250728`, sur lequel le modèle est entraîné, mais dont le schéma n'est pas modifiable.

### 3. Boucle

- Historique en ajout seul.
- Ajouter `response.content` en entier, thinking compris.
- Tous les `tool_result` dans un seul message `user`, avec `is_error` en cas d'échec.
- Gérer `max_tokens`, `refusal` et `pause_turn`.
- Plafonner le nombre de tours et le budget.

### 4. Sécurité

- Canonicaliser les chemins sous la racine du workspace.
- Approbation dans l'UI pour `write` et `shell`, avec une allowlist de commandes en lecture seule.
- Modes inspirés de `default`, `acceptEdits` et `plan`.
- Timeouts et plafonds de taille de sortie.
- Sandbox : `sandbox-exec` sur macOS, `bwrap` sur Linux, en s'inspirant des politiques de Codex.
- Ne jamais exécuter un `tool_use` issu d'une réponse tronquée.

### 5. Coût

- System et outils figés et triés, breakpoint en fin de system, cache automatique sur la conversation.
- Suivre `cache_read_input_tokens` à chaque tour.
- Utiliser `count_tokens` pour décider quand compacter.

### 6. Modèle

- `claude-opus-5-5` avec un `effort` explicite : `high` pour coder, `low` pour les sous-tâches.
- `display: "summarized"` si l'UI affiche le thinking.
- Pas de `tool_choice` forcé.
- Streaming avec `eager_input_streaming`.

### 7. Persistance

- Sessions en JSONL, un événement par ligne, à la manière de Codex. Permet resume et fork.
- Compaction : d'abord la compaction serveur, ou un résumé client qui garde les N derniers tours.

### 8. Ensuite

Client MCP (`@modelcontextprotocol/sdk`), couche multi-fournisseurs (Vercel AI SDK ou adapters maison), sous-agents.

## Incertain ou récent

**MCP**
- Révision 2026-07-28 (sans état, MRTR) très récente : support partiel probable dans les SDK et les serveurs.

**Modèles**
- Haiku 5.5 apparaît sur la page de prix mais pas dans la table de référence. Contexte non vérifié.

**API Claude**
- En bêta : compaction (deux variantes, deux headers), context editing, task budgets, tool runner. Les noms de headers peuvent changer.

**Agent SDK**
- Le mode de permission par défaut a changé (`auto` possible).
- Le binaire évolue vite (2.1.2xx).

**Codex**
- Doc déplacée sur learn.chatgpt.com.
- Bascule de Landlock vers bwrap sur Linux.
- Repo très actif.

**OpenCode**
- Repo renommé (anomalyco).
- Stockage en migration vers SQL.

**macOS**
- Non vérifié : `sandbox-exec` est-il marqué déprécié par Apple ?
