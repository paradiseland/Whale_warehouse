# coding=utf-8
# /usr/bin/Python3.6

"""
Author: Xingwei CHEN
Email:cxw19@mails.tsinghua.edu.cn
"""
from CONSTANT import width, length, WIDTH
from PSB import PSB


class PSBs:
    def __init__(self, env, v_h, v_v, psb_w, a_h, a_v, number_of_psbs=WIDTH):
        self.fleet = [PSB(env, v_h, v_v, psb_w, a_h, a_v, i)
                      for i in range(number_of_psbs)]
        self.num = number_of_psbs
        self.resource = [psb.resource for psb in self.fleet]

    def get_closest_available(self, target):
        target_line, target_y = target
        available_psbs_index = [ind for ind, psb in enumerate(self.fleet) if psb.state == 1]
        distance = [(self.fleet[ind].current_place[1] + target_y) * length +
                    abs(ind - target_line) * width for ind in available_psbs_index]
        chosen_psb_index = available_psbs_index[distance.index(min(distance))]

        return chosen_psb_index

    def get_line_state(self):
        """
        whether each line has a available psb.
        """
        state = [0]*self.num
        for line in [psb.current_line for psb in self.fleet]:
            state[line] = True
        return state
if __name__ == "__main__":
    pass
