# 重点在于 Storage policy and Reshuffling policy
import simpy
import random
from function import rand_product


class Simulation:
    """
    define the overall simulation class to realize discrete event simulation.
    """

    """
    1. arrive at poisson process
    2. system randomly assigns an available robot to order /wait
    3. move in shortest path
    4. robot fetches the retrieval bin.
        dedicated storage: pick up the yop bin
        shared policy:
                if retrieval bin is on peek: pick up
                else: reshuffling
                        immediate reshuffling
                        delayed reshuffling
    5. robot trans to designated workstation,drop off and pick up a storage bin
    6. robot transports to storage point. random stack: at any position
                    zoned stacks: got to the zone determined by turnover.
    7. robot drop off the bin
    8. if previous retrieval includes a reshuffling, then returning blockings
                                                            to storage rack.
    """

    def __init__(self, env, psbs, pst):
        self.env = env
        self.SR = env.process(self.souce_storage(env, psbs, pst,))

    @property
    def E_C(self):
        return 0

    @property
    def U_V(self):
        return 0

    def source_order(self, psbs, pst, stack, warehouse):
        """
        In simulation time, keeping registering [Storage&Retrieval] process
        into the simulation environment.
        """
        ind_order = 0
        while True:
            ind_order += 1
            o = self.retrieve_store(env, f'STORAGE {ind_order}', psbs,
                                    pst, warehouse)
            env.process(o)
            t_OrderArrive = random.expovariate(lambd)
            yield env.timeout(t_OrderArrive)

    def retrieve_store(self, env, name, warehouse):
        """
        z
        """
        timepoint_arrive = env.now
        yield env.timeout(0)

        dest = rand_product(warehouse)
        warehouse.retrieve(dest)
        



if __name__ == "__main__":
    env = simpy.Environment()
    lambd = []



stack : 3-dim [[[], [], [], ]]