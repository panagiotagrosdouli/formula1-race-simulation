"""Layout primitives for the F1 Base44 Elite Streamlit interface."""

from __future__ import annotations

import html

import streamlit as st


def hero(title: str, body: str, badges: list[str] | None = None) -> None:
    """Render the main product hero block."""

    badge_html = "".join(f"<span class='f1-badge'>{html.escape(badge)}</span>" for badge in (badges or []))
    st.markdown(
        f"""
        <div class="f1-hero">
          <h1>{html.escape(title)}</h1>
          <p>{html.escape(body)}</p>
          {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str | None = None) -> None:
    """Render a consistent section heading."""

    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)


def page_caption(text: str) -> None:
    """Render a consistent scientific-honesty caption."""

    st.caption(text)
