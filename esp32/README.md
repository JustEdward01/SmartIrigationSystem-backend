# Firmware ESP32

Acest folder conține firmware-ul pentru placa ESP32 folosită în proiectul **SmartPlant**.

## Setup PlatformIO / Arduino IDE

1. Instalează [VSCode](https://code.visualstudio.com/) și extensia [PlatformIO](https://platformio.org/), **sau** folosește Arduino IDE 2.x.
2. Deschide directorul `esp32` ca proiect PlatformIO (`Open Project`) sau copiază fișierele din `src/` în Arduino IDE.
3. Pentru Arduino IDE trebuie să instalezi pachetul de board *esp32* (Boards Manager > `esp32` by Espressif Systems).

## Instalare biblioteci

PlatformIO va instala automat dependențele din `platformio.ini`:

```
lib_deps =
    bblanchon/ArduinoJson@^6.21.2
    adafruit/DHT sensor library@^1.4.4
```

În Arduino IDE folosește Library Manager pentru **ArduinoJson** și **DHT sensor library**.

## Upload firmware

1. Conectează placa ESP32 la PC și selectează portul corespunzător.
2. Board: `ESP32 Dev Module` (`esp32dev`).
3. În PlatformIO rulează:
   ```bash
   pio run -t upload
   ```
   sau folosește butonul *Upload* din IDE. În Arduino IDE alege *Upload* după ce ai selectat placa și portul.

## Structura directoarelor

- `src/` – codul principal (`main.cpp`, `sensors.h`).
- `include/` – headere suplimentare.
- `lib/` – librării personalizate.
- `test/` – teste UnitTest/Mock.
- `platformio.ini` – configurare PlatformIO.
- `ESP32.code-workspace` – configurare VSCode.

## Testare pe Emulator / Mock

Exemplu de test se găsește în `test/test_sensors.cpp`. Acesta simulează citirile de senzori și verifică că funcțiile nu blochează programul.

Rularea testelor (dacă ai PlatformIO instalat):

```bash
pio test
```

Testele folosesc framework-ul [Unity](https://docs.platformio.org/en/latest/plus/unit-testing.html) și pot rula nativ sau pe placă.
