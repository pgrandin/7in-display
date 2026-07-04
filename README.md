# 7in Display Notes

This repo documents the 7in display connected to Pierre's Linux desktop and
keeps the small control script used to manage it.

## Observed Hardware

- Display name from EDID: `MPI7002`
- Display connector in XRandR: `DP-4`
- Native mode: `1024x600 @ 60.04 Hz`
- Reported physical size: `255mm x 255mm`
- USB touch device: `QDTECH MPI700 MPI7002`
- USB touch product ID: `0484:5750`
- Touch input device observed at setup time: `/dev/input/event24`
- Adapter path observed in `lsusb`:
  - `413c:b080` Dell DA20 Adapter
  - `2109:2211` VIA Labs USB2.0 Hub
  - `2109:0211` VIA Labs USB3.0 Hub
- DisplayLink device also present on the host: `17e9:6000 DisplayLink Subosen DL6350`

## Working Display Setup

The display was detected but initially was not part of the active desktop
layout. This enabled it at native resolution to the right of the existing
desktop:

```bash
xrandr --output DP-4 --mode 1024x600 --pos 7280x0
```

After enabling it, `xrandr --listmonitors` showed:

```text
DP-4 1024/255x600/255+7280+0
```

The full active mode line observed for the panel:

```text
DP-4 connected 1024x600+7280+0
1024x600 60.04*+
```

## Touch Mapping

The USB touch controller appears in XInput as:

```text
QDTECH MPI700 MPI7002
```

At setup time the XInput device id was `20`. The id can change after reboot or
replug, so find it with:

```bash
xinput list
```

Map the touch area to the panel:

```bash
xinput map-to-output 20 DP-4
```

After mapping, the observed coordinate transform was:

```text
0.123314, 0.000000, 0.876686,
0.000000, 0.277778, 0.000000,
0.000000, 0.000000, 1.000000
```

## Brightness

The panel does not expose a kernel backlight device on this host. The only
device under `/sys/class/backlight` was the laptop panel:

```text
/sys/class/backlight/intel_backlight
actual_brightness=504
brightness=504
max_brightness=504
type=raw
```

No `/dev/i2c-*` device was visible and `ddcutil` was not installed, so hardware
DDC brightness was not available during setup.

Brightness control here uses XRandR's per-output software brightness multiplier
for `DP-4`. This changes the rendered image intensity but does not change the
panel backlight power.

## Brightness Script

Use `./7in-brightness`:

```bash
./7in-brightness get
./7in-brightness set 0.70
./7in-brightness down
./7in-brightness up
./7in-brightness set 1.00
```

Loop from 0% to 100% in 10% increments:

```bash
./7in-brightness loop
```

Use a custom delay between steps:

```bash
./7in-brightness loop 0.2
```

Stop the loop with `Ctrl-C`.

XRandR does not use percentage values directly. The loop maps:

- `0%` to `0.05`, because `0.00` effectively blanks the output
- `10%` to `0.10`
- `20%` to `0.20`
- ...
- `100%` to `1.00`

The script allows values from `0.05` to `1.50`. `1.00` is normal brightness.

## Useful Commands

Inspect the display:

```bash
xrandr --query
xrandr --verbose
xrandr --listmonitors
```

Inspect touch:

```bash
xinput list
xinput list-props <device-id>
```

Inspect USB:

```bash
lsusb
dmesg | tail -n 120
```

Restore the observed working state:

```bash
xrandr --output DP-4 --mode 1024x600 --pos 7280x0 --brightness 1.00
xinput map-to-output 20 DP-4
```

If the XInput id changes, replace `20` with the current `QDTECH MPI700 MPI7002`
device id from `xinput list`.
