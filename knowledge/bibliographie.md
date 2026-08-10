# Bibliographie — La mère Michu

Bibliographie de référence de l'outil. Chaque source est classée par **tier de fiabilité** :

| Tier | Critère | Usage dans l'outil |
|------|---------|--------------------|
| **A** | Revue à comité de lecture ou ouvrage académique | Citable dans les analyses (règles + IA) |
| **B** | Donnée institutionnelle sérieuse (OCDE, Arcom, médiation, sondage n>1000) | Citable dans les analyses (règles + IA) |
| **C** | Blog, tribune, étude marketing financée par un acteur intéressé | **Jamais citée par l'outil.** Contexte de veille uniquement |

Les sources A et B sont encodées dans `knowledge_base.py` (dict `BIBLIO`) et alimentent les règles mécaniques et le prompt IA. Les PDF archivés sont dans `knowledge/etudes/`.

---

## Tier A — Études publiées en revue à comité de lecture

### Mémoire et charge cognitive

- **Miller, G. A. (1956).** *The Magical Number Seven, Plus or Minus Two.* Psychological Review. — Estimation initiale de la capacité de mémoire de travail (7±2), révisée à la baisse depuis. 📄 `etudes/01`
- **Cowan, N. (2001).** *The Magical Number 4 in Short-Term Memory.* Behavioral and Brain Sciences. — Capacité réelle : 3 à 5 chunks. Fonde le seuil de longueur de phrase. 📄 `etudes/03`
- **Baddeley, A. & Hitch, G. (1974-2000).** *Modèle de mémoire de travail.* — La boucle phonologique retient l'info auditive ~2 secondes. 📄 `etudes/07`
- **Sweller, J. (1988).** *Cognitive Load Theory.* Cognitive Science. — La surcharge extrinsèque empêche le transfert en mémoire à long terme. 📄 `etudes/29-30`
- **Baker et al. (2018).** *Cognitive Load Affects Numerical and Temporal Judgments.* Frontiers in Psychology. — Sous charge, les chiffres sont sous-estimés et mal retenus. Fonde le seuil « max 2 chiffres/phrase ». 📄 `etudes/31`
- **Glanzer, M. & Cunitz, A. (1966).** *Two Storage Mechanisms in Free Recall.* — Effet de position sérielle : primauté + récence, creux au milieu.

### Concret vs abstrait, imagerie mentale

- **Paivio, A.** *Théorie du double codage.* — Les mots concrets activent deux voies de rappel (verbale + visuelle), les abstraits une seule. Fonde le score VIF/FLOU/GRIS.
- **Binder et al. (2009).** *Neural representation of abstract and concrete concepts.* Human Brain Mapping. — Les mots concrets sont reconnus plus vite et mieux mémorisés. 📄 `etudes/34-35`

### Syntaxe et complexité

- **Caplan, D. & Waters, G. (1999).** *Verbal working memory and sentence comprehension.* Behavioral and Brain Sciences. — Les phrases complexes sont plus lentes à comprendre à l'oral ; les faibles capacités de mémoire de travail sont les plus pénalisées.
- **Fedorenko et al. (2024).** *Language and communication.* Nature. — Le juste niveau de complexité et d'inattendu active le cerveau. 📄 `etudes/36`

### Attention et vagabondage mental

- **Kopp, D'Mello & Mills (2015).** Frontiers in Psychology. — L'écoute passive produit 32-43% de vagabondage mental. 📄 `etudes/13`
- **Murray et al. (2023).** Scientific Reports. — Vagabondage fréquent → rappel plus faible, immédiatement et à une semaine. 📄 `etudes/15`
- **Soemer et al. (2023).** *Mind wandering and noise.* 📄 `etudes/14`
- **Wilson, K. & Korn, J. (2007).** *Attention during lectures.* 📄 `etudes/08`
- **Wolpaw et al. (2022).** Western J. Emergency Medicine. — Attention EEG pendant un podcast ≈ pendant la lecture. 📄 `etudes/37`

### Prosodie et voix (radio)

- **Rodero, E. (2012).** *See It on a Radio Story.* Communication Research. — Effets et plans sonores augmentent imagerie mentale et attention. 📄 `etudes/21`
- **Rodero, E. (2015).** *Prosody and coherence.* 📄 `etudes/23`
- **Rodero, E. (2017).** *Pitch Range Variations Improve Cognitive Processing.* Human Communication Research. — Variations de hauteur tonale : +15-25% d'attention. 📄 `etudes/24`
- **Rodero, E. (2022).** *Voice pitch and gestures.* 📄 `etudes/26`
- **Rodero, E. (2023).** *Best Prosody for News.* Communication Research. — Style narratif (~175 mots/min) > style broadcast (~200 mots/min). 📄 `etudes/27`
- **Simon, A. C., Auchlin, A. & Goldman, J.-P. (2013).** *Tendances prosodiques de la parole radiophonique.* Cahiers de praxématique n°61. — Prosodie de la parole radio **en français** ; l'accélération + montée mélodique comme signal d'alerte attentionnelle. 🇫🇷
- **Stephens et al. (2010).** *Neural coupling speaker-listener.* 📄 `etudes/17`
- **Cuadrado et al. (2020).** *Arousing sound.* 📄 `etudes/20`

### Vitesse de traitement de la parole

- **Rayner et al. (2008).** Psychophysiology. — Lecture : 200-400 mots/min ; compréhension orale : 125-160 mots/min.
- **Leroy et al. (2019).** JAMIA. — Compréhension texte ≈ audio, rétention légèrement inférieure à l'écoute.
- **Coupé, Oh, Dediu & Pellegrino (2019).** *Different languages, similar encoding efficiency.* Science Advances (CNRS / Univ. Lyon 2). — Toutes les langues transmettent ~39 bits/s : il existe un débit optimal de traitement cérébral. 🇫🇷
- **Morillon et al. (2025).** *Décodage cérébral de la parole.* Science Advances (INSERM / Aix-Marseille Université). — Le cortex auditif suit en parallèle le rythme des syllabes et celui des phonèmes (vérifié dans 17 langues dont le français). Débit trop rapide ou articulation imprécise dégradent la compréhension. 🇫🇷
- **Étude time-compressed audio.** 📄 `etudes/40`

### Formats audio et engagement

- **Brain Sciences / MDPI (2024).** *Radio, Podcasts, and Music Streaming — An EEG and Physiological Analysis.* — Chaque format audio engage différemment attention, mémoire, émotion.

### Multimédia et redondance

- **Mayer, R.** *Principes de redondance et de cohérence.* Multimedia Learning. — Doubler narration + texte surcharge ; éliminer le non-essentiel améliore l'apprentissage. 📄 `etudes/32-33`

### Linguistique du discours radiophonique 🇫🇷

- **Cahiers de praxématique n°61 (2013).** *Le discours radiophonique en pratiques.* Praxiling, Université Paul-Valéry Montpellier. — Première synthèse académique francophone : syntaxe de la phrase radio, prosodie, genres. Constat clé : les études de **réception** par les auditeurs sont quasi inexistantes.
- **Charaudeau, P. (1984-).** *Le discours d'information médiatique.* Université Sorbonne Paris-Nord. — Théorie du « contrat de communication » : captation, crédibilisation, information. La clarté est une clause implicite du contrat avec l'auditeur.
- **EGJLLE (2024).** *L'influence des anglicismes et emprunts étrangers sur le français.* — L'excès d'anglicismes non intégrés entrave la compréhension, surtout entre générations. 🇫🇷

---

## Tier B — Données institutionnelles

- **Sondage de compréhension du vocabulaire journalistique (2025).** ⚠️ *Document interne, non versionné.* Données et enseignements encodés dans `sondage_prive.py` (hors git, disponible en local uniquement) — alimente le détecteur de jargon.
- **OCDE — PIAAC (2024).** *Évaluation internationale des compétences des adultes.* — 28% des adultes français au niveau ≤1 en littératie (+6 pts vs 2012) ; 48% des 55-65 ans en difficulté. Difficultés écrit/oral fortement corrélées. 🇫🇷
- **Médiatrice de Radio France (2022-2026).** Comptes rendus des courriers d'auditeurs sur la langue. — Plainte n°1 : anglicismes non nécessaires (casting, think tank, storytelling, impacter...) ; puis appauvrissement lexical et relâchement syntaxique. → fonde la liste `ANGLICISMES` 🇫🇷
- **Olsen, M.-J. — Cégep de Jonquière (2024).** *La langue dans les radios québécoises.* 40 matinales, 134 grilles d'écoute, 65 professionnels. — Anglicismes dans 40/40 émissions ; motif n°1 : « se rapprocher de l'auditeur » ; 60% des pros perçoivent une dégradation.
- **Arcom / IFOP (2025).** *Les Français et la radio.* — 83% de confiance dans l'info radio ; 73% d'écoute hebdomadaire. La confiance est un capital lié à la clarté. 🇫🇷
- **CNSA / Vivre FM (2023).** *« Tout compris ! »*, première émission radio en FALC. — Référence d'accessibilité maximale : phrases ≤ 12 mots, vocabulaire courant, ni jargon ni métaphore. 🇫🇷
- **CSA (2005).** *Recommandation relative à l'emploi de la langue française.* — Cadre réglementaire (loi Toubon) : les traductions doivent être « aussi audibles ou intelligibles » que l'original. 🇫🇷
- **NPR (données d'audience).** — Décision de l'auditeur en 18 mots ; 40% d'attrition en 7 minutes.
- **BBC Audio:Activated (2019).** — Écoute en activité : +18% engagement, +40% intensité émotionnelle, +22% encodage mémoire. 📄 `etudes/39`
- **Trenaman — BBC.** 📄 `etudes/10`

---

## Tier C — Sources écartées (jamais citées par l'outil)

Documentées ici par transparence ; exclues de `knowledge_base.py` car non vérifiables, intéressées ou non académiques.

- **Spotify / Neuro-Insight — « Sonic Science » (2021-2023).** Étude marketing financée par un acteur du secteur, conçue pour valoriser l'audio digital vs la radio linéaire. Conflit d'intérêts évident.
- **We Are COM (2026).** *Neurosciences et communication.* Blog de communicants — synthèse de seconde main, sans méthode.
- **Parody, E. / Minted (2025).** *La chute des capacités de lecture.* Tribune d'opinion — les chiffres qu'elle agrège (PISA, PIAAC) sont à citer via leurs sources primaires (tier B).

---

## Lacunes documentées de la recherche (angles morts)

1. Aucune étude nationale publiée ne mesure la compréhension des auditeurs face au vocabulaire des journalistes radio français.
2. Pas d'indice de lisibilité systématique des scripts radio français (le Gunning-Fog n'a été appliqué qu'à la presse écrite).
3. Les études de réception radiophonique restent rares (constat des Cahiers de praxématique, 2013).
4. Aucune étude neuro-cognitive franco-française ne mesure l'encodage de discours journalistiques selon leur complexité lexicale.

## Pistes si le POC est validé

- Adapter la méthodologie québécoise (Olsen 2024) à un corpus d'émissions françaises.
- Croiser PIAAC et scores de compréhension d'extraits radio réels par âge et CSP.
- Co-construire un protocole avec l'INSERM (équipe Morillon) ou le LPL d'Aix-en-Provence.
- Corpus INA + TAL pour mesurer l'évolution de la complexité du discours radio dans le temps.

---

*Convention : 🇫🇷 = donnée portant spécifiquement sur le français ou la France. 📄 `etudes/NN` = PDF archivé dans `knowledge/etudes/`.*
