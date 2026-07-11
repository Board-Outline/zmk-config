The board is broadly functional, but there are several worthwhile improvements. The biggest confirmed opportunities are deep sleep, reproducible dependencies, debounce latency, and separating production firmware from Studio/debug features. Hardware recommendations remain conditional because this repository contains no schematic or PCB layout.

## Highest-value firmware improvements

1. Enable deep sleep

Deep sleep is currently disabled. Your matrix already has `wakeup-source`, so the basic wake mechanism is present.

Candidate settings:

```ini
CONFIG_ZMK_SLEEP=y
CONFIG_ZMK_IDLE_SLEEP_TIMEOUT=900000
```

The default timeout shown above is 15 minutes. Deep sleep substantially reduces long-term idle consumption, but disconnects Bluetooth and may take a few seconds to reconnect after waking. [ZMK low-power documentation](https://zmk.dev/docs/features/low-power-states)

2. Pin the external behavior module

In [west.yml](D:/Board_Outline/zmk-config/config/west.yml), `zmk-userspace` tracks:

```yaml
revision: main
```

That means an unrelated upstream change can alter or break future builds. Pin it to a tested commit hash, just as ZMK itself is pinned. This is primarily a reliability and reproducibility improvement.

3. Reduce press latency after resolving the faulty switches

Your current 12 ms press and release debounce is robust but adds around 12 ms before every key transition is accepted.

After replacing or repairing bouncing switches, a responsive asymmetric configuration might be:

```dts
debounce-press-ms = <5>;
debounce-release-ms = <15>;
```

Presses feel faster while release gets stronger bounce protection. Do not lower it until the hardware diagnosis is complete.

4. Keep the expanded queue

Your current setting is:

```ini
CONFIG_ZMK_KSCAN_EVENT_QUEUE_SIZE=32
```

That costs approximately 384 bytes of static event storage and has already improved missed inputs. It is reasonable on an nRF52840.

5. Treat the matrix waits as experimental

Both 5 µs waits add approximately 180 µs per complete 18-column scan. That is acceptable, but retain them only if controlled testing shows improvement. Otherwise, return them to zero.

6. Separate normal and Studio builds

[build.yaml](D:/Board_Outline/zmk-config/build.yaml) forces ZMK Studio and the USB-UART RPC snippet into every build:

```yaml
snippet: studio-rpc-usb-uart
cmake-args: -DCONFIG_ZMK_STUDIO=y
```

Consider separate production and Studio artifacts. Removing Studio from the normal build reduces firmware size and complexity. The USB-UART interface is unlikely to dominate battery consumption while unplugged, so this is mainly reliability and maintenance rather than a dramatic power saving.

7. Consider longer battery-report intervals

ZMK samples/reports battery level every 60 seconds by default. If minute-level updates are unnecessary:

```ini
CONFIG_ZMK_BATTERY_REPORT_INTERVAL=300
```

Five-minute sampling slightly reduces ADC and BLE activity. The gain will be modest.

## Responsiveness and rollover

The default USB polling interval is already 1 ms, so USB configuration is not your main latency source.

The default HID mode reports six simultaneous ordinary keys plus modifiers. That is sufficient for normal typing and shortcuts. NKRO is available:

```ini
CONFIG_ZMK_HID_REPORT_TYPE_NKRO=y
```

However, it can reduce BIOS/UEFI and host compatibility. Your keymap also uses F13–F24, which complicates NKRO unless extended reports are enabled; extended reports can break Android compatibility. I would retain the default unless you genuinely need more than six non-modifier keys simultaneously.

## Power-hardware checks

1. Verify both DC/DC networks

The DTS enables REG0 and REG1 DC/DC operation. That is good for battery life only if the required inductors and capacitors are physically fitted correctly. Verify both networks against Nordic’s QIAA reference design.

Do not enable either DC/DC stage without its required LC components. Poor component values or layout can also introduce supply noise that manifests as unstable GPIO or reduced radio performance.

2. Confirm how the battery is connected

The firmware uses:

```dts
compatible = "zmk,battery-nrf-vddh";
```

That is correct only when the measured supply is connected through the nRF52840’s VDDH power path. If the battery passes through another regulator or feeds VDD instead, the reported battery percentage may be wrong. ZMK supports VDDH sensing, ADC voltage dividers, and compatible fuel gauges. [ZMK battery-sensing documentation](https://zmk.dev/docs/hardware-integration/battery)

For better accuracy in a future revision, consider a low-power fuel gauge. A permanent resistor divider is simpler but creates continuous leakage unless it is switched or uses very high-value resistors.

3. Confirm the 32.768 kHz crystal

Your defconfig currently assumes an external low-frequency crystal because the RC-clock option is commented out.

If there is no 32.768 kHz crystal, the clock configuration must be corrected. If one is fitted, retain it: Nordic specifies very low LFXO running current, and it generally provides better BLE timing and lower long-term consumption than repeatedly calibrating an internal RC clock. The external 32 MHz HFXO and its correct load network are essential for radio operation. [Nordic clock specification](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/clock.html)

## Range improvements

Radio layout will usually matter more than firmware transmit power:

- Copy Nordic’s nRF52840-QIAA RF matching layout closely.
- Preserve the antenna manufacturer’s keepout area on every copper layer.
- Keep the battery, USB connector/cable, switch plate, metal case, ground fill, and matrix traces away from the antenna.
- Provide a continuous ground plane under the MCU and RF feed, excluding specified keepouts.
- Include a tunable antenna matching network.
- Measure the assembled product with a VNA if range matters.
- For future revisions, a certified nRF52840 module is lower-risk than chip-down RF design.

Nordic explicitly warns that layout changes around the RF matching network can degrade performance and publishes QIAA reference layouts. [Nordic reference-layout downloads](https://www.nordicsemi.com/Products/nRF52840/Compatible-downloads)

The nRF52840 can transmit at higher power, potentially up to +8 dBm depending on configuration. That can improve range but increases peak current, may worsen interference, and creates regulatory implications. Fix antenna efficiency before increasing transmit power.

## Matrix and PCB improvements

For a future PCB revision:

- Converting to `row2col` gives 7 driven outputs instead of 18, as discussed. This can improve settling if the 18 long row/column arrangement is electrically unfavorable.
- An `8×15` matrix accommodates 120 positions using 23 GPIOs instead of the current 25. It would provide eight outputs and fifteen inputs, saving two GPIOs while keeping the driven dimension small.
- Place each diode and hot-swap socket to minimize unsupported mechanical stress.
- Add accessible test points for every matrix row and column.
- Inspect socket solder pads carefully; hot-swap sockets frequently develop cracked or lifted joints.
- Use short, well-referenced input traces and avoid routing them beside antenna or switching-regulator nodes.
- Avoid blindly adding strong external pull-downs: they may improve noise immunity but increase current when a switch connects an active output to that pull-down.
- RC filters on every matrix input can suppress noise, but they also increase settling time and can distort rapid transitions. Add footprints only if measurement supports their use.

## Configuration and maintenance cleanup

These will not materially improve performance, but they will reduce mistakes:

- Replace the placeholder URL in `ortholinear_kb.zmk.yml`.
- Remove unused template comments and the empty pinctrl include.
- Remove unused layer constants and verify placeholder `&kp N1` bindings.
- Avoid placing `BT_CLR` and multiple bootloader bindings where accidental activation is easy.
- Document whether the board requires VDDH, REG0/REG1 inductors, LFXO, and the particular bootloader flash map.
- Add a hardware revision to `board.yml` before producing a revised PCB.
- Preserve the existing flash partition map unless it is checked against the bootloader; firmware and bootloader address disagreement can make updates unbootable.

My priority order would be: pin the external module, enable/test deep sleep, finish the switch/socket diagnosis, validate clocks and DC/DC hardware, then inspect antenna layout and battery sensing. No files were changed.
