"""Utility module listing Python-only libraries useful for smoother animations in
CustomTkinter/Tkinter interfaces.

This module is purely informational; import it and inspect the
``PYTHON_ANIMATION_LIBRARIES`` constant to discover vetted packages that remain
within the Python ecosystem while providing higher-level animation helpers.
"""

from __future__ import annotations

PYTHON_ANIMATION_LIBRARIES = {
    "tkinter-animate": {
        "description": (
            "Extends standard Tk widgets with animation primitives (fade, slide, "
            "scale) implemented in pure Python. Works alongside CustomTkinter "
            "widgets because they inherit from Tk widgets, so you can schedule "
            "transitions on frames instead of calling pack_forget()/pack() "
            "directly."
        ),
        "install": "pip install tkinter-animate",
        "documentation": "https://github.com/RedFantom/tkinter-animate",
        "integration_tips": [
            "Wrap each mode panel in an AnimatedFrame and call slide_to()/fade_to()",
            "Use easing functions to smooth the motion when toggling dark mode",
            "Limit frame rate (e.g. 60 Hz) to avoid overloading Tk's event loop",
        ],
    },
    "tkinterweb": {
        "description": (
            "Pure-Python HTML/CSS renderer for Tk that supports basic CSS "
            "transitions. Embed a CTkFrame with an HtmlFrame inside to leverage "
            "CSS-driven fades/opacity changes without shipping an external browser."
        ),
        "install": "pip install tkinterweb",
        "documentation": "https://github.com/Andereoo/TkinterWeb",
        "integration_tips": [
            "Use a lightweight HTML template for animated banners or loaders",
            "Communicate events back to Python via HtmlFrame.evaluate_javascript",
            "Keep CSS animations short to minimize redraw artifacts",
        ],
    },
    "pytweening": {
        "description": (
            "Easing function collection written in Python. Combine with Tk's "
            "after() loop or CustomTkinter's .after() to compute smooth progress "
            "values for manual slide/fade animations without relying on JS."
        ),
        "install": "pip install pytweening",
        "documentation": "https://github.com/asweigart/pytweening",
        "integration_tips": [
            "Calculate tweened positions for frames when switching modes",
            "Pair with canvas/place geometry managers for pixel-precise motion",
            "Precompute tweens to reduce runtime overhead on slower machines",
        ],
    },
}


def list_animation_libraries() -> dict[str, dict[str, object]]:
    """Return the curated mapping of Python-only animation helper libraries."""

    return PYTHON_ANIMATION_LIBRARIES.copy()


__all__ = ["PYTHON_ANIMATION_LIBRARIES", "list_animation_libraries"]
