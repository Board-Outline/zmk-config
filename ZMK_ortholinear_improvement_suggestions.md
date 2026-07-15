The board is broadly functional, but there are several worthwhile improvements. The biggest confirmed opportunities are reproducible dependencies and separating production firmware from Studio/debug features. Hardware recommendations remain conditional because this repository contains no schematic or PCB layout.

## Highest-value firmware improvements

1. Pin the external behavior module NICK NOTE - good catch. Should implement it.

In [west.yml](D:/Board_Outline/zmk-config/config/west.yml), `zmk-userspace` tracks:

```yaml
revision: main
```

That means an unrelated upstream change can alter or break future builds. Pin it to a tested commit hash, just as ZMK itself is pinned. This is primarily a reliability and reproducibility improvement.

2. Separate normal and Studio builds NICK NOTE - consider this further.

[build.yaml](D:/Board_Outline/zmk-config/build.yaml) forces ZMK Studio and the USB-UART RPC snippet into every build:

```yaml
snippet: studio-rpc-usb-uart
cmake-args: -DCONFIG_ZMK_STUDIO=y
```

Consider separate production and Studio artifacts. Removing Studio from the normal build reduces firmware size and complexity. The USB-UART interface is unlikely to dominate battery consumption while unplugged, so this is mainly reliability and maintenance rather than a dramatic power saving.

3. Consider longer battery-report intervals NICK NOTE - do this

ZMK samples/reports battery level every 60 seconds by default. If minute-level updates are unnecessary:

```ini
CONFIG_ZMK_BATTERY_REPORT_INTERVAL=300
```

Five-minute sampling slightly reduces ADC and BLE activity. The gain will be modest.

## Responsiveness and rollover - NICK NOTE - not needed for now. Leave as a suggestion.

The default USB polling interval is already 1 ms, so USB configuration is not your main latency source.

The default HID mode reports six simultaneous ordinary keys plus modifiers. That is sufficient for normal typing and shortcuts. NKRO is available:

```ini
CONFIG_ZMK_HID_REPORT_TYPE_NKRO=y
```

However, it can reduce BIOS/UEFI and host compatibility. Your keymap also uses F13-F24, which complicates NKRO unless extended reports are enabled; extended reports can break Android compatibility. I would retain the default unless you genuinely need more than six non-modifier keys simultaneously.

## Range improvements

The nRF52840 can transmit at higher power, potentially up to +8 dBm depending on configuration. That can improve range but increases peak current, may worsen interference, and creates regulatory implications. Fix antenna efficiency before increasing transmit power.

## Matrix and PCB improvements

For a future PCB revision:

- Converting to `row2col` gives 7 driven outputs instead of 18, as discussed. This can improve settling if the 18 long row/column arrangement is electrically unfavorable. NICK NOTE - consider this
- Place each diode and hot-swap socket to minimize unsupported mechanical stress. - NICK NOTE - no idea what that reffers to.

## Configuration and maintenance cleanup

These will not materially improve performance, but they will reduce mistakes:

- Replace the placeholder URL in `ortholinear_kb.zmk.yml`.
- Remove unused template comments and the empty pinctrl include.
- Remove unused layer constants and verify placeholder `&kp N1` bindings.
- Avoid placing `BT_CLR` and multiple bootloader bindings where accidental activation is easy. NICK NOTE - this is done for test only.
- Document whether the board requires VDDH, REG0/REG1 inductors, LFXO, and the particular bootloader flash map. NICK NOTE - how?
- Add a hardware revision to `board.yml` before producing a revised PCB. NICK NOTE - good point.
- Preserve the existing flash partition map unless it is checked against the bootloader; firmware and bootloader address disagreement can make updates unbootable. NICK NOTE - works well now.

My priority order would be: pin the external module, consider separate normal and Studio builds, and lengthen the battery-report interval if minute-level updates are unnecessary.
