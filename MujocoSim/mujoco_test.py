import mujoco
import mujoco.viewer
from robot_descriptions import ur5e_mj_description
import time
from math import cos, sin
from rtb_test import UR5e
import roboticstoolbox as rtb
import numpy as np
from spatialmath import SE3
  
def main():
    # Load the model
    model = mujoco.MjModel.from_xml_path("scene.xml")
    data = mujoco.MjData(model)

    id_shoulder_pan = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, "shoulder_pan")
    id_shoulder_lift = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, "shoulder_lift")
    id_elbow = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, "elbow")
    id_wrist_1 = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, "wrist_1")
    id_wrist_2 = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, "wrist_2")
    id_wrist_3 = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, "wrist_3")

    def set_ang_targets(ang_vel_targets):
        data.ctrl[id_shoulder_pan] = ang_vel_targets[0] 
        data.ctrl[id_shoulder_lift] = ang_vel_targets[1]
        data.ctrl[id_elbow] = ang_vel_targets[2]
        data.ctrl[id_wrist_1] = ang_vel_targets[3]
        data.ctrl[id_wrist_2] = ang_vel_targets[4]
        data.ctrl[id_wrist_3] = ang_vel_targets[5]

    robot = UR5e()
    timestep = model.opt.timestep
    print(timestep)
    timestep_count = 0

    time_vector = np.arange(0,10,timestep)
    q2 = robot.ikine_LM(SE3.Trans(0.0, 0.5, 0.5) * SE3.RPY(-180,0,0,unit="deg")).q
    q3 = robot.ikine_LM(SE3.Trans(0.0, 0.5, 0.25) * SE3.RPY(-180,0,0,unit="deg")).q
    # q4 = robot.ikine_LM(SE3.Trans(0.0, 0.5, 0.5) * SE3.RPY(-180,0,90,unit="deg")).q
    traj1 = rtb.jtraj(robot.configs["q0"], robot.configs["qh"], t=time_vector)
    traj2 = rtb.jtraj(robot.configs["qh"], q2, t=time_vector)
    traj3 = rtb.jtraj(q2, q3, t=time_vector)
    traj4 = rtb.jtraj(q3, q2, t=time_vector)
    traj5 = rtb.jtraj(q2, robot.configs["qh"], t=time_vector)
    traj = np.concatenate((traj1.q, traj2.q, traj3.q, traj4.q, traj5.q), axis=0)
    print(traj)
    
    set_ang_targets([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]) # Start with time step 0 speeds
    with mujoco.viewer.launch_passive(model, data) as viewer:
        start = time.time()    
        while viewer.is_running():
            step_start = time.time()

            if timestep_count < len(traj):
                set_ang_targets(traj[timestep_count])
            mujoco.mj_step(model, data)

            # Read robot base position
            # pos = data.xpos[id_base]
            # y, x = pos[0], -pos[1]

            viewer.sync()
            timestep_count += 1
            
            # Rudimentary time keeping, will drift relative to wall clock.
            time_until_next_step = model.opt.timestep - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)

if __name__ == "__main__":
    main()
