# Retours du mainteneur — #23 Process élagué (K1-2)

Note de suivi de l'orchestrateur de tâche (Q-058), non relue comme un livrable.

## 1. Les messages au mainteneur se lisent seuls

**Reçu** le 2026-10-13, relayé par le coordinateur depuis sa session sur `main`. Accord sur la règle : « Ok », 21:45, session du coordinateur.

**Le retour.** Le mainteneur suit plusieurs projets et ne lit que les sessions de `main`. Il ne peut pas retenir à quoi renvoient « issue #22 » ou « friction 18 ». Un message qui en dépend l'oblige à aller chercher le sens ailleurs.

**Analyse.** Le défaut est réel et vient de cette tâche même : la tête « À décider » du fichier de recette parlait de « friction 18 » et de « #22 » sans dire ce qu'ils désignent. Les numéros servent aux rôles, qui ont les fichiers sous la main. Le mainteneur, lui, lit hors contexte, à côté d'autres projets. La règle vaut pour tout ce qui lui est adressé : la carte, la tête « À décider » d'un fichier ouvert pour lui, le résumé du coordinateur. Elle ne touche pas les fichiers de travail entre rôles. Elle coûte quelques mots par message, ce qui reste sous le plafond du process.

**Ce qui change** (dans `process/README.md`, section « Messages au mainteneur ») : deux phrases au plus. Tout message au mainteneur se lit seul. Il nomme le projet et la tâche en mots, et chaque référence interne (issue, friction, ADR, RET, FR) est remplacée par ce qu'elle désigne, le numéro au plus entre parenthèses.

## 2. Le mainteneur ne valide pas le chiffre de la mesure

**Reçu** avec le retour 1, même relais.

**Le retour.** La section « Mesure » de `process/README.md` se termine par « Le mainteneur valide le chiffre ». C'est contraire à sa consigne : il ne compte rien lui-même.

**Analyse.** La phrase est un reste du relevé à la main. Le script estime le temps, et ses limites sont écrites dans la PR ; une validation par le mainteneur ajouterait le temps même que la mesure veut réduire.

**Ce qui change** : la phrase est retirée.
