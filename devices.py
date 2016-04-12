import numpy as np
import math
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
        self.ic = ic
        self.inum = inum
        self.islinear = islinear


class Inductor(Object):
    def __init__(self, part_id=None, n1=None, n2=None, value=None, ic=0, inum=None,islinear=1):
        self.part_id = part_id
        self.n1 = n1
        self.n2 = n2
        self.value = value
        self.ic = ic
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
    def __init__(self, part_id=None, n1=None, n2=None, model_label=None,islinear=1, alpha=40,vn=0.1, isat=1):
        self.part_id = part_id
        self.n1 = n1
        self.n2 = n2
        self.model_label = model_label
        self.islinear = islinear
        self.alpha = alpha
        self.vn = vn
        self.isat = isat


class Mosfet(object):
    def __init__(self, part_id=None, nd=None, ng=None, ns=None, nb=None, w=None, l=None):
        self.part_id = part_id
        self.nd = nd
        self.ng = ng
        self.ns = ns
        self.nb = nb
        self.w = w
        self.l = l



