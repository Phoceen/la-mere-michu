import os
import re
import unicodedata
import streamlit as st
import streamlit.components.v1 as components

# Bridge Streamlit Cloud secrets → os.environ (avant import ai_analyzer)
if "ANTHROPIC_API_KEY" not in os.environ:
    try:
        os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass

from rules import analyze_text, summarize_for_prompt
from ai_analyzer import analyze_with_ai, deep_analyze_phrase, get_client
from knowledge_base import FINDINGS

DEBIT_OPTIMAL = FINDINGS["prosodie"]["debit_optimal_mots_min"]  # 175 mots/min
MAX_AI_CALLS = 5  # Quota par session (analyses + chirurgies)


def _word_count(text):
    if not text or not text.strip():
        return 0
    return len(text.split())


def _number_oral_words(num_str):
    """Mots oraux quand on lit un nombre en français.

    '12457' → 'douze mille quatre cent cinquante-sept' ≈ 5 mots oraux.
    Heuristique : ~1 mot oral par chiffre, plafonné à 7.
    """
    cleaned = re.sub(r"[\s.,\u00a0]", "", num_str)
    if not cleaned.isdigit():
        return 1
    n = len(cleaned)
    if n <= 1:
        return 1
    if n == 2:
        return 2
    return min(n, 7)


def _estimate_oral_seconds(text):
    """Durée orale estimée (secondes) avec poids syntaxique.

    - Chiffres → expansés en mots oraux (ex: '12457' = 5 mots au lieu de 1)
    - Sigles → chaque lettre épelée (ex: 'SNCF' = 4 mots oraux au lieu de 1)
    """
    if not text or not text.strip():
        return 0
    oral_words = 0
    for token in text.split():
        clean = token.strip(".,;:!?()\"'«»—–")
        if re.match(r"^\d[\d.,]*$", clean):
            oral_words += _number_oral_words(clean)
        elif re.match(r"^[A-Z]{2,}$", clean):
            oral_words += len(clean)
        else:
            oral_words += 1
    return round(oral_words / DEBIT_OPTIMAL * 60)


def _format_duration(seconds):
    """Formate une durée en format radio : 1'24\"."""
    if not seconds or seconds <= 0:
        return "—"
    seconds = int(round(seconds))
    m, s = divmod(seconds, 60)
    if m:
        return f"{m}'{s:02d}\""
    return f'{s}"'

st.set_page_config(page_title="La mère Michu", page_icon="🎙️", layout="wide")

st.markdown("""
<div style="text-align:center; margin-bottom:1.5rem;">
<h1 style="margin-bottom:0.2rem;">🎙️ La mère Michu</h1>
<p style="opacity:0.6;"><b style="color:#ef4444;">Ceci est un outil de relecture !</b> Dans un premier temps, il va effectuer une relecture dites "mécanique"<br>
            en <b style="color:#ef4444;">se basant sur une trentaine d'étude cognitive et neurologique</b> traitant de l'écoute et de l'attention.<br>
            <b style="color:#ef4444;">Il va appliquer les savoirs issus de ces études scientifiques !</b> Dans un second temps, il enverra le texte annoté à Claude. Ce dernier effectuera<br>
            une relecture en deux temps : <b>d'abord comme un auditeur lambda</b> et dans un second temps comme un rédacteur chef. <b style="color:#ef4444;">Il ne fact-check pas !</b><br>
            <b style="color:#ef4444;">Il alerte</b> sur les chiffres à revérifier, les tournures à regarder, etc. <b style="color:#ef4444;">Il ne fait pas de proposition !</b></p>
</div>""", unsafe_allow_html=True)

has_api = get_client() is not None
if not has_api:
    st.warning("Clé API non configurée. Créez un `.env` avec `ANTHROPIC_API_KEY` pour activer l'analyse IA.")

use_ai = st.toggle("Analyse IA (Claude)", value=has_api, disabled=not has_api)

# --- Zone 1 : Lancement ---
st.markdown("#### Lancement")
lancement_text = st.text_area(
    "Lancement (optionnel)",
    height=120,
    placeholder="Collez votre lancement ici...",
    key="lancement",
    label_visibility="collapsed",
)
_wc_l = _word_count(lancement_text)
_dur_l = _estimate_oral_seconds(lancement_text)
if _wc_l:
    st.caption(f"⏱️ {_wc_l} mots · ~{_format_duration(_dur_l)}")

# --- Zone 2 : Papier / QR ---
papier_type = st.radio("Type", ["Papier", "Q/R avec relances"], horizontal=True, label_visibility="collapsed")
papier_text = st.text_area(
    f"{papier_type} (optionnel)",
    height=200,
    placeholder=f"Collez votre {papier_type.lower()} ici...",
    key="papier",
    label_visibility="collapsed",
)
_wc_p = _word_count(papier_text)
_dur_p = _estimate_oral_seconds(papier_text)
if _wc_p:
    st.caption(f"⏱️ {_wc_p} mots · ~{_format_duration(_dur_p)}")

# --- Chrono ---
_dur_total = _dur_l + _dur_p
_wc_total = _wc_l + _wc_p

col_chrono, col_target = st.columns([3, 1])
with col_target:
    target_sec = st.number_input(
        "Format imparti (sec)",
        min_value=0, max_value=600, value=0, step=5,
        help="0 = pas de limite. Ex: 75 = 1'15\", 90 = 1'30\"",
    )
    if target_sec:
        st.caption(f"= {_format_duration(target_sec)}")

with col_chrono:
    if _wc_total:
        if target_sec > 0:
            if _dur_total <= target_sec:
                color, icon = "#10b981", "✅"
                delta_msg = f"marge de {_format_duration(target_sec - _dur_total)}"
            elif _dur_total <= target_sec * 1.1:
                color, icon = "#f59e0b", "⚠️"
                delta_msg = f"+{_format_duration(_dur_total - target_sec)} de dépassement"
            else:
                color, icon = "#ef4444", "🔴"
                delta_msg = f"+{_format_duration(_dur_total - target_sec)} de dépassement"
        else:
            color, icon = "#aaa", "📻"
            delta_msg = ""

        target_str = f" / {_format_duration(target_sec)}" if target_sec > 0 else ""
        delta_html = f'<span style="font-size:0.85rem;margin-left:8px;">{delta_msg}</span>' if delta_msg else ""

        bar_html = ""
        if target_sec > 0:
            pct = min(_dur_total / target_sec * 100, 100)
            bar_html = (
                f'<div style="height:6px;background:#333;border-radius:3px;margin:8px 0 4px;">'
                f'<div style="width:{pct:.0f}%;height:100%;background:{color};border-radius:3px;"></div>'
                f'</div>'
            )

        st.markdown(
            f'<div style="padding:10px 16px;border:1px solid {color}40;border-radius:10px;">'
            f'<div style="font-size:1.1rem;color:{color};">'
            f'{icon} <b>{_format_duration(_dur_total)}</b>{target_str}{delta_html}'
            f'</div>'
            f'{bar_html}'
            f'<div style="font-size:0.7rem;color:#666;margin-top:2px;">'
            f'{_wc_total} mots · poids syntaxique inclus · {DEBIT_OPTIMAL} mots/min (Rodero, 2023)</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

analyze_btn = st.button("Analyser", type="primary", use_container_width=True)


# --- Fonctions utilitaires ---

def normalize(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u00a0", " ")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def match_ai(sentence_id, sentence_text, ai_phrases):
    # Matching par ID (prioritaire)
    for p in ai_phrases:
        if p.get("id") == sentence_id:
            return p
    # Fallback textuel (si l'IA n'a pas renvoyé l'ID)
    norm = normalize(sentence_text)
    for p in ai_phrases:
        if normalize(p.get("original", "")) == norm:
            return p
    for p in ai_phrases:
        if normalize(p.get("original", ""))[:30] == norm[:30]:
            return p
    return None


def calculate_friction_score(alerts, ai_verdict):
    score = 0
    for a in alerts:
        if a.severity == "error": score += 3.0
        elif a.severity == "warning": score += 1.5
        elif a.severity == "info": score += 0.5
    ai_weights = {"probleme": 2.5, "a_verifier": 1.0, "ok": 0}
    score += ai_weights.get(ai_verdict, 0)
    return score


INC_COLORS = {"VIF": "#10b981", "FLOU": "#f59e0b", "GRIS": "#ef4444"}


def _friction_color(score):
    if score <= 1.5:
        return "#10b981"
    if score <= 3.5:
        return "#f59e0b"
    return "#ef4444"


def render_heatmap(sentences_data):
    """Heatmap proportionnelle à double bande (friction + incarnation).

    sentences_data: list of dicts with keys:
        words: int, friction_score: float, inc_label: str|None
    """
    if not sentences_data:
        return
    total_words = sum(s["words"] for s in sentences_data)
    if total_words == 0:
        return

    sep = "1px solid rgba(128,128,128,0.25)"

    # Friction band (top)
    friction_segs = ""
    for s in sentences_data:
        w = max(s["words"] / total_words * 100, 0.5)
        friction_segs += (
            f'<div style="width:{w:.2f}%;min-width:4px;height:14px;'
            f'background:{_friction_color(s["friction_score"])};'
            f'border-right:{sep};"></div>'
        )

    # Incarnation band (bottom) — only if AI data exists
    has_ai = any(s.get("inc_label") for s in sentences_data)
    inc_html = ""
    if has_ai:
        inc_segs = ""
        for s in sentences_data:
            w = max(s["words"] / total_words * 100, 0.5)
            color = INC_COLORS.get(s.get("inc_label", ""), "rgba(128,128,128,0.1)")
            inc_segs += (
                f'<div style="width:{w:.2f}%;min-width:4px;height:6px;'
                f'background:{color};border-right:{sep};"></div>'
            )
        inc_html = f'<div style="display:flex;width:100%;">{inc_segs}</div>'

    st.markdown(
        f'<div style="display:flex;flex-direction:column;width:100%;border-radius:4px;'
        f'overflow:hidden;border:1px solid rgba(128,128,128,0.2);">'
        f'<div style="display:flex;width:100%;">{friction_segs}</div>'
        f'{inc_html}'
        f'</div>'
        f'<div style="display:flex;justify-content:space-between;font-size:0.65rem;'
        f'color:#888;margin:4px 0 8px;">'
        f'<span>Début</span><span>Milieu</span><span>Fin</span></div>',
        unsafe_allow_html=True,
    )


def build_html(results, ai_phrases, prefix=""):
    issues = []
    spans = ""

    for i, r in enumerate(results):
        messages = []
        for a in r.alerts:
            msg = f"⚙️ {a.rule} — {a.message}"
            if a.source:
                msg += f' <span style="color:#8b5cf6;font-size:0.75rem;">📚 {a.source}</span>'
            messages.append(msg)
        severity = r.severity

        sentence_id = f"#{prefix}{i + 1}"
        ai_match = match_ai(sentence_id, r.sentence, ai_phrases)
        if ai_match:
            verdict = ai_match.get("verdict", "ok")
            if verdict == "probleme":
                severity = "error"
            elif verdict == "a_verifier" and severity in ("ok", "info"):
                severity = "warning"
            # Double regard
            redac = ai_match.get("regard_redac", "") or ai_match.get("commentaire", "")
            auditeur = ai_match.get("regard_auditeur", "")
            if redac:
                messages.append(f"📰 <b>Rédac chef :</b> {redac}")
            if auditeur:
                messages.append(f"👂 <b>Auditeur :</b> {auditeur}")
            suggestion = ai_match.get("suggestion")
            if suggestion and suggestion not in ("null", "None", None):
                messages.append(f"✏️ {suggestion}")
            # Score d'incarnation (image mentale)
            incarnation = ai_match.get("score_incarnation", "")
            incarnation_map = {
                "VIF": ("✨", "#10b981", "Image claire : l'auditeur visualise l'action"),
                "FLOU": ("🌫️", "#f59e0b", "Image diffuse : risque de distraction"),
                "GRIS": ("📉", "#ef4444", "Zone de brouillard : l'auditeur décroche"),
            }
            if incarnation in incarnation_map:
                inc_icon, inc_color, inc_msg = incarnation_map[incarnation]
                messages.append(
                    f'{inc_icon} <b style="color:{inc_color};">{incarnation}</b> — {inc_msg}'
                )
            if severity == "ok" and messages:
                severity = "info"

        if not messages:
            spans += f'<span class="s-ok">{r.sentence}</span> '
        else:
            tooltip = "".join(f"<div>{m}</div>" for m in messages)
            spans += (
                f'<span class="s-{severity}">'
                f'{r.sentence}'
                f'<span class="tooltip">{tooltip}</span>'
                f'</span> '
            )
            short = r.sentence[:55] + ("..." if len(r.sentence) > 55 else "")
            issues.append((severity, short, messages))

    panel = ""
    for sev, short, msgs in issues:
        icon = {"info": "🔵", "warning": "🟡", "error": "🔴"}[sev]
        details = "".join(f"<div class='pd'>{m}</div>" for m in msgs)
        panel += f'<div class="pi {sev}"><div class="pp">{icon} {short}</div>{details}</div>'

    return f"""<!DOCTYPE html><html><head><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Inter',-apple-system,sans-serif; background:transparent; color:#e0e0e0; display:flex; gap:20px; padding:10px 0; }}

.text-area {{ flex:3; font-size:1.05rem; line-height:2.1; }}
.panel {{ flex:1; min-width:250px; max-height:600px; overflow-y:auto; border-left:1px solid #444; padding-left:16px; }}
.panel h3 {{ font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; color:#888; margin-bottom:10px; }}

.legend {{ display:flex; gap:18px; margin-bottom:14px; font-size:0.78rem; color:#aaa; }}
.legend span {{ display:flex; align-items:center; gap:5px; }}
.dot {{ width:10px; height:10px; border-radius:50%; display:inline-block; }}
.dot.ok {{ background:#10b981; }} .dot.info {{ background:#3b82f6; }}
.dot.warn {{ background:#f59e0b; }} .dot.err {{ background:#ef4444; }}

.s-ok {{ padding:1px 2px; }}
.s-info, .s-warning, .s-error {{ position:relative; cursor:help; border-radius:3px; padding:2px 3px; }}
.s-info {{ background:rgba(59,130,246,0.2); border-bottom:2px solid #3b82f6; }}
.s-warning {{ background:rgba(245,158,11,0.2); border-bottom:2px solid #f59e0b; }}
.s-error {{ background:rgba(239,68,68,0.25); border-bottom:2px solid #ef4444; }}
.s-info:hover,.s-warning:hover,.s-error:hover {{ filter:brightness(1.4); }}

.tooltip {{
    display:none; position:absolute; bottom:calc(100% + 8px); left:0;
    min-width:300px; max-width:420px;
    background:#1a1a2e; border:1px solid #555; border-radius:10px;
    padding:12px 14px; font-size:0.82rem; line-height:1.5; color:#ddd;
    z-index:1000; box-shadow:0 8px 24px rgba(0,0,0,0.6);
}}
.tooltip div {{ margin:4px 0; }}
.s-info:hover .tooltip, .s-warning:hover .tooltip, .s-error:hover .tooltip {{ display:block; }}

.pi {{ padding:8px 10px; margin-bottom:8px; border-radius:8px; }}
.pi.info {{ background:rgba(59,130,246,0.1); border-left:3px solid #3b82f6; }}
.pi.warning {{ background:rgba(245,158,11,0.1); border-left:3px solid #f59e0b; }}
.pi.error {{ background:rgba(239,68,68,0.1); border-left:3px solid #ef4444; }}
.pp {{ font-size:0.8rem; font-weight:600; margin-bottom:4px; }}
.pd {{ font-size:0.75rem; color:#aaa; margin:2px 0; }}
</style></head><body>

<div class="text-area">
    <div class="legend">
        <span><span class="dot ok"></span> OK</span>
        <span><span class="dot info"></span> Info</span>
        <span><span class="dot warn"></span> À vérifier</span>
        <span><span class="dot err"></span> Problème</span>
    </div>
    {spans}
</div>
<div class="panel">
    <h3>Problèmes détectés</h3>
    {panel if panel else "<p style='color:#666;font-size:0.85rem;'>Aucun problème 🎉</p>"}
</div>

</body></html>"""


def render_claims(claims):
    type_colors = {
        "chiffre": "#f59e0b",
        "nom_propre": "#3b82f6",
        "date": "#8b5cf6",
        "fait": "#ef4444",
        "citation": "#10b981",
    }
    for claim in claims:
        color = type_colors.get(claim.get("type", "fait"), "#888")
        zone = claim.get("zone", "").upper()
        st.markdown(
            f'<div style="background:rgba(255,255,255,0.03);border-left:3px solid {color};'
            f'padding:10px 14px;border-radius:6px;margin:6px 0;">'
            f'<span style="background:{color};color:#000;padding:2px 8px;border-radius:4px;'
            f'font-size:0.7rem;font-weight:700;margin-right:8px;">{claim.get("type","").upper()}</span>'
            f'<span style="font-size:0.7rem;color:#888;">{zone}</span>'
            f'<div style="margin-top:6px;font-style:italic;">« {claim.get("extrait","")} »</div>'
            f'<div style="margin-top:4px;font-size:0.85rem;color:#aaa;">{claim.get("note","")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_zone(label, text, results, ai_forme, prefix=""):
    st.markdown(f"### {label}")
    # Build heatmap data in a single pass
    heatmap_data = []
    for i, r in enumerate(results):
        sentence_id = f"#{prefix}{i + 1}"
        ai_match = match_ai(sentence_id, r.sentence, ai_forme)
        ai_verdict = ai_match.get("verdict", "ok") if ai_match else "ok"
        inc_label = ai_match.get("score_incarnation") if ai_match else None
        heatmap_data.append({
            "words": len(r.sentence.split()),
            "friction_score": calculate_friction_score(r.alerts, ai_verdict),
            "inc_label": inc_label,
        })
    render_heatmap(heatmap_data)
    # Texte surligné
    html = build_html(results, ai_forme, prefix)
    n_lines = max(len(text) // 60, len(results)) + 5
    components.html(html, height=min(max(n_lines * 36, 250), 600), scrolling=True)


def compute_verdict(results, ai_forme, prefix):
    """Compte les phrases par catégorie : prête / à retravailler / problématique."""
    pretes, retrav, prob = 0, 0, 0
    for i, r in enumerate(results):
        sentence_id = f"#{prefix}{i + 1}"
        ai_match = match_ai(sentence_id, r.sentence, ai_forme)
        ai_verdict = ai_match.get("verdict", "ok") if ai_match else "ok"
        severity = r.severity
        if ai_verdict == "probleme":
            severity = "error"
        elif ai_verdict == "a_verifier" and severity in ("ok", "info"):
            severity = "warning"
        if severity == "error":
            prob += 1
        elif severity == "warning":
            retrav += 1
        else:
            pretes += 1
    return pretes, retrav, prob


@st.dialog("Chirurgie de la phrase", width="large")
def _surgery_dialog(phrase, prefix, idx, context, text_type, prev_sentence, next_sentence):
    """Modal d'analyse approfondie d'une phrase."""
    state_key = f"deep_aide_{prefix}_{idx}"

    if state_key not in st.session_state:
        if st.session_state.get("ai_calls", 0) >= MAX_AI_CALLS:
            st.warning(f"Quota atteint ({MAX_AI_CALLS} appels IA par session).")
            return
        with st.spinner("Analyse chirurgicale..."):
            st.session_state[state_key] = deep_analyze_phrase(phrase, context, text_type)
        st.session_state["ai_calls"] = st.session_state.get("ai_calls", 0) + 1

    deep = st.session_state[state_key]

    if not deep or "error" in deep:
        st.error(deep.get("error", "Analyse indisponible.") if deep else "Analyse indisponible.")
        return

    # Contexte ±1 phrase
    with st.container(border=True):
        if prev_sentence:
            st.caption(f"...{prev_sentence}")
        st.markdown(f"**{phrase}**")
        if next_sentence:
            st.caption(f"{next_sentence}...")

    # Image mentale (le miroir)
    img = deep.get("image_mentale", "")
    if img:
        st.markdown(
            f'<div style="background:rgba(139,92,246,0.1);border-left:3px solid #8b5cf6;'
            f'padding:10px 14px;border-radius:6px;margin-bottom:12px;">'
            f'<span style="font-size:0.75rem;color:#8b5cf6;font-weight:700;">IMAGE MENTALE</span>'
            f'<div style="font-size:1rem;margin-top:4px;">🎬 <i>{img}</i></div></div>',
            unsafe_allow_html=True,
        )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Oralisation**")
        st.markdown(deep.get("oralisation", ""))
        st.markdown("**Compréhension**")
        st.markdown(deep.get("comprehension", ""))
    with col_b:
        st.markdown("**Impact**")
        st.markdown(deep.get("impact", ""))

    st.markdown("**Réécritures proposées**")
    for rew in deep.get("reecritures", []):
        rew_label = "Conservatrice" if rew.get("type") == "conservatrice" else "Radicale"
        rew_icon = "🔧" if rew_label == "Conservatrice" else "💡"
        st.markdown(f"{rew_icon} **{rew_label}**")
        st.code(rew.get("texte", ""), language=None)


def render_aide_moi(results, ai_forme, prefix, context, text_type):
    """Boutons Aide-moi ouvrant un dialog chirurgical pour chaque phrase problématique."""
    problematic = []
    for i, r in enumerate(results):
        sentence_id = f"#{prefix}{i + 1}"
        ai_match = match_ai(sentence_id, r.sentence, ai_forme)
        ai_verdict = ai_match.get("verdict", "ok") if ai_match else "ok"
        severity = r.severity
        if ai_verdict == "probleme":
            severity = "error"
        elif ai_verdict == "a_verifier" and severity in ("ok", "info"):
            severity = "warning"
        if severity in ("warning", "error"):
            prev_s = results[i - 1].sentence if i > 0 else ""
            next_s = results[i + 1].sentence if i < len(results) - 1 else ""
            problematic.append((i, r.sentence, severity, prev_s, next_s))

    if not problematic:
        return

    n = len(problematic)
    st.caption(f"💡 {n} phrase{'s' if n > 1 else ''} à approfondir")

    for idx, sentence, sev, prev_s, next_s in problematic:
        key = f"aide_{prefix}_{idx}"
        icon = "🔴" if sev == "error" else "🟡"
        short = sentence[:70] + ("..." if len(sentence) > 70 else "")

        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"{icon} *{short}*")
        with col2:
            if st.button("🔍", key=key, help="Analyse approfondie"):
                _surgery_dialog(sentence, prefix, idx, context, text_type, prev_s, next_s)


# --- Logique principale ---

if analyze_btn:
    has_lancement = bool(lancement_text and lancement_text.strip())
    has_papier = bool(papier_text and papier_text.strip())

    if not has_lancement and not has_papier:
        st.warning("Collez au moins un texte avant de lancer l'analyse.")
        st.stop()

    # Étape 1 : règles mécaniques
    lancement_results = analyze_text(lancement_text) if has_lancement else []
    papier_results = analyze_text(papier_text) if has_papier else []

    # Étape 2 : analyse IA
    ai_result = None
    if "ai_calls" not in st.session_state:
        st.session_state["ai_calls"] = 0
    if use_ai:
        if st.session_state["ai_calls"] >= MAX_AI_CALLS:
            st.warning(f"Quota atteint ({MAX_AI_CALLS} appels IA par session). Les règles mécaniques restent actives.")
        else:
            with st.spinner("Claude analyse votre texte..."):
                ai_result = analyze_with_ai(
                    lancement_text=lancement_text if has_lancement else None,
                    lancement_rules=summarize_for_prompt(lancement_results) if has_lancement else None,
                    papier_text=papier_text if has_papier else None,
                    papier_rules=summarize_for_prompt(papier_results) if has_papier else None,
                    papier_type=papier_type,
                )
            st.session_state["ai_calls"] += 1
            if ai_result and "error" in ai_result:
                st.error(ai_result["error"])
                ai_result = None

    # Stocker les résultats — nettoyer les anciennes analyses approfondies
    for key in list(st.session_state.keys()):
        if key.startswith("deep_aide_"):
            del st.session_state[key]
    st.session_state["analysis"] = {
        "has_lancement": has_lancement,
        "has_papier": has_papier,
        "lancement_text": lancement_text if has_lancement else None,
        "papier_text": papier_text if has_papier else None,
        "papier_type": papier_type,
        "lancement_results": lancement_results,
        "papier_results": papier_results,
        "ai_result": ai_result,
    }

# --- Rendu des résultats (depuis session_state) ---

if "analysis" in st.session_state:
    data = st.session_state["analysis"]

    ai_zones = (data["ai_result"] or {}).get("zones", {})
    ai_claims = (data["ai_result"] or {}).get("claims", [])
    ai_coherence = (data["ai_result"] or {}).get("coherence")
    ai_general = (data["ai_result"] or {}).get("impression_generale", "")
    ai_note = (data["ai_result"] or {}).get("note_relecture", "")

    # Pré-calculer les formes IA par zone (utilisées partout)
    ai_lancement = ai_zones.get("lancement", {}).get("forme", []) if data["has_lancement"] else []
    zone_key = ("papier" if data.get("papier_type") == "Papier" else "qr") if data["has_papier"] else ""
    ai_papier = ai_zones.get(zone_key, {}).get("forme", []) if data["has_papier"] else []

    # --- Verdict ---
    total_p, total_r, total_prob = 0, 0, 0
    if data["has_lancement"]:
        p, r, prob = compute_verdict(data["lancement_results"], ai_lancement, "L")
        total_p += p; total_r += r; total_prob += prob
    if data["has_papier"]:
        p, r, prob = compute_verdict(data["papier_results"], ai_papier, "P")
        total_p += p; total_r += r; total_prob += prob
    total = total_p + total_r + total_prob
    if total:
        if total_prob:
            v_icon, v_color = "🔴", "#ef4444"
        elif total_r:
            v_icon, v_color = "⚠️", "#f59e0b"
        else:
            v_icon, v_color = "✅", "#10b981"
        parts = [f"<b>{total_p}/{total}</b> phrases prêtes"]
        if total_r:
            parts.append(f"<b>{total_r}</b> à retravailler")
        if total_prob:
            parts.append(f"<b>{total_prob}</b> problématiques")
        st.markdown(
            f'<div style="padding:12px 16px;border:1px solid {v_color}40;border-radius:10px;'
            f'margin:0 0 16px;font-size:1.05rem;color:{v_color};">'
            f'{v_icon} {" · ".join(parts)}</div>',
            unsafe_allow_html=True,
        )

    # =============================================
    # COUCHE 1 — Note de relecture (ce qu'on lit en premier)
    # =============================================
    if ai_note:
        # Convertir les \n en <br> pour le rendu HTML
        note_html = ai_note.replace("\n", "<br>")
        st.markdown(
            f'<div style="background:rgba(99,102,241,0.07);border-left:4px solid #6366f1;'
            f'padding:16px 20px;border-radius:8px;margin:8px 0 20px;'
            f'font-size:1.02rem;line-height:1.75;">'
            f'{note_html}</div>',
            unsafe_allow_html=True,
        )

    # Cohérence lancement / papier (toujours visible, couche 1)
    if ai_coherence and data["has_lancement"] and data["has_papier"]:
        st.markdown(
            f'<div style="background:rgba(245,158,11,0.07);border-left:4px solid #f59e0b;'
            f'padding:12px 16px;border-radius:8px;margin:8px 0 16px;'
            f'font-size:0.95rem;line-height:1.6;">'
            f'**Cohérence lancement / papier** — {ai_coherence}</div>',
            unsafe_allow_html=True,
        )

    # Assertions à vérifier (toujours visible, couche 1)
    if ai_claims:
        st.markdown("### Assertions à vérifier")
        st.caption("Ces éléments factuels méritent une vérification avant antenne.")
        render_claims(ai_claims)

    # =============================================
    # COUCHE 2 — Détail phrase par phrase (expander)
    # =============================================
    full_context = ""
    if data["lancement_text"]:
        full_context += data["lancement_text"]
    if data["papier_text"]:
        full_context += "\n" + data["papier_text"]

    with st.expander("Détail phrase par phrase", expanded=False):
        if data["has_lancement"]:
            render_zone("Lancement", data["lancement_text"], data["lancement_results"], ai_lancement, prefix="L")
            if has_api:
                render_aide_moi(data["lancement_results"], ai_lancement, "L", full_context, "lancement")

        if data["has_papier"]:
            render_zone(data["papier_type"], data["papier_text"], data["papier_results"], ai_papier, prefix="P")
            if has_api:
                render_aide_moi(data["papier_results"], ai_papier, "P", full_context, data["papier_type"])
