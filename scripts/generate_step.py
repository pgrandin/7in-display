#!/usr/bin/env python3
"""Generate a STEP CAD model for the LCDwiki MPI7002 display module."""

from __future__ import annotations

from pathlib import Path

import cadquery as cq


OUT = Path("cad/MPI7002.step")
OUT_STP = Path("cad/MPI7002.stp")
OUT_GITHUB_STL = Path("cad/MPI7002_github_preview.stl")

PCB_W = 164.90
PCB_H = 124.27
PCB_T = 1.60
PCB_R = 4.00
TOTAL_T = 8.88

HOLE_D = 3.00
HOLE_DX = 148.90
HOLE_DY = 114.96
HOLE_X0 = (PCB_W - HOLE_DX) / 2
HOLE_Y0 = (PCB_H - HOLE_DY) / 2

LCD_TAPE_T = 2.00
LCD_T = 3.50
TOUCH_TAPE_T = 0.30
TOUCH_T = 1.48

SCREEN_Y0 = PCB_H - 100.00
TOUCH_LENS_W = 164.28
TOUCH_LENS_H = 99.17
TOUCH_VA_W = 154.68
TOUCH_VA_H = 87.02
ACTIVE_W = 154.21
ACTIVE_H = 85.92


def box(x: float, y: float, z: float, w: float, h: float, d: float) -> cq.Workplane:
    return cq.Workplane("XY").box(w, h, d, centered=False).translate((x, y, z))


def board() -> cq.Workplane:
    # CadQuery fillets are applied after creating the board so the STEP remains
    # a real B-rep solid with rounded outer corners and through holes.
    part = cq.Workplane("XY").box(PCB_W, PCB_H, PCB_T, centered=False)
    for x in (HOLE_X0, HOLE_X0 + HOLE_DX):
        for y in (HOLE_Y0, HOLE_Y0 + HOLE_DY):
            cutter = (
                cq.Workplane("XY")
                .circle(HOLE_D / 2)
                .extrude(PCB_T + 1.0)
                .translate((x, y, -0.5))
            )
            part = part.cut(cutter)

    # Fillet only the four vertical outside corners, not the hole edges.
    return part.edges("|Z and (not %CIRCLE)").fillet(PCB_R)


def add_part(assy: cq.Assembly, part: cq.Workplane, name: str, color: cq.Color) -> None:
    assy.add(part, name=name, color=color)


def build() -> cq.Assembly:
    assy = cq.Assembly(name="MPI7002_7inch_HDMI_Display_C")

    add_part(assy, board(), "pcb_164p90x124p27x1p60", cq.Color(0.02, 0.14, 0.32, 1.0))

    add_part(
        assy,
        box(0, SCREEN_Y0, PCB_T, 164.90, 100.00, LCD_TAPE_T),
        "lcd_back_tape_2p00",
        cq.Color(0.02, 0.02, 0.02, 0.35),
    )
    add_part(
        assy,
        box(0, SCREEN_Y0, PCB_T + LCD_TAPE_T, 164.90, 100.00, LCD_T),
        "lcd_backlight_164p90x100p00x3p50",
        cq.Color(0.02, 0.02, 0.02, 1.0),
    )
    add_part(
        assy,
        box(
            (PCB_W - TOUCH_LENS_W) / 2,
            SCREEN_Y0 + (100.00 - TOUCH_LENS_H) / 2,
            PCB_T + LCD_TAPE_T + LCD_T + TOUCH_TAPE_T,
            TOUCH_LENS_W,
            TOUCH_LENS_H,
            TOUCH_T,
        ),
        "capacitive_touch_lens_164p28x99p17x1p48",
        cq.Color(0.01, 0.01, 0.012, 0.55),
    )
    add_part(
        assy,
        box(
            (PCB_W - ACTIVE_W) / 2,
            SCREEN_Y0 + (100.00 - ACTIVE_H) / 2,
            TOTAL_T - 0.04,
            ACTIVE_W,
            ACTIVE_H,
            0.03,
        ),
        "active_area_154p21x85p92_marker",
        cq.Color(0.04, 0.06, 0.08, 1.0),
    )
    add_part(
        assy,
        box(
            (PCB_W - TOUCH_VA_W) / 2,
            SCREEN_Y0 + (100.00 - TOUCH_VA_H) / 2,
            TOTAL_T - 0.01,
            TOUCH_VA_W,
            TOUCH_VA_H,
            0.01,
        ),
        "touch_visual_area_154p68x87p02_reference",
        cq.Color(0.8, 0.8, 0.8, 0.25),
    )

    # Approximate connector/component keepouts. These are intentionally named as
    # keepouts because the exact 3D details should be measured before enclosure
    # cutouts are finalized.
    keepouts = [
        ("hdmi_keepout_left_edge", -6.27, PCB_H - 34.0, PCB_T, 6.27, 14.0, 4.5),
        ("touch_usb_keepout_upper", -4.7, PCB_H - 58.0, PCB_T, 4.7, 8.0, 3.2),
        ("touch_usb_keepout_lower", -4.7, PCB_H - 78.0, PCB_T, 4.7, 8.0, 3.2),
        ("backlight_switch_keepout", -4.7, PCB_H - 96.0, PCB_T, 4.7, 8.5, 3.0),
        ("controller_ic_keepout", 68, 53, PCB_T, 24, 20, 1.5),
        ("ic_keepout_1", 118, 73, PCB_T, 12, 12, 2.0),
        ("ic_keepout_2", 139, 73, PCB_T, 12, 12, 2.0),
    ]
    for name, x, y, z, w, h, d in keepouts:
        add_part(assy, box(x, y, z, w, h, d), name, cq.Color(0.75, 0.75, 0.75, 1.0))

    return assy


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    assy = build()
    assy.save(str(OUT), exportType="STEP")
    OUT_STP.write_bytes(OUT.read_bytes())
    cq.exporters.export(assy.toCompound(), str(OUT_GITHUB_STL), tolerance=0.05, angularTolerance=0.1)
    print(OUT)
    print(OUT_STP)
    print(OUT_GITHUB_STL)


if __name__ == "__main__":
    main()
