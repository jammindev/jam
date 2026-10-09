# ADR 0014 : l'implémenteur lit le clone de référence d'Orca pour une reprise

- **Statut** : acceptée
- **Date** : 2026-10-09
- **Tranche** : RET-011, précise l'[ADR 0009](0009-permissions-par-role.md)

## Contexte

RET-011 fait consulter Orca par le planificateur, dans un clone de référence en lecture seule, hors du repo ([`docs/references/orca.md`](../references/orca.md), §0). On s'inspire d'Orca par défaut ; on ne copie qu'un petit morceau autonome, que le plan marque « repris ».

Pour copier ce morceau et le texte de sa licence, l'implémenteur doit lire le clone. Or le tableau de l'ADR 0009 lui donne « lecture et écriture dans le worktree », rien au-dehors. Le planificateur, lui, est en lecture seule sans restriction de lieu : le clone ne change rien pour lui.

## Décision

- **Quand le plan marque un morceau « repris »**, l'implémenteur lit aussi le clone de référence : son brief en donne le chemin et sa commande se termine par `--add-dir <clone-orca>`. Il n'écrit rien hors du worktree.
- Sans reprise prévue, son profil ne change pas.
- **Profil précisé**, sur le modèle des profils tracés dans l'[ADR 0012](0012-coordinateur-role-garde-fous-hook.md) :

| Rôle | Fichiers | Shell | Réseau / Git distant |
|---|---|---|---|
| Implémenteur, variante « reprise d'Orca » | Comme l'implémenteur ; en plus, lecture du clone de référence | Comme l'implémenteur | Non |

- À l'acceptation de cette ADR, le statut de l'ADR 0009 mentionne cette précision.

## Conséquences

- (+) La copie par exception de RET-011 a une voie d'application, et la licence se copie depuis sa source.
- (+) Aucune écriture n'est ajoutée : le principe de l'ADR 0009 tient.
- (−) Ce n'est sans doute pas un contrôle d'accès : la règle `"Read"` des profils n'est pas restreinte par chemin, et l'accès tient surtout au chemin donné dans le brief (à vérifier, Q-043).
- (−) Le clone est protégé en écriture par ses droits de fichiers seulement. Le shell de l'implémenteur (`node -e`) pourrait les lever : seul un sandbox système fermera cette voie (risque R-03).
