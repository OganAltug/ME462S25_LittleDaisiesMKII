import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# 1) GEOMETRY VALUES - CHANGE THESE ACCORDING TO YOUR SYSTEM
# ============================================================

a1 = 100.0      # link a1 length
a2 = 80.0       # link a2 length
a3 = 120.0      # link a3 length

cx = 50.0       # horizontal distance OA
cy = 40.0       # vertical distance OD

e1 = 20.0       # horizontal offset for orange point
d1 = 30.0       # orange point distance from point C

gamma_deg = 90.0
gamma = np.deg2rad(gamma_deg)

# Choose mechanism assembly branch: +1 or -1
BRANCH_THETA1_INPUT = +1
BRANCH_THETA3_INPUT = +1

# Sweep ranges for plots
theta1_min_deg = 0.0
theta1_max_deg = 180.0

theta3_min_deg = 0.0
theta3_max_deg = 180.0

N = 1000


# ============================================================
# 2) BASIC FUNCTIONS
# ============================================================

def rad2deg_unwrap(angle_rad):
    return np.rad2deg(np.unwrap(angle_rad))


def compute_L(theta2, theta3):
    """
    Calculates Lx, Ly, and L.
    Angles must be in radians.
    """
    Lx = e1 + a3 * np.cos(theta3) + d1 * np.cos(gamma + theta2 - np.pi)
    Ly = cy + a3 * np.sin(theta3) + d1 * np.sin(gamma + theta2 - np.pi)
    L = np.sqrt(Lx**2 + Ly**2)
    return Lx, Ly, L


def solve_from_theta1(theta1, branch=+1):
    """
    Input: theta1 in radians
    Output: theta2, theta3, Lx, Ly, L, valid
    """

    theta1 = np.asarray(theta1)

    C1 = cx + a1 * np.cos(theta1)
    C2 = a1 * np.sin(theta1) - cy

    d = np.sqrt(C1**2 + C2**2)
    phi = np.arctan2(C2, C1)

    arg = (a3**2 - a2**2 - d**2) / (2 * a2 * d)

    valid = (d > 1e-9) & (arg >= -1.0) & (arg <= 1.0)
    arg_clip = np.clip(arg, -1.0, 1.0)

    theta2 = phi + branch * np.arccos(arg_clip)

    theta3 = np.arctan2(
        C2 + a2 * np.sin(theta2),
        C1 + a2 * np.cos(theta2)
    )

    Lx, Ly, L = compute_L(theta2, theta3)

    theta2 = np.where(valid, theta2, np.nan)
    theta3 = np.where(valid, theta3, np.nan)
    Lx = np.where(valid, Lx, np.nan)
    Ly = np.where(valid, Ly, np.nan)
    L = np.where(valid, L, np.nan)

    return theta2, theta3, Lx, Ly, L, valid


def solve_from_theta3(theta3, branch=+1):
    """
    Input: theta3 in radians
    Output: theta1, theta2, Lx, Ly, L, valid
    """

    theta3 = np.asarray(theta3)

    K1 = a3 * np.cos(theta3) - cx
    K2 = cy + a3 * np.sin(theta3)

    s = np.sqrt(K1**2 + K2**2)
    psi = np.arctan2(K2, K1)

    arg = (s**2 + a2**2 - a1**2) / (2 * a2 * s)

    valid = (s > 1e-9) & (arg >= -1.0) & (arg <= 1.0)
    arg_clip = np.clip(arg, -1.0, 1.0)

    theta2 = psi + branch * np.arccos(arg_clip)

    theta1 = np.arctan2(
        K2 - a2 * np.sin(theta2),
        K1 - a2 * np.cos(theta2)
    )

    Lx, Ly, L = compute_L(theta2, theta3)

    theta1 = np.where(valid, theta1, np.nan)
    theta2 = np.where(valid, theta2, np.nan)
    Lx = np.where(valid, Lx, np.nan)
    Ly = np.where(valid, Ly, np.nan)
    L = np.where(valid, L, np.nan)

    return theta1, theta2, Lx, Ly, L, valid


def is_valid_scalar(valid):
    return bool(np.asarray(valid).item())


# ============================================================
# 3) OPTION 1 - PLOT WHOLE VALUES FOR INPUT THETA1
# ============================================================

def plot_for_input_theta1():
    theta1_deg = np.linspace(theta1_min_deg, theta1_max_deg, N)
    theta1 = np.deg2rad(theta1_deg)

    theta2, theta3, Lx, Ly, L, valid = solve_from_theta1(
        theta1,
        branch=BRANCH_THETA1_INPUT
    )

    fig, ax = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax[0].plot(theta1_deg, theta1_deg, label=r"$\theta_1$")
    ax[0].plot(theta1_deg, rad2deg_unwrap(theta2), label=r"$\theta_2$")
    ax[0].plot(theta1_deg, rad2deg_unwrap(theta3), label=r"$\theta_3$")
    ax[0].set_ylabel("Angle (deg)")
    ax[0].set_title(r"Whole Solution for Input $\theta_1$")
    ax[0].grid(True)
    ax[0].legend()

    ax[1].plot(theta1_deg, Lx, label=r"$L_x$")
    ax[1].plot(theta1_deg, Ly, label=r"$L_y$")
    ax[1].set_xlabel(r"Input $\theta_1$ (deg)")
    ax[1].set_ylabel("Length / Position")
    ax[1].grid(True)
    ax[1].legend()

    plt.tight_layout()
    plt.show()


# ============================================================
# 4) OPTION 2 - PLOT WHOLE VALUES FOR INPUT THETA3
# ============================================================

def plot_for_input_theta3():
    theta3_deg = np.linspace(theta3_min_deg, theta3_max_deg, N)
    theta3 = np.deg2rad(theta3_deg)

    theta1, theta2, Lx, Ly, L, valid = solve_from_theta3(
        theta3,
        branch=BRANCH_THETA3_INPUT
    )

    fig, ax = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax[0].plot(theta3_deg, rad2deg_unwrap(theta1), label=r"$\theta_1$")
    ax[0].plot(theta3_deg, rad2deg_unwrap(theta2), label=r"$\theta_2$")
    ax[0].plot(theta3_deg, theta3_deg, label=r"$\theta_3$")
    ax[0].set_ylabel("Angle (deg)")
    ax[0].set_title(r"Whole Solution for Input $\theta_3$")
    ax[0].grid(True)
    ax[0].legend()

    ax[1].plot(theta3_deg, Lx, label=r"$L_x$")
    ax[1].plot(theta3_deg, Ly, label=r"$L_y$")
    ax[1].set_xlabel(r"Input $\theta_3$ (deg)")
    ax[1].set_ylabel("Length / Position")
    ax[1].grid(True)
    ax[1].legend()

    plt.tight_layout()
    plt.show()


# ============================================================
# 5) OPTION 3 - GIVEN THETA3, WRITE THETA1 AND LX
# ============================================================

def value_from_theta3():
    theta3_input_deg = float(input("Enter theta3 input in degrees: "))

    theta3 = np.deg2rad(theta3_input_deg)

    theta1, theta2, Lx, Ly, L, valid = solve_from_theta3(
        theta3,
        branch=BRANCH_THETA3_INPUT
    )

    if not is_valid_scalar(valid):
        print("\nNo valid mechanism solution for this theta3.")
        return

    print("\nResult for given theta3:")
    print("--------------------------------")
    print(f"Input theta3 = {theta3_input_deg:.4f} deg")
    print(f"theta1       = {float(np.rad2deg(theta1)):.4f} deg")
    print(f"theta2       = {float(np.rad2deg(theta2)):.4f} deg")
    print(f"Lx           = {float(Lx):.4f}")
    print(f"Ly           = {float(Ly):.4f}")
    print(f"L            = {float(L):.4f}")


# ============================================================
# 6) OPTION 4 - GIVEN THETA1, WRITE THETA3 AND LX
# ============================================================

def value_from_theta1():
    theta1_input_deg = float(input("Enter theta1 input in degrees: "))

    theta1 = np.deg2rad(theta1_input_deg)

    theta2, theta3, Lx, Ly, L, valid = solve_from_theta1(
        theta1,
        branch=BRANCH_THETA1_INPUT
    )

    if not is_valid_scalar(valid):
        print("\nNo valid mechanism solution for this theta1.")
        return

    print("\nResult for given theta1:")
    print("--------------------------------")
    print(f"Input theta1 = {theta1_input_deg:.4f} deg")
    print(f"theta2       = {float(np.rad2deg(theta2)):.4f} deg")
    print(f"theta3       = {float(np.rad2deg(theta3)):.4f} deg")
    print(f"Lx           = {float(Lx):.4f}")
    print(f"Ly           = {float(Ly):.4f}")
    print(f"L            = {float(L):.4f}")


# ============================================================
# 7) OPTION 5 - GIVEN DESIRED LX, WRITE THETA1 AND THETA3
# ============================================================

def bisection_root(func, a, b, tol=1e-8, max_iter=100):
    fa = func(a)
    fb = func(b)

    if np.isnan(fa) or np.isnan(fb):
        return None

    if fa == 0:
        return a

    if fb == 0:
        return b

    if fa * fb > 0:
        return None

    for _ in range(max_iter):
        c = 0.5 * (a + b)
        fc = func(c)

        if np.isnan(fc):
            return None

        if abs(fc) < tol:
            return c

        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc

    return 0.5 * (a + b)


def Lx_error_from_theta1(theta1_rad, desired_Lx):
    theta2, theta3, Lx, Ly, L, valid = solve_from_theta1(
        theta1_rad,
        branch=BRANCH_THETA1_INPUT
    )

    if not is_valid_scalar(valid):
        return np.nan

    return float(Lx - desired_Lx)


def value_from_desired_Lx():
    desired_Lx = float(input("Enter desired Lx value: "))

    theta1_grid_deg = np.linspace(theta1_min_deg, theta1_max_deg, N)
    theta1_grid = np.deg2rad(theta1_grid_deg)

    theta2, theta3, Lx, Ly, L, valid = solve_from_theta1(
        theta1_grid,
        branch=BRANCH_THETA1_INPUT
    )

    error = Lx - desired_Lx
    solutions = []

    for i in range(len(theta1_grid) - 1):
        if not valid[i] or not valid[i + 1]:
            continue

        e_a = error[i]
        e_b = error[i + 1]

        if np.isnan(e_a) or np.isnan(e_b):
            continue

        if e_a * e_b <= 0:
            root = bisection_root(
                lambda th: Lx_error_from_theta1(th, desired_Lx),
                theta1_grid[i],
                theta1_grid[i + 1]
            )

            if root is None:
                continue

            theta2_r, theta3_r, Lx_r, Ly_r, L_r, valid_r = solve_from_theta1(
                root,
                branch=BRANCH_THETA1_INPUT
            )

            if is_valid_scalar(valid_r):
                theta1_deg = float(np.rad2deg(root))
                theta3_deg = float(np.rad2deg(theta3_r))

                # Prevent repeated nearly identical roots
                already_exists = False
                for old in solutions:
                    if abs(old[0] - theta1_deg) < 1e-4:
                        already_exists = True
                        break

                if not already_exists:
                    solutions.append(
                        (
                            theta1_deg,
                            theta3_deg,
                            float(Lx_r),
                            float(Ly_r),
                            float(L_r)
                        )
                    )

    print("\nResult for desired Lx:")
    print("--------------------------------")
    print(f"Desired Lx = {desired_Lx:.4f}")

    if len(solutions) == 0:
        print("No theta1 and theta3 solution found for this Lx.")
        return

    for k, sol in enumerate(solutions, start=1):
        theta1_deg, theta3_deg, Lx_val, Ly_val, L_val = sol

        print(f"\nSolution {k}")
        print(f"theta1 = {theta1_deg:.4f} deg")
        print(f"theta3 = {theta3_deg:.4f} deg")
        print(f"Lx     = {Lx_val:.4f}")
        print(f"Ly     = {Ly_val:.4f}")
        print(f"L      = {L_val:.4f}")


# ============================================================
# 8) MENU
# ============================================================

def print_menu():
    print("\n========================================")
    print("KINEMATIC SOLUTION MENU")
    print("========================================")
    print("1 - Plot whole values for input theta1")
    print("2 - Plot whole values for input theta3")
    print("3 - Given theta3, calculate theta1 and Lx")
    print("4 - Given theta1, calculate theta3 and Lx")
    print("5 - Given desired Lx, calculate theta1 and theta3")
    print("0 - Exit")
    print("========================================")


def main():
    while True:
        print_menu()

        choice = input("Select an option: ")

        if choice == "1":
            plot_for_input_theta1()

        elif choice == "2":
            plot_for_input_theta3()

        elif choice == "3":
            value_from_theta3()

        elif choice == "4":
            value_from_theta1()

        elif choice == "5":
            value_from_desired_Lx()

        elif choice == "0":
            print("Program finished.")
            break

        else:
            print("Invalid option. Please select 0, 1, 2, 3, 4, or 5.")


if __name__ == "__main__":
    main()