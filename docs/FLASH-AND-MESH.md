# Ender-5 Pro r3 — 5x5 manual mesh

For the stock Ender-5 Pro with the photographed Creality V4.2.2 STM32F103RET6 board, code-A standalone drivers, original knob display, and no probe.

This revision changes the manual mesh from 3x3 to 5x5: 25 measurements. The mesh still spans X/Y 10–210 mm, now at 50 mm intervals (10, 60, 110, 160, 210). Marlin's existing measurement wizard, mesh interpolation, editor, and EEPROM storage use the new compile-time dimensions. No runtime grid-size selector was added.

All r2 performance features and motion/temperature settings remain configured as before. Input Shaping starts at F0 and Linear Advance at K0 until calibrated. The display identifies this version as **Ender-5 Pro r3**.

## Flash and migrate from r2

1. Record any calibration values you changed after installing r2, especially E steps, PID, acceleration, Input Shaping, and Linear Advance. Use `M503` or photograph the LCD settings. Initializing EEPROM restores the firmware defaults.
2. Copy only **E5P5X5R3.bin** to the root of a FAT32 microSD card. Remove other firmware `.bin` files from that card, keeping your backups on the computer.
3. Power off, insert the card, then power on and wait for normal startup. Confirm **Ender-5 Pro r3**.
4. If asked to initialize EEPROM, select **Reset**. This loads and saves the new defaults. Otherwise use **Initialize EEPROM**, or `M502` followed by `M500`.
5. Reapply only known calibration values recorded in step 1. Do not restore the old 3x3 mesh. The grid and EEPROM layout changed, so measure a fresh 5x5 mesh.

## Measure and use the new mesh

1. Home carefully and check normal motion and temperature readings. Bring the bed to the temperature at which you will measure it and tram the corners.
2. Open **Motion > Bed Leveling > Level Bed** and complete all **25** measurements. The on-screen progress should now end at 25/25.
3. Select **Store Settings** (`M500`) to save the mesh.
4. Keep these commands in Cura's Start G-code, in this order:

```gcode
G28       ; Home
M420 S1   ; Enable the saved mesh
```

The mesh coordinates survive power-off; the enabled state does not. Marlin performs the Z compensation while printing, with the existing 10 mm fade height. Cura does not need the mesh coordinates.

The firmware has been compiled and checked; physical operation of this 5x5 revision still requires verification on the printer. See [verification results](../verification/r3/build-checks.json). This repository contains the complete configured Marlin 2.1.2.8 source and GPL license.

To rebuild from extracted source with PlatformIO: `python -m platformio run -e STM32F103RE_creality`.

