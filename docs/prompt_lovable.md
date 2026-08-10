# Prompt Lovable — Stabilo v2

> Copier-coller le bloc ci-dessous comme premier prompt dans Lovable.
> Puis itérer écran par écran (Lovable travaille mieux par petites étapes).
>
> ⚠️ **Avant de commencer, lis les consignes de sécurité en bas de ce fichier.**

---

## Le prompt

```
Je veux construire « Stabilo », un outil de relecture pour l'écriture radio destiné
aux journalistes d'une rédaction. Ce n'est PAS un correcteur d'orthographe ni un
réécriveur : c'est un relecteur exigeant qui pointe ce qui ne fonctionne pas À L'ORAL
et explique pourquoi, études scientifiques à l'appui.

## Principes produit (non négociables)
1. La science d'abord : chaque alerte s'appuie sur une étude citée (auteur + année).
2. Des directions, jamais de réécriture imposée : le journaliste garde la main sur son style.
3. L'entonnoir : d'abord une note de relecture globale, le détail phrase par phrase en option.
4. PAS de score ni de note chiffrée globale : aucune gamification du processus d'écriture.
   Les problèmes sont montrés par des repères visuels de zones, pas par des points.

## Écrans

### Écran principal — Relecture
- Deux zones de saisie : « Lancement » (accroche courte) et « Papier / Q-R » (le corps).
- Bouton « Relire mon texte ».
- Résultat en 3 niveaux, dans cet ordre, présenté comme un mémo de rédacteur en chef
  (texte rédigé, pas des bullet points secs) :
  1. 🔴 LE PLUS URGENT — ce qui empêche le texte de passer à l'antenne
  2. 🟡 À SURVEILLER — ce qui affaiblit sans bloquer
  3. 🟢 CE QUI FONCTIONNE — ce qu'il faut garder, cité précisément
- Sous le mémo : le texte du journaliste reproduit avec les zones à revoir surlignées
  (repère immédiat, au survol : l'explication + la source scientifique).
- Clic sur une phrase surlignée → panneau latéral « phrase par phrase » : le problème,
  la direction de correction, la source. Le journaliste corrige SON texte, l'outil
  ne remplace jamais sa formulation.
- Une liste « Faits à vérifier avant antenne » (chiffres, noms, dates, citations relevés).

### Écran admin — Monitoring (accès restreint par rôle)
- Nombre d'utilisateurs, nombre d'analyses par jour/semaine, quota d'appels IA
  par utilisateur (5 par session), coût API estimé.
- Aucune conservation du contenu des textes analysés au-delà de la session
  (confidentialité rédactionnelle) : ne stocker que des métadonnées (horodatage,
  compteurs, longueur du texte).

## Backend
- Auth simple (magic link email) + rôles user/admin.
- Appel à l'API Claude d'Anthropic (modèle claude-sonnet-5) via une edge function :
  la clé API reste côté serveur, jamais dans le client.
- Le prompt système impose : ton de rédac chef bienveillant mais exigeant, tutoiement,
  jamais de réécriture complète, citations uniquement issues des sources fournies
  par le RAG (jamais de source inventée), réponse JSON structurée
  {memo_urgent, memo_surveiller, memo_fonctionne, phrases[], faits_a_verifier[]}.

## RAG sur la base de connaissances
- Je téléverserai un corpus d'études scientifiques (PDF, ~30 documents : sciences
  cognitives, prosodie, littératie) et une bibliographie structurée en markdown
  avec des tiers de fiabilité (A = revue à comité de lecture, B = donnée
  institutionnelle).
- Pipeline : extraction texte des PDF → découpage en chunks (~800 tokens, avec
  métadonnées : titre, auteurs, année, tier) → embeddings → base vectorielle
  (Supabase pgvector).
- À chaque analyse : les passages les plus pertinents pour le texte soumis sont
  récupérés (top 8) et injectés dans le prompt de Claude avec leurs métadonnées.
- Règle stricte : Claude ne peut citer QUE les sources récupérées, avec auteur + année.
  Si le RAG ne renvoie rien de pertinent sur un point, l'analyse le dit sans citer.
- Prévois un écran admin « Corpus » : liste des documents indexés, ajout/suppression,
  ré-indexation.

Commence par l'écran principal de relecture avec des données mockées (pas encore
d'appel API), pour valider le design : mémo 3 niveaux + surlignage des zones +
panneau phrase par phrase. Design sobre, typographie lisible, ambiance salle de
rédaction — pas de gadgets.
```

---

## 📦 Checklist — fichiers à donner à Lovable

### ✅ À téléverser (corpus RAG)
- [ ] Les PDF d'études de `knowledge/etudes/` (01 à 54) — **sauf tout document interne**
- [ ] `knowledge/bibliographie.md` — donne à l'app les métadonnées (tiers A/B, auteurs, années) pour étiqueter les chunks
- [ ] `knowledge/README.md`

### 📋 À copier-coller dans le chat Lovable (référence de construction)
- [ ] Le prompt système d'`ai_analyzer.py` (les 5 mandats) — c'est le cœur métier à reproduire
- [ ] Le dict `ANGLICISMES` de `knowledge_base.py` (liste + équivalents français)
- [ ] Les seuils de `FINDINGS` dans `knowledge_base.py` (25/30 mots, 2 chiffres, etc.)
- [ ] La section « REX du POC » de `BILAN.md` (session 5) — pour que Lovable comprenne le pourquoi des choix design

### 🚫 À ne JAMAIS donner à Lovable
- [ ] `sondage_prive.py` et l'étude interne de compréhension des termes (PDF)
- [ ] `.env` / clé API Anthropic (à saisir uniquement dans les secrets backend de Lovable)
- [ ] Tout document estampillé interne ou non trouvable publiquement sur Google

---

## ⚠️ Consignes de sécurité (à respecter, hors prompt)

1. **NE JAMAIS téléverser dans Lovable** l'étude interne de compréhension des termes
   ni le fichier `sondage_prive.py`. Si tu veux le détecteur de jargon
   dans la v2 Lovable, on injectera les données par une variable d'environnement
   serveur — on fera ça ensemble, pas via upload.
2. Dans toute sortie visible de l'app, cette étude est citée uniquement comme :
   « étude réalisée en 2023 auprès d'un panel d'auditeurs ».
3. La clé API Anthropic : dans les secrets/env du backend Lovable, jamais en dur.
4. Les PDF de `knowledge/etudes/` peuvent être téléversés pour le RAG **sauf**
   tout document interne. En cas de doute : demande-toi si le doc est trouvable
   sur Google. Non → il ne part pas dans Lovable.
5. Le corpus téléversé sur Lovable/Supabase sort de ta machine : vérifie que les
   PDF d'études sous droits (payants) ne sont pas re-exposés publiquement par l'app
   (index admin protégé par rôle, pas de lien de téléchargement public).
```
