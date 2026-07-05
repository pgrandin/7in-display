#!/usr/bin/env python3
"""Render README preview images of the case assembly.

Tessellates the CadQuery models directly (no intermediate STL) and renders
two shaded views with matplotlib: the assembled enclosure and an exploded
stack. Outputs docs/render_assembly.png and docs/render_exploded.png.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_step as disp
import generate_panel as panel
import generate_case as case

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


OUT_DIR = Path("docs")

DISPLAY_COLORS = {
    "pcb_164p90x124p27x1p60": "#1a3a6b",
    "lcd_back_tape_2p00": "#26282c",
    "lcd_backlight_164p90x100p00x3p50": "#202226",
    "ctp_back_tape_0p30": "#26282c",
    "capacitive_touch_lens_164p28x99p17x1p48": "#141519",
    "lcd_active_area_154p21x85p92_marker": "#0b1420",
    "ctp_visual_area_154p68x87p02_reference": "#20242a",
    "hdmi_a_receptacle": "#b9bec4",
    "micro_usb_touch_upper": "#b9bec4",
    "micro_usb_touch_lower": "#b9bec4",
    "backlight_switch": "#cdd2d7",
}
PI_COLORS = {
    "pi5_board_85x56_approx": "#2e6e48",
    "pi5_usb_eth_stack_approx": "#a8adb3",
    "pi5_usbc_hdmi_row_approx": "#a8adb3",
    "pi5_soc_cooler_approx": "#8f959b",
    "pi5_gpio_header_approx": "#33363a",
}
PANEL_COLOR = "#9099a1"
CASE_COLOR = "#4a525b"


def tessellate(workplane, tol=0.4) -> np.ndarray:
    """Return an (n, 3, 3) triangle array for a Workplane/Shape."""
    shape = workplane.val() if hasattr(workplane, "val") else workplane
    verts, faces = shape.tessellate(tol)
    v = np.array([(p.x, p.y, p.z) for p in verts])
    return v[np.array(faces)]


def assembly_parts(explode: float = 0.0) -> list[tuple[np.ndarray, str]]:
    """(triangles, color) for every part, optionally exploded along Z."""
    parts: list[tuple[np.ndarray, str]] = []

    def add(workplane, color, dz):
        tri = tessellate(workplane)
        tri = tri + np.array([0.0, 0.0, dz])
        parts.append((tri, color))

    for child in disp.build().children:
        add(child.obj, DISPLAY_COLORS.get(child.name, "#888888"), explode * 1.0)
    add(panel.build_panel(), PANEL_COLOR, explode * 2.0)
    add(case.build_case(), CASE_COLOR, 0.0)
    for child in case.build_pi_mock().children:
        add(child.obj, PI_COLORS.get(child.name, "#888888"), 0.0)
    return parts


def render(parts, out: Path, elev: float, azim: float, zspan: tuple[float, float]) -> None:
    light = np.array([0.35, -0.5, 0.8])
    light = light / np.linalg.norm(light)

    tris, colors = [], []
    for tri, color in parts:
        base = np.array(matplotlib.colors.to_rgb(color))
        a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
        n = np.cross(b - a, c - a)
        norm = np.linalg.norm(n, axis=1, keepdims=True)
        n = np.divide(n, norm, out=np.zeros_like(n), where=norm > 0)
        shade = 0.45 + 0.55 * np.abs(n @ light)
        tris.append(tri)
        colors.append(base[None, :] * shade[:, None])

    tri = np.concatenate(tris)
    col = np.clip(np.concatenate(colors), 0, 1)

    fig = plt.figure(figsize=(11, 8), facecolor="white")
    ax = fig.add_subplot(projection="3d")
    pc = Poly3DCollection(tri, facecolors=col, edgecolors="none", zsort="average")
    ax.add_collection3d(pc)

    cx, cy = 96.5, 62.0
    half = 118.0
    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy - half, cy + half)
    ax.set_zlim(*zspan)
    ax.set_box_aspect((1, 1, (zspan[1] - zspan[0]) / (2 * half)))
    ax.view_init(elev=elev, azim=azim)
    ax.set_proj_type("persp", focal_length=0.35)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.savefig(out, dpi=130, bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close(fig)
    print(out)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    render(assembly_parts(0.0), OUT_DIR / "render_assembly.png",
           elev=38, azim=-58, zspan=(-45, 40))
    render(assembly_parts(28.0), OUT_DIR / "render_exploded.png",
           elev=22, azim=-58, zspan=(-40, 95))


if __name__ == "__main__":
    main()
