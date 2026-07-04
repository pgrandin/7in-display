# Observed State

Captured on July 4, 2026 from the Linux desktop where the panel was first
tested.

## Detection Summary

The panel was detected by XRandR as `DP-4` and enabled successfully:

```text
DP-4 connected 1024x600+7280+0 (normal left inverted right x axis y axis) 255mm x 255mm
   1024x600      60.04*+
   1920x1080     60.00    50.00    59.94
   1280x1024     75.02    60.02
   1440x900      74.98    59.90
   1152x864      75.00
   1280x720      60.00    50.00    59.94
   1024x768      75.03    70.07    60.00
   832x624       74.55
   800x600       72.19    75.00    60.32    56.25
   720x576       50.00
   720x480       60.00    59.94
   640x480       75.00    72.81    60.00    59.94
   720x400       70.08
```

The active monitor layout after enabling it:

```text
Monitors: 5
 0: +*eDP-1 1920/366x1200/229+5360+0  eDP-1
 1: +DP-1 3440/800x1440/335+1920+0  DP-1
 2: +DP-2-2 1920/477x1080/268+0+0  DP-2-2
 3: +DP-4 1024/255x600/255+7280+0  DP-4
 4: +DVI-I-1-1 1920/477x1080/268+0+1080  DVI-I-1-1
```

Before enabling, `DP-4` appeared as connected but was not listed by
`xrandr --listmonitors`.

## XRandR Verbose Details

```text
Identifier: 0x46
Gamma: 1.0:1.0:1.0
Brightness: 1.0
CRTC: 3
subconnector: HDMI
link-status: Good
CONNECTOR_ID: 275
non-desktop: 0
```

Preferred/current mode:

```text
1024x600 (0xa7c) 49.000MHz -HSync +VSync *current +preferred
        h: width  1024 start 1029 end 1042 total 1312 skew    0 clock  37.35KHz
        v: height  600 start  602 end  605 total  622           clock  60.04Hz
```

EDID from `xrandr --verbose`:

```text
00ffffffffffff003609027001010101
2215010380291a78eee5b5a355499927
135054afef00714f81c0818081808180
9500950fd1c02413002041581620050d
2300ffff0000001c000000fc004d5049
373030320a2020202020000000fd0032
4c1e510e000a202020202020000000ff
004d5049373030320a2020202020014a
020321714e0607020315961112130414
051f90230907078301000065030c0010
008c0ad090204031200c405500b98821
000018011d8018711c1620582c2500b9
882100009e011d80d0721c1620102c25
80b9882100009e011d00bc52d01e20b8
285540b9882100001e023a80d072382d
40102c4580b9882100001e00000000d0
```

The EDID includes the display name `MPI7002` and serial text `MPI7002`.

## DRM State

Relevant connector statuses:

```text
/sys/class/drm/card0-DP-4/status: connected
/sys/class/drm/card0-DP-1/status: connected
/sys/class/drm/card0-DP-2/status: disconnected
/sys/class/drm/card0-DP-3/status: disconnected
/sys/class/drm/card0-DP-5/status: disconnected
/sys/class/drm/card0-DP-6/status: connected
/sys/class/drm/card0-eDP-1/status: connected
/sys/class/drm/card2-DVI-I-1/status: connected
```

Modes exposed at `/sys/class/drm/card0-DP-4/modes` started with:

```text
1024x600
1920x1080
1920x1080
1920x1080
1920x1080
1280x1024
1280x1024
1440x900
1440x900
1152x864
```

## USB and Touch

Relevant `lsusb` lines:

```text
Bus 001 Device 048: ID 2109:2211 VIA Labs, Inc. USB2.0 Hub
Bus 001 Device 049: ID 413c:b080 Dell Computer Corp. Dell DA20 Adapter
Bus 001 Device 050: ID 0484:5750 Specialix MPI7002
Bus 004 Device 013: ID 2109:0211 VIA Labs, Inc. USB3.0 Hub
Bus 006 Device 009: ID 17e9:6000 DisplayLink Subosen DL6350
```

Relevant kernel messages at connection time:

```text
usb 1-1.2: Product: Dell DA20 Adapter
usb 1-1.2: Manufacturer: Luxshare
usb 1-1.1: Product: MPI7002
usb 1-1.1: Manufacturer: QDTECH MPI700
usb 1-1.1: SerialNumber: STM32
input: QDTECH MPI700 MPI7002 as /devices/pci0000:00/0000:00:14.0/usb1/1-1/1-1.1/1-1.1:1.0/0003:0484:5750.0013/input/input42
hid-multitouch 0003:0484:5750.0013: input,hiddev100,hidraw8: USB HID v1.01 Device [QDTECH MPI700 MPI7002] on usb-0000:00:14.0-1.1/input0
```

The original dmesg output contained an odd combining character in
`QDTECH MPI700`; the normalized name is used here for readability.

XInput list entry:

```text
QDTECH MPI700 MPI7002  id=20  [slave pointer (2)]
```

Touch properties after mapping to `DP-4`:

```text
Device Enabled: 1
Coordinate Transformation Matrix:
  0.123314, 0.000000, 0.876686,
  0.000000, 0.277778, 0.000000,
  0.000000, 0.000000, 1.000000
libinput Rotation Angle: 0.000000
libinput Calibration Matrix:
  1.000000, 0.000000, 0.000000,
  0.000000, 1.000000, 0.000000,
  0.000000, 0.000000, 1.000000
Device Node: "/dev/input/event24"
Device Product ID: 1156, 22352
```

`1156, 22352` is decimal for USB ID `0484:5750`.

## Brightness Findings

No hardware backlight interface for this panel was exposed:

```text
/sys/class/backlight/intel_backlight
  actual_brightness=504
  brightness=504
  max_brightness=504
  type=raw
```

There were no `/dev/i2c-*` devices visible during setup, and `ddcutil`,
`brightnessctl`, and `light` were not installed. `xbacklight` was installed but
is not useful for targeting this HDMI-style external panel.

The working control path is:

```bash
xrandr --output DP-4 --brightness <value>
```

Tested values:

```text
1.00 -> normal
0.70 -> visibly dimmer
0.05 -> used as practical minimum for the loop's 0% step
```

The loop test successfully stepped:

```text
0% -> 0.05
10% -> 0.10
20% -> 0.20
30% -> 0.30
40% -> 0.40
50% -> 0.50
60% -> 0.60
70% -> 0.70
80% -> 0.80
90% -> 0.90
100% -> 1.00
```
