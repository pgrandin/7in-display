#!/usr/bin/env python3
"""Generate STEP and 3MF CAD models for the LCDwiki MPI7002 display module.

All dimensions come from the official LCM outline drawing
(MPI7002_Size.pdf, V1.0, 2024-2-21) cross-checked against
MPI7002_Product_Dimensions.png. See cad/README.md for the source
discrepancies and how they were resolved.

Coordinate system: origin at the lower-left PCB corner viewed from the
front (screen side). +X right, +Y up, +Z out of the screen. z=0 is the
PCB back face (component side); connectors extend into -Z.
"""

from __future__ import annotations

from pathlib import Path

import cadquery as cq


OUT_STEP = Path("cad/MPI7002.step")
OUT_STP = Path("cad/MPI7002.stp")
OUT_3MF = Path("cad/MPI7002.3mf")
OUT_GITHUB_STL = Path("cad/MPI7002_github_preview.stl")

# --- PCB ---
# The board is not a plain rectangle: the main body is 164.90 x 106.96 and
# four 8.00-wide mounting ears at the corners extend it to 124.27 overall
# (back view of the outline drawing: 106.96 body height, 8.65 ear depth,
# 148.90 between ear inner edges). All outline corners are R4.00, which
# makes the 8.00-wide ear tips semicircular.
PCB_W = 164.90
PCB_H = 124.27
PCB_T = 1.60
PCB_R = 4.00
BODY_H = 106.96
EAR_W = 8.00
NOTCH_D = (PCB_H - BODY_H) / 2   # 8.655 recess on top and bottom edges
NOTCH_W = PCB_W - 2 * EAR_W      # 148.90 between ear inner edges

# Mounting holes: 4x Ø3.00 centered in the ears, spacing 156.90 x 114.96
# per the front view of the outline drawing and the extension lines of the
# product dimensions image (4.00 from the side edges, 4.655 from
# top/bottom edges).
HOLE_D = 3.00
HOLE_DX = 156.90
HOLE_DY = 114.96
HOLE_X0 = (PCB_W - HOLE_DX) / 2  # 4.00
HOLE_Y0 = (PCB_H - HOLE_DY) / 2  # 4.655

# --- Screen stack (z, back to front): PCB, LCD back tape, LCD, CTP back
# tape, CTP lens. Total 8.88. ---
LCD_TAPE_T = 2.00
LCD_T = 3.50
TOUCH_TAPE_T = 0.30
TOUCH_T = 1.48
TOTAL_T = PCB_T + LCD_TAPE_T + LCD_T + TOUCH_TAPE_T + TOUCH_T  # 8.88

Z_LCD_TAPE = PCB_T
Z_LCD = Z_LCD_TAPE + LCD_TAPE_T
Z_TOUCH_TAPE = Z_LCD + LCD_T
Z_TOUCH = Z_TOUCH_TAPE + TOUCH_TAPE_T

# --- Screen layer footprints. Offsets are from the drawing's front view:
# horizontal offsets dimensioned from the right (connector) edge, vertical
# offsets from the top edge. ---
LCD_BL_W, LCD_BL_H, LCD_BL_TOP = 164.90, 100.00, 9.52
LENS_W, LENS_H, LENS_RIGHT, LENS_TOP = 164.28, 99.17, 0.21, 10.08
VA_W, VA_H, VA_RIGHT, VA_TOP = 154.68, 87.02, 6.75, 13.80
AA_W, AA_H, AA_RIGHT, AA_TOP = 154.21, 85.92, 6.99, 14.35

# --- Connectors, all on the right edge (viewed from the front), mounted on
# the PCB back face and extending into -Z. Vertical centers follow the
# dimension chain on the product drawing: top edge -> hole 4.66 -> HDMI
# 15.59 -> micro-USB 18.37 -> micro-USB 13.11 -> backlight switch 11.14.
# The 6.27 HDMI height is from the drawing; the other body sizes are
# standard receptacle dimensions (not dimensioned on the drawing). ---
HDMI_CY = PCB_H - (4.66 + 15.59)          # 104.02
USB1_CY = HDMI_CY - 18.37                 # 85.65
USB2_CY = USB1_CY - 13.11                 # 72.54
SW_CY = USB2_CY - 11.14                   # 61.40

HDMI_W, HDMI_DEPTH, HDMI_T = 15.00, 11.60, 6.27
USB_W, USB_DEPTH, USB_T = 7.70, 5.40, 2.45
SW_W, SW_DEPTH, SW_T = 9.00, 4.20, 3.60


def box(x: float, y: float, z: float, w: float, h: float, d: float) -> cq.Workplane:
    return cq.Workplane("XY").box(w, h, d, centered=False).translate((x, y, z))


def edge_connector(cy: float, w: float, depth: float, t: float) -> cq.Workplane:
    """Connector body flush with the right PCB edge, on the back face."""
    return box(PCB_W - depth, cy - w / 2, -t, depth, w, t)


def board() -> cq.Workplane:
    # The outline is drawn explicitly: R4.00 on the 8.00-wide ears makes
    # their tips exact semicircles, which OCC's fillet builder cannot
    # produce (tangent adjacent fillets), so filleting after the fact is
    # not an option.
    r = PCB_R
    floor_top = PCB_H - NOTCH_D          # 115.615
    floor_bot = NOTCH_D                  # 8.655
    part = (
        cq.Workplane("XY")
        .moveTo(0, r)
        .lineTo(0, PCB_H - r)
        # top-left ear tip (semicircle)
        .threePointArc((r, PCB_H), (EAR_W, PCB_H - r))
        .lineTo(EAR_W, floor_top + r)
        # concave root fillet into the top recess
        .radiusArc((EAR_W + r, floor_top), -r)
        .lineTo(PCB_W - EAR_W - r, floor_top)
        .radiusArc((PCB_W - EAR_W, floor_top + r), -r)
        .lineTo(PCB_W - EAR_W, PCB_H - r)
        # top-right ear tip
        .threePointArc((PCB_W - r, PCB_H), (PCB_W, PCB_H - r))
        .lineTo(PCB_W, r)
        # bottom-right ear tip
        .threePointArc((PCB_W - r, 0), (PCB_W - EAR_W, r))
        .lineTo(PCB_W - EAR_W, floor_bot - r)
        .radiusArc((PCB_W - EAR_W - r, floor_bot), -r)
        .lineTo(EAR_W + r, floor_bot)
        .radiusArc((EAR_W, floor_bot - r), -r)
        .lineTo(EAR_W, r)
        # bottom-left ear tip
        .threePointArc((r, 0), (0, r))
        .close()
        .extrude(PCB_T)
    )

    for x in (HOLE_X0, HOLE_X0 + HOLE_DX):
        for y in (HOLE_Y0, HOLE_Y0 + HOLE_DY):
            cutter = (
                cq.Workplane("XY")
                .circle(HOLE_D / 2)
                .extrude(PCB_T + 1.0)
                .translate((x, y, -0.5))
            )
            part = part.cut(cutter)

    return part


def build() -> cq.Assembly:
    assy = cq.Assembly(name="MPI7002_7inch_HDMI_Display_C")

    assy.add(board(), name="pcb_164p90x124p27x1p60", color=cq.Color(0.02, 0.14, 0.32, 1.0))

    assy.add(
        box(0, PCB_H - LCD_BL_TOP - LCD_BL_H, Z_LCD_TAPE, LCD_BL_W, LCD_BL_H, LCD_TAPE_T),
        name="lcd_back_tape_2p00",
        color=cq.Color(0.02, 0.02, 0.02, 0.35),
    )
    assy.add(
        box(0, PCB_H - LCD_BL_TOP - LCD_BL_H, Z_LCD, LCD_BL_W, LCD_BL_H, LCD_T),
        name="lcd_backlight_164p90x100p00x3p50",
        color=cq.Color(0.02, 0.02, 0.02, 1.0),
    )
    lens_x = PCB_W - LENS_RIGHT - LENS_W
    lens_y = PCB_H - LENS_TOP - LENS_H
    assy.add(
        box(lens_x, lens_y, Z_TOUCH_TAPE, LENS_W, LENS_H, TOUCH_TAPE_T),
        name="ctp_back_tape_0p30",
        color=cq.Color(0.02, 0.02, 0.02, 0.35),
    )
    assy.add(
        box(lens_x, lens_y, Z_TOUCH, LENS_W, LENS_H, TOUCH_T),
        name="capacitive_touch_lens_164p28x99p17x1p48",
        color=cq.Color(0.01, 0.01, 0.012, 0.55),
    )
    assy.add(
        box(
            PCB_W - AA_RIGHT - AA_W,
            PCB_H - AA_TOP - AA_H,
            TOTAL_T - 0.04,
            AA_W,
            AA_H,
            0.03,
        ),
        name="lcd_active_area_154p21x85p92_marker",
        color=cq.Color(0.04, 0.06, 0.08, 1.0),
    )
    assy.add(
        box(
            PCB_W - VA_RIGHT - VA_W,
            PCB_H - VA_TOP - VA_H,
            TOTAL_T - 0.01,
            VA_W,
            VA_H,
            0.01,
        ),
        name="ctp_visual_area_154p68x87p02_reference",
        color=cq.Color(0.8, 0.8, 0.8, 0.25),
    )

    assy.add(
        edge_connector(HDMI_CY, HDMI_W, HDMI_DEPTH, HDMI_T),
        name="hdmi_a_receptacle",
        color=cq.Color(0.75, 0.75, 0.75, 1.0),
    )
    assy.add(
        edge_connector(USB1_CY, USB_W, USB_DEPTH, USB_T),
        name="micro_usb_touch_upper",
        color=cq.Color(0.75, 0.75, 0.75, 1.0),
    )
    assy.add(
        edge_connector(USB2_CY, USB_W, USB_DEPTH, USB_T),
        name="micro_usb_touch_lower",
        color=cq.Color(0.75, 0.75, 0.75, 1.0),
    )
    assy.add(
        edge_connector(SW_CY, SW_W, SW_DEPTH, SW_T),
        name="backlight_switch",
        color=cq.Color(0.9, 0.9, 0.9, 1.0),
    )

    return assy


def main() -> None:
    OUT_STEP.parent.mkdir(parents=True, exist_ok=True)
    assy = build()
    assy.export(str(OUT_STEP), exportType="STEP")
    OUT_STP.write_bytes(OUT_STEP.read_bytes())
    compound = assy.toCompound()
    cq.exporters.export(compound, str(OUT_3MF), tolerance=0.05, angularTolerance=0.1)
    cq.exporters.export(compound, str(OUT_GITHUB_STL), tolerance=0.05, angularTolerance=0.1)
    for p in (OUT_STEP, OUT_STP, OUT_3MF, OUT_GITHUB_STL):
        print(p)


if __name__ == "__main__":
    main()
