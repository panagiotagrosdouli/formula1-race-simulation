from app.ui.cards import kpi_card
from app.ui.theme import TOKENS, base_css


def test_theme_tokens_include_f1_brand_color():
    assert TOKENS.primary == "#e10600"
    assert TOKENS.primary in TOKENS.palette


def test_base_css_contains_core_base44_classes():
    css = base_css()

    assert ".f1-hero" in css
    assert ".f1-card" in css
    assert ".f1-driver-card" in css
    assert "--f1-primary" in css


def test_card_component_is_importable():
    assert callable(kpi_card)
