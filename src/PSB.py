from simpy import Resource


class PSB(Resource):
    """
    Define a class of the psb Resource.
    """
    def __init__(self, env, v_h, v_v, psb_w, a_h=0, a_v=0,  capacity: int = 1):
        """
        Resouce:
        available property: users, queue, count,
        available method: request, release
        """
        super().__init__(self, env, capacity)
        self.h_velocity = v_h
        self.v_velocity = v_v
        self.h_acc = a_h
        self.v_acc = a_v
        self.weight = psb_w
        # TODO: provide the psb place update funtion
        self.place = 0
        self.assignment_reshuffle = False

    def get_H_transport_time(self, o, d):

        self.update_dwpoint(d)

    def get_V_transpoert_time(self, dest_tier, peek_tier):
        pass

    def retrieve_bin(self, dest, peek):

        self.register_reshuffle(self)

    def reshuffle(self, ):
        pass

    def update_dwpoint(self, dest):
        self.place = dest

    def register_reshuffle(self, dest, peek):
        self.assignment_reshuffle = True

    @property
    def state(self):
        return len(self.users)
