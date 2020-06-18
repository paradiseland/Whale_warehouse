from simpy import Resource
from CONSTANT import *
"""
Current line or adjacent psb robot will be designated to the new order.

"""


class PSB(Resource):
    """
    Define a class of the psb Resource.
    """

    def __init__(
            self,
            env,
            v_h,
            v_v,
            psb_w,
            a_h=float('inf'),
            a_v=float('inf'),
            capacity: int = 1):
        """
        Resource:
        available property: users, queue, count,
        available method: request, release
        """
        super().__init__(env, capacity)
        self.horizontal_velocity = v_h
        self.vertical_velocity = v_v
        self.horizontal_acceleration = a_h
        self.vertical_acceleration = a_v
        self.weight = psb_w
        # TODO: provide the psb place update funtion
        self.current_line = 0
        self.current_place = (self.current_line, 0)
        self.assignment_reshuffle = False

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

    def goto_workstation(self):
        _, _, time = self.get_horizontal_transport_time(self.current_place[1] * length)
        self.update_dwell_point((self.current_line, 0))
        return time

    def retrieve_bin(self, warehouse, designated_bin_xy: tuple, target_bin):
        cur_stack = warehouse.record[designated_bin_xy]
        cur_y = designated_bin_xy[1]
        blocking_bins = cur_stack[target_bin + 1:]

        adjacent_stack = [n for m in [(cur_y + i, cur_y - i) for i in range(1, 10)] for n in m if 0 < n <= LENGTH]
        #
        adjacent_place_chosen = 0
        time_reshuffle_blocking_bins = 0
        for i in range(len(blocking_bins)):
            pass
        while warehouse.record[self.current_line][adjacent_stack[adjacent_place_chosen]].size < HEIGHT_AVAILABLE:
            time_reshuffle_blocking_bins += self.transport_bin_to_destination()

    def transport_bin_to_destination(self, previous_y, new_y, previous_stack, new_stack):
        up_to_peek = self.get_vertical_transport_time((HEIGHT-previous_stack)*height)
        horizon_to_adjacent = self.get_horizontal_transport_time((abs(previous_y-new_y))*length)
        drop_off = self.get_vertical_transport_time((HEIGHT-new_stack)*height)
        total_time = up_to_peek + horizon_to_adjacent + drop_off
        return total_time

    def immediate_return_blocking_bins(self):
        pass

    def reshuffle(self, ):
        pass

    def update_dwell_point(self, destination):
        self.current_place = destination

    def register_reshuffle(self, destination, peek):
        self.assignment_reshuffle = True

    @property
    def state(self):
        return len(self.users)

    def change_line(self, new_line):
        self.current_line = new_line
