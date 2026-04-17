# Arduino STEAMI Sample

A collection of Arduino (PlatformIO) sample projects for the STM32WB55 microcontroller.
This repository demonstrates various features such as LED control, button input, BLE communication, sensors, displays, and simple interactive demos — ideal for STEAM education and embedded experimentation.

---

##  Project Structure

```
arduino-steami-sample/
│
├── BLE/        # Bluetooth Low Energy communication
├── BUTTON/     # Button input examples
├── DEMO/       # Combined demos
├── GAME/       # Mini games
├── LED/        # LED control and animations
├── SCREEN/     # Display examples
├── SENSOR/     # Sensor data acquisition
├──  src/
│   └── main.cpp   # Entry point (selects which sample to run)
├── boards/ 
├── platformio.ini
└── README.md
```

Each folder contains standalone `.cpp` sample files.

---

##  How It Works

This project uses a **simple approach**:

 Samples are included directly in `src/main.cpp` using `#include`.

Example:

```cpp
#include <Arduino.h>
#include "../LED/blink.cpp"

void setup() {
  setup_blink();
}

void loop() {
  loop_blink();
}
```

Each sample must define:

* a `setup_<name>()` function
* a `loop_<name>()` function

---

## Switching Between Samples

To run a different example, simply edit `src/main.cpp`:

```cpp
#include <Arduino.h>

// Select your sample here:
#include "../LED/blink.cpp"
// #include "../BUTTON/read_button.cpp"
// #include "../BLE/advertiser.cpp"

void setup() {
  setup_blink();   // change accordingly
}

void loop() {
  loop_blink();    // change accordingly
}
```

Comment/uncomment the desired sample and update the function calls.

---

## Requirements

### Hardware

* STM32WB55 development board

### Software

* [PlatformIO](https://platformio.org/)
* Python 3.x

### Installation

Install PlatformIO Core:

```bash
pip install platformio
```

Verify installation:

```bash
pio --version
```

---

## Build, Upload and Monitor

From the root of the project:

```bash
pio run -t clean
pio run -t upload
pio device monitor -b 115200
```

---

## Available Examples

* LED blinking : `LED/blink.cpp`

---

## Notes

* This project intentionally uses a **simple and beginner-friendly structure**
* `.cpp` files are directly included (not standard C++ practice, but practical for quick experimentation)
* Only one sample should be included at a time in `main.cpp`

---

## Goal

Provide a simple, hackable, and educational environment to explore embedded programming on STM32WB55 using Arduino and PlatformIO.
