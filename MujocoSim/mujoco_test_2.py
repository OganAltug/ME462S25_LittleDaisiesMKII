import mujoco
import mujoco.viewer
from robot_descriptions import ur5e_mj_description
import time
from math import cos, sin
from rtb_test import UR5e
import roboticstoolbox as rtb
import numpy as np
from spatialmath import SE3
import copy

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

    def set_ang_targets(ang_targets):
        data.ctrl[id_shoulder_pan] = ang_targets[0] 
        data.ctrl[id_shoulder_lift] = ang_targets[1]
        data.ctrl[id_elbow] = ang_targets[2]
        data.ctrl[id_wrist_1] = ang_targets[3]
        data.ctrl[id_wrist_2] = ang_targets[4]
        data.ctrl[id_wrist_3] = ang_targets[5]

    robot = UR5e()
    timestep = model.opt.timestep
    print(f"Timestep: {timestep}")
    timestep_count = 0

    time_vector = np.arange(0, 2, timestep)
    steps = len(time_vector)
    
    q0 = robot.configs["q0"]
    q1 = robot.configs["qh"]
    q2 = robot.ikine_LM(SE3.Trans(0.0, 0.5, 0.5) * SE3.RPY(-180, 0, 0, unit="deg")).q
    q3 = robot.ikine_LM(SE3.Trans(0.0, 0.5, 0.25) * SE3.RPY(-180, 0, 0, unit="deg")).q

    # 1. Get Forward Kinematics as proper SE3 poses
    f0 = robot.fkine(q0)
    f1 = robot.fkine(q1)
    f2 = robot.fkine(q2)
    f3 = robot.fkine(q3)

    # 2. Generate smooth Cartesian trajectories (returns arrays of SE3 objects)
    print("Generating Cartesian paths...")
    path01_SE3 = rtb.ctraj(f0, f1, steps)
    path12_SE3 = rtb.ctraj(f1, f2, steps)
    path23_SE3 = rtb.ctraj(f2, f3, steps)

    # 3. Solve Inverse Kinematics iteratively, seeding the solver with the previous pose
    print("Solving IK for trajectory...")
    q_path01 = []
    q_guess = q0
    for pose in path01_SE3:
        sol = robot.ikine_LM(pose, q0=q_guess).q
        q_path01.append(sol)
        q_guess = sol  # update guess for next point

    q_path12 = []
    for pose in path12_SE3:
        sol = robot.ikine_LM(pose, q0=q_guess).q
        q_path12.append(sol)
        q_guess = sol
        
    q_path23 = []
    for pose in path23_SE3:
        sol = robot.ikine_LM(pose, q0=q_guess).q
        q_path23.append(sol)
        q_guess = sol

    # 4. Concatenate the full trajectory
    q_path = np.concatenate((q_path01, q_path12, q_path23), axis=0)

    # Initialize robot with 0 position
    q = copy.copy(q0)
    
    #=== JOINT SPACE INTERPOLATION (Kept as comments per your script) ===
    # traj1 = rtb.mtraj(rtb.quintic, q0, q1, t=time_vector)
    # traj2 = rtb.mtraj(rtb.quintic, q1, q2, t=time_vector)
    # traj3 = rtb.mtraj(rtb.quintic, q2, q3, t=time_vector)
    # traj4 = rtb.mtraj(rtb.quintic, q3, q2, t=time_vector)
    # traj5 = rtb.mtraj(rtb.quintic, q2, q1, t=time_vector)
    # traj = np.concatenate((traj1.q, traj2.q, traj3.q, traj4.q, traj5.q), axis=0)
    
    set_ang_targets(q0) # Start with time step 0 speeds
    print("Start simulating!")
    
    with mujoco.viewer.launch_passive(model, data) as viewer:
        start = time.time()    
        while viewer.is_running():
            step_start = time.time()
            q = data.qpos
            forward0 = robot.fkine(q)

            # Workspace interpolation playback
            if timestep_count < len(q_path):
                set_ang_targets(q_path[timestep_count])

            mujoco.mj_step(model, data)

            viewer.sync()
            timestep_count += 1
            
            # Rudimentary time keeping, will drift relative to wall clock.
            time_until_next_step = model.opt.timestep - (time.time() - step_start)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)

if __name__ == "__main__":
    main()