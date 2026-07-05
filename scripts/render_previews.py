#!/usr/bin/env python3
"""Render README preview images of the case assembly.

Tessellates the CadQuery models and renders them offscreen with VTK
(proper z-buffer, phong shading, smooth normals with crisp feature
edges, multisample antialiasing). Outputs docs/render_assembly.png and
docs/render_exploded.png.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import vtk

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_step as disp
import generate_panel as panel
import generate_case as case


OUT_DIR = Path("docs")

DISPLAY_COLORS = {
    "pcb_164p90x124p27x1p60": (0.10, 0.23, 0.42),
    "lcd_back_tape_2p00": (0.15, 0.16, 0.17),
    "lcd_backlight_164p90x100p00x3p50": (0.13, 0.13, 0.15),
    "ctp_back_tape_0p30": (0.15, 0.16, 0.17),
    "capacitive_touch_lens_164p28x99p17x1p48": (0.08, 0.08, 0.10),
    "lcd_active_area_154p21x85p92_marker": (0.04, 0.08, 0.13),
    "ctp_visual_area_154p68x87p02_reference": (0.13, 0.14, 0.16),
    "hdmi_a_receptacle": (0.73, 0.75, 0.77),
    "micro_usb_touch_upper": (0.73, 0.75, 0.77),
    "micro_usb_touch_lower": (0.73, 0.75, 0.77),
    "backlight_switch": (0.80, 0.82, 0.84),
}
PI_COLORS = {
    "pi5_board_85x56_approx": (0.18, 0.43, 0.28),
    "pi5_usb_eth_stack_approx": (0.66, 0.68, 0.70),
    "pi5_usbc_hdmi_row_approx": (0.66, 0.68, 0.70),
    "pi5_soc_cooler_approx": (0.56, 0.59, 0.61),
    "pi5_gpio_header_approx": (0.20, 0.21, 0.23),
}
PANEL_COLOR = (0.56, 0.60, 0.63)
CASE_COLOR = (0.29, 0.32, 0.36)


def to_polydata(workplane) -> vtk.vtkPolyData:
    shape = workplane.val() if hasattr(workplane, "val") else workplane
    verts, faces = shape.tessellate(0.08, 0.15)
    points = vtk.vtkPoints()
    for p in verts:
        points.InsertNextPoint(p.x, p.y, p.z)
    cells = vtk.vtkCellArray()
    for f in faces:
        cells.InsertNextCell(3)
        for i in f:
            cells.InsertCellPoint(i)
    pd = vtk.vtkPolyData()
    pd.SetPoints(points)
    pd.SetPolys(cells)
    return pd


def make_actor(workplane, color, metallic=False) -> vtk.vtkActor:
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(to_polydata(workplane))
    normals.SetFeatureAngle(40.0)
    normals.SplittingOn()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    prop = actor.GetProperty()
    prop.SetColor(*color)
    prop.SetInterpolationToPhong()
    if metallic:
        prop.SetSpecular(0.55)
        prop.SetSpecularPower(45)
    else:
        prop.SetSpecular(0.15)
        prop.SetSpecularPower(18)
    return actor


def assembly_actors(explode: float = 0.0) -> list[vtk.vtkActor]:
    actors = []

    def add(workplane, color, dz, metallic=False):
        a = make_actor(workplane, color, metallic)
        a.SetPosition(0.0, 0.0, dz)
        actors.append(a)

    for child in disp.build().children:
        metallic = "receptacle" in child.name or "usb" in child.name or "switch" in child.name
        add(child.obj, DISPLAY_COLORS.get(child.name, (0.5, 0.5, 0.5)), explode * 1.0, metallic)
    add(panel.build_panel(), PANEL_COLOR, explode * 2.0)
    add(case.build_case(), CASE_COLOR, 0.0)
    for child in case.build_pi_mock().children:
        metallic = "stack" in child.name or "row" in child.name
        add(child.obj, PI_COLORS.get(child.name, (0.5, 0.5, 0.5)), 0.0, metallic)
    return actors


def render(actors, out: Path, elev_deg: float, azim_deg: float,
           center: tuple[float, float, float], distance: float) -> None:
    ren = vtk.vtkRenderer()
    ren.SetBackground(1.0, 1.0, 1.0)
    for a in actors:
        ren.AddActor(a)

    kit = vtk.vtkLightKit()
    kit.SetKeyLightIntensity(1.0)
    kit.SetKeyToFillRatio(2.2)
    kit.SetKeyToHeadRatio(6.0)
    kit.AddLightsToRenderer(ren)

    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetSize(1500, 1100)
    win.SetMultiSamples(8)
    win.AddRenderer(ren)

    elev, azim = math.radians(elev_deg), math.radians(azim_deg)
    direction = (
        math.cos(elev) * math.cos(azim),
        math.cos(elev) * math.sin(azim),
        math.sin(elev),
    )
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(*center)
    cam.SetPosition(*(c + d * distance for c, d in zip(center, direction)))
    cam.SetViewUp(0, 0, 1)
    cam.SetViewAngle(24)
    ren.ResetCameraClippingRange()

    win.Render()
    grab = vtk.vtkWindowToImageFilter()
    grab.SetInput(win)
    grab.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(out))
    writer.SetInputConnection(grab.GetOutputPort())
    writer.Write()
    print(out)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    render(assembly_actors(0.0), OUT_DIR / "render_assembly.png",
           elev_deg=32, azim_deg=-58, center=(96.5, 62.0, -6.0), distance=520)
    render(assembly_actors(28.0), OUT_DIR / "render_exploded.png",
           elev_deg=20, azim_deg=-58, center=(96.5, 62.0, 22.0), distance=640)


if __name__ == "__main__":
    main()
