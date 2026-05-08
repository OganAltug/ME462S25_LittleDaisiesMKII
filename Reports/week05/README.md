# Weekly Report: LittleDaisiesMKII - Week 5

**Date Range:** March 10 - March 16, 2026

## 📊 Team Performance & Scoring

*Evaluation of specific tasks and deliverables based on project requirements.*

| Deliverable / Metric                 | Score           | Notes                    |
| :----------------------------------- | :-------------- | :----------------------- |
| Naming Convention                    | 6/10            | Revision in progress     |
| Meeting Minutes                      | 10/10           | Completed                |
| Locking Interface PCB Requirements   | 5/10            | Further detail needed    |
| Locking Interface Mech. Requirements | 8/10            | Well-defined             |
| Robot Control                        | 7/10            | Progressing              |
| Zen Tool (Rotated by π/2)           | 8/10            | Design and manufacturing |
| **Total Score**                | **44/60** | **Avg: 7.33/10**   |

---

## 🤝 Meeting Notes

### Monday Meeting

**Key Discussion Points:**

* **Decisions:** Naming convention finalized and documented via visual reference.
* **Hardware Progress:** Designed and manufactured the first version of the Zen Tool; designed a sieve for the tool.
* **Simulation & Control:** Successfully tested basic UR5e pose-to-pose motion using MuJoCo and Robotictoolbox.
* **Manufacturing:** Discussed laser-cut PCB manufacturing details, including Xtool and KiCAD settings and via manufacturing ideas.
* **Mechanism Brainstorming:** Evaluated kinematic coupling ideas including self-releasing grapples, bearing-style ball locks, and active locking via the UR5e power cable.

### Tuesday Meeting

* **Electronic Specs:** Researched microcontroller features including Wi-Fi support, deep-sleep modes, and Wi-Fi wake capabilities.
* **Communication:** Initiated review of communication protocols.

---

## 🖼️ Visual Documentation & Progress

*Capturing hardware builds and simulation results.*

* **Naming Convention:**
  `<img src="./img/name_convention.jpeg" alt="Name Convention" width="600"/>`
* **Zen Tool Mounted:**
  `<img src="./img/ZenToolMounted.jpeg" alt="ZenToolMounted" width="300"/>`
* **Sieve Design:**
  `<img src="./img/sieve.jpeg" alt="Sieve Design" width="300">`
* **MuJoCo Simulation:**
  `<img src="./img/mujoco.gif" alt="Mujoco Sim" width="400">`

---

## 🔗 Documentation Links

* [Tool Interface/Handler Requirements](../../Requirements/Readme.md)
* [PCB Manufacturing Report](../../PCB/HowToLaserPCB.md)
* [Locking Mechanism Ideas (Google Doc)](https://docs.google.com/document/d/15yzl3hxYkYvtqdlGrBOaPBBX_cD7uZbD/edit?usp=sharing&ouid=110519594456022773011&rtpof=true&sd=true)

---

## 📝 To-Do List (Action Items)

### Immediate Priority

- [ ] **Hardware:** Redesign/tweak Zen Tool based on structural and functional testing.
- [ ] **Hardware:** Manufacture sieve (obtain wire first).
- [ ] **Software:** Implement Zen Tool into MuJoCo and test.
- [ ] **Electronics:** Research PCB components and UR5e serial connection details.

### Research & Documentation

- [ ] **Research:** Look into alternative simulators and quick connect/release mechanisms.
- [ ] **Reports:** List all potential locking mechanisms in a dedicated file and write interface requirements.
- [ ] **Maintenance:** Document the naming convention and add links to the "README.md".
