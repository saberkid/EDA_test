import devices
import netlist_parser
import numpy as np
from math import *
import matplotlib.pyplot as plt
import  plot


def solve_nonlinear(i, h, simumode):
    global res
    global elements
    solved = 0
    build_stamps_tran(i, h, simumode)
    res = np.linalg.solve(stamp, rhs)
    while not solved:
        solved = 1
        build_stamps_tran(i, h, simumode)
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
                    # print res[ng] * ng_en-res[ns] * ns_en-elements[j].vgs
                    # print res[nd] * nd_en-res[ns] * ns_en-elements[j].vds
                    solved = 0
                    elements[j].vgs = res[ng] * ng_en - res[ns] * ns_en
                    elements[j].vds = res[nd] * nd_en - res[ns] * ns_en
                    # print stamp
                    # print res
                    # print elements[j].vgs
        # print solved


# class simuValue_tran:
#     def __init__(self, list_prim=[], list_deri=[]):
#         self.list_prim = list_prim
#         self.list_deri = list_deri
#
#     def lst_append(self, init, init_deri=0):
#         self.list_prim.append(init)
#         self.list_deri.append(init_deri)
# class non_linear_unit:
#     def __init__(self,part_id,node1,node2):
#         self.


def tran(t, h=0.001, simumode=2):
    global stamp
    global rhs
    global res_tran
    global ilist
    global vlist
    ilist = None
    vlist = None
    times = int(ceil(t/h))
    res_tran = {}
    if netlist_parser.VLIST:
        vlist = netlist_parser.VLIST
    if netlist_parser.ILIST:
        ilist = netlist_parser.ILIST
    for i in xrange(times):
        solve_stamps(i, h, simumode)
    x_axis = np.arange(0, t, h)
    print vlist
    print ilist
    if vlist:
        for i in xrange(len(vlist.id_list)):
            y_axis = np.array(res_tran[vlist.id_list[i]])
            plt.plot(x_axis, y_axis, linestyle='-', label=vlist.id_list[i])
        plt.legend()
        plt.xlabel("t(s)")
        plt.ylabel("v(v)")
        plt.show()
    elif ilist:
        for i in xrange(len(ilist.id_list)):
            y_axis = np.array(res_tran[ilist.id_list[i]])
            plt.plot(x_axis, y_axis, linestyle='-', label=ilist.id_list[i])
        plt.legend()
        plt.xlabel("t(s)")
        plt.ylabel("i(A)")
        plt.show()


def build_stamps_tran(i, h, simumode=2):
    global stamp
    global rhs
    stamp = np.zeros((matrix_size+inum, matrix_size+inum))
    rhs = np.zeros(matrix_size+inum)
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
                if elements[k].value == 0:
                    pass
                else:
                    stamp[n1, n1] += (1/float(elements[k].value))*n1_en
                    stamp[n2, n2] += (1/float(elements[k].value))*n2_en
                    stamp[n1, n2] -= (1/float(elements[k].value))*n1_en*n2_en
                    stamp[n2, n1] -= (1/float(elements[k].value))*n1_en*n2_en
            elif isinstance(elements[k], devices.ISource):
                if elements[k].is_timedependent:
                    rhs[n1] -= (elements[k].function.calculate_value(i*h))*n1_en
                    rhs[n2] += (elements[k].function.calculate_value(i*h))*n2_en
                else:
                    rhs[n1] -= float(elements[k].dc_value)*n1_en
                    rhs[n2] += float(elements[k].dc_value)*n2_en
            elif isinstance(elements[k], devices.VSource):
                if elements[k].is_timedependent:
                    stamp[n1, matrix_size+elements[k].inum-1] += 1*n1_en
                    stamp[n2, matrix_size+elements[k].inum-1] += -1*n2_en
                    stamp[matrix_size+elements[k].inum-1, n1] += 1*n1_en
                    stamp[matrix_size+elements[k].inum-1, n2] += -1*n2_en
                    rhs[matrix_size+elements[k].inum-1] += elements[k].function.calculate_value(i*h)
                else:
                    stamp[n1, matrix_size+elements[k].inum-1] += 1*n1_en
                    stamp[n2, matrix_size+elements[k].inum-1] += -1*n2_en
                    stamp[matrix_size+elements[k].inum-1, n1] += 1*n1_en
                    stamp[matrix_size+elements[k].inum-1, n2] += -1*n2_en
                    rhs[matrix_size+elements[k].inum-1] += float(elements[k].dc_value)
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
                if simumode == 1:
                    pass
                elif simumode == 2:
                    stamp[n1, matrix_size+elements[k].inum-1] += 1*n1_en
                    stamp[n2, matrix_size+elements[k].inum-1] += -1*n2_en
                    stamp[matrix_size+elements[k].inum-1, n1] += float(elements[k].value)*n1_en/h
                    stamp[matrix_size+elements[k].inum-1, n2] -= float(elements[k].value)*n2_en/h
                    stamp[matrix_size+elements[k].inum-1, matrix_size+elements[k].inum-1] -= 1
                    rhs[matrix_size+elements[k].inum-1] += float(elements[k].value) * elements[k].vn / h
                elif simumode == 3:
                    if elements[k].i == None:
                        stamp[matrix_size+elements[k].inum-1, matrix_size+elements[k].inum-1] += 1
                    else:
                        stamp[n1, matrix_size+elements[k].inum-1] += 1*n1_en
                        stamp[n2, matrix_size+elements[k].inum-1] += -1*n2_en
                        stamp[matrix_size+elements[k].inum-1, n1] += 2*float(elements[k].value)*n1_en/h
                        stamp[matrix_size+elements[k].inum-1, n2] -= 2*float(elements[k].value)*n2_en/h
                        stamp[matrix_size+elements[k].inum-1, matrix_size+elements[k].inum-1] -= 1
                        rhs[matrix_size+elements[k].inum-1] += 2*float(elements[k].value) * elements[k].vn / h + elements[k].i

            elif isinstance(elements[k], devices.Inductor):
                if simumode == 1:
                    pass
                elif simumode == 2:
                    stamp[n1, matrix_size+elements[k].inum-1] += 1*n1_en
                    stamp[n2, matrix_size+elements[k].inum-1] += -1*n2_en
                    stamp[matrix_size+elements[k].inum-1, n1] += 1*n1_en
                    stamp[matrix_size+elements[k].inum-1, n2] -= 1*n2_en
                    stamp[matrix_size+elements[k].inum-1, matrix_size+elements[k].inum-1] -= elements[k].value/h
                    rhs[matrix_size+elements[k].inum-1] -= float(elements[k].value) * elements[k].i / h
                elif simumode == 3:
                    if elements[k].vn == None:
                        stamp[matrix_size+elements[k].inum-1, n1] += 1 * n1_en
                        stamp[matrix_size+elements[k].inum-1, n2] += -1 * n2_en
                        stamp[n1, matrix_size+elements[k].inum-1] += 1 * n1_en
                        stamp[n2, matrix_size+elements[k].inum-1] += -1 * n2_en
                    else:
                        stamp[n1, matrix_size+elements[k].inum-1] += 1*n1_en
                        stamp[n2, matrix_size+elements[k].inum-1] += -1*n2_en
                        stamp[matrix_size+elements[k].inum-1, n1] += 1*n1_en
                        stamp[matrix_size+elements[k].inum-1, n2] -= 1*n2_en
                        stamp[matrix_size+elements[k].inum-1, matrix_size+elements[k].inum-1] -= (2*elements[k].value)/h
                        rhs[matrix_size+elements[k].inum-1] -= 2*float(elements[k].value)*elements[k].i / h + elements[k].vn
            elif isinstance(elements[k], devices.Diode):
                stamp[n1, n1] += elements[k].alpha*exp(elements[k].alpha*elements[k].vn)*n1_en*elements[k].isat
                stamp[n2, n2] += elements[k].alpha*exp(elements[k].alpha*elements[k].vn)*n2_en*elements[k].isat
                stamp[n1, n2] -= elements[k].alpha*exp(elements[k].alpha*elements[k].vn)*n1_en*n2_en*elements[k].isat
                stamp[n2, n1] -= elements[k].alpha*exp(elements[k].alpha*elements[k].vn)*n1_en*n2_en*elements[k].isat
                rhs[n1] -= n1_en*(exp(elements[k].alpha * elements[k].vn) - 1 - elements[k].alpha * exp(elements[k].alpha * elements[k].vn) * elements[k].vn) * elements[k].isat
                rhs[n2] += n2_en*(exp(elements[k].alpha * elements[k].vn) - 1 - elements[k].alpha * exp(elements[k].alpha * elements[k].vn) * elements[k].vn) * elements[k].isat
    # print stamp
    # print rhs


def solve_stamps(i, h, simumode):
    global stamp
    global rhs
    global vlist
    global ilist
    global res_tran
    global res
    global inum
    global matrix_size
    global elements
    elements = netlist_parser.circ.elements
    matrix_size = netlist_parser.matrix_size-1
    inum = netlist_parser.inum
    if i == 0 and simumode == 3:# TR initialization
        build_stamps_tran(elements, matrix_size, i, h, simumode)
        res = np.linalg.solve(stamp, rhs)
        for z in xrange(len(elements)):
            if isinstance(elements[z], devices.Capacitor) or isinstance(elements[z], devices.Inductor):
                n1_en = 1
                n2_en = 1
                n1 = elements[z].n1-1
                n2 = elements[z].n2-1
                if n1 == -1:
                    n1_en = 0
                if n2 == -1:
                    n2_en = 0
                # print res[n1]*n1_en-res[n2]*n2_en
                if isinstance(elements[z], devices.Capacitor):
                    elements[z].vn = res[n1]*n1_en-res[n2]*n2_en
                elif isinstance(elements[z], devices.Inductor):
                    elements[z].i = res[matrix_size+elements[z].inum-1]
    # build_stamps_tran(elements, matrix_size, i, h, simumode)
    # res = np.linalg.solve(stamp, rhs)
    # print stamp
    # print rhs
    #
    # print stamp
    # print rhs
    # for j in xrange(len(elements)):
    #     if isinstance(elements[j], devices.Diode):
    #         solved = 0
    #         while not solved:
    #             n1_en = 1
    #             n2_en = 1
    #             n1 = elements[j].n1-1
    #             n2 = elements[j].n2-1
    #             if n1 == -1:
    #                 n1_en = 0
    #             if n2 == -1:
    #                 n2_en = 0
    #             solve_nonlinear(elements[j], n1, n2, n1_en, n2_en, i, h)
    solve_nonlinear(i, h, simumode)

    # print res
    for j in xrange(len(elements)):
        if isinstance(elements[j], devices.Capacitor) or isinstance(elements[j], devices.Inductor):
            n1_en = 1
            n2_en = 1
            n1 = elements[j].n1-1
            n2 = elements[j].n2-1
            if n1 == -1:
                n1_en = 0
            if n2 == -1:
                n2_en = 0
            # print res[n1]*n1_en-res[n2]*n2_en
            if isinstance(elements[j], devices.Capacitor):
                elements[j].vn = res[n1]*n1_en-res[n2]*n2_en
                elements[j].i = res[matrix_size+elements[j].inum-1]
            elif isinstance(elements[j], devices.Inductor):
                elements[j].vn = res[n1]*n1_en-res[n2]*n2_en
                elements[j].i = res[matrix_size+elements[j].inum-1]
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
                res_tran[vlist.id_list[m]] = value_list
            else:
                res_tran[vlist.id_list[m]].append(res[n1]*n1_en-res[n2]*n2_en) #save value for the plot
        # print res_tran["v2"]
    if ilist:
        for n in xrange(len(ilist.id_list)):
            vsrc = ilist.vid_list[n]
            for j in xrange(len(elements)):
                if elements[j].part_id == vsrc:
                    inum = elements[j].inum

            if i == 0:
                value_list = [res[matrix_size+inum-1]]#init a dictionary
                res_tran[ilist.id_list[n]] = value_list
            else:
                res_tran[ilist.id_list[n]].append(res[matrix_size+inum-1])

