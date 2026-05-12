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
    print(timestep)
    timestep_count = 0

    time_vector = np.arange(0,2,timestep)
    
    q0 = robot.configs["q0"]
    q1 = robot.configs["qh"]
    q2 = robot.ikine_LM(SE3.Trans(0.0, 0.5, 0.5) * SE3.RPY(-180,0,0,unit="deg")).q
    q3 = robot.ikine_LM(SE3.Trans(0.0, 0.5, 0.25) * SE3.RPY(-180,0,0,unit="deg")).q

    f0 = robot.fkine(q0)
    f1 = robot.fkine(q1)
    f2 = robot.fkine(q2)
    f3 = robot.fkine(q3)

    w0 = np.append(f0.t, f0.rpy())
    w1 = np.append(f1.t, f1.rpy())
    w2 = np.append(f2.t, f2.rpy())
    w3 = np.append(f3.t, f3.rpy())

    w_path01 = np.linspace(w0,w1,len(time_vector))
    w_path12 = np.linspace(w1,w2,len(time_vector))
    w_path23 = np.linspace(w2,w3,len(time_vector))

    # q_path01 = [robot.ikine_LM(SE3.Trans(w[0:3:1]) * SE3.RPY(w[3:6:1])).q for w in w_path01]
    # q_path12 = [robot.ikine_LM(SE3.Trans(w[0:3:1]) * SE3.RPY(w[3:6:1])).q for w in w_path12]
    # q_path23 = [robot.ikine_LM(SE3.Trans(w[0:3:1]) * SE3.RPY(w[3:6:1])).q for w in w_path23]

    # q_path = np.concatenate((q_path01, q_path12, q_path23), axis=0)

    #initialize robot with 0 position
    q = copy.copy(q0)
    
    #=== JOINT SPACE INTERPOLATION ===
    traj1 = rtb.mtraj(rtb.quintic, q0, q1, t=time_vector)
    traj2 = rtb.mtraj(rtb.quintic, q1, q2, t=time_vector)
    traj3 = rtb.mtraj(rtb.quintic, q2, q3, t=time_vector)
    traj4 = rtb.mtraj(rtb.quintic, q3, q2, t=time_vector)
    traj5 = rtb.mtraj(rtb.quintic, q2, q1, t=time_vector)
    traj = np.concatenate((traj1.q, traj2.q, traj3.q, traj4.q, traj5.q), axis=0)
    
    set_ang_targets(q0) # Start with time step 0 speeds
    print("start simulating")
    with mujoco.viewer.launch_passive(model, data) as viewer:
        start = time.time()    
        prev_diff = 0
        accumulated_error = 0
        while viewer.is_running():
            step_start = time.time()
            q = data.qpos
            forward0 = robot.fkine(q)

            # #Joint space interpolation
            if timestep_count < len(traj):
                set_ang_targets(traj[timestep_count])

            #workspace interpolation
            # if timestep_count < len(q_path):
            #     set_ang_targets(q_path[timestep_count])

            #Resolved rate control    
            # Kp = 0.6
            # Kd = 0.001
            # Ki = 0.03
            # q_des = q1
            # forward1 = robot.fkine(q1)
            # des_pos = np.append(forward1.t, forward1.rpy())
            # pos = np.append(forward0.t, forward0.rpy())
            # t_diff = des_pos - pos
            # accumulated_error += t_diff
            # vel_diff = t_diff - prev_diff
            # prev_diff = copy.copy(t_diff)
            # vel = t_diff * Kp + vel_diff * Kd + accumulated_error * Ki
            # qd = np.linalg.pinv(robot.jacobe(q)) @ vel
            # q_target = q + qd*timestep
            # set_ang_targets(q_target)

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
