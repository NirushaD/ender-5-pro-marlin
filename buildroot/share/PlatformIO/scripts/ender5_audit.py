"""Check this printer's effective configuration before a PlatformIO build.

Uses Marlin's compiler-preprocessed feature set, not commented configuration text.
These checks validate configuration choices, not physical printer behavior.
"""
import hashlib
import json
from pathlib import Path
import pioutil

if pioutil.is_pio_build():
    env = pioutil.env
    features = dict(env["MARLIN_FEATURES"])
    checks = []

    def check(name, condition):
        checks.append({"check": name, "passed": bool(condition)})

    def resolve(value):
        value = str(value).strip()
        seen = set()
        while value in features and value not in seen:
            seen.add(value)
            value = str(features[value]).strip()
        return value

    def enabled(name):
        return name in features and resolve(features[name]).lower() not in ("0", "false")

    def equal(name, expected):
        actual = resolve(features.get(name, "<undefined>"))
        check(name + " = " + str(expected), "".join(actual.split()) == "".join(resolve(expected).split()))

    check("STM32F103RE Creality environment", env["PIOENV"] == "STM32F103RE_creality")
    check("512 KiB STM32F103RE board", env["BOARD"] == "genericSTM32F103RE")
    board = env.BoardConfig()
    check("28 KiB bootloader offset", int(str(board.get("build.offset")), 0) == 0x7000)
    check("64 KiB physical SRAM", int(board.get("upload.maximum_ram_size")) == 65536)
    equal("MOTHERBOARD", "BOARD_CREALITY_V422")
    equal("SERIAL_PORT", 1)
    equal("BAUDRATE", 115200)
    for axis in ("X", "Y", "Z", "E0"):
        equal(axis + "_DRIVER_TYPE", "TMC2208_STANDALONE")
        equal(axis + "_ENABLE_PIN", "PC3")
        equal("INVERT_" + axis + "_DIR", "false")
    for name, value in {
        "EXTRUDERS": 1, "TEMP_SENSOR_0": 1, "TEMP_SENSOR_BED": 1,
        "X_BED_SIZE": 220, "Y_BED_SIZE": 220, "Z_MAX_POS": 300,
        "X_HOME_DIR": 1, "Y_HOME_DIR": 1, "Z_HOME_DIR": -1,
        "X_MAX_PIN": "PA5", "Y_MAX_PIN": "PA6", "Z_MIN_PIN": "PA7",
        "HEATER_0_PIN": "PA1", "HEATER_BED_PIN": "PA2", "FAN0_PIN": "PA0",
        "TEMP_0_PIN": "PC5", "TEMP_BED_PIN": "PC4",
        "DEFAULT_AXIS_STEPS_PER_UNIT": "{ 80, 80, 800, 93 }",
        "DEFAULT_MAX_FEEDRATE": "{ 500, 500, 5, 25 }",
        "DEFAULT_MAX_ACCELERATION": "{ 700, 700, 100, 5000 }",
        "DEFAULT_ACCELERATION": 500, "DEFAULT_TRAVEL_ACCELERATION": 500,
        "HEATER_0_MAXTEMP": 275, "HOTEND_OVERSHOOT": 15,
        "BED_MAXTEMP": 125, "BED_OVERSHOOT": 10,
        "EXTRUDE_MINTEMP": 170, "BLOCK_BUFFER_SIZE": 32,
        "SHAPING_FREQ_X": "0.0", "SHAPING_FREQ_Y": "0.0",
        "SHAPING_MIN_FREQ": "20.0", "ADVANCE_K": "0.0",
        "DEFAULT_EJERK": "5.0", "GRID_MAX_POINTS_X": 5,
        "GRID_MAX_POINTS_Y": 5,
        "MARLIN_EEPROM_SIZE": "0x800",
    }.items():
        equal(name, value)
    for name in (
        "THERMAL_PROTECTION_HOTENDS", "THERMAL_PROTECTION_BED", "USE_WATCHDOG",
        "PREVENT_COLD_EXTRUSION", "PREVENT_LENGTHY_EXTRUDE", "VALIDATE_HOMING_ENDSTOPS",
        "MIN_SOFTWARE_ENDSTOPS", "MAX_SOFTWARE_ENDSTOPS", "PIDTEMP",
        "SDSUPPORT", "ONBOARD_SDIO", "EEPROM_SETTINGS", "IIC_BL24CXX_EEPROM",
        "CR10_STOCKDISPLAY", "RET6_12864_LCD", "FAN_SOFT_PWM", "CLASSIC_JERK",
        "FASTER_GCODE_PARSER", "SLOWDOWN", "ARC_SUPPORT", "ADVANCED_PAUSE_FEATURE",
        "LCD_BED_TRAMMING", "BABYSTEPPING", "EMERGENCY_PARSER", "NO_SD_AUTOSTART",
        "LIN_ADVANCE", "ALLOW_LOW_EJERK", "ADAPTIVE_STEP_SMOOTHING",
        "INPUT_SHAPING_X", "INPUT_SHAPING_Y", "SHAPING_MENU",
        "MESH_BED_LEVELING", "LCD_BED_LEVELING", "MESH_EDIT_MENU",
        "RESTORE_LEVELING_AFTER_G28", "ENABLE_LEVELING_FADE_HEIGHT",
    ):
        check(name + " enabled", enabled(name))
    for name in (
        "BLTOUCH", "HAS_BED_PROBE", "HOMING_Z_WITH_PROBE", "FILAMENT_RUNOUT_SENSOR",
        "AUTO_BED_LEVELING_BILINEAR", "AUTO_BED_LEVELING_UBL",
        "POWER_LOSS_RECOVERY", "AUTOTEMP", "SHOW_CUSTOM_BOOTSCREEN",
        "S_CURVE_ACCELERATION", "MPCTEMP",
        "PIDTEMPBED", "DISABLE_IDLE_Z", "SD_ABORT_NO_COOLDOWN", "MARLIN_DEV_MODE",
        "HAS_TRINAMIC_CONFIG", "COREXY", "DELTA",
    ):
        check(name + " disabled", not enabled(name))

    root = Path(env["PROJECT_DIR"])
    paths = ("Marlin/Configuration.h", "Marlin/Configuration_adv.h", "platformio.ini",
             "Marlin/src/lcd/menu/menu_advanced.cpp")
    hashes = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths}
    report = {"environment": env["PIOENV"], "configuration_sha256": hashes,
              "checks": checks, "features": features}
    destination = Path(env["PROJECT_BUILD_DIR"]) / env["PIOENV"] / "review-checks.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    failed = [item["check"] for item in checks if not item["passed"]]
    if failed:
        raise RuntimeError("Ender-5 configuration review failed: " + "; ".join(failed))
    print("Ender-5 effective configuration: %d checks passed." % len(checks))

