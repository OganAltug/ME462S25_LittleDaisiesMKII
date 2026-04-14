import roboticstoolbox as rtb
import matplotlib.pyplot as plt
import numpy as np
from numpy import pi
import spatialmath as sm

class UR5e(rtb.DHRobot):
    def __init__(self):
        super().__init__(
                [
                    rtb.RevoluteDH(d=0.1625, alpha=pi/2),
                    rtb.RevoluteDH(a=-0.425),
                    rtb.RevoluteDH(a=-0.3922),
                    rtb.RevoluteDH(d=0.1333, alpha=pi/2),
                    rtb.RevoluteDH(d=0.0997, alpha=-pi/2),
                    rtb.RevoluteDH(d=0.0996)
                ], name="UR5e"
                )
        self.addconfiguration(name="q0", q=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.addconfiguration(name="qh", q=[-pi/4, -5/36*pi, -29/36*pi, -1/18*pi, 0.0, 0.0])


if __name__ == "__main__":
    robot = UR5e()
    # traj = rtb.jtraj(np.array(robot.configs["q0"]), np.array(robot.configs["qh"]), 100)

    robot.q = robot.configs["qh"]
    Tep = robot.fkine(robot.q) * sm.SE3.Trans(0.2, 0.2, 0.45)
    arrived = False

    dt = 0.05

    while not arrived:
        v, arrived = rtb.p_servo(robot.fkine(robot.q), Tep, 1)
        robot.qd = np.linalg.pinv(robot.jacobe(robot.q)) @ v

    robot.plot(traj.q, block=True)