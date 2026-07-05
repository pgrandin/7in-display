// LCDwiki MPI7002 / 7inch HDMI Display-C mechanical reference model.
// Units: millimeters.
//
// Dimensions come from the official LCM outline drawing (MPI7002_Size.pdf,
// V1.0, 2024-2-21) cross-checked against MPI7002_Product_Dimensions.png.
// Origin: lower-left PCB corner viewed from the front (screen side).
// +X right, +Y up, +Z out of the screen. z=0 is the PCB back face
// (component side); connectors extend into -Z.

$fn = 64;

// The board is not a plain rectangle: the main body is 164.90 x 106.96 and
// four 8.00-wide mounting ears at the corners extend it to 124.27 overall.
// All outline corners are R4.00, making the ear tips semicircular.
pcb_w = 164.90;
pcb_h = 124.27;
pcb_t = 1.60;
pcb_r = 4.00;
body_h = 106.96;
ear_w = 8.00;
notch_d = (pcb_h - body_h) / 2; // 8.655 recess on top and bottom edges

// 4x Ø3.00 holes centered in the ears, 156.90 x 114.96 spacing
// (4.00 / 4.655 from the edges).
hole_d = 3.00;
hole_dx = 156.90;
hole_dy = 114.96;
hole_x0 = (pcb_w - hole_dx) / 2;
hole_y0 = (pcb_h - hole_dy) / 2;

// Stack, back to front: PCB, LCD back tape, LCD, CTP back tape, CTP lens.
lcd_tape_t = 2.00;
lcd_t = 3.50;
touch_tape_t = 0.30;
touch_t = 1.48;
total_t = pcb_t + lcd_tape_t + lcd_t + touch_tape_t + touch_t; // 8.88

z_lcd_tape = pcb_t;
z_lcd = z_lcd_tape + lcd_tape_t;
z_touch_tape = z_lcd + lcd_t;
z_touch = z_touch_tape + touch_tape_t;

// Layer footprints. Horizontal offsets are from the right (connector)
// edge, vertical offsets from the top edge, per the drawing's front view.
lcd_bl_w = 164.90; lcd_bl_h = 100.00; lcd_bl_top = 9.52;
lens_w = 164.28; lens_h = 99.17; lens_right = 0.21; lens_top = 10.08;
va_w = 154.68; va_h = 87.02; va_right = 6.75; va_top = 13.80;
aa_w = 154.21; aa_h = 85.92; aa_right = 6.99; aa_top = 14.35;

// Connectors on the right edge, mounted on the PCB back face (-Z).
// Vertical centers from the drawing's dimension chain; HDMI height 6.27
// from the drawing, other body sizes are standard receptacle dimensions.
hdmi_cy = pcb_h - (4.66 + 15.59); // 104.02
usb1_cy = hdmi_cy - 18.37;        // 85.65
usb2_cy = usb1_cy - 13.11;        // 72.54
sw_cy = usb2_cy - 11.14;          // 61.40

// Mounting ear: stadium shape from the semicircular tip (R4) hulled with
// its root on the body edge. tip_y is the tip arc center.
module ear_2d(cx, tip_y, root_y) {
  hull() {
    translate([cx, tip_y]) circle(r = pcb_r);
    translate([cx - ear_w / 2, min(tip_y, root_y)])
      square([ear_w, abs(root_y - tip_y)]);
  }
}

// Board outline: recessed body plus four corner ears. The concave R4.00
// root fillets of the STEP model are omitted here (cosmetic).
module pcb_outline_2d() {
  translate([0, notch_d]) square([pcb_w, body_h]);
  for (cx = [ear_w / 2, pcb_w - ear_w / 2]) {
    ear_2d(cx, pcb_h - pcb_r, pcb_h - notch_d); // top ears
    ear_2d(cx, pcb_r, notch_d);                 // bottom ears
  }
}

module board() {
  color("#173d73")
    difference() {
      linear_extrude(height = pcb_t)
        pcb_outline_2d();

      for (x = [hole_x0, hole_x0 + hole_dx])
        for (y = [hole_y0, hole_y0 + hole_dy])
          translate([x, y, -0.5])
            cylinder(h = pcb_t + 1.0, d = hole_d);
    }
}

module screen_stack() {
  // LCD back tape layer.
  color([0.1, 0.1, 0.1, 0.35])
    translate([0, pcb_h - lcd_bl_top - lcd_bl_h, z_lcd_tape])
      cube([lcd_bl_w, lcd_bl_h, lcd_tape_t]);

  // Backlight/LCD block.
  color("#1b1b1b")
    translate([0, pcb_h - lcd_bl_top - lcd_bl_h, z_lcd])
      cube([lcd_bl_w, lcd_bl_h, lcd_t]);

  // CTP back tape.
  color([0.1, 0.1, 0.1, 0.35])
    translate([pcb_w - lens_right - lens_w, pcb_h - lens_top - lens_h, z_touch_tape])
      cube([lens_w, lens_h, touch_tape_t]);

  // Capacitive touch glass/lens.
  color([0.02, 0.02, 0.025, 0.62])
    translate([pcb_w - lens_right - lens_w, pcb_h - lens_top - lens_h, z_touch])
      cube([lens_w, lens_h, touch_t]);

  // LCD active area marker, just under the glass surface.
  color([0.05, 0.08, 0.10, 0.92])
    translate([pcb_w - aa_right - aa_w, pcb_h - aa_top - aa_h, total_t - 0.04])
      cube([aa_w, aa_h, 0.03]);

  // CTP visual-area outline.
  color([0.9, 0.9, 0.9, 0.35])
    translate([pcb_w - va_right - va_w, pcb_h - va_top - va_h, total_t - 0.01])
      difference() {
        cube([va_w, va_h, 0.01]);
        translate([(va_w - aa_w) / 2, (va_h - aa_h) / 2, -0.01])
          cube([aa_w, aa_h, 0.03]);
      }
}

// Connector body flush with the right PCB edge, on the back face.
module edge_connector(cy, w, depth, t) {
  translate([pcb_w - depth, cy - w / 2, -t])
    cube([depth, w, t]);
}

module connectors() {
  // HDMI type A receptacle ("Display").
  color("#c8c8c8") edge_connector(hdmi_cy, 15.00, 11.60, 6.27);

  // Two micro-USB receptacles (silkscreened "Touch").
  color("#d0d0d0") edge_connector(usb1_cy, 7.70, 5.40, 2.45);
  color("#d0d0d0") edge_connector(usb2_cy, 7.70, 5.40, 2.45);

  // Backlight slide switch (ON/OFF).
  color("#eeeeee") edge_connector(sw_cy, 9.00, 4.20, 3.60);
}

module labels() {
  color("white")
    translate([112, 37, -0.05])
      rotate([180, 0, 0])
        linear_extrude(height = 0.05)
          text("MPI7002", size = 7, halign = "left", valign = "center");
}

module mpi7002() {
  board();
  screen_stack();
  connectors();
  labels();
}

mpi7002();
