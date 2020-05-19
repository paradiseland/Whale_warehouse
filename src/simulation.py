# 重点在于 Storage policy and Reshuffling policy
import simpy
import random
from function import rand_place
from PSB import PSB


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
        work flow of the psb
        """
        timepoint_arrive = env.now
        yield env.timeout(0)
        # dest first dimension is the width code.
        # that is the ordianl number of workstation and psb.
        # TODO: choose one of the arrival: designated product/designated place.
        dest = rand_place(warehouse)
        line = dest[0]
        psb = psbs[line]
        # TODO: workstation = [line, 0 , 0, 0]
        with psb.request() as req_psb:
            yield req_psb
            
            label_psb_start = env.now
            T_storage = psb.get_H_transport_time(workstation, dest)
            if psb.assignment_reshuffle:
                T_reshuffle = psb.reshuffle()
            else:
                T_reshuffle = 0

            T_retrievebin = psb.retrieve_bin(dest, len(warehouse[dest]))

            T_retrieval_workstation = psb.get_H_transport_time(
                place, workstation)

            T_workstation = T_storage + T_reshuffle + \
                T_retrievebin + T_retrieval_workstation
            env.timeout()

        warehouse.retrieve(dest)

        



if __name__ == "__main__":
    width = 10


    env = simpy.Environment()
    lambd = []
    psbs = [PSB(env, v_h, v_v, psb_w) for i in range(width)]


stack : 3-dim [[[], [], [], ]]
