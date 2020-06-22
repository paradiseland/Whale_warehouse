WIDTH = 10
LENGTH = 30
HEIGHT = 10
width = .8
length = .6
height = .33

R = 30  # R is the number of robots.
N_WORKSTATIONS = WIDTH
ARRIVAL_RATE = 650/3600  # 650 orders/h
TAU = .2      # Fraction of total storage space reserved for further growth
GAMMA = .2    # Honeycombing effect factor
N_STACKS = WIDTH * LENGTH

HEIGHT_AVAILABLE = int(HEIGHT*(1-GAMMA))

v_horizontal = 3
v_vertical = 1.6
acc_horizontal = float('inf')
acc_vertical = float('inf')

t_lu = 1.2  # time for a psb to load/unload a bin
t_t = 1  # time for a pst seize a psb robot.

T_p = [5, 15]

psb_weight = 20

# Ratio of ordering cost to holding cost rate. Without loss of generality, we assume that K is the same for all products
K = 500
