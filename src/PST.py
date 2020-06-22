from CONSTANT import *
import simpy


class PST:
    def __init__(self, env, v_h, v_v, a_h, a_v, capacity=1):
        self.env = env
        self.horizontal_velocity = v_h
        self.vertical_velocity = v_v
        self.horizontal_acceleration = a_h
        self.vertical_acceleration = a_v
        self.current_line = 0
        self.num = capacity
        self.resource = simpy.Resource(self.env)

    def change_line(self, pre, new, psb):
        _, _, time_psb_pst = psb.get_horizontal_transport_time(psb.current_place[1]*length)
        _, _, t_current_place_to_previous_line = self.get_horizontal_transport_time(abs(self.current_line-pre)*width)
        _, _, t_previous_new = self.get_horizontal_transport_time(abs(new-pre)*width)

        self.current_line = new
        time_change_line = max(time_psb_pst, t_current_place_to_previous_line) + t_previous_new
        psb.update_dwell_point((new, 0))
        return time_change_line

    @property
    def horizontal_distance_sign(self):
        return self.horizontal_velocity ** 2 / self.horizontal_acceleration

    def get_horizontal_transport_time(self, dis):
        if dis <= self.horizontal_distance_sign:
            # return accelerate-time (=decelerate), constant-time, total-time
            t_1 = pow((dis / self.horizontal_acceleration), 1 / 2)
            return t_1, 0, 2 * t_1
        else:
            t_1 = self.horizontal_velocity / self.horizontal_acceleration
            t_2 = (dis - self.horizontal_distance_sign) / self.horizontal_velocity
            return t_1, t_2, 2 * t_1 + t_2


if __name__ == '__main__':
    env = simpy.Environment()
    pass
