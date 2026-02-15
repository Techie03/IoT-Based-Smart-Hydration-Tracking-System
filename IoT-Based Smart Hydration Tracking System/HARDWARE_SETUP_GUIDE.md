# IoT Hydration Tracker - Hardware Setup Guide

## 📦 Required Components

### Electronics
1. **ESP8266 NodeMCU** (1x) - WiFi-enabled microcontroller
2. **HC-SR04 Ultrasonic Sensor** (1x) - Distance measurement
3. **Micro USB Cable** (1x) - Power and programming
4. **Jumper Wires** (4x Female-to-Female) - Connections
5. **Breadboard** (Optional) - For prototyping

### Mounting Hardware
6. **Water Bottle** (1L capacity recommended)
7. **Bottle Cap Adapter/Mount** - To secure sensor
8. **Hot Glue/Epoxy** - Waterproof mounting
9. **Zip Ties/Velcro** (Optional) - Cable management

### Optional
10. **5V Power Bank** - Portable power
11. **Waterproof Case** - Protect electronics
12. **LED Indicator** - Visual status (built-in on NodeMCU)

---

## 🔌 Wiring Diagram

```
╔═══════════════════════════════════════════════════════════╗
║         ESP8266 NodeMCU ↔ HC-SR04 Ultrasonic Sensor      ║
╚═══════════════════════════════════════════════════════════╝

ESP8266 NodeMCU                    HC-SR04 Ultrasonic Sensor
┌─────────────────┐                ┌──────────────────────┐
│                 │                │                      │
│   [USB Port]    │                │   ┌──────────────┐  │
│                 │                │   │ Transm. Recv.│  │
│                 │                │   │   T      R   │  │
│                 │                │   └──────────────┘  │
│                 │                │                      │
│  3V3 ●──────────┼────────────────┼──● VCC              │
│                 │   (Red Wire)   │                      │
│                 │                │                      │
│  GND ●──────────┼────────────────┼──● GND              │
│                 │   (Black Wire) │                      │
│                 │                │                      │
│  D1  ●──────────┼────────────────┼──● TRIG (Trigger)   │
│  (GPIO5)        │   (Yellow Wire)│                      │
│                 │                │                      │
│  D2  ●──────────┼────────────────┼──● ECHO (Receive)   │
│  (GPIO4)        │   (Green Wire) │                      │
│                 │                │                      │
│  [LED]●         │                │                      │
│  (Built-in)     │                │                      │
│                 │                │                      │
└─────────────────┘                └──────────────────────┘
      ║                                      ║
      ║                                      ║
   [Power]                             [Ultrasonic]
   USB/5V                              Measurement


PIN CONNECTIONS:
================
ESP8266 Pin  →  HC-SR04 Pin  →  Wire Color (Suggested)
-----------     -----------     ---------------------
3V3         →   VCC          →  Red
GND         →   GND          →  Black
D1 (GPIO5)  →   TRIG         →  Yellow
D2 (GPIO4)  →   ECHO         →  Green
```

---

## 🏗️ Physical Assembly Diagram

```
╔═══════════════════════════════════════════════════════════╗
║              BOTTLE MOUNTING - TOP VIEW                    ║
╚═══════════════════════════════════════════════════════════╝

Step 1: Sensor Placement on Bottle Cap
═══════════════════════════════════════

         ┌─────────────────────────┐
         │   BOTTLE CAP (TOP)      │
         │                         │
         │    ┌──────────────┐    │
         │    │   HC-SR04    │    │  ← Sensor faces DOWN
         │    │  ┌────────┐  │    │     into bottle
         │    │  │ T    R │  │    │
         │    │  └────────┘  │    │
         │    └──────┬───────┘    │
         │           │            │
         │      [Hot Glue]        │
         │           │            │
         └───────────┼────────────┘
                     │
                     ▼
              (Sensor beam)


Step 2: Side View Assembly
═══════════════════════════

    ESP8266 NodeMCU          Wires           Sensor
    ┌─────────────┐         ╱╲╱╲╱╲      ┌────────────┐
    │   NodeMCU   │═══════════════════╗ │  HC-SR04   │
    │             │                   ║ │            │
    │   [USB]●    │                   ║ │  [●][●]    │
    │             │                   ║ │   T   R    │
    └─────────────┘                   ║ └──────┬─────┘
         │                            ║        │
         │ (Velcro/Zip Tie)          ║        │ (Hot Glue)
         │                            ║        │
    ═════╧════════════════════════════╬════════╧═══════
                BOTTLE CAP             ║
    ══════════════════════════════════╬════════════════
    ║                                 ║              ║
    ║                                 ║              ║
    ║          WATER BOTTLE           ║    AIR GAP   ║
    ║         (1000ml / 1L)           ║      ↕       ║
    ║                                 ║   Distance   ║
    ║                                 ║   Measured   ║
    ║            ≈≈≈≈≈≈≈            ║      ↕       ║
    ║           ≈≈≈≈≈≈≈≈≈          ║              ║
    ║          ≈≈≈≈≈≈≈≈≈≈≈         ║   [Sensor    ║
    ║         ≈≈≈ WATER ≈≈≈         ║    Beam]     ║
    ║          ≈≈≈≈≈≈≈≈≈≈≈         ║      ↓       ║
    ║           ≈≈≈≈≈≈≈≈≈          ║      ↓       ║
    ║            ≈≈≈≈≈≈≈            ║      ↓       ║
    ║                                 ║      ↓       ║
    ║                                 ║   ≈≈≈≈≈≈≈   ║
    ╚═════════════════════════════════╩══════════════╝
                BOTTLE BOTTOM


Step 3: Complete System View
═════════════════════════════

         [Power Bank]
              │
              ▼
         ┌─────────┐
         │ ESP8266 │◄── WiFi to Cloud
         │ NodeMCU │
         └────┬────┘
              │ (4 wires)
              │
         ╔════╧════╗
         ║ Sensor  ║
         ║ HC-SR04 ║
         ╚════╤════╝
              │ (Mounted on cap)
              │
         ┌────┴────┐
         │  Water  │
         │ Bottle  │
         │         │
         │  ≈≈≈≈≈ │ ← Water Level
         │  ≈≈≈≈≈ │   (Measured)
         └─────────┘
```

---

## 📐 Detailed Mounting Instructions

### Method 1: Cap Mount (Recommended)

```
MATERIALS NEEDED:
- Bottle cap (original or spare)
- Hot glue gun or epoxy
- Drill with 2mm bit (optional)

STEPS:

1. Prepare the Cap
   ┌─────────────────┐
   │  ORIGINAL CAP   │
   │  ╭─────────╮   │
   │  │  Drill  │   │ ← Drill small holes for wires
   │  ╰─────────╯   │    (optional, can route around edge)
   └─────────────────┘

2. Position Sensor
   - Place HC-SR04 on INSIDE of cap
   - Transducer side facing DOWN into bottle
   - Center it for best measurement
   
   ┌─────────────────┐
   │     CAP TOP     │
   ├─────────────────┤
   │   ┌─────────┐  │
   │   │ SENSOR  │  │ ← Glue sensor here
   │   │  ┌─┐ ┌─┐ │ │
   │   │  │T│ │R│ │ │
   │   │  └─┘ └─┘ │ │
   │   └─────────┘  │
   └─────────────────┘

3. Secure with Hot Glue
   - Apply glue around sensor edges
   - DO NOT cover transducers (T/R)
   - Let dry for 30 minutes
   - Test waterproof seal

4. Route Wires
   - Feed wires through drilled holes OR
   - Route around cap threads
   - Ensure bottle can still screw on

5. Attach NodeMCU
   - Use velcro on bottle side
   - Or zip tie to bottle
   - Keep USB port accessible
```

### Method 2: External Mount

```
For non-permanent installation:

1. 3D Print/Buy Clip Mount
   ┌──────────────┐
   │   ╭──────╮  │
   │   │Sensor│  │
   │   ╰──────╯  │
   │   ║      ║  │ ← Clip design
   │   ║      ║  │
   └───╨──────╨──┘
       │      │
       └──┐┐──┘
          ││ ← Clips onto bottle

2. Positioning
   - Mount 2-3cm below cap
   - Sensor faces straight down
   - Secure with rubber bands
```

---

## ⚡ Power Options

### Option 1: USB Power (Recommended for Testing)
```
[Computer USB] ──→ [Micro USB Cable] ──→ [NodeMCU]
     or
[USB Charger] ──→ [Micro USB Cable] ──→ [NodeMCU]
```

### Option 2: Portable Power Bank
```
                 ┌──────────────┐
[Power Bank] ──→ │ 5V/2A Output │ ──→ [NodeMCU]
(5000+ mAh)      └──────────────┘
                                       Battery Life:
                                       5000mAh ≈ 24+ hours
```

### Option 3: Battery Pack (Advanced)
```
[3x AA Batteries] ──→ [Voltage Regulator] ──→ [NodeMCU]
   (4.5V)              (5V output)              
```

---

## 🔧 Assembly Steps (Detailed)

### Step 1: Test Components First

```bash
1. Connect HC-SR04 to NodeMCU on breadboard
2. Upload test sketch
3. Open Serial Monitor
4. Verify distance readings
5. Move hand above sensor to test
```

### Step 2: Prepare Bottle

```
1. Clean bottle thoroughly
2. Dry completely
3. Remove any labels
4. Ensure cap threads are clean
```

### Step 3: Mount Sensor

```
1. Apply hot glue to sensor edges
2. Press firmly onto cap interior
3. Hold for 30 seconds
4. Let cure for 30 minutes
5. Test seal with water drops
```

### Step 4: Wire Management

```
1. Route wires neatly along bottle
2. Use zip ties every 5cm
3. Leave slack near cap (for opening)
4. Secure NodeMCU to bottle side
```

### Step 5: Final Testing

```
1. Fill bottle with water
2. Screw on modified cap
3. Power on NodeMCU
4. Check WiFi connection
5. Verify Firebase uploads
6. Test by drinking water
```

---

## 📏 Measurement Specifications

```
BOTTLE SPECIFICATIONS:
=====================
Height: 20cm (8 inches)
Capacity: 1000ml (1 liter)
Opening: Standard water bottle

SENSOR RANGE:
=============
Minimum: 2cm
Maximum: 400cm
Accuracy: ±3mm
Resolution: 0.3cm

MEASUREMENT ZONES:
==================
┌──────────────┐
│   Sensor     │ ← 0cm (reference)
├──────────────┤
│              │ 
│   AIR GAP    │ ← 2cm minimum
│              │
├≈≈≈≈≈≈≈≈≈≈≈≈≈┤
│≈≈≈≈≈≈≈≈≈≈≈≈≈│
│≈≈ WATER ≈≈≈≈│ ← 2-20cm (measured)
│≈≈≈≈≈≈≈≈≈≈≈≈≈│
│≈≈≈≈≈≈≈≈≈≈≈≈≈│
└──────────────┘ ← 20cm (bottle bottom)

Water Level Calculation:
Water Height = 20cm - Measured Distance
Water % = (Water Height / 20cm) × 100
Volume (ml) = Water % × 1000ml
```

---

## 🔍 Troubleshooting Hardware

### Problem: No Distance Reading

```
CHECK:
1. ✓ 4 wires connected correctly
2. ✓ VCC to 3V3 (not 5V)
3. ✓ Sensor transducers not covered
4. ✓ Sensor facing correct direction

TEST:
- Move hand above sensor
- Should read 5-30cm
- Serial monitor shows values
```

### Problem: Erratic Readings

```
CAUSES:
1. ✗ Wires too long (>15cm)
2. ✗ Loose connections
3. ✗ Condensation on sensor
4. ✗ Bottle cap loose

FIXES:
- Shorten wires
- Resolder connections
- Add silica gel packet
- Tighten cap securely
```

### Problem: Water Detection Issues

```
CALIBRATION:
1. Fill bottle to 100%
2. Note distance reading
3. Update BOTTLE_HEIGHT in code
4. Test at various levels
5. Adjust MIN_DISTANCE if needed
```

---

## 📷 Photos/Diagrams Legend

```
SYMBOL KEY:
===========
●  = Connection point
─  = Wire
║  = Bottle
≈  = Water
□  = Component
┌┐ = Housing/Case
╔╗ = Mounting bracket
```

---

## ✅ Pre-Deployment Checklist

```
HARDWARE:
□ All 4 wires connected correctly
□ Sensor firmly glued to cap
□ No glue on transducers
□ Wires have strain relief
□ NodeMCU securely mounted
□ USB port accessible
□ Power source connected

SOFTWARE:
□ Firmware uploaded successfully
□ WiFi credentials configured
□ Firebase URL and auth set
□ Device ID unique
□ Serial output shows readings
□ Data appears in Firebase

TESTING:
□ Empty bottle reads ~100%
□ Full bottle reads ~100%
□ Half full reads ~50%
□ Drinking event detected
□ WiFi reconnects automatically
□ Runs for 24+ hours stable
```

---

## 🎓 Tips for Best Results

1. **Sensor Positioning**: Center sensor on cap for best accuracy
2. **Wire Management**: Use spiral cable wrap for clean look
3. **Power**: Use 2A+ power bank for reliable operation
4. **Waterproofing**: Add silicone sealant around sensor edges
5. **Calibration**: Calibrate with full bottle first
6. **Testing**: Test for 24 hours before deployment
7. **Maintenance**: Clean sensor lens monthly
8. **Backup**: Keep spare jumper wires

---

## 📞 Support

**Issues?**
- Check wiring diagram
- Test components individually  
- Verify code settings
- Monitor Serial output

**Need Help?**
- GitHub Issues
- Arduino Forums
- ESP8266 Community

---
