import simpy
from CONSTANT import *

"""
Current line or adjacent psb robot will be designated to the new order.
"""


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
        self.state = 1
        self.resource = simpy.Resource(self.env)

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
        time_cur_place2target = self.get_horizontal_transport_time((target[1] - self.current_place[1]) * length)[-1]
        self.update_dwell_point(target)
        return time_cur_place2target

    def get_bin_with_immediate_return(self, warehouse, xy, stack_tier):
        """
        immediate return
        reshuffle -> target bin go to temporarily place -> return blocking bins -> go to workstation.
        """
        target_bin_new_stack_y, _ = self.reshuffle_blocking_bin(warehouse, xy, stack_tier)
        time_target_bin_temporarily = self.transport_bin_to_destination(
                stack_tier,
                warehouse.record[self.current_line][target_bin_new_stack_y].size(), xy[1], target_bin_new_stack_y)
        time_return_blocking_bins = self.return_blocking_bins(warehouse)
        time_to_temporarily = self.get_horizontal_transport_time(abs(target_bin_new_stack_y-xy[1])*length)[-1]+t_lu*2
        time_to_workstation = self.retrieve_target_bin_to_workstation(
                warehouse.record[self.current_line][target_bin_new_stack_y].size(), target_bin_new_stack_y)
        total_time = time_target_bin_temporarily + time_return_blocking_bins + time_to_temporarily + time_to_workstation

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

    def reshuffle_blocking_bin(self, warehouse, designated_bin_xy: tuple, target_bin):
        cur_stack = warehouse.record[designated_bin_xy[0]][designated_bin_xy[1]]
        cur_y = designated_bin_xy[1]
        # blocking_bins = cur_stack[target_bin + 1:]

        adjacent_stack = [n for m in [(cur_y + i, cur_y - i) for i in range(1, WIDTH)] for n in m if 0 < n <= LENGTH]
        # put blocking bins on the top of adjacent stack to form a line with length direction.
        adjacent_place_chosen = 0
        time_reshuffle_blocking_bins = 0

        while cur_stack.size() != target_bin+1:
            next_stack = warehouse.record[self.current_line][adjacent_stack[adjacent_place_chosen]]
            current_bin = cur_stack.size()
            next_bin = next_stack.size() + 1
            if next_stack.size() < HEIGHT_AVAILABLE:
                self.register_reshuffle(adjacent_stack[adjacent_place_chosen])
                cur_stack.pop()
                next_stack.items.append(1)
                time_reshuffle_blocking_bins += self.transport_bin_to_destination(
                        cur_y, adjacent_stack[adjacent_place_chosen], current_bin, next_bin)
                adjacent_place_chosen += 1
            else:
                pass

        self.register_reshuffle(cur_y)
        return adjacent_stack[adjacent_place_chosen+1], time_reshuffle_blocking_bins

    def return_blocking_bins(self, warehouse):
        previous_y = self.reshuffle_task.pop()
        current_stack = warehouse.record[self.current_line][previous_y]
        time_return = 0

        while len(self.reshuffle_task) > 0:
            next_task = self.reshuffle_task.pop()
            new_stack = current_stack.size()
            time_return += self.transport_bin_to_destination(
                    next_task, previous_y, warehouse.record[self.current_line][next_task].size()+1, new_stack)

        return time_return

    def transport_bin_to_destination(self, previous_y, new_y, previous_stack, new_stack):
        down_up_to_peek = self.get_vertical_transport_time((HEIGHT-previous_stack)*height)[-1] * 2
        horizon_to_back_adjacent = self.get_horizontal_transport_time((abs(previous_y-new_y))*length)[-1] * 2
        drop_off_up = self.get_vertical_transport_time((HEIGHT-new_stack)*height)[-1] * 2
        total_time = down_up_to_peek + horizon_to_back_adjacent + drop_off_up + t_lu * 2
        return total_time

    def storage(self, target, warehouse):
        # down -> up -> storage place -> down -> up
        down_up_to_peek = self.get_vertical_transport_time(HEIGHT * height)[-1] * 2
        time_wk2storage = self.goto(target)
        st = warehouse.record[target[0]][target[1]]
        drop_off_up = self.get_vertical_transport_time((HEIGHT - (st.size()+1)) * height)[-1] * 2
        total_time = down_up_to_peek + time_wk2storage + drop_off_up + t_lu * 2

        return  total_time

    def update_dwell_point(self, destination):
        self.current_place = destination

    def register_reshuffle(self, y: int):
        # reshuffle task is recorded in the form of int of y coordinate.
        self.reshuffle_task.append(y)

    # def clear_reshuffle(self):
    #     self.reshuffle_task = []

    def change_line(self, pre_line, new_line, pst):
        time_change_line = pst.change_line(pre_line, new_line, self)
        self.current_line = new_line
        return time_change_line

    def busy(self):
        self.state = 0

    def release(self):
        self.state = 1
