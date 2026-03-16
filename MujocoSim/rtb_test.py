import roboticstoolbox as rtb
import matplotlib.pyplot as plt
import numpy as np
from numpy import pi

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
    traj = rtb.jtraj(np.array(robot.configs["q0"]), np.array(robot.configs["qh"]), 100)
    # traj_func = rtb.trapezoidal_func(robot.configs["q0"], robot.configs["qh"], 100)
    # print(traj.q)
    robot.plot(traj.q, block=True)
    # traj.plot()