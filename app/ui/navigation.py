"""Navigation primitives for the F1 Base44 Elite app."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class Workspace:
    """A product workspace shown in the sidebar selector."""

    key: str
    label: str
    icon: str
    description: str

    @property
    def display(self) -> str:
        return f"{self.icon} {self.label}"


WORKSPACES: tuple[Workspace, ...] = (
    Workspace("overview", "Overview", "🏠", "Executive race-intelligence overview."),
    Workspace("fan", "Fan Hub", "🏎️", "Driver cards, race drama and shareable predictions."),
    Workspace("race", "Race Control", "📡", "Live classification, track map and Monte Carlo probability."),
    Workspace("strategy", "Strategy", "🛞", "Race pace, compound context and team-radio interpretation."),
    Workspace("weather", "Weather & Alerts", "🌦️", "Weather radar, DRS and overtake alerting."),
    Workspace("engineer", "Engineer Mode", "🧪", "Uncertainty, assumptions, diagnostics and limitations."),
)


def workspace_by_display(display: str) -> Workspace:
    """Resolve a workspace from its rendered display label."""

    for workspace in WORKSPACES:
        if workspace.display == display:
            return workspace
    return WORKSPACES[0]


def sidebar_workspace_selector(default_key: str = "overview") -> Workspace:
    """Render a premium workspace selector in the sidebar."""

    default_index = next((idx for idx, item in enumerate(WORKSPACES) if item.key == default_key), 0)
    selected = st.radio(
        "Workspace",
        [workspace.display for workspace in WORKSPACES],
        index=default_index,
        help="Choose the product workspace to focus the page.",
    )
    workspace = workspace_by_display(selected)
    st.caption(workspace.description)
    return workspace
