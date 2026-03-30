import mujoco
import mujoco.viewer
import time
import numpy as np
import roboticstoolbox as rtb
from spatialmath import SE3
from rtb_test import UR5e # Assuming this loads your URDF/DH parameters

def wrap_to_shortest(q_start, q_end):
    """
    Adjusts q_end so that the distance from q_start is minimized 
    by accounting for 2pi wrap-around.
    """
    diff = q_end - q_start
    # Standard wrap to [-pi, pi]
    diff_normalized = (diff + np.pi) % (2 * np.pi) - np.pi
    return q_start + diff_normalized

def main():
    model = mujoco.MjModel.from_xml_path("scene.xml")
    data = mujoco.MjData(model)
    robot = UR5e()
    
    # Get actuator IDs
    actuator_names = ["shoulder_pan", "shoulder_lift", "elbow", "wrist_1", "wrist_2", "wrist_3"]
    actuator_ids = [mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, name) for name in actuator_names]

    # 1. Define Keyframes
    q0 = robot.configs["q0"]
    qh = robot.configs["qh"]
    
    # Solve IK for targets
    # Note: ikine_LM returns a solution, but it might be 2*pi away from your current pose
    raw_q2 = robot.ikine_LM(SE3.Trans(0.0, 0.5, 0.5) * SE3.RPY(-np.pi, 0, 0)).q
    raw_q3 = robot.ikine_LM(SE3.Trans(0.0, 0.5, 0.25) * SE3.RPY(-np.pi, 0, 0)).q

    # 2. Normalize targets to ensure shortest path
    q2 = wrap_to_shortest(qh, raw_q2)
    q3 = wrap_to_shortest(q2, raw_q3)

    # 3. Generate Trajectories
    dt = model.opt.timestep
    t_vec = np.arange(0, 5, dt) # 2-second segments for smoother motion

    segments = [
        rtb.jtraj(q0, qh, t_vec).q,
        rtb.jtraj(qh, q2, t_vec).q,
        rtb.jtraj(q2, q3, t_vec).q,
        rtb.jtraj(q3, q2, t_vec).q,
        rtb.jtraj(q2, qh, t_vec).q
    ]
    
    full_traj = np.concatenate(segments, axis=0)

    # Sync MuJoCo initial state with trajectory start
    data.qpos[:6] = q0
    mujoco.mj_forward(model, data)

    with mujoco.viewer.launch_passive(model, data) as viewer:
        for target_q in full_traj:
            step_start = time.time()
            
            # Apply control
            data.ctrl[actuator_ids] = target_q
            
            mujoco.mj_step(model, data)
            viewer.sync()

            # Real-time sync
            elapsed = time.time() - step_start
            if elapsed < dt:
                time.sleep(dt - elapsed)
            
            if not viewer.is_running():
                break

if __name__ == "__main__":
    main()