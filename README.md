# Ender-5 Pro — Custom Marlin

Marlin 2.1.2.8 configured for an original Ender-5 Pro with a Creality V4.2.2 board, STM32F103RET6 processor, TMC2208 standalone drivers (SD-slot code A), original knob display, and no bed probe. Other processors or board variants require reviewing the configuration before use.

## r3: 5×5 manual mesh

[Download E5P5X5R3.bin](firmware/r3/E5P5X5R3.bin) using GitHub's **Download raw file** button. The file should be 171,096 bytes. [Read the flashing and mesh instructions](docs/FLASH-AND-MESH.md) before installation.

- Guided 25-point manual mesh, 10–210 mm on X/Y, with 10 mm compensation fade.
- X/Y ZV Input Shaping with LCD controls and `M593`.
- Linear Advance 1.5 with `M900`.
- Adaptive Step Smoothing and a 32-block planner buffer.
- Serial emergency parser, thermal protection, watchdog, SDIO, and onboard EEPROM.

Input Shaping starts at F0 and Linear Advance at K0: both require calibration on the actual printer. Default motion limits are conservative. A successful build is not a physical print-quality or stability test.

The measured mesh persists after **Store Settings** (`M500`), but its enabled state does not persist after power-off. After creating a valid mesh, use this order at the start of a print:

```gcode
G28
M420 S1
```

When upgrading from r2, record existing calibration values, initialize the new settings, and measure a fresh 5×5 mesh. The old 3×3 mesh must not be reused.

## Verification

r3 compiled with no compiler warnings or errors and passed 109 effective-configuration checks. Compiled symbols/debug information confirm 25 wizard points and a 100-byte mesh array. EEPROM settings occupy 688 bytes plus a 100-byte offset within the 2,048-byte storage capacity.

| Metric | r3 |
|---|---:|
| Application flash | 170,524 / 495,616 bytes |
| Static RAM | 19,396 / 65,536 bytes |
| Binary length | 171,096 bytes |
| Application start | `0x08007000` |

SHA-256 of `E5P5X5R3.bin`:

```text
8be3ccfed4aa0d082ab25210aace16fedd140b366f88230598181a46f27b8b79
```

[Machine-readable verification](verification/r3/build-checks.json). Runtime memory peaks and operation of this revision on the physical printer have not been measured.

## Build

Install Python and PlatformIO, then run from this repository:

```sh
python -m pip install platformio==6.2.0
python -m platformio run -e STM32F103RE_creality
```

Build outputs appear under `.pio/build/STM32F103RE_creality/`. Build timestamps change the output checksum. The included build audit checks the target hardware, protections, and expected features before compilation.

The tested toolchain uses ST STM32 platform 12.1.1, STM32 Arduino framework 1.9.0, CMSIS 5.5.1, GCC ARM 9.2.1, and U8glib-HAL 0.5.4. Dependencies are downloaded by PlatformIO; this repository is not an offline toolchain bundle.

## Source and license

This repository is a configured source snapshot based on [Marlin 2.1.2.8](https://github.com/MarlinFirmware/Marlin/tree/1cd56c4ccd483045eb5a92c99e3ad3b5ab1bea6d), with the [official Ender-5 Pro V422 configuration](https://github.com/MarlinFirmware/Configurations/tree/f083973abeb6ece641e3437ddf03dc43a268c6a4/config/examples/Creality/Ender-5%20Pro/CrealityV422) as its starting point. The original upstream Git history is not included in this snapshot.

Customization is primarily in `Marlin/Configuration.h`, `Marlin/Configuration_adv.h`, `platformio.ini`, and `buildroot/share/PlatformIO/scripts/ender5_audit.py`. A small change in `Marlin/src/lcd/menu/menu_advanced.cpp` allows enabling input shaping from the LCD when its startup frequency is zero; the menu uses 20 Hz as an initial calibration value, not a measured resonance.

Marlin and the included modifications are distributed under the [GNU GPL v3 or later](LICENSE). Upstream copyright notices and the [original Marlin README](docs/MARLIN-UPSTREAM-README.md) are retained.

