import devices
import netlist_parser
import numpy as np
from math import *
import matplotlib.pyplot as plt


class Vlist_ac:
    def __init__(self):
        self.id_list = []
        self.node1 = []
        self.node2 = []

    def lst_append(self, id, node_1, node_2=0):
        self.id_list.append(id)
        self.node1.append(node_1)
        self.node2.append(node_2)


class Ilist_ac:
    def __init__(self):
        self.id_list = []
        self.vid_list = []

    def lst_append(self, id, vid):
        self.id_list.append(id)
        self.vid_list.append(vid)


def solve_nonlinear(omega):
    global res
    global elements
    solved = 0
    build_stamps_ac(omega)
    res = np.linalg.solve(stamp, rhs)
    while not solved:
        solved = 1
        build_stamps_ac(omega)
        res = np.linalg.solve(stamp, rhs)
        for j in xrange(len(elements)):
            if isinstance(elements[j], devices.Diode):
                n1_en = 1
                n2_en = 1
                n1 = elements[j].n1-1
                n2 = elements[j].n2-1
                if n1 == -1:
                    n1_en = 0
                if n2 == -1:
                    n2_en = 0
                if abs(res[n1] * n1_en-res[n2] * n2_en-elements[j].vn) <= min(0.001 * abs(elements[j].vn), 1e-6):
                        # solved = 1
                    elements[j].vn = 0.1
                else:
                    solved = 0
                    elements[j].vn = res[n1]*n1_en - res[n2]*n2_en

            if isinstance(elements[j], devices.Mosfet):
                nd_en = 1
                ng_en = 1
                ns_en = 1
                nd = elements[j].nd - 1
                ng = elements[j].ng - 1
                ns = elements[j].ns - 1
                if nd == -1:
                    nd_en = 0
                if ng == -1:
                    ng_en = 0
                if ns == -1:
                    ns_en = 0
                if (abs(res[ng] * ng_en-res[ns] * ns_en-elements[j].vgs) <= min(0.0001 * abs(elements[j].vgs), 1e-6) and \
                        abs(res[nd] * nd_en-res[ns] * ns_en-elements[j].vds) <= min(0.0001 * abs(elements[j].vds), 1e-6))\
                        or (abs(res[ng] * ng_en-res[ns] * ns_en-elements[j].vgs) <= 1e-15 and abs(res[nd] * nd_en-res[ns] * ns_en-elements[j].vds) <= 1e-15):
                    pass
                        # solved = 1
                        # elements[j].find_model()
                else:
                    print res[ng] * ng_en-res[ns] * ns_en-elements[j].vgs
                    print res[nd] * nd_en-res[ns] * ns_en-elements[j].vds
                    solved = 0
                    elements[j].vgs = res[ng] * ng_en - res[ns] * ns_en
                    elements[j].vds = res[nd] * nd_en - res[ns] * ns_en
                    # print stamp
                    # print res
                    # print elements[j].vgs
        # print solved


def ac(n, fstart, fstop):
    global res_ac
    global vlist
    global ilist

    res_ac = {}
    vlist = None
    ilist = None
    if netlist_parser.VLIST:
        vlist = netlist_parser.VLIST
    if netlist_parser.ILIST:
        ilist = netlist_parser.ILIST
    fvalue = fstart
    omega = 2*pi*fvalue
    x_axis = []
    i = 0
    while fvalue < fstop:
        solve_stamps(i, omega)
        x_axis.append(fvalue)
        i += 1
        fvalue = fstart * 10**(i/n)
        omega = 2 * pi * fvalue

    x_axis = np.array(x_axis)

    if vlist:
        for i in xrange(len(vlist.id_list)):
            y_axis = np.array(res_ac[vlist.id_list[i]])
            plt.plot(x_axis, y_axis, label=vlist.id_list[i])
            plt.xlabel("f(Hz)")
            plt.ylabel("v(v)")
        plt.legend()
        plt.show()
    # elif ilist:
    #     for i in xrange(len(ilist.id_list)):
    #         y_axis = np.array(res_ac[ilist.id_list[i]])
    #         plt.plot(x_axis, y_axis, linestyle='-', label=ilist.id_list[i])
    #     plt.legend()
    #     plt.xlabel("t(s)")
    #     plt.ylabel("i(A)")
    #     plt.show()


def build_stamps_ac(omega):
    global stamp
    global rhs
    stamp = np.zeros((matrix_size+inum, matrix_size+inum))
    stamp = stamp.astype(complex)
    rhs = np.zeros(matrix_size+inum)
    rhs = rhs.astype(complex)
    for k in xrange(len(elements)):
        if isinstance(elements[k], devices.Mosfet):
            nd_en = 1
            ng_en = 1
            ns_en = 1
            nd = elements[k].nd - 1
            ng = elements[k].ng - 1
            ns = elements[k].ns - 1
            if nd == -1:
                nd_en = 0
            if ng == -1:
                ng_en = 0
            if ns == -1:
                ns_en = 0

            if not elements[k].k:
                elements[k].find_model()

            gm = elements[k].cal_gm()
            gds = elements[k].cal_gds()
            ids = elements[k].cal_ids()
            # print elements[k].part_id
            # print gm
            # print gds
            # print ids
            stamp[nd, nd] += gds * nd_en
            stamp[nd, ns] -= (gds + gm) * nd_en * ns_en
            stamp[nd, ng] += gm * nd_en * ng_en
            stamp[ns, nd] -= gds * ns_en * nd_en
            stamp[ns, ns] += (gds + gm) * ns_en
            stamp[ns, ng] -= gm * ns_en * ng_en
            rhs[nd] -= (ids - elements[k].vgs * gm - elements[k].vds * gds) * nd_en
            rhs[ns] += (ids - elements[k].vgs * gm - elements[k].vds * gds) * ns_en

        else:
            n1_en = 1
            n2_en = 1
            n1 = elements[k].n1-1
            n2 = elements[k].n2-1
            if n1 == -1:
                n1_en = 0
            if n2 == -1:
                n2_en = 0
            if isinstance(elements[k], devices.Resistor):
                stamp[n1, n1] += (1/float(elements[k].value))*n1_en
                stamp[n2, n2] += (1/float(elements[k].value))*n2_en
                stamp[n1, n2] -= (1/float(elements[k].value))*n1_en*n2_en
                stamp[n2, n1] -= (1/float(elements[k].value))*n1_en*n2_en
            elif isinstance(elements[k], devices.ISource):
                rhs[n1] -= float(elements[k].ac_value)*n1_en
                rhs[n2] += float(elements[k].ac_value)*n2_en
            elif isinstance(elements[k], devices.VSource):
                stamp[n1, matrix_size+elements[k].inum-1] += 1*n1_en
                stamp[n2, matrix_size+elements[k].inum-1] += -1*n2_en
                stamp[matrix_size+elements[k].inum-1, n1] += 1*n1_en
                stamp[matrix_size+elements[k].inum-1, n2] += -1*n2_en
                rhs[matrix_size+elements[k].inum-1] += float(elements[k].ac_value)

            elif isinstance(elements[k], devices.VCVS):
                sn1 = elements[k].sn1-1
                sn2 = elements[k].sn2-1
                stamp[matrix_size+elements[k].inum-1, n1] += 1*n1_en
                stamp[matrix_size+elements[k].inum-1, n2] += -1*n2_en
                stamp[matrix_size+elements[k].inum-1, sn1] -= float(elements[k].value)
                stamp[matrix_size+elements[k].inum-1, sn2] += float(elements[k].value)
                stamp[n1, matrix_size+elements[k].inum-1] += 1*n1_en
                stamp[n2, matrix_size+elements[k].inum-1] += -1*n2_en

            elif isinstance(elements[k], devices.VCCS):
                sn1 = elements[k].sn1-1
                sn2 = elements[k].sn2-1
                stamp[n1, sn1] += elements[k].value*n1_en*n2_en
                stamp[n1, sn2] -= elements[k].value*n1_en*n2_en
                stamp[n2, sn1] -= elements[k].value*n1_en*n2_en
                stamp[n2, sn2] += elements[k].value*n1_en*n2_en

            elif isinstance(elements[k], devices.CCVS):
                my_inum = netlist_parser.find_vnam(elements[k].vnam)
                stamp[matrix_size+elements[k].inum-1, matrix_size+my_inum-1] -= float(elements[k].value)
                stamp[matrix_size+elements[k].inum-1, n1] += 1*n1_en
                stamp[matrix_size+elements[k].inum-1, n2] += -1*n2_en
                stamp[n1, matrix_size+elements[k].inum-1] += 1*n1_en
                stamp[n2, matrix_size+elements[k].inum-1] += -1*n2_en

            elif isinstance(elements[k], devices.CCCS):
                my_inum = netlist_parser.find_vnam(elements[k].vnam)
                stamp[n1, matrix_size+my_inum-1] += float(elements[k].value)*n1_en
                stamp[n2, matrix_size+my_inum-1] += float(elements[k].value)*n2_en

            elif isinstance(elements[k], devices.Capacitor):
                stamp[n1, n1] += 1j * omega * elements[k].value * n1_en
                stamp[n1, n2] -= 1j * omega * elements[k].value * n1_en * n2_en
                stamp[n2, n1] -= 1j * omega * elements[k].value * n1_en * n2_en
                stamp[n2, n2] += 1j * omega * elements[k].value * n2_en

            elif isinstance(elements[k], devices.Inductor):
                stamp[matrix_size+elements[k].inum-1, matrix_size+elements[k].inum-1] += -1j * omega * elements[k].value
            elif isinstance(elements[k], devices.Diode):
                stamp[n1, n1] += elements[k].alpha*exp(elements[k].alpha*elements[k].vn)*n1_en*elements[k].isat
                stamp[n2, n2] += elements[k].alpha*exp(elements[k].alpha*elements[k].vn)*n2_en*elements[k].isat
                stamp[n1, n2] -= elements[k].alpha*exp(elements[k].alpha*elements[k].vn)*n1_en*n2_en*elements[k].isat
                stamp[n2, n1] -= elements[k].alpha*exp(elements[k].alpha*elements[k].vn)*n1_en*n2_en*elements[k].isat
                rhs[n1] -= n1_en*(exp(elements[k].alpha * elements[k].vn) - 1 - elements[k].alpha * exp(elements[k].alpha * elements[k].vn) * elements[k].vn) * elements[k].isat
                rhs[n2] += n2_en*(exp(elements[k].alpha * elements[k].vn) - 1 - elements[k].alpha * exp(elements[k].alpha * elements[k].vn) * elements[k].vn) * elements[k].isat
    # print stamp
    # print rhs


def solve_stamps(i, omega):
    global stamp
    global rhs
    global vlist
    global res_ac
    global res
    global inum
    global matrix_size
    global elements
    elements = netlist_parser.circ.elements
    matrix_size = netlist_parser.matrix_size-1
    inum = netlist_parser.inum
    for x in xrange(len(elements)):
        if isinstance(elements[x], devices.Capacitor):
            inum -= 1
    solve_nonlinear(omega)

    # print res
    if vlist:
        for m in xrange(len(vlist.id_list)):
            n1 = vlist.node1[m]-1# node needed to be plotted
            n2 = vlist.node2[m]-1
            n1_en = 1
            n2_en = 1
            if n1 == -1:
                n1_en = 0
            if n2 == -1:
                n2_en = 0
            if i == 0:
                value_list = [res[n1]*n1_en-res[n2]*n2_en]#init a dictionary
                res_ac[vlist.id_list[m]] = value_list
            else:
                res_ac[vlist.id_list[m]].append(res[n1]*n1_en-res[n2]*n2_en) #save value for the plot

    # if ilist:
    #     for n in xrange(len(ilist.id_list)):
    #         vsrc = ilist.vid_list[n]
    #         for j in xrange(len(elements)):
    #             if elements[j].part_id == vsrc:
    #                 inum = elements[j].inum
    #
    #         if i == 0:
    #             value_list = [res[matrix_size+inum-1]]#init a dictionary
    #             res_ac[ilist.id_list[n]] = value_list
    #         else:
    #             res_ac[ilist.id_list[n]].append(res[matrix_size+inum-1])
