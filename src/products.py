class Products:
    """
    Define a Products class to describe the characteristics of various products.
    """
    def __init__(self, total_num):

        self.total_num = total_num
        self.category = []
        self.demand_rate = [] 
        self.safety_stock = []
        self.required_space = []

    def stacks_demand(self):
        from math import ceil
        pass

