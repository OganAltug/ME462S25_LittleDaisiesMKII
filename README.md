# Little Daisies MKII: Modular Robotic Tool Changer & Active End-Effector Ecosystem 🦾🌼

## 📖 Project Overview

**Little Daisies MKII** is a comprehensive modular mechatronic ecosystem developed for industrial robotic manipulation. While demonstrated and tested on the **Universal Robots UR5e (6-DOF manipulator)**, the tool changer is **arm-agnostic**—its universal mechanical and electrical coupling architecture adapts to **any industrial robotic arm** simply by changing a single robot-side mounting plate.

The system features **3 Active Tools** and **1 Passive Tool Set (Zen Garden Tools)**, all capable of rapid, automated docking, engagement, and power transfer via the custom-built quick-change locking mechanism:
* **Automated Quick-Change Locking Mechanism:** Universal mechanical and 8-channel electrical coupling.
* **Intelligent Toolbox Charging Station:** Autonomous docking, charging, and battery telemetry.
* **In-House Laser-Cut PCB Rapid Prototyping:** Custom MOPA IR laser manufacturing at ROMER.
* **MuJoCo Physics Digital Twin:** High-fidelity simulation for arm trajectory planning and validation.
* **3 Active Tools & 1 Passive Tool Set:** Comprehensive end-effector suite for adaptive manipulation and precision tasks.

---

## 👥 Academic Background & Project Team

This capstone project was developed as part of the **ME462 (Mechatronics Design)** course at **Middle East Technical University (METU)**, conducted at the **ROMER (Robotics and Mechatronics Center)** under the supervision of **Assoc. Prof. Dr. Ahmet Buğra Koku**.

### 🛠️ Team Members & Core Contributions:

* **Abdullah Naci Bodur:**
  * Mechanical design, 3D CAD modeling, and manufacturing of the universal quick-change locking mechanism, toolbox, and end-effector chassis.
  * Electrical interface integration, power distribution, Waveshare SDK integration, and gripper hardware control functions.
* **Ogan Altuğ Okutan:**
  * UR5e robotic arm control foundation and trajectory planning.
  * MuJoCo physics simulation environment and digital twin development (`MujocoSim/`).
  * PCB design, routing, and laser-cutting manufacturing methodology at ROMER (`PCB/`).
* **Ahmet Deniz Eröz:**
  * UR5e robotic arm control stack development and motion integration (with Ogan).
  * ROS 2 Jazzy workspace architecture, Docker virtualization, and teleoperation bridges.
  * Tutan-Khamun gripper control software and derivative-based sensorless homing algorithms.
* **Buğra Çınaroğlu:**
  * 2F-85 Pico W MicroPython software architecture and wireless MQTT communication stack.
  * Force Sensing Resistor (FSR) tactile feedback integration and independent closing control.
  * Mechatronic electronic assembly, wiring, and hardware control testing.

---

## 📦 Products & Sub-Repositories Ecosystem

All tools and controllers in the Little Daisies MKII ecosystem are integrated as sub-repositories under the [`products/`](products/) directory:

### 🦾 Active Tools (3 End-Effectors)

#### 1. [Tutan-Khamun Active Gripper](https://gitlab.com/littledaisies/tutan-khamun.git) (`products/tutan-khamun/`) *(Industrial Adaptive Gripper)*
* **Compute:** Raspberry Pi 4 / 5 (Linux Bookworm + ROS 2 Jazzy).
* **Actuation:** Dual ST3215 Serial Bus Servos (Half-Duplex TTL, 30kg.cm).
* **Power:** Waveshare 3S UPS Module (11.1V – 12.6V).
* **Features:** Mathematical **Derivative-Based Sensorless Homing** ($dLoad/dt$), Logitech Gamepad teleoperation, real-time 100Hz telemetry logging, containerized ROS 2 driver nodes with ArUco vision tracking, and [Onshape 3D CAD](https://cad.onshape.com/documents/0e67541168c599776dc2a496/w/5087dd88fe122563ce5245cb/e/e0f4186113e8f8473ac20371).

#### 2. [2F-85 Active Gripper](https://gitlab.com/littledaisies/2f-85.git) (`products/2f-85/`) *(Smart Budget Adaptive Gripper)*
* **Compute:** Raspberry Pi Pico W (MicroPython embedded core).
* **Actuation:** Dual RDS3115MG Digital Metal Gear Servos (20kg.cm, 50Hz PWM).
* **Power:** Waveshare 2S UPS HAT/Module with live **INA219 I2C battery telemetry**.
* **Features:** Dual **Force Sensing Resistor (FSR)** tactile pressure sensing for independent compliant object wrapping, **MQTT over Wi-Fi** remote teleoperation, interactive CLI client, optional ROS 2 MQTT bridge, and [Onshape 3D CAD](https://cad.onshape.com/documents/83aca715113abc33bf7a7ea1/w/fca71dd4afa92649c36d50d7/e/11c9b139ab6dce3549fb3baa).

#### 3. [Daisy Active Tool](https://gitlab.com/littledaisies/daisy.git) (`products/daisy/`) *(Interactive Smart Robot Head)*
* **Compute:** Waveshare RP2350 Touch LCD 1.28" + Raspberry Pi 4/5 Host.
* **Actuation & Sensors:** 2-DOF Pan/Tilt digital servos, GC9A01 240x240 circular IPS LCD, CST816S capacitive touch, QMI8658 6-axis IMU, wide-angle camera.
* **Features:** Animated expressive eye rendering engine, text display & countdown on circular LCD, choreographed gestures (nod, dance, greet, celebrate), YOLO/ONNX vision tracking, ROS 2 Jazzy bridge & Docker containerization, and [Onshape 3D CAD](https://cad.onshape.com/documents/f9f45dfda5ef28b74127ebf8/w/7af2920ccaf33b33f47e854c/e/35cb9935fa98d83f1ac8e302).

---

### 🕹️ Master Robotic Arm Control & Visual Servoing

#### 4. [General Robot Control](https://gitlab.com/littledaisies/generalrobotcontrol.git) (`products/generalrobotcontrol/`) *(UR5e Master Integration)*
* **Compute & Middleware:** ROS 2 Jazzy, MoveIt 2, MoveIt Servo, and Pilz Industrial Motion Planner.
* **Features:** Universal Robots UR5e driver integration, real-time velocity IK teleoperation, AI Face Tracking (35cm distance tracking), ArUco visual servoing, dynamic collision object manager (pick/drop tool meshes), headless MoveIt dashboard, and automated Zen garden drawing and surface cleaning engine.

---

### 🖌️ Passive Tools (1 Multi-Tool Set)

#### 5. Zen Garden Passive Tool Set
* **Overview:** Precision passive tool attachments designed for automated drawing, path following, and surface clearing operations in a Zen garden or canvas environment.
* **Tool Attachments:**
  * **Precision Pen Tool:** Compliant pen holder fixture for high-accuracy trajectory tracing and drawing.
  * **Surface Eraser Tool:** Wide-contact surface eraser attachment for clearing and resetting the workspace.
* **Operation:** Automatically picked, operated, and returned to the toolbox by the robotic arm via the locking mechanism.

---

## 🧩 Core Subsystems & Components

### 🔄 1. Quick-Change Tool Locking Mechanism
* **Rapid Tool Switching:** Allows the UR5e arm to engage and disengage tools in under 30 seconds.
* **Mechanical Strength:** Designed to withstand 5 kg axial load, 6 Nm torsional load, and 3 Nm bending moment with $<1\text{ mm}$ shift.
* **Integrated Electrical Interface:** Transmits power and 8-channel electrical signals across the locking interface to power active tools without external tethering.
* **Fail-Safe Operation:** Manual emergency release mechanism disengageable in $<5\text{ seconds}$.

### 🧰 2. Modular Charging Toolbox Station
* **Multi-Bay Housing:** Firmly stores multiple end-effectors within the UR5e reachable workspace.
* **Autonomous Charging:** Integrated charging contacts maintain battery levels for untethered active grippers.
* **Battery Protection & Telemetry:** Monitors charge levels to prevent overcharge/undercharge and signals state to the robot controller.

### 🦾 3. UR5e Robotic Arm Integration & Control
* **Primary Manipulator:** 6-DOF Universal Robots UR5e industrial manipulator.
* **Control Pipeline:** Developed by Ogan and Deniz, implementing joint trajectory control, Cartesian path planning, and tool-changing routines.

### 🎮 4. Physics Simulation & Digital Twin (`MujocoSim/`)
* **Engine:** MuJoCo physics engine with Universal Robots UR5e Menagerie models.
* **Visualization & Kinematics:** Integrated with Robotics Toolbox for Python (Swift) for forward/inverse kinematics, workspace validation, and dynamic collision checking before real-world deployment.

### ⚡ 5. Laser-Cut PCB Rapid Prototyping (`PCB/`)
* **In-House Manufacturing at ROMER:** Custom workflow utilizing the **xTool F2 Ultra MOPA IR laser** to engrave copper and cut FR4 substrate boards.
* **Documentation:** Complete step-by-step workflow covering Inkscape vector conversion, laser power/pulse parameters, and flame-prevention techniques in [`PCB/HowToLaserPCB.md`](PCB/HowToLaserPCB.md).

### 📋 6. Engineering Requirements & Specifications (`Requirements/`)
* Contains the baseline design constraints, mechanical tolerances, electrical specifications, and weight budgets established for the project in [`Requirements/Readme.md`](Requirements/Readme.md).

---

## 📂 Repository Structure

```bash
ME462S25_LittleDaisiesMKII/
├── products/                                  # 📦 Sub-Repositories (Git Submodules)
│   ├── tutan-khamun/                          # Industrial ST3215 Serial Bus Servo Gripper
│   ├── 2f-85/                                 # Smart Budget Pico W / MQTT Gripper
│   ├── daisy/                                 # Interactive Smart Robot Head (RP2350 / ROS 2)
│   └── generalrobotcontrol/                   # UR5e Master Motion, MoveIt 2 & Visual Servoing
│
├── MujocoSim/                                 # 🦾 UR5e Physics Simulation (MuJoCo)
│   ├── assets/                                # UR5e 3D meshes (base, shoulder, arm, wrist)
│   ├── scene.xml                              # MuJoCo world and environment definition
│   ├── ur5e.xml                               # UR5e kinematic & dynamic robot description
│   ├── mujoco_test.py                         # Interactive simulation script
│   └── rtb_swift_test.py                      # Robotics Toolbox Swift visualization
│
├── PCB/                                       # ⚡ Rapid PCB Prototyping at ROMER
│   ├── HowToLaserPCB.md                       # Complete guide for MOPA IR laser PCB engraving
│   ├── PCB_Drafts_Ogan.pdf                    # Schematic and layout drafts
│   └── firstPrototype.jpeg                    # Photograph of manufactured board
│
├── Requirements/                              # 📋 Project Specifications & Metrics
│   └── Readme.md                              # Mechanical, electrical, and operational benchmarks
│
├── Reports/                                   # 📑 Weekly Progress & Milestone Reports
│   ├── week02/ ... week12/                    # Weekly engineering design logs
│   └── week_template/                         # Standardized report format
│
├── .gitignore                                 # Git exclusion rules
├── .gitmodules                                # Submodule definitions
└── README.md                                  # Main project documentation
```

---

## 🚀 Getting Started

### 1. Cloning the Repository with Submodules
To clone the entire project along with all product sub-repositories:
```bash
git clone --recurse-submodules https://gitlab.com/littledaisies/ME462S25_LittleDaisiesMKII.git
```

If you already cloned the repository without submodules, initialize and update them:
```bash
git submodule update --init --recursive
```

### 2. Exploring the Sub-Repositories
* **Tutan-Khamun (ST3215 Gripper):** See [`products/tutan-khamun/README.md`](products/tutan-khamun/README.md)
* **2F-85 (Pico W Gripper):** See [`products/2f-85/README.md`](products/2f-85/README.md)
* **Daisy (Interactive Robot Head):** See [`products/daisy/README.md`](products/daisy/README.md)
* **General Robot Control (UR5e Master Workspace):** See [`products/generalrobotcontrol/README.md`](products/generalrobotcontrol/README.md)

### 3. Running the UR5e MuJoCo Simulation
```bash
cd MujocoSim
pip install mujoco robot_descriptions roboticstoolbox-python
python mujoco_test.py
```

### 4. Reviewing Manufacturing Guides
* For rapid laser PCB production: [`PCB/HowToLaserPCB.md`](PCB/HowToLaserPCB.md)
* For technical requirements: [`Requirements/Readme.md`](Requirements/Readme.md)

