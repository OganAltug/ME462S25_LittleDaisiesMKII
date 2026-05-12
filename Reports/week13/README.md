# Weekly Report: LittleDaisiesMKII - Week 13

**Date Range:** May 5 - May 12
---
## 📊 Team Performance & Scoring

*Evaluation of specific tasks and deliverables based on project requirements.*
| Deliverable / Metric            | Score          | Notes                            |
| :------------------------------------------ | :------------- | :--------------------- |
| Robot control and sand writing  | 10/10          | We are able to write onto the sand  |
| Checking the new hardware given | 8/10           | Mini esp and the camera is checked  |
| Gripper force control           | 7/10           | both force with current and fsr is tried|
| Image Processing                | 5/10           | an object is followed via servo no updat eon arucos |
| TutanKhamun Gripper Assembly    | 10/10          | TutanKhamun the Heybetli is Assembled      |
| **Total Score**  | **X/60** | **Avg: X.XX/10**           |
---

## 🤝 Meeting Notes

### May 11 - Group Meeting

**Key Discussion Points:**
Everyone is explained what they have done for the past week. 
* Buğra worked on image processing on Rasppery Pi, and successfully followed and object (human) by tip of the servo. He also tried to work with FSR, and sucessfully implemented the FSR force control to the 2f-85 gripper machanism. Finally, he tried to work with the given esp32 with integrated camera but did not like the output feed quality.
* Some search about the head is done.
  - [IDEA 1](https://www.youtube.com/shorts/ejHmpcbf4PA)
  - [IDEA 2](https://www.youtube.com/shorts/wkof60aqg6w)
  - [IDEA 3](https://www.youtube.com/shorts/eSnn20z8AxQ)
  - [IDEA 4](https://www.youtube.com/watch?v=IT1uBUsOmUY)
  - [IDEA 5](https://www.youtube.com/shorts/pm9Umdwg9uo)
  - [IDEA 6](https://www.youtube.com/shorts/5SJYWTB2Nf4)
  - [IDEA 7](https://youtube.com/shorts/Qu2Ccx3YggI?si=xmM9Od8_wPeU3PLN)
  - [IDEA 8](https://youtube.com/shorts/5SJYWTB2Nf4?si=HgB3RJdVCw9v34qi)
  - [IDEA 9](https://youtube.com/shorts/ARHM2iDbWIY?si=fSSAW8HbxofMi2Qx)
  - [IDEA 10] <img src="./img/kafakol.jpeg" alt="Kafa Kol" width="320"/>
  - [IDEA 11] <img src="./img/sakaladam.png" alt="Sakal Adam" width="320"/>
* Ogan kept working on the robot control. He finalized the sand-writing process, and now we are able to write on the sand. He also created a docker file for other members to efficiently and easiliy get into the robot control. Thanks Ogan.
* Naci kept wroking on the gripper mechanism, electronics and software. He mainly focussed on the force control via current readings, however he faced with some problems. Currently the current-force control is not as reliable as we wanted. He also gathered the documentations and files about the gripper so that other members of the group can succesfully get into the gripper part.
* Deniz, wrote this meeting minute.
<img src="./img/group_photo.jpg" alt="Group Photo" width="320"/>
<img src="./img/outside_meeting.jpg" alt="Outside Meeting" width="320"/>
<img src="./img/sunset.jpeg" alt="Sunset" width="320"/>
<img src="./img/sunset_closeup.jpeg" alt="Sunset Closeup" width="320"/>
## 🖼️ Visual Documentation & Progress
* Writing Little Daisies on the sandpool
<img src="./img/sand_writing.jpg" alt="Little Daisies on the Sand" width="320"/>
* Feed from esp32
<img src="./img/esp_32_feed.jpg" alt="Feed from esp32" width="320"/>
* Tutan Khamun Assembly
<img src="./img/tutan_kahmun.jpeg" alt="tutan_kahmun" width="320"/>
* Plots from Tutan-Khamun current-force control
<img src="./plots/servo_telemetry_20260511_195408.png" alt="Only Threshold" width="320"/>
<img src="./plots/servo_telemetry_20260511_210122.png" alt="Delta Threshold" width="320"/>
<img src="./plots/servo_telemetry_20260511_211433.png" alt="Burn-out" width="320"/>

## 🔗 Documentation Links
[Robot Control Docker Repo](https://github.com/OganAltug/ME462ZenPoolWorkspace)


## 📝 To-Do List (Action Items)

### Immediate Priority

- [ ] **Hardware:** Redesign [Component] based on recent test results.
- [ ] **Software:** Implement [Feature] in simulation environment.
- [ ] **Manufacturing:** Obtain [Material/Part] and fabricate [Item].

### Research & Documentation

- [ ] **Research:** Investigate [Mechanism/Protocol] alternatives.
- [ ] **Reports:** Document [Naming Convention/Interface Requirements].
- [ ] **Maintenance:** Update README with latest links and media.
