#!/usr/bin/env python3
"""Generate a 3D-printable back case for the MPI7002 display + Raspberry Pi 5.

Pairs with the front panel from scripts/generate_panel.py. The enclosure
holds the display against the panel and carries a Raspberry Pi 5 mounted
on the case back, with fully internal cabling:

- The display's HDMI / micro-USB / backlight switch open into an internal
  cable bay on the right side (30 mm deep); use right-angle or short-boot
  plugs there. No display ports are exposed.
- The Pi 5 mounts component-side-up on four standoffs, its USB-C /
  micro-HDMI edge facing the cable bay. Micro-HDMI-to-HDMI and USB-A-to-
  micro-USB (touch) cables run inside the case.
- The Pi's USB/Ethernet edge faces the case interior (accessible with the
  case opened); the only external opening is a cable pass-through slot in
  the bay wall (power cord, optionally Ethernet) plus vent slots in the
  back under the Pi.
- Four hollow pillars rise from the case floor to the PCB mounting ears.
  M3 x 35 socket-head screws driven from the back go through the pillars
  and ear holes into the front panel bosses, clamping case, display, and
  panel with the same four screws.

Same coordinate system as the display model. Print back-face-down: walls,
pillars, and standoffs rise straight up; the bay roof is a single 33 mm
bridge (prints fine with cooling, or enable supports for it).
"""

from __future__ import annotations

import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_step as disp
import generate_panel as panel


OUT_STEP = Path("cad/MPI7002_case_back.step")
OUT_STP = Path("cad/MPI7002_case_back.stp")
OUT_3MF = Path("cad/MPI7002_case_back.3mf")
OUT_GITHUB_STL = Path("cad/MPI7002_case_back_github_preview.stl")
OUT_ASSY_STEP = Path("cad/MPI7002_case_assembly.step")

FIT_CLEAR = 0.75          # cavity clearance around the PCB, per side
WALL_T = 2.5              # bay right wall thickness
BACK_T = 2.5              # back wall thickness
ROOF_T = 2.5              # bay roof thickness

# Depth budget: Pi standoff 3.0 + board 1.4 + USB/Ethernet stack ~16 +
# clearance to the display's back-side components.
Z_TOP = disp.TOTAL_T                          # 8.88, meets the panel
Z_CAVITY = -28.0                              # interior floor
Z_BACK = Z_CAVITY - BACK_T                    # -30.5 exterior back

# Cable bay on the right: display connectors open into it.
BAY_W = 30.0                                  # interior depth for plugs
BAY_X0 = disp.PCB_W + 0.5                     # 165.4, roof/bay inner edge
BAY_X1 = BAY_X0 + BAY_W                       # 195.4
Z_BAY_TOP = Z_TOP - ROOF_T                    # 6.38, bay ceiling

EXT_X0 = -panel.PANEL_MARGIN
EXT_Y0 = -panel.PANEL_MARGIN
EXT_X1 = BAY_X1 + WALL_T                      # 197.9
EXT_Y1 = disp.PCB_H + panel.PANEL_MARGIN
EXT_R = panel.PANEL_R

PILLAR_D = 9.0
SCREW_CLEAR_D = 3.4       # M3 clearance through pillar and back wall
CBORE_D = 6.5             # M3 socket head counterbore
CBORE_DEPTH = 3.0

# --- Raspberry Pi 5 ---
# Board 85 x 56, mounting holes 58 x 49 at 3.5 from the edges. Placed with
# the long axis vertical: USB-C / 2x micro-HDMI long edge faces the cable
# bay (+X), 40-pin GPIO long edge faces the interior (-X), USB/Ethernet
# short edge faces up (+Y), microSD short edge faces down (-Y). The board
# stops short of the bottom-right case pillar.
PI_W, PI_L = 56.0, 85.0
PI_X1 = 156.0                                 # clears the pillar at x 156.4
PI_X0 = PI_X1 - PI_W                          # 100.0
PI_Y0 = 10.0
PI_Y1 = PI_Y0 + PI_L                          # 95.0
PI_HOLE_OFF = 3.5
PI_HOLE_DX, PI_HOLE_DY = 49.0, 58.0
PI_HOLES = [
    (PI_X0 + PI_HOLE_OFF + dx, PI_Y0 + PI_HOLE_OFF + dy)
    for dx in (0.0, PI_HOLE_DX)
    for dy in (0.0, PI_HOLE_DY)
]
STANDOFF_D = 6.0
STANDOFF_H = 3.0
PI_PILOT_D = 2.05         # M2.5 thread-forming; 3.5 + heat-set insert
PI_PILOT_DEPTH = 5.0
PI_BOARD_T = 1.4
Z_PI_BOT = Z_CAVITY + STANDOFF_H              # -25.0
Z_PI_TOP = Z_PI_BOT + PI_BOARD_T              # -23.6

# Cable pass-through slot in the bay's right wall (power cord etc.).
SLOT_Y0, SLOT_Y1 = 25.0, 41.0
SLOT_Z0, SLOT_Z1 = -26.0, -13.0

# Vent slots in the back wall under the Pi.
VENT_X0, VENT_LEN, VENT_W = 108.0, 40.0, 3.0
VENT_YS = [22.0 + 8.0 * i for i in range(9)]


def box(x, y, z, w, h, d) -> cq.Workplane:
    return cq.Workplane("XY").box(w, h, d, centered=False).translate((x, y, z))


def build_case() -> cq.Workplane:
    shell = (
        cq.Workplane("XY")
        .box(EXT_X1 - EXT_X0, EXT_Y1 - EXT_Y0, Z_TOP - Z_BACK, centered=False)
        .translate((EXT_X0, EXT_Y0, Z_BACK))
        .edges("|Z")
        .fillet(EXT_R)
    )

    # Main cavity: open toward the front, closed by the front panel.
    main = box(
        -FIT_CLEAR,
        -FIT_CLEAR,
        Z_CAVITY,
        BAY_X0 + FIT_CLEAR,
        disp.PCB_H + 2 * FIT_CLEAR,
        (Z_TOP - Z_CAVITY) + 1.0,
    ).edges("|Z").fillet(3.0)
    shell = shell.cut(main)

    # Cable bay: same floor, closed on the front by an integral roof that
    # also supports the front panel's right border.
    bay = box(
        BAY_X0 - 1.0,
        -FIT_CLEAR,
        Z_CAVITY,
        (BAY_X1 - BAY_X0) + 1.0,
        disp.PCB_H + 2 * FIT_CLEAR,
        Z_BAY_TOP - Z_CAVITY,
    ).edges("|Z").fillet(3.0)
    shell = shell.cut(bay)

    # Cable pass-through in the bay's right wall.
    shell = shell.cut(
        box(BAY_X1 - 1.0, SLOT_Y0, SLOT_Z0, WALL_T + 3.0, SLOT_Y1 - SLOT_Y0, SLOT_Z1 - SLOT_Z0)
    )

    # Vent slots through the back wall, under the Pi.
    for y in VENT_YS:
        shell = shell.cut(
            box(VENT_X0, y - VENT_W / 2, Z_BACK - 1.0, VENT_LEN, VENT_W, BACK_T + 2.0)
        )

    # Display clamping pillars (M3 x 35 from the back into the panel bosses).
    for x, y in panel.HOLES:
        pillar = (
            cq.Workplane("XY")
            .circle(PILLAR_D / 2)
            .extrude(0.0 - Z_CAVITY)
            .translate((x, y, Z_CAVITY))
        )
        shell = shell.union(pillar)
        shell = shell.cut(
            cq.Workplane("XY")
            .circle(SCREW_CLEAR_D / 2)
            .extrude(0.0 - Z_BACK + 1.0)
            .translate((x, y, Z_BACK - 0.5))
        )
        shell = shell.cut(
            cq.Workplane("XY")
            .circle(CBORE_D / 2)
            .extrude(CBORE_DEPTH + 0.5)
            .translate((x, y, Z_BACK - 0.5))
        )

    # Pi standoffs with M2.5 pilot holes.
    for x, y in PI_HOLES:
        standoff = (
            cq.Workplane("XY")
            .circle(STANDOFF_D / 2)
            .extrude(STANDOFF_H)
            .translate((x, y, Z_CAVITY))
        )
        shell = shell.union(standoff)
        shell = shell.cut(
            cq.Workplane("XY")
            .circle(PI_PILOT_D / 2)
            .extrude(PI_PILOT_DEPTH)
            .translate((x, y, Z_CAVITY + STANDOFF_H - PI_PILOT_DEPTH))
        )

    return shell


def build_pi_mock() -> cq.Assembly:
    """Approximate Raspberry Pi 5 envelope for clearance checks."""
    assy = cq.Assembly(name="raspberry_pi_5_approx")
    board = (
        cq.Workplane("XY")
        .box(PI_W, PI_L, PI_BOARD_T, centered=False)
        .edges("|Z")
        .fillet(3.0)
        .translate((PI_X0, PI_Y0, Z_PI_BOT))
    )
    holes = cq.Workplane("XY")
    for x, y in PI_HOLES:
        board = board.cut(
            cq.Workplane("XY")
            .circle(2.7 / 2)
            .extrude(PI_BOARD_T + 1.0)
            .translate((x, y, Z_PI_BOT - 0.5))
        )
    assy.add(board, name="pi5_board_85x56_approx", color=cq.Color(0.0, 0.35, 0.2, 1.0))
    blocks = [
        # USB/Ethernet stacks on the +Y edge (ports overhang ~2 mm).
        ("pi5_usb_eth_stack_approx", PI_X0 + 5.0, PI_Y1 - 17.5, Z_PI_TOP, 46.0, 19.5, 16.0),
        # USB-C + 2x micro-HDMI along the bay-facing edge (overhang ~1 mm).
        ("pi5_usbc_hdmi_row_approx", PI_X1 - 7.5, PI_Y0 + 5.0, Z_PI_TOP, 8.5, 50.0, 3.3),
        # SoC + official active cooler envelope.
        ("pi5_soc_cooler_approx", PI_X0 + 10.0, PI_Y0 + 20.0, Z_PI_TOP, 30.0, 40.0, 11.0),
        # 40-pin GPIO header along the -X edge.
        ("pi5_gpio_header_approx", PI_X0 + 1.0, PI_Y0 + 7.0, Z_PI_TOP, 5.0, 51.0, 8.5),
    ]
    for name, x, y, z, w, h, d in blocks:
        assy.add(box(x, y, z, w, h, d), name=name, color=cq.Color(0.6, 0.6, 0.6, 1.0))
    return assy


def main() -> None:
    OUT_STEP.parent.mkdir(parents=True, exist_ok=True)
    case = build_case()

    case_assy = cq.Assembly(name="MPI7002_case_back")
    case_assy.add(case, name="case_back", color=cq.Color(0.25, 0.27, 0.30, 1.0))
    case_assy.export(str(OUT_STEP), exportType="STEP")
    OUT_STP.write_bytes(OUT_STEP.read_bytes())

    # The 3MF is print-oriented: exterior back down on the bed (z=0),
    # walls and pillars up. The STEP stays in assembly coordinates.
    printable = case.translate((0, 0, -Z_BACK))
    cq.exporters.export(printable.val(), str(OUT_3MF), tolerance=0.05, angularTolerance=0.1)

    cq.exporters.export(case.val(), str(OUT_GITHUB_STL), tolerance=0.05, angularTolerance=0.1)

    # Full assembly: display + front panel + case + Pi 5 reference model.
    assy = disp.build()
    assy.add(panel.build_panel(), name="front_panel", color=cq.Color(0.35, 0.38, 0.42, 0.9))
    assy.add(case, name="case_back", color=cq.Color(0.25, 0.27, 0.30, 0.9))
    assy.add(build_pi_mock(), name="raspberry_pi_5_approx")
    assy.export(str(OUT_ASSY_STEP), exportType="STEP")

    for p in (OUT_STEP, OUT_STP, OUT_3MF, OUT_GITHUB_STL, OUT_ASSY_STEP):
        print(p)


if __name__ == "__main__":
    main()
