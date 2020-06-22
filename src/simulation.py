# 重点在于 Storage policy and Reshuffling policy
import logging
import simpy
import random
from src.cell import Cell
from warehouse import Warehouse
from PST import PST
from CONSTANT import *
from PSBs import PSBs
from workstation import Workstation


class Simulation:
    """
    define the overall simulation class to realize discrete event simulation.
    """

    """
    1. Order arrives at poisson process
    2. System  assigns an available and closer robot to the order OR wait in the queue.
    3. PSB robot moves in shortest path
    4. PSB robot fetches the retrieval bin.
        dedicated storage: pick up the top bin.
    ✓✓✓✓shared storage policy: ✓✓✓✓
                if retrieval bin is on peek: pick up
                else: reshuffling
                            ✓✓✓✓ immediate reshuffling ✓✓✓✓
                                 delayed reshuffling
    5. PSB robot transports bin to designated workstation, drop off and pick up a storage bin.
    6. PSB robot transports to storage point. random stack:
                                at any position zoned stacks: got to the zone determined by turnover.
    7. PSB robot drop off the bin on the top of a randomly stack.
    8. If previous retrieval includes a reshuffling, then returning blocking bins to storage rack.
    """

    def __init__(self, environment, warehouse_, psbs_, pst_, wk, wk_re):
        self.env = environment
        self.psbs = psbs_
        self.pst = pst_
        self.warehouse = warehouse_
        self.workstation = wk
        self.workstation_re = wk_re
        self.SR = environment.process(self.source_order())

    @property
    def energy_consumption(self):
        return 0

    @property
    def utility_consumption(self):
        return 0

    def source_order(self):
        """
        In simulation time, keeping registering [Storage&Retrieval] process
        into the simulation environment.
        """
        index_order = 0
        while True:
            index_order += 1
            order = self.retrieve_store(f'Order {index_order}')
            self.env.process(order)
            t_order_arrive = random.expovariate(ARRIVAL_RATE)
            yield self.env.timeout(t_order_arrive)

    def retrieve_store(self, name):
        """
        work flow of the psb
        """
        time_order_arrive = env.now
        logging.info(
            "{:10.2f}, {} arrives.".format(
                time_order_arrive, name))
        yield env.timeout(0)
        # destination first dimension is the width code.
        # that is the ordinal number of workstation and psb.
        # ARRIVAL: designated place.

        order_place, stack_tier = self.warehouse.rand_place()  # (x, y), z
        logging.info(
            "{:10.2f}, {} target x,y={}, tier={}".format(
                env.now, name, order_place, stack_tier))
        current_line = order_place[0]
        target_y = order_place[1]
        warehouse_record = self.warehouse.record
        if self.psbs.get_line_state()[current_line]:
            logging.info("{:10.2f}, this line has a psb.".format(env.now))
            psb = self.psbs.fleet[current_line]
            with self.psbs.resource[current_line].request() as req_psb:
                yield req_psb
                logging.info(
                    "{:10.2f}, {} has seized the [psb_{}]".format(
                        env.now, name, current_line))

                # label_psb_start = env.now
                # immediate return blocking bins.
                if warehouse_record[current_line][target_y].is_peek(
                        stack_tier):
                    logging.info(
                        "{:10.2f}, target is on the peek of that stack. peek:{}".format(
                            env.now, stack_tier))
                    time_psb2retrieve_point = psb.goto(order_place)
                    yield env.timeout(time_psb2retrieve_point)
                    logging.info(
                        "{:10.2f}, [psb_{}] has arrived at the target place.".format(
                            env.now, current_line))

                    time_retrieve2workstation = psb.retrieve_target_bin_to_workstation(
                        stack_tier, order_place[1])
                    yield env.timeout(time_retrieve2workstation)
                    logging.info(
                        "{:10.2f}, [psb_{}] has transported {} at the target place.".format(
                            env.now, current_line, name))

                else:
                    logging.info(
                        "{:10.2f}, target is not on the peek of the stack. peek:{}".format(
                            env.now, warehouse_record[current_line][target_y].size()))
                    time_psb2retrieve_point = psb.goto(order_place)
                    yield env.timeout(time_psb2retrieve_point)
                    logging.info(
                        "{:10.2f}, [psb_{}] has arrived at the retrieve point {}.".format(
                            env.now, current_line, order_place))

                    time_reshuffle_return_go = psb.get_bin_with_immediate_return(
                        warehouse, order_place, stack_tier)
                    yield env.timeout(time_reshuffle_return_go)
                    logging.info(
                        "{:10.2f}, {} [psb_{}] has finished the reshuffling and went to the workstation.".format(
                            env.now, name, current_line))

            psb.release()
            psb.update_dwell_point(
                (current_line, self.workstation[current_line].place_y))
            logging.info(
                "{:10.2f}, [psb_{}] has been released at {}".format(
                    env.now, current_line, psb.current_place))

        else:
            pass

        with self.workstation_re[current_line].request() as req_wk:
            logging.info(
                "{:10.2f}, {} request the workstation".format(
                    env.now, name))
            yield req_wk
            logging.info(
                    "{:10.2f}, {} seized the workstation".format(
                            env.now, name))
            time_pickup = self.workstation[current_line].pick_up()
            yield env.timeout(time_pickup)
            logging.info(
                    "{:10.2f}, workstation {} has finished {} picking up".format(
                            env.now, current_line, name))

        env.process(self.store(current_line, name))

    def store(self, line, name):
        # time_storage_arrive = env.now
        yield env.timeout(0)
        logging.info(
                "{:10.2f}, {}_store has arrived".format(
                        env.now, name))
        target_y = random.randint(1, self.warehouse.LENGTH)
        logging.info(
                "{:10.2f}, {}_store will be stored at {}".format(
                        env.now, name, (line, target_y)))
        if self.psbs.get_line_state()[line]:
            logging.info(
                    "{:10.2f}, line {} has a psb".format(
                            env.now, line))
            psb = self.psbs.fleet[line]
            with self.psbs.resource[line].request() as req_psb:
                yield req_psb
                logging.info(
                        "{:10.2f}, {}_store seized psb_{}".format(
                                env.now, name, line))

                # label_psb_start = env.now
                time_store = psb.storage((line, target_y - 1), self.warehouse)
                yield env.timeout(time_store)
                logging.info(
                        "{:10.2f}, {}_store has been finished".format(
                                env.now, name))
                psb.release()
                psb.update_dwell_point((line, target_y - 1))
                logging.info(
                        "{:10.2f}, [psb_{}]has been released at {}".format(
                                env.now, line, (line, target_y - 1)))
        else:
            pass


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename='test.log',
        filemode='w')

    # storage_policy = ["dedicated", "shared", "random&zoned"]
    storage_policy = "shared"
    # reshuffling_policy = ["immediate", "delayed"]
    reshuffling_policy = "immediate"
    psb_dwell_policy = "dwell in the place where the last ordered finished"
    constraint_psb = 3

    env = simpy.Environment()
    cell = Cell()
    warehouse = Warehouse(cell)
    psbs = PSBs(
        env,
        v_horizontal,
        v_vertical,
        psb_weight,
        acc_horizontal,
        acc_vertical)
    pst = PST(
        v_horizontal,
        v_vertical,
        psb_weight,
        acc_horizontal,
        acc_vertical)
    workstations = [Workstation(i) for i in range(N_WORKSTATIONS)]
    workstation_resource = [simpy.Resource(env) for i in range(N_WORKSTATIONS)]

    sim = Simulation(
        env,
        warehouse,
        psbs,
        pst,
        workstations,
        workstation_resource)

    simulation_time = 60 * 60
    env.run(simulation_time)
