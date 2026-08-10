# Stabilo — Bilan & Archives

## Résumé du projet

**Outil de relecture pour l'écriture radio, fondé sur la science cognitive.**

Aider les journalistes radio à écrire des textes qui passent mieux à l'oreille. Pas un correcteur orthographique, pas un réécriveur automatique — un relecteur exigeant qui pointe ce qui ne fonctionne pas à l'oral et explique *pourquoi*, études scientifiques à l'appui.

- **Repo** : https://github.com/Phoceen/stabilo
- **Live** : https://la-mere-michu.streamlit.app/ *(URL à renommer dans la console Streamlit Cloud — dernier vestige de l'ancien nom)*
- **Stack** : Streamlit + Claude API (pipeline Sonnet 5 + Haiku 4.5) + Python 3.12
- **Quota** : 5 appels IA max par session

---

## Architecture

4 fichiers, ~1200 lignes :

| Fichier | Rôle | Lignes |
|---------|------|--------|
| `knowledge_base.py` | Base de connaissances : BIBLIO (35 sources tierées A/B) + FINDINGS + anglicismes + jargon mesuré | ~330 |
| `rules.py` | Moteur de règles mécaniques (9 détecteurs, zéro IA) | ~290 |
| `agents.py` | Pipeline orchestré : 5 agents spécialisés (forme, assertions, cohérence, écoute ∥ puis mémo), sorties structurées | ~440 |
| `ai_analyzer.py` | Façade de compatibilité vers agents.py | ~25 |
| `app.py` | Interface Streamlit (2 zones, rendu en entonnoir) | ~697 |

### Deux étages complémentaires

**Étage 1 — Règles mécaniques** (rules.py) : rapides, déterministes, auditables.
- Longueur de phrase (> 25 mots warning, > 30 error)
- Voix passive
- Densité de chiffres (> 2 par phrase)
- Mots complexes (> 4 syllabes)
- Cacophonies
- Tournures écrites
- Adverbes faibles

**Étage 2 — Pipeline d'agents** (agents.py, via la façade ai_analyzer.py) : reçoit le texte *déjà annoté* par l'étage 1.
- Agent FORME : oralité phrase par phrase (regard rédac) + incarnation (VIF / FLOU / GRIS)
- Agent ASSERTIONS : faits à vérifier (Haiku, extraction pure, fusion des recouvrements)
- Agent COHÉRENCE : lancement ↔ papier, transitions manquantes, sobriété
- Agent ÉCOUTE : auditeur simulé multi-tours (une passe, morceau par morceau, inspiré STORM) → restitution + trace d'écoute
- Agent MÉMO : la note de relecture, synthèse des 4 précédents, ouvre sur la restitution

### Sortie (entonnoir)

- **Couche 1** : Verdict global → Note de relecture (ouvre sur « ce qu'il reste après une écoute ») → Trace d'écoute → Cohérence → Assertions à vérifier
- **Couche 2** (expander) : Détail phrase par phrase (heatmap, tooltips, chirurgie)

Diagramme complet : voir `architecture.mmd` (ouvrir dans mermaid.live).

---

## Philosophie

1. **La science d'abord, l'opinion ensuite.** Chaque alerte s'appuie sur une étude publiée. Pas de conventions de métier ni de préférences subjectives.
2. **Des directions, jamais de réécriture.** L'outil montre où ça coince et dans quelle direction aller. Le style, c'est celui du journaliste.
3. **L'entonnoir : du global au détail.** On lit la note de relecture d'abord. Le phrase-par-phrase est en option.
4. **Deux cerveaux complémentaires.** Les règles mécaniques attrapent le mesurable. Claude se concentre sur ce qu'elles ne captent pas.
5. **L'oreille, pas l'œil.** Tout est pensé pour l'oral. L'orthographe et la grammaire ne sont pas le sujet.

---

## Base scientifique

~20 études publiées dans des revues à comité de lecture couvrant 10 domaines :

| Domaine | Études clés | Seuil/Application |
|---------|-------------|-------------------|
| Mémoire de travail | Cowan (2001), Miller (1956), Baddeley & Hitch (1974) | 3-5 chunks, boucle phonologique ~2s |
| Longueur de phrase | Cowan (2001), Caplan & Waters (1999) | Warning > 25 mots, Error > 30 mots |
| Charge cognitive (chiffres) | Baker et al. (2018), Sweller (1988) | Max 2 chiffres par phrase |
| Double codage (images mentales) | Binder et al. (2009), Paivio | Score VIF/FLOU/GRIS |
| Position sérielle | Glanzer & Cunitz (1966) | Primauté + récence |
| Vagabondage mental | Kopp et al. (2015), Murray et al. (2023) | 30-40% de décrochage en écoute passive |
| Prosodie | Rodero (2012, 2017, 2023) | Débit optimal ~175 mots/min |
| Vitesse de traitement | Rayner et al. (2008), Leroy et al. (2019) | Écoute ~2x plus lente que lecture |
| Attention podcast | NPR, BBC (2019), Wolpaw et al. (2022) | Décision en 18 mots, 40% d'attrition en 7 min |
| Complexité syntaxique | Caplan & Waters (1999), Fedorenko et al. (2024, Nature) | Juste niveau de complexité |
| Redondance | Mayer (principes de redondance et cohérence) | Pas de surcharge multimodale |

---

## Historique des itérations

### Session 1 — Construction initiale
- Architecture 4 fichiers
- Règles mécaniques (7 détecteurs)
- Prompt IA monolithique
- Interface basique (1 zone de texte)

### Session 2 — Refonte "Forme / Fond"
- Séparation en 2 zones (lancement + papier/QR)
- `summarize_for_prompt()` pour que Claude ne duplique pas les alertes mécaniques
- Nouveau prompt à mandats multiples (A, B, C, D)
- Heatmap proportionnelle à double bande (friction + incarnation)
- Score d'incarnation (VIF/FLOU/GRIS)
- Chirurgie de phrase (dialog modal)
- Chrono oral avec poids syntaxique
- Verdict global

### Session 3 — Déploiement + UX overhaul
- Déploiement Streamlit Cloud (bridge st.secrets → os.environ)
- Rate limiter (5 appels IA / session)
- GitHub repo créé
- **Feedback utilisateur post-test** : trop d'infos, pas de hiérarchie, phrase-par-phrase écrasant
- Seuils assouplis (20→25 warning, 25→30 error)
- Ajout Mandat E (note de relecture) comme sortie principale
- Restructuration en entonnoir (couche 1 / couche 2 en expander)
- Comparaison avec ChatGPT → expansion de la note en mémo éditorial structuré (3 sections)
- Nettoyage code (variable ai_general inutilisée supprimée)

### Session 4 — Base de savoir v2 (août 2026)
- **Bibliographie en dur** : `knowledge/bibliographie.md` — toutes les sources, classées par tier de fiabilité (A revues à comité de lecture / B données institutionnelles / C écartées : blogs, études marketing type Spotify-Neuro-Insight)
- **`knowledge_base.py` restructuré** : dict `BIBLIO` (id → référence complète + tier) ; `FINDINGS` pointe vers les ids — zéro duplication de sources
- **Corpus francophone intégré** : Morillon/INSERM 2025 (double rythme syllabes/phonèmes), Coupé/CNRS 2019 (39 bits/s), Cahiers de praxématique 2013, Charaudeau, PIAAC 2024 (28% des adultes ≤ niveau 1), Médiatrice Radio France, Cégep de Jonquière 2024, Arcom/IFOP 2025, FALC
- **Nouveau détecteur : anglicismes** (~50 termes + équivalents français, formes conjuguées incluses) — fondé sur la plainte n°1 des auditeurs (Médiatrice)
- **Nouveau détecteur : jargon institutionnel** — fondé sur un sondage interne de compréhension (données dans `sondage_prive.py`, hors git) : warning sous le seuil de compréhension majoritaire, info en zone intermédiaire. Couvre périphrases, métonymies, sigles et jargon judiciaire/économique/européen
- **Prompt IA** : mandat de généralisation — Claude signale le jargon *similaire* non couvert par la liste mesurée ; interdiction de citer une source hors liste

### Session 5 — POC validé, renommage Stabilo (août 2026)
- **Le projet s'appelle désormais Stabilo** (ex-nom banni de partout : code, docs, repo GitHub renommé `Phoceen/stabilo`)
- **Attribution anonymisée** de l'étude de compréhension : citée uniquement comme « étude réalisée en 2023 auprès d'un panel d'auditeurs » dans toute sortie visible
- **Études francophones complètes** ajoutées dans `knowledge/etudes/` (48-53) : Simon 2013, Olsen 2024, EGJLLE 2024, Arcom 2025, Coupé 2019, Morillon 2025 — pour ne plus dépendre des résumés IA

#### REX du POC (retours journalistes)
- ✅ **Très utile** — architecture OK, retours du LLM très pertinents
- ✅ Très bon pour trouver les faits à vérifier et proposer un langage plus visuel pour la radio
- ✅ Structure de réponse validée : 3 niveaux **Urgent / À surveiller / Ce qui fonctionne**
- ❌ **Design pas au point** → piste : dupliquer sur Lovable (interface monitorable : nombre d'utilisateurs, etc.)
- ❌ **Le score « gamifie » inutilement** le processus d'écriture → à retirer probablement
- 🎯 À préserver : repère immédiat des zones en question, retour phrase par phrase pour corriger sans tout refaire, le journaliste garde la main sur le style

#### Backlog v2 (à itérer)
1. **Temps 1** : cahier des charges de la refonte (design, suppression du score, monitoring)
2. **Temps 2** : outil IA pour redesigner la maquette (Lovable — prompt dans `docs/prompt_lovable.md`)
3. Renommer l'URL Streamlit (console Streamlit Cloud)

### Session 6 — Pipeline d'agents (août 2026)
- **L'appel LLM monolithique éclaté en pipeline orchestré** (`agents.py`) : 3 agents en parallèle (forme phrase par phrase / extraction des assertions / cohérence-transitions-sobriété) puis 1 agent de synthèse (le mémo). Orchestration Python déterministe, pas d'« agents » autonomes.
- **Sorties structurées** (`messages.parse` + Pydantic) : les schémas sont validés par l'API — suppression définitive des rustines de parsing JSON tronqué.
- **Modèles par tâche** : jugement éditorial sur `claude-sonnet-5`, extraction des faits sur `claude-haiku-4-5` (~10× moins cher). Contexte scientifique ciblé par agent (~800 tokens au lieu de ~2200).
- **Le mémo est désormais une vraie synthèse** : il reçoit les constats des 3 autres agents et hiérarchise, au lieu d'être généré en même temps.
- **Dégradation propre** : un agent qui échoue laisse son champ vide, l'analyse continue. Quota inchangé : 1 analyse = 1 crédit.
- Nouveaux champs exploitables par l'UI v2 : `transitions` et `sobriete` (listes).
- Testé en réel sur un Q/R : détecte transitions manquantes + sur-dramatisation (les 2 forces de ChatGPT) tout en gardant les forces propres (faits à vérifier, mesures sourcées).

### Session 7 — L'agent écoute (août 2026)
- **Constat** (idée utilisateur, inspirée de STORM, Shao et al., Stanford 2024) : le « côté auditeur » n'était qu'un champ de prompt — Sonnet jouait un auditeur *en lisant* le texte, avec tout le contexte sous les yeux. Un auditeur réel n'a qu'une passe, linéaire, sans retour arrière.
- **Banc d'essai** de 2 variantes sur le Q/R ISS : V1 restitution (1 appel, l'auditeur « a entendu » le papier) vs V2 multi-tours (le texte arrive morceau par morceau, l'agent dit ce qu'il retient sans voir la suite, puis restitue).
- **La V2 gagne** : elle situe le décrochage *au moment où il se produit* — sur l'ISS, au paragraphe exact où l'agent cohérence signalait le pivot manquant et où le mémo plaçait la zone de creux (3 méthodes indépendantes convergentes). Elle montre aussi l'effet de récence en direct (Glanzer & Cunitz appliqué).
- **`agent_ecoute`** intégré en 4ᵉ branche parallèle : persona calibré (une passe, mémoire 3-4 éléments, niveau de lecture moyen — PIAAC), morceaux de 2 unités de souffle, sortie `{restitution, perdus, malentendus, decrochage}` + trace des états intermédiaires.
- **Le mémo ouvre désormais sur la restitution** (« CE QU'IL RESTE APRÈS UNE ÉCOUTE ») — le miroir en premier. Le `regard_auditeur` du phrase-par-phrase est recentré sur la compréhension locale (jargon, sigles, ambiguïtés sonores) pour éviter le doublon.
- **Fusion des assertions** qui se recouvrent (un extrait contenu dans un autre = une seule vérification, notes fusionnées) — en prompt ET en post-traitement Python.
- **Latence inchangée** : 106,6 s (vs 109 s) — l'écoute multi-tours (7 appels séquentiels) tourne dans l'ombre de l'agent forme. Toujours 1 analyse = 1 crédit.
- UI Streamlit : expander « 🎧 Trace d'écoute » sous la note. Pour la v2 Lovable : la trace alimente une courbe d'attention en marge du texte surligné (spec dans `docs/prompt_lovable.md`, mis à jour avec l'architecture complète).

### Session 8 — v2 Lovable : transposition et gouvernance (août 2026)
- Le pipeline à 5 agents transposé dans Lovable (edge functions), validé par **test différentiel** sur le Q/R ISS : convergence sur le décrochage, le pivot manquant et la sobriété ; une divergence assumée (l'attaque jugée bonne parce que la trace d'écoute le montrait — la mesure prime la théorie).
- Bascule de la passerelle IA par défaut de Lovable (Gemini) vers **l'API Anthropic directe** : mêmes modèles que le POC, sorties structurées natives (`output_config.format`), thinking adaptatif préservé, clé dédiée dans les secrets backend.
- Corrections croisées v2 → POC : extraction des faits de causalité/comparaison/tendance, **fusion non destructive** des assertions (rétroportées dans `agents.py` — le POC reste l'implémentation de référence).
- Auth magic link verrouillée au domaine e-mail de la rédaction (trigger en base, tient contre un appel direct à l'API d'auth), quota 5/session, RLS + privilèges Postgres révoqués sur la table des rôles, journal admin **sans aucune colonne de texte** (métadonnées seules, par construction).
- RAG pgvector : 38 études indexées (2 537 passages), bucket privé, manifeste miroir de `bibliographie.md`, un passage max par étude, bonus tier A. Puis remplacement de la vectorisation à l'analyse par un **cache thématique précalculé** (requêtes constantes par thème + socle de thèmes toujours injecté) — la validation a posteriori du choix « bibliographie en dur » du POC.
- **Résultat de gouvernance** : le texte du journaliste n'a qu'une seule destination possible, l'API Anthropic — aucun chemin de code sortant, y compris en mode dégradé (embeddings tiers réservés à l'indexation du corpus public, hors analyse).
- **Recette citations VALIDÉE** (2 textes de test + analyse de contrôle) : attributions conformes, zéro source hors liste, zéro « des études montrent » anonyme. Elle a débusqué deux vrais défauts, corrigés des deux côtés : un liage seuil→sources manquant (le seuil de longueur cité sur Baddeley au lieu de Cowan/Caplan — corrigé v2 ET POC : chaque seuil affiche désormais ses seules sources citables) et un chiffre non traçable dans NOTRE base (le « 48 % des 55-65 ans » de la presse, remplacé par les 51 points d'écart de la note pays archivée). La traçabilité s'applique aussi à nous-mêmes.
- **v2 complète et validée.** Étape suivante : le protocole POC en conditions réelles (5 journalistes, 30 papiers, 4 semaines). Points de veille : quota par session (bascule user_id/jour si contournement), gestion des comptes admin, accroches dramatisées type « séisme » absoutes par le mémo.

### Commits

| Hash | Message |
|------|---------|
| `dcbf9dd` | Initial commit |
| `6c31cde` | Quota IA: 10 → 5 |
| `2cf4ab3` | UX: note de relecture, seuils assouplis, entonnoir |
| `41d10e6` | Note de relecture: memo editorial structuré en 3 sections |
| `f416785` | Supprime variable ai_general inutilisée |

---

## Présentation (deck 12 slides)

Structure validée pour pitcher le projet en interne :

| # | Contenu | Durée |
|---|---------|-------|
| 1 | Titre + accroche | 10s |
| 2 | Le risque shadow IA (levier politique) | 45s |
| 3 | La réalité radio (1 écoute, pas de retour arrière) | 30s |
| 4 | Le vrai problème : la relecture est un goulot (scène 17h42) | 30s |
| 5 | Ce qu'on veut : un tiers neutre, scientifique, traçable | 30s |
| 6 | Ce que le journaliste reçoit (la note + exemple réel) | 45s |
| 7 | Pourquoi c'est fiable (3 piliers science) | 30s |
| 8 | Démo live | 60s |
| 9 | L'outil est / n'est pas (désamorçage) | 20s |
| 10 | Ce qui manque (honnêteté) | 20s |
| 11 | La demande : 4 semaines, 5 journalistes, 30 papiers | 20s |
| 12 | Et après (perspective) | 20s |

**3 messages que la salle doit retenir :**
1. Le risque shadow IA existe déjà, on peut le cadrer
2. L'outil est scientifique pas magique — et il respecte le journaliste
3. La demande est un POC de 4 semaines, pas un engagement à 6 mois

**Annexes prévues :** KPIs + protocole POC, bibliographie complète, architecture + données, risques & mitigations.

---

## Prochaines étapes identifiées (si GO)

- Calibrer les seuils sur des papiers maison (pas encore fait)
- Mesurer l'impact via tests d'écoute (A/B, compréhension 1ère écoute)
- Protocole POC : 4 semaines, 5 journalistes, 30 papiers
- Gouvernance : où transitent les textes, conservation, logs, accès
- À terme : RAG sur les études (remplacer knowledge_base.py statique)
- Extension possible : autres rédactions, règles éditoriales internes
