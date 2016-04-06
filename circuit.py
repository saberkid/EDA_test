class Circuit:
    def __init__(self,description=None):
        self.nodes_dict = {}
        self.elements = []
        self.description = ""

    def add_node(self,ext_name):
        if ext_name not in self.nodes_dict:
            if ext_name == '0':
                int_node = 0
            else:
                got_ref = 0 in self.nodes_dict
                int_node = int(len(self.nodes_dict)/2) + 1*(not got_ref)
            self.nodes_dict.update({int_node:ext_name})
            self.nodes_dict.update({ext_name:int_node})
        else:
            int_node = self.nodes_dict[ext_name]
        return int_node