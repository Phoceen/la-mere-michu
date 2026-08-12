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
- Résultat : un mémo de rédacteur en chef en 4 sections, dans cet ordre
  (texte rédigé, pas des bullet points secs) :
  1. 🎧 CE QU'IL RESTE APRÈS UNE ÉCOUTE — la restitution d'un auditeur simulé qui n'a
     entendu le papier qu'une seule fois : ce qui survit, ce qui s'est perdu, l'écart
     avec l'intention. C'est le miroir, il s'affiche en premier.
  2. 🔴 LE PLUS URGENT — ce qui empêche le texte de passer à l'antenne
  3. 🟡 À SURVEILLER — ce qui affaiblit sans bloquer
  4. 🟢 CE QUI FONCTIONNE — ce qu'il faut garder, cité précisément
- Sous le mémo : le texte du journaliste reproduit avec les zones à revoir surlignées
  (repère immédiat, au survol : l'explication + la source scientifique).
- En marge du texte surligné : la « trace d'écoute » — l'état mental de l'auditeur
  simulé à chaque étape du texte (« là, ça devient flou », « ça boucle avec le
  début »), avec un marqueur visuel au point exact de décrochage. C'est une courbe
  d'attention le long du papier.
- Clic sur une phrase surlignée → panneau latéral « phrase par phrase » : le problème,
  la direction de correction, la source. Le journaliste corrige SON texte, l'outil
  ne remplace jamais sa formulation.
- Une liste « Faits à vérifier avant antenne » (chiffres, noms, dates, citations
  relevés — une seule entrée par passage, jamais deux vérifications qui se recouvrent).

### Écran admin — Monitoring (accès restreint par rôle)
- Nombre d'utilisateurs, nombre d'analyses par jour/semaine, quota d'appels IA
  par utilisateur (5 par session), coût API estimé.
- Aucune conservation du contenu des textes analysés au-delà de la session
  (confidentialité rédactionnelle) : ne stocker que des métadonnées (horodatage,
  compteurs, longueur du texte).

## Backend — pipeline d'agents (pas un appel LLM monolithique)
- Auth simple (magic link email) + rôles user/admin.
- Appels à l'API Claude d'Anthropic via une edge function : la clé API reste côté
  serveur, jamais dans le client. Sorties structurées (structured outputs de l'API
  Anthropic) : chaque agent renvoie un JSON validé par schéma, pas de parsing manuel.
- Une analyse = UN pipeline orchestré de 5 agents (mais 1 seul « crédit » côté
  utilisateur, le quota compte l'action, pas la tuyauterie) :
  1. Règles mécaniques déterministes côté serveur, sans IA, gratuites (longueur de
     phrase, chiffres, jargon, anglicismes, voix passive...) — leurs alertes sont
     transmises aux agents pour qu'ils ne les répètent pas.
  En parallèle :
  2. Agent FORME (claude-sonnet-5) — phrase par phrase : regard rédacteur en chef
     (rythme, souffle, oralité) + incarnation (image mentale VIF/FLOU/GRIS).
  3. Agent ASSERTIONS (claude-haiku-4-5, extraction pure) — liste les faits à
     vérifier ; fusion serveur des assertions dont les extraits se recouvrent.
  4. Agent COHÉRENCE (claude-sonnet-5) — cohérence lancement/papier, transitions
     manquantes (sauts sans phrase pivot), sobriété (sur-dramatisation).
  5. Agent ÉCOUTE (claude-sonnet-5, multi-tours, inspiré de STORM, Stanford 2024) —
     un auditeur simulé calibré (une seule passe, mémoire 3-4 éléments, niveau de
     lecture moyen) reçoit le texte MORCEAU PAR MORCEAU (2 unités de souffle) et dit
     ce qu'il retient à chaque étape SANS voir la suite ; à la fin il restitue :
     {restitution, perdus[], malentendus[], decrochage} + la trace des états
     intermédiaires. C'est cette trace qui alimente la courbe d'attention de l'UI.
  Puis :
  6. Agent MÉMO (claude-sonnet-5) — rédige la note de relecture en SYNTHÈSE des
     constats précédents (il ne ré-analyse pas), en OUVRANT sur la restitution
     de l'agent écoute.
- Le prompt système de chaque agent impose : ton de rédac chef bienveillant mais
  exigeant, tutoiement, jamais de réécriture complète, citations uniquement issues
  des sources fournies par le RAG (jamais de source inventée).
- Règle métier ABSOLUE, dans tous les prompts : les journalistes radio ponctuent
  avec des marques de respiration (« / », « // », « ... », retours à la ligne) —
  ce n'est JAMAIS une faute. Pas de correction d'orthographe (ça ne s'entend pas
  à l'antenne), sauf coquille qui fait trébucher la lecture à voix haute.
- Le découpage en phrases côté serveur traite ces marques comme des frontières
  d'unités de souffle (en préservant « km/h » et autres barres internes).
- Les repères de diffusion sonore — « bob », « son », « extrait », numérotés ou
  non — sont des indications techniques, pas du texte lu : exclus des règles
  mécaniques, et consigne aux agents de ne jamais les signaler.

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
- [ ] `agents.py` EN ENTIER (sauf aucune donnée sensible dedans, vérifié) — c'est le
      cœur métier : les 5 agents, leurs prompts système, les schémas de sortie,
      l'orchestration parallèle et la fusion des assertions. Lovable doit le
      transposer en edge functions, pas le réinventer.
- [ ] La regex de découpage en unités de souffle de `rules.py` (`split_sentences`)
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
   « étude réalisée en 2025 auprès d'un panel d'auditeurs ».
3. La clé API Anthropic : dans les secrets/env du backend Lovable, jamais en dur.
4. Les PDF de `knowledge/etudes/` peuvent être téléversés pour le RAG **sauf**
   tout document interne. En cas de doute : demande-toi si le doc est trouvable
   sur Google. Non → il ne part pas dans Lovable.
5. Le corpus téléversé sur Lovable/Supabase sort de ta machine : vérifie que les
   PDF d'études sous droits (payants) ne sont pas re-exposés publiquement par l'app
   (index admin protégé par rôle, pas de lien de téléchargement public).
```
