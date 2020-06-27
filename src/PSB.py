import simpy
from CONSTANT import *

"""
Current line or adjacent psb robot will be designated to the new order.
"""
import logging


# class PSB(Resource):
class PSB:
    """
    Define a class of the psb Resource.
    """
    def __init__(
            self,
            env,
            v_h,
            v_v,
            psb_weigh,
            a_h,
            a_v,
            i,
            capacity: int = 1,):
        """
        Resource:
        available property: users, queue, count,
        available method: request, release
        """
        # super().__init__(env, capacity)
        self.env = env
        self.horizontal_velocity = v_h
        self.vertical_velocity = v_v
        self.horizontal_acceleration = a_h
        self.vertical_acceleration = a_v
        self.weight = psb_weigh
        self.capacity = capacity
        self.current_line = i
        self.current_place = (self.current_line, 0)
        self.reshuffle_task = []
        self.state = 1  # initial state is idle
        self.resource = simpy.Resource(self.env)
        # self.pick_weight = GOOD_WEIGHT
        # self.power = 600  # 600W/h

    @property
    def horizontal_distance_sign(self):
        return self.horizontal_velocity ** 2 / self.horizontal_acceleration

    @property
    def vertical_distance_sign(self):
        return self.vertical_velocity ** 2 / self.vertical_acceleration

    def get_horizontal_transport_time(self, dis):
        if dis <= self.horizontal_distance_sign:
            # return accelerate-time (=decelerate), constant-time, total-time
            t_1 = pow((dis / self.horizontal_acceleration), 1 / 2)
            return t_1, 0, 2 * t_1
        else:
            t_1 = self.horizontal_velocity / self.horizontal_acceleration
            t_2 = (dis - self.horizontal_distance_sign) / self.horizontal_velocity
            return t_1, t_2, 2 * t_1 + t_2

    def get_vertical_transport_time(self, dis):
        if dis <= self.vertical_distance_sign:
            # return accelerate-time (=decelerate), constant-time, total-time
            t_1 = pow((dis / self.vertical_acceleration), 1 / 2)
            return t_1, 0, 2 * t_1
        else:
            t_1 = self.vertical_velocity / self.vertical_acceleration
            t_2 = (dis - self.vertical_distance_sign) / self.vertical_velocity
            return t_1, t_2, 2 * t_1 + t_2

    def goto(self, target):
        """
        compute the time consumption from current place to target place
        """
        _, _, time_cur_place2target = self.get_horizontal_transport_time(abs(target[1] - self.current_place[1]) * length)
        self.update_dwell_point(target)
        return time_cur_place2target

    def get_bin_with_immediate_return(self, warehouse, xy, stack_tier):
        """
        immediate return
        reshuffle -> target bin go to temporarily place -> return blocking bins -> go to workstation.
        """
        target_bin_new_stack_y, time_reshuffle = self.reshuffle_blocking_bin(warehouse, xy, stack_tier)
#         # logging.debug(f"current line = {self.current_line}, target y = {target_bin_new_stack_y}, xy = {xy}")
        time_target_bin_temporarily = self.transport_bin_to_destination(
                stack_tier,
                warehouse.record[self.current_line][target_bin_new_stack_y].size(), xy[1], target_bin_new_stack_y)
        warehouse.record[xy[0]][xy[1]].pop()
        warehouse.record[xy[0]][target_bin_new_stack_y].push(1)
        time_return_blocking_bins = self.return_blocking_bins(warehouse, xy[1])
        time_to_temporarily = self.get_horizontal_transport_time(abs(target_bin_new_stack_y-xy[1])*length)[-1]+t_lu*2
        time_to_workstation = self.retrieve_target_bin_to_workstation(
                warehouse.record[self.current_line][target_bin_new_stack_y].size(), target_bin_new_stack_y)
        warehouse.record[xy[0]][target_bin_new_stack_y].pop()

        total_time = time_reshuffle + time_target_bin_temporarily + time_return_blocking_bins\
                        + time_to_temporarily + time_to_workstation

        return total_time

    def get_bin_with_delayed_return(self, warehouse, xy, stack_tier):
        """
        delayed return: finish the transportation from target point to workstation.
        omit the return blocking time, refresh it #TODO: in the simulation
        """
        _, time_reshuffle = self.reshuffle_blocking_bin(warehouse, xy, stack_tier)
        time_to_workstation = self.retrieve_target_bin_to_workstation(stack_tier, xy[1])
        total_time = time_reshuffle + time_to_workstation + t_lu * 2

        return total_time

    def retrieve_target_bin_to_workstation(self, target_bin_stack, previous_y):
        down_up_to_peek = self.get_vertical_transport_time((HEIGHT - target_bin_stack) * height)[-1] * 2
        horizon_to_workstation = self.get_horizontal_transport_time(previous_y * length)[-1]
        drop_off_up = self.get_vertical_transport_time(HEIGHT * height)[-1] * 2
        total_time = down_up_to_peek + horizon_to_workstation + drop_off_up + t_lu * 2
        self.update_dwell_point((self.current_line, 0))
        return total_time

    def reshuffle_blocking_bin(self, warehouse, designated_bin_xy: tuple, stack_tier):
        """
        by reshuffle the bin of certain stack, get the target bin blocking by some bins.
        """

        cur_stack = warehouse.record[designated_bin_xy[0]][designated_bin_xy[1]]
        logging.debug("current stack size :{}".format(cur_stack.size()))
        logging.debug("target tier : {}".format(stack_tier))
        cur_y = designated_bin_xy[1]
        # logging.debug("sum of this line = {}".format(sum([i.size() for i in warehouse.record[designated_bin_xy[0]]])))
        # logging.debug("[{}] line state: {}".format(designated_bin_xy[0], [i.size() for i in warehouse.record[designated_bin_xy[0]]]))
        # blocking_bins = cur_stack[target_bin + 1:]

        adjacent_stack = [n for m in [(cur_y+i, cur_y-i) for i in range(1, LENGTH)] for n in m if 0 <= n <= LENGTH-1]
        # put blocking bins on the top of adjacent stack to form a line with length direction.
        adjacent_place_chosen = 0  # start place blocking bins in sequence.
        time_reshuffle_blocking_bins = 0
        # logging.debug("cur stack [{}] size : {} , and target tier is [{}]".format(cur_y, cur_stack.size(), stack_tier))
        while cur_stack.size() != stack_tier + 1:

            next_stack = warehouse.record[self.current_line][adjacent_stack[adjacent_place_chosen]]

            current_bin = cur_stack.size()
            next_bin = next_stack.size() + 1
            if next_stack.size() < HEIGHT_AVAILABLE:
                self.register_reshuffle(adjacent_stack[adjacent_place_chosen])
                # logging.debug("cur_stack [{}] not poped, size:{}".format(cur_y, cur_stack.size()))
                cur_stack.pop()
                # logging.debug("cur_stack [{}] poped, size{}".format(cur_y, cur_stack.size()))
                # logging.debug("next stack [{}] not pushed, size:{}".format(adjacent_stack[adjacent_place_chosen], next_stack.size()))

                next_stack.push(1)
                # logging.debug("******next stack [{}] pushed, size:{}".format(adjacent_stack[adjacent_place_chosen], next_stack.size()))
                time_reshuffle_blocking_bins += self.transport_bin_to_destination(
                        cur_y, adjacent_stack[adjacent_place_chosen], current_bin, next_bin)
            else:
                pass
#                 # logging.debug("next stack [{}] size: {} and be skipped".format(adjacent_stack[adjacent_place_chosen], next_stack.size()))

            adjacent_place_chosen += 1
            # print(f"adjacent_chosen = {adjacent_place_chosen},
            # {adjacent_stack[adjacent_place_chosen]},{self.current_line}")
            # print(f"{warehouse.record[self.current_line][adjacent_stack[adjacent_place_chosen]].items}")
            # print(adjacent_stack)
        # self.register_reshuffle(cur_y)
        # self.reshuffle_task.append(cur_y)
#         #     logging.debug("adjacent_place_chosen = {}".format(adjacent_place_chosen))
#         logging.debug("sum of this line = {}".format(sum([i.size() for i in warehouse.record[designated_bin_xy[0]]])))

        return adjacent_stack[adjacent_place_chosen], time_reshuffle_blocking_bins

    def return_blocking_bins(self, warehouse, last_y):
        """
        when the reshuffle task is not null, we came back and complete the reshuffling
        """
        # previous_y = self.reshuffle_task.pop()
        previous_stack = warehouse.record[self.current_line][last_y]
        time_return_blocking = 0

        while len(self.reshuffle_task) > 0:
            next_y = self.reshuffle_task.pop()
            warehouse.record[self.current_line][next_y].pop()
            previous_stack.items.append(1)
            new_stack_tier = previous_stack.size()
            time_return_blocking += self.transport_bin_to_destination(
                    next_y, last_y, warehouse.record[self.current_line][next_y].size()+1, new_stack_tier)
        return time_return_blocking

    def transport_bin_to_destination(self, previous_y, new_y, previous_stack, new_stack):
        """
        transport the blocking bins to peek of adjacent stack.
        the current place of PSB doesn't change
        """
        down_up_to_peek = self.get_vertical_transport_time((HEIGHT-previous_stack)*height)[-1] * 2
        horizon_to_back_adjacent = self.get_horizontal_transport_time((abs(previous_y-new_y))*length)[-1] * 2
        drop_off_up = self.get_vertical_transport_time((HEIGHT-new_stack)*height)[-1] * 2
        total_time = down_up_to_peek + horizon_to_back_adjacent + drop_off_up + t_lu * 2
        return total_time

    def storage(self, target, warehouse):
        # down -> up -> storage place -> down -> up
        line, target_y = target
        down_up_to_peek = self.get_vertical_transport_time(HEIGHT * height)[-1] * 2
        time_wk2storage = self.goto((line, target_y-1))
        st = warehouse.record[target[0]][target[1]]
        drop_off_up = self.get_vertical_transport_time((HEIGHT - (st.size()+1)) * height)[-1] * 2
        total_time = down_up_to_peek + time_wk2storage + drop_off_up + t_lu * 2

        return total_time

    def update_dwell_point(self, destination):
        self.current_place = destination

    def register_reshuffle(self, y: int):
        # reshuffle task is recorded in the form of int of y coordinate + [last y].
        self.reshuffle_task.append(y)

    def change_line(self, pre_line, new_line, pst):
        time_change_line = pst.change_line(pre_line, new_line, self)
        self.current_line = new_line
        return time_change_line

    def busy(self):
        self.state = 0

    def release(self):
        self.state = 1
