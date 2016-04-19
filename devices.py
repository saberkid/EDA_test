import model
import netlist_parser

class Object():
    def __init__(self, part_id=None, n1=None, n2=None, value=None, islinear=1):
        self.part_id = part_id
        self.n1 = n1
        self.n2 = n2
        self.value = value
        self.islinear = islinear


class Resistor(Object):
    def __init__(self, part_id=None, n1=None, n2=None, value=None, islinear=1):
        self.part_id = part_id
        self.n1 = n1
        self.n2 = n2
        self.value = value
        self.islinear = islinear



class Capacitor(Object):
    def __init__(self, part_id=None, n1=None, n2=None, value=None, ic=0, inum=None,islinear=1):
        self.part_id = part_id
        self.n1 = n1
        self.n2 = n2
        self.value = value
        self.vn = ic
        self.inum = inum
        self.islinear = islinear
        self.i = None


class Inductor(Object):
    def __init__(self, part_id=None, n1=None, n2=None, value=None, ic=0, inum=None,islinear=1):
        self.part_id = part_id
        self.n1 = n1
        self.n2 = n2
        self.value = value
        self.vn = None
        self.i = ic
        self.inum = inum
        self.islinear = islinear


class VSource(Object):
    def __init__(self, part_id=None, n1=None, n2=None, dc_value=None, ac_value=None, ac_phase=None, inum=None, islinear=1):
        self.part_id = part_id
        self.dc_value = dc_value
        self.ac_value = ac_value
        self.ac_phace = ac_phase
        self.n1 = n1
        self.n2 = n2
        self.is_timedependent = False
        self.function = None
        self.inum = inum
        self.islinear = islinear


class ISource(Object):
    def __init__(self, part_id=None, n1=None, n2=None, dc_value=None, ac_value=None, ac_phase=None,islinear=1):
        self.part_id = part_id
        self.dc_value = dc_value
        self.ac_value = ac_value
        self.ac_phace = ac_phase
        self.n1 = n1
        self.n2 = n2
        self.is_timedependent = False
        self.islinear = islinear

class VCVS(Object):
    def __init__(self, part_id=None, n1=None, n2=None, sn1=None, sn2=None, value=None, inum=None,islinear=1):
        self.part_id = part_id
        self.n1 = n1
        self.n2 = n2
        self.sn1 = sn1
        self.sn2 = sn2
        self.value = value
        self.inum = inum
        self.islinear = islinear


class VCCS(Object):
    def __init__(self, part_id=None, n1=None, n2=None, sn1=None, sn2=None, value=None,islinear=1):
        self.part_id = part_id
        self.n1 = n1
        self.n2 = n2
        self.sn1 = sn1
        self.sn2 = sn2
        self.value = value
        self.islinear = islinear


class CCVS(Object):
    def __init__(self, part_id=None, n1=None, n2=None, vnam=None, value=None, inum=None,islinear=1):
        self.part_id = part_id
        self.n1 = n1
        self.n2 = n2
        self.vnam = vnam
        self.value = value
        self.inum = inum
        self.islinear = islinear


class CCCS(Object):
    def __init__(self, part_id=None, n1=None, n2=None, value=None,vnam=None,islinear=1):
        self.part_id = part_id
        self.n1 = n1
        self.n2 = n2
        self.vnam = vnam
        self.value = value
        self.islinear = islinear


class Diode(Object):
    def __init__(self, part_id=None, n1=None, n2=None, model_label=None,islinear=1, alpha=40,vn=0.1, isat=1e-14):
        self.part_id = part_id
        self.n1 = n1
        self.n2 = n2
        self.model_label = model_label
        self.islinear = islinear
        self.alpha = alpha
        self.vn = vn
        self.isat = isat



class Mosfet(object):
    def __init__(self, part_id, nd, ng, ns, nb, model_name):
        self.part_id = part_id
        self.nd = nd
        self.ng = ng
        self.ns = ns
        self.nb = nb
        self.model_name = model_name
        self.k = None
        self.vt = None
        self.lb = None
        self.vgs = None
        self.vds = None
        self.type = None
        self.wl_ratio = None

    def find_model(self):
        try:
            self.k = netlist_parser.MODEL_DIC[self.model_name].k
            self.vt = netlist_parser.MODEL_DIC[self.model_name].vt
            self.lb = netlist_parser.MODEL_DIC[self.model_name].lb
            self.type = netlist_parser.MODEL_DIC[self.model_name].type
            self.wl_ratio = netlist_parser.MODEL_DIC[self.model_name].wl_ratio
            if self.type == "nmos":
                self.vgs = 1
                self.vds = 1

            elif self.type == "pmos":
                self.vgs = -1
                self.vds = -1
        except KeyError:
            print "No model called %s is found" % self.model_name

    def cal_gm(self):
        if self.type == "nmos":
            if self.vgs <= self.vt:
                return 0
            else:
                if self.vds > self.vgs - self.vt:
                    return self.k * self.wl_ratio * (self.vgs - self.vt) * (1 + self.lb * self.vds)
                elif self.vds > 0:
                    return self.k * self.wl_ratio * self.vds * (1 + self.lb * self.vds)
                else:
                    return self.k * self.wl_ratio * self.vds

        elif self.type == "pmos":
            if self.vgs >= self.vt:
                return 0
            else:
                if self.vds < self.vgs - self.vt:
                    return self.k * self.wl_ratio * (self.vgs - self.vt) * (1 + self.lb * self.vds)
                elif self.vds < 0:
                    return self.k * self.wl_ratio * self.vds * (1 + self.lb * self.vds)
                else:
                    return self.k * self.wl_ratio * self.vds

    def cal_gds(self):
        if self.type == "nmos":
            if self.vgs <= self.vt:
                return 0
            else:
                if self.vds > self.vgs - self.vt:
                    return 0.5 * self.k * self.wl_ratio * (self.vgs - self.vt)**2 * self.lb
                elif self.vds > 0:
                    return self.k * self.wl_ratio * (self.vgs - self.vt - self.vds +
                                                     2 * self.lb * (self.vgs - self.vt) * self.vds -
                                                     1.5 * self.lb * self.vds**2)
                else:
                    return self.k * self.wl_ratio * (self.vgs - self.vt - self.vds)

        elif self.type == "pmos":
            if self.vgs >= self.vt:
                return 0
            else:
                if self.vds < self.vgs - self.vt:
                    return 0.5 * self.k * self.wl_ratio * (self.vgs - self.vt)**2 * self.lb
                elif self.vds < 0:
                    return self.k * self.wl_ratio * (self.vgs - self.vt - self.vds +
                                                     2 * self.lb * (self.vgs - self.vt) * self.vds -
                                                     1.5 * self.lb * self.vds**2)
                else:
                    return self.k * self.wl_ratio * (self.vgs - self.vt - self.vds)

    def cal_ids(self):
        if self.type == "nmos":
            if self.vgs <= self.vt:
                return 0
            else:
                if self.vds > self.vgs - self.vt:
                    return 0.5 * self.k * self.wl_ratio * (self.vgs - self.vt)**2 * (1 + self.lb *self.vds)

                elif self.vds > 0:
                    return self.k * self.wl_ratio * ((self.vgs - self.vt) * self.vds - 0.5 * self.vds**2) * \
                             (1 + self.lb * self.vds)
                else:
                    return self.k * self.wl_ratio * ((self.vgs - self.vt) * self.vds - 0.5 * self.vds**2)

        elif self.type == "pmos":
            if self.vgs >= self.vt:
                return 0
            else:
                if self.vds < self.vgs - self.vt:
                    return 0.5 * self.k * self.wl_ratio * (self.vgs - self.vt)**2 * (1 + self.lb *self.vds)

                elif self.vds < 0:
                    return self.k * self.wl_ratio * ((self.vgs - self.vt) * self.vds - 0.5 * self.vds**2) * \
                             (1 + self.lb * self.vds)
                else:
                    return self.k * self.wl_ratio * ((self.vgs - self.vt) * self.vds - 0.5 * self.vds**2)
        # else:
        #     pass






