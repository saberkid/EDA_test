# model_dic = {
#
# }
LAMBDA_DEFAULT = 0
VTN_DEFAULT = 0.7
VTP_DEFAULT = -0.8
KN_DEFAULT = 1.3429e-6
KP_DEFAULT = 3.8367e-7


class Mos_Model():
    def __init__(self, name, type):
        if type == "nmos":
            self.k = KN_DEFAULT
            self.vt = VTN_DEFAULT
            self.lb = LAMBDA_DEFAULT
        elif type == "pmos":
            self.k = KP_DEFAULT
            self.vt = VTP_DEFAULT
            self.lb = LAMBDA_DEFAULT

