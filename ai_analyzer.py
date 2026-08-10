"""
Façade de compatibilité — l'analyse IA vit désormais dans agents.py.

app.py continue d'importer analyze_with_ai / deep_analyze_phrase / get_client
d'ici ; sous le capot, c'est le pipeline orchestré (4 agents spécialisés avec
sorties structurées) qui tourne. Voir agents.py pour l'architecture.
"""

from agents import analyze_pipeline, deep_analyze_phrase, get_client

__all__ = ["analyze_with_ai", "deep_analyze_phrase", "get_client"]


def analyze_with_ai(
    lancement_text: str | None,
    lancement_rules: str | None,
    papier_text: str | None,
    papier_rules: str | None,
    papier_type: str,
) -> dict | None:
    return analyze_pipeline(
        lancement_text, lancement_rules, papier_text, papier_rules, papier_type
    )
