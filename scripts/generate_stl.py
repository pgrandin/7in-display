#!/usr/bin/env python3
"""Generate a simple STL envelope model for the MPI7002 display.

The authoritative editable CAD source is cad/MPI7002.scad. This STL generator
exists because OpenSCAD is not installed on the current workstation.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sin
from pathlib import Path


OUT = Path("cad/MPI7002_envelope.stl")


@dataclass(frozen=True)
class Box:
    name: str
    x: float
    y: float
    z: float
    w: float
    h: float
    d: float


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

LCD_T = 3.50
LCD_TAPE_T = 2.00
TOUCH_T = 1.48
TOUCH_TAPE_T = 0.30

SCREEN_Y0 = PCB_H - 100.00
TOUCH_LENS_W = 164.28
TOUCH_LENS_H = 99.17
ACTIVE_W = 154.21
ACTIVE_H = 85.92


def fmt(v: tuple[float, float, float]) -> str:
    return f"{v[0]:.5f} {v[1]:.5f} {v[2]:.5f}"


def normal(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    mag = (nx * nx + ny * ny + nz * nz) ** 0.5 or 1
    return nx / mag, ny / mag, nz / mag


def tri(lines, a, b, c):
    n = normal(a, b, c)
    lines.append(f"  facet normal {fmt(n)}")
    lines.append("    outer loop")
    lines.append(f"      vertex {fmt(a)}")
    lines.append(f"      vertex {fmt(b)}")
    lines.append(f"      vertex {fmt(c)}")
    lines.append("    endloop")
    lines.append("  endfacet")


def box(lines, box_: Box):
    x, y, z, w, h, d = box_.x, box_.y, box_.z, box_.w, box_.h, box_.d
    v = [
        (x, y, z),
        (x + w, y, z),
        (x + w, y + h, z),
        (x, y + h, z),
        (x, y, z + d),
        (x + w, y, z + d),
        (x + w, y + h, z + d),
        (x, y + h, z + d),
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
    ]
    for a, b, c, d_ in faces:
        tri(lines, v[a], v[b], v[c])
        tri(lines, v[a], v[c], v[d_])


def cylinder(lines, name, cx, cy, z, diameter, height, segments=32):
    r = diameter / 2
    bottom = [(cx + r * cos(2 * pi * i / segments),
               cy + r * sin(2 * pi * i / segments), z)
              for i in range(segments)]
    top = [(x, y, z + height) for x, y, _ in bottom]
    center_bottom = (cx, cy, z)
    center_top = (cx, cy, z + height)
    for i in range(segments):
        j = (i + 1) % segments
        tri(lines, bottom[i], bottom[j], top[j])
        tri(lines, bottom[i], top[j], top[i])
        tri(lines, center_bottom, bottom[i], bottom[j])
        tri(lines, center_top, top[j], top[i])


def main():
    boxes = [
        Box("pcb", 0, 0, 0, PCB_W, PCB_H, PCB_T),
        Box("lcd_back_tape", 0, SCREEN_Y0, PCB_T, 164.90, 100.00, LCD_TAPE_T),
        Box("lcd_backlight", 0, SCREEN_Y0, PCB_T + LCD_TAPE_T, 164.90, 100.00, LCD_T),
        Box("touch_lens", (PCB_W - TOUCH_LENS_W) / 2,
            SCREEN_Y0 + (100.00 - TOUCH_LENS_H) / 2,
            PCB_T + LCD_TAPE_T + LCD_T + TOUCH_TAPE_T,
            TOUCH_LENS_W, TOUCH_LENS_H, TOUCH_T),
        Box("active_area_marker", (PCB_W - ACTIVE_W) / 2,
            SCREEN_Y0 + (100.00 - ACTIVE_H) / 2,
            TOTAL_T - 0.04,
            ACTIVE_W, ACTIVE_H, 0.03),
        Box("hdmi_keepout", -6.27, PCB_H - 34.0, PCB_T, 6.27, 14.0, 4.5),
        Box("usb_keepout_1", -4.7, PCB_H - 58.0, PCB_T, 4.7, 8.0, 3.2),
        Box("usb_keepout_2", -4.7, PCB_H - 78.0, PCB_T, 4.7, 8.0, 3.2),
        Box("backlight_switch_keepout", -4.7, PCB_H - 96.0, PCB_T, 4.7, 8.5, 3.0),
        Box("controller_keepout", 68, 53, PCB_T, 24, 20, 1.5),
        Box("ic_keepout_1", 118, 73, PCB_T, 12, 12, 2.0),
        Box("ic_keepout_2", 139, 73, PCB_T, 12, 12, 2.0),
    ]

    lines = ["solid MPI7002_envelope"]
    for item in boxes:
        box(lines, item)

    # Visualize the mounting holes as vertical cylinders. In the SCAD source
    # they are real subtracted holes; here they are reference markers.
    for x in (HOLE_X0, HOLE_X0 + HOLE_DX):
        for y in (HOLE_Y0, HOLE_Y0 + HOLE_DY):
            cylinder(lines, "mount_hole_marker", x, y, PCB_T, HOLE_D, 0.8)

    lines.append("endsolid MPI7002_envelope")
    OUT.write_text("\n".join(lines) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
