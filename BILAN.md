# La mère Michu — Bilan & Archives

## Résumé du projet

**Outil de relecture pour l'écriture radio, fondé sur la science cognitive.**

Aider les journalistes radio à écrire des textes qui passent mieux à l'oreille. Pas un correcteur orthographique, pas un réécriveur automatique — un relecteur exigeant qui pointe ce qui ne fonctionne pas à l'oral et explique *pourquoi*, études scientifiques à l'appui.

- **Repo** : https://github.com/Phoceen/la-mere-michu
- **Live** : https://la-mere-michu.streamlit.app/
- **Stack** : Streamlit + Claude API (Sonnet 4.5) + Python 3.12
- **Quota** : 5 appels IA max par session

---

## Architecture

4 fichiers, ~1200 lignes :

| Fichier | Rôle | Lignes |
|---------|------|--------|
| `knowledge_base.py` | Base de connaissances : BIBLIO (35 sources tierées A/B) + FINDINGS + anglicismes + jargon mesuré | ~330 |
| `rules.py` | Moteur de règles mécaniques (9 détecteurs, zéro IA) | ~290 |
| `ai_analyzer.py` | Prompt et appel Claude (5 mandats) | ~222 |
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

**Étage 2 — Analyse IA** (ai_analyzer.py → Claude) : reçoit le texte *déjà annoté* par l'étage 1.
- Mandat A : Forme orale (rythme, souffle, fluidité)
- Mandat D : Incarnation (VIF / FLOU / GRIS)
- Mandat E : Note de relecture (urgent / à surveiller / ce qui fonctionne)
- Mandat B : Repérage d'assertions (chiffres, noms, dates, faits)
- Mandat C : Cohérence lancement ↔ papier

### Sortie (entonnoir)

- **Couche 1** : Verdict global → Note de relecture → Cohérence → Assertions à vérifier
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
- GitHub repo créé (Phoceen/la-mere-michu)
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
