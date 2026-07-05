#!/usr/bin/env python3
"""Generate a 3D-printable front panel (bezel) for the MPI7002 display.

The display hangs behind the panel: four Ø8 bosses on the panel back
reach down to the PCB mounting ears, and M3 screws driven from behind
through the ear holes pull the module against the panel. The touch lens
seats on the flat panel back; the boss faces stop 0.18 mm short of the
nominal PCB plane so the screws lightly preload the glass against the
panel (absorbed by the module's foam tapes).

Same coordinate system as the display model (scripts/generate_step.py):
the panel plate spans z 8.88..11.88 in front of the touch lens.

Print face-down (front face on the bed): flat plate, bosses straight up,
window chamfer at 45 degrees — no supports needed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_step as disp  # display model constants and assembly


OUT_STEP = Path("cad/MPI7002_front_panel.step")
OUT_STP = Path("cad/MPI7002_front_panel.stp")
OUT_3MF = Path("cad/MPI7002_front_panel.3mf")
OUT_GITHUB_STL = Path("cad/MPI7002_front_panel_github_preview.stl")
OUT_ASSY_STEP = Path("cad/MPI7002_panel_assembly.step")

PANEL_MARGIN = 5.0        # plate border beyond the PCB on all sides
PANEL_T = 3.0
PANEL_R = 6.0             # outer corner radius
WINDOW_CLEAR = 1.0        # window opening beyond the LCD active area
CHAMFER = 1.5             # 45-degree chamfer on the front face edges

BOSS_D = 8.0              # matches the mounting ear width
BOSS_PRELOAD = 0.18       # boss stops short of the PCB plane by this much
PILOT_D = 2.8             # M3 thread-forming pilot; use 4.6 + heat-set insert
PILOT_DEPTH = 6.5

Z_GLASS = disp.TOTAL_T                          # 8.88, panel back face
BOSS_TOP = Z_GLASS
BOSS_BOT = disp.PCB_T + BOSS_PRELOAD            # 1.78

# Window: LCD active area grown by WINDOW_CLEAR per side. Stays inside the
# CTP visual area's surround and well inside the lens.
WIN_X0 = disp.PCB_W - disp.AA_RIGHT - disp.AA_W - WINDOW_CLEAR
WIN_Y0 = disp.PCB_H - disp.AA_TOP - disp.AA_H - WINDOW_CLEAR
WIN_W = disp.AA_W + 2 * WINDOW_CLEAR
WIN_H = disp.AA_H + 2 * WINDOW_CLEAR

HOLES = [
    (disp.HOLE_X0 + dx, disp.HOLE_Y0 + dy)
    for dx in (0.0, disp.HOLE_DX)
    for dy in (0.0, disp.HOLE_DY)
]


def build_panel() -> cq.Workplane:
    plate = (
        cq.Workplane("XY")
        .box(
            disp.PCB_W + 2 * PANEL_MARGIN,
            disp.PCB_H + 2 * PANEL_MARGIN,
            PANEL_T,
            centered=False,
        )
        .translate((-PANEL_MARGIN, -PANEL_MARGIN, Z_GLASS))
        .edges("|Z")
        .fillet(PANEL_R)
    )

    window = (
        cq.Workplane("XY")
        .box(WIN_W, WIN_H, PANEL_T + 2.0, centered=False)
        .translate((WIN_X0, WIN_Y0, Z_GLASS - 1.0))
    )
    plate = plate.cut(window)

    # 45-degree chamfer on the front face: window rim and outer rim.
    plate = plate.edges(">Z").chamfer(CHAMFER)

    for x, y in HOLES:
        boss = (
            cq.Workplane("XY")
            .circle(BOSS_D / 2)
            .extrude(BOSS_TOP - BOSS_BOT)
            .translate((x, y, BOSS_BOT))
        )
        plate = plate.union(boss)
        pilot = (
            cq.Workplane("XY")
            .circle(PILOT_D / 2)
            .extrude(PILOT_DEPTH + 0.1)
            .translate((x, y, BOSS_BOT - 0.1))
        )
        plate = plate.cut(pilot)

    return plate


def main() -> None:
    OUT_STEP.parent.mkdir(parents=True, exist_ok=True)
    panel = build_panel()

    panel_assy = cq.Assembly(name="MPI7002_front_panel")
    panel_assy.add(panel, name="front_panel", color=cq.Color(0.35, 0.38, 0.42, 1.0))
    panel_assy.export(str(OUT_STEP), exportType="STEP")
    OUT_STP.write_bytes(OUT_STEP.read_bytes())
    cq.exporters.export(panel.val(), str(OUT_3MF), tolerance=0.05, angularTolerance=0.1)
    cq.exporters.export(panel.val(), str(OUT_GITHUB_STL), tolerance=0.05, angularTolerance=0.1)

    # Combined assembly for CAD reference: display module + panel in place.
    assy = disp.build()
    assy.add(panel, name="front_panel", color=cq.Color(0.35, 0.38, 0.42, 0.9))
    assy.export(str(OUT_ASSY_STEP), exportType="STEP")

    for p in (OUT_STEP, OUT_STP, OUT_3MF, OUT_GITHUB_STL, OUT_ASSY_STEP):
        print(p)


if __name__ == "__main__":
    main()
