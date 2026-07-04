// LCDwiki MPI7002 / 7inch HDMI Display-C mechanical reference model.
// Units: millimeters.
//
// This is an envelope and mounting model, not a board-level component model.
// Dimensions come from LCDwiki MPI7002 public product dimensions/datasheet.

$fn = 64;

pcb_w = 164.90;
pcb_h = 124.27;
pcb_t = 1.60;
pcb_r = 4.00;

hole_d = 3.00;
hole_dx = 148.90;
hole_dy = 114.96;
hole_x0 = (pcb_w - hole_dx) / 2;
hole_y0 = (pcb_h - hole_dy) / 2;

total_t = 8.88;
lcd_t = 3.50;
touch_t = 1.48;
touch_tape_t = 0.30;
lcd_tape_t = 2.00;

touch_lens_w = 164.28;
touch_lens_h = 99.17;
touch_va_w = 154.68;
touch_va_h = 87.02;
active_w = 154.21;
active_h = 85.92;

// The drawing gives exact sizes but the OCR text does not expose every origin.
// The lens/backlight stack is modeled top-aligned with the PCB, leaving the
// lower electronics strip visible.
screen_y0 = pcb_h - 100.00;
screen_x0 = (pcb_w - touch_lens_w) / 2;

module rounded_rect_2d(w, h, r) {
  offset(r = r)
    square([w - 2 * r, h - 2 * r], center = true);
}

module board() {
  color("#173d73")
    difference() {
      linear_extrude(height = pcb_t)
        translate([pcb_w / 2, pcb_h / 2, 0])
          rounded_rect_2d(pcb_w, pcb_h, pcb_r);

      for (x = [hole_x0, hole_x0 + hole_dx])
        for (y = [hole_y0, hole_y0 + hole_dy])
          translate([x, y, -0.5])
            cylinder(h = pcb_t + 1.0, d = hole_d);
    }
}

module screen_stack() {
  // LCD back tape layer.
  color([0.1, 0.1, 0.1, 0.35])
    translate([(pcb_w - 164.90) / 2, screen_y0, pcb_t])
      cube([164.90, 100.00, lcd_tape_t]);

  // Backlight/LCD block.
  color("#1b1b1b")
    translate([(pcb_w - 164.90) / 2, screen_y0, pcb_t + lcd_tape_t])
      cube([164.90, 100.00, lcd_t]);

  // Capacitive touch glass/lens.
  color([0.02, 0.02, 0.025, 0.62])
    translate([screen_x0, screen_y0 + (100.00 - touch_lens_h) / 2,
               pcb_t + lcd_tape_t + lcd_t + touch_tape_t])
      cube([touch_lens_w, touch_lens_h, touch_t]);

  // Visible active area marker, slightly above glass.
  color([0.05, 0.08, 0.10, 0.92])
    translate([(pcb_w - active_w) / 2,
               screen_y0 + (100.00 - active_h) / 2,
               total_t - 0.04])
      cube([active_w, active_h, 0.03]);

  // Visual-area outline.
  color([0.9, 0.9, 0.9, 0.35])
    translate([(pcb_w - touch_va_w) / 2,
               screen_y0 + (100.00 - touch_va_h) / 2,
               total_t - 0.01])
      difference() {
        cube([touch_va_w, touch_va_h, 0.01]);
        translate([(touch_va_w - active_w) / 2,
                   (touch_va_h - active_h) / 2, -0.01])
          cube([active_w, active_h, 0.03]);
      }
}

module connector_envelopes() {
  // Approximate back-side keepout envelopes based on the product drawing.
  // These are intentionally conservative and should be measured before making
  // a tight enclosure.

  // HDMI connector on left edge near the top.
  color("#c8c8c8")
    translate([-6.27, pcb_h - 34.0, pcb_t])
      cube([6.27, 14.0, 4.5]);

  // Two Micro-USB touch/power connectors on left edge.
  for (y = [pcb_h - 58.0, pcb_h - 78.0])
    color("#d0d0d0")
      translate([-4.7, y, pcb_t])
        cube([4.7, 8.0, 3.2]);

  // Backlight switch on left edge.
  color("#eeeeee")
    translate([-4.7, pcb_h - 96.0, pcb_t])
      cube([4.7, 8.5, 3.0]);

  // Representative controller IC and passives keepout on back.
  color("#202020")
    translate([68, 53, pcb_t])
      cube([24, 20, 1.5]);

  color("#202020")
    translate([118, 73, pcb_t])
      cube([12, 12, 2.0]);

  color("#202020")
    translate([139, 73, pcb_t])
      cube([12, 12, 2.0]);
}

module labels() {
  color("white")
    translate([112, 37, pcb_t + 0.05])
      linear_extrude(height = 0.05)
        text("MPI7002", size = 7, halign = "left", valign = "center");

  color("white")
    translate([112, 27, pcb_t + 0.05])
      linear_extrude(height = 0.05)
        text("1024x600", size = 4, halign = "left", valign = "center");
}

module mpi7002() {
  board();
  screen_stack();
  connector_envelopes();
  labels();
}

mpi7002();
