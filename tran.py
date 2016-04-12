
import devices
import netlist_parser
import numpy as np
from math import *
import matplotlib.pyplot as plt
import  plot


def solve_nonlinear(element, n1, n2, n1_en, n2_en, i, h):
    global res
    global solved
    res = np.linalg.solve(stamp, rhs)
    # print res
    # print element.vn
    if abs(res[n1]*n1_en-res[n2]*n2_en-element.vn) <= min(0.001*abs(element.vn), 1e-6):
        solved = 1
        # print element.vn
        # print res
        element.vn = 0.1
    else:
        element.vn = res[n1]*n1_en - res[n2]*n2_en
        build_stamps(elements, matrix_size, i, h)


class Vlist_tran:
    def __init__(self):
        self.id_list = []
        self.node1 = []
        self.node2 = []

    def lst_append(self, id, node_1, node_2=0):
        self.id_list.append(id)
        self.node1.append(node_1)
        self.node2.append(node_2)


class res_tran:
    def __init__(self):
        self.id_list = []
        self.value = []


class Ilist_tran:
    def __init__(self):
        self.id_list = []
        self.vid_list = []

    def lst_append(self, id, vid):
        self.id_list.append(id)
        self.vid_list.append(vid)


class simuValue_tran:
    def __init__(self,list_prim=[],list_deri=[]):
        self.list_prim = list_prim
        self.list_deri = list_deri
    def lst_append(self,init,init_deri=0):
        self.list_prim.append(init)
        self.list_deri.append(init_deri)
# class non_linear_unit:
#     def __init__(self,part_id,node1,node2):
#         self.
def tran(t,h=0.001,simumode=2):
    global stamp
    global rhs
    global simuValue_tran_dic
    global res_tran
    global vlist
    times = int(ceil(t/h))
    simuValue_tran_dic = {}
    res_tran = {}
    vlist = netlist_parser.vlist
    for i in xrange(times):
        solve_stamps(i,h,simumode)
    x_axis = np.arange(0,t,h)
    for i in xrange(len(vlist.id_list)):
        y_axis = np.array(res_tran[vlist.id_list[i]])
        plt.plot(x_axis, y_axis)
        plt.xlabel("t(s)")
        plt.ylabel("%s(v)" % vlist.id_list[i])
        plt.show()


def build_stamps(elements, matrix_size, i, h,simumode=2):
    global stamp
    global rhs
    stamp = np.zeros((matrix_size+inum,matrix_size+inum))
    rhs = np.zeros(matrix_size+inum)
    for k in xrange(len(elements)):
        n1_en = 1
        n2_en = 1
        n1 = elements[k].n1-1
        n2 = elements[k].n2-1
        if n1==-1:
            n1_en = 0
        if n2==-1:
            n2_en = 0
        if isinstance(elements[k],devices.Resistor):
            stamp[n1,n1] += (1/float(elements[k].value))*n1_en
            stamp[n2,n2] += (1/float(elements[k].value))*n2_en
            stamp[n1,n2] -= (1/float(elements[k].value))*n1_en*n2_en
            stamp[n2,n1] -= (1/float(elements[k].value))*n1_en*n2_en
        elif isinstance(elements[k],devices.ISource):
            if elements[k].is_timedependent:
                rhs[n1] -= (elements[k].function.calculate_value(i*h))*n1_en
                rhs[n2] += (elements[k].function.calculate_value(i*h))*n2_en
            else:
                rhs[n1] -= float(elements[k].dc_value)*n1_en
                rhs[n2] += float(elements[k].dc_value)*n2_en
        elif isinstance(elements[k],devices.VSource):
            if elements[k].is_timedependent:
                stamp[n1,matrix_size+elements[k].inum-1] += 1*n1_en
                stamp[n2,matrix_size+elements[k].inum-1] += -1*n2_en
                stamp[matrix_size+elements[k].inum-1,n1] += 1*n1_en
                stamp[matrix_size+elements[k].inum-1,n2] += -1*n2_en
                rhs[matrix_size+elements[k].inum-1] += elements[k].function.calculate_value(i*h)
            else:
                stamp[n1,matrix_size+elements[k].inum-1] += 1*n1_en
                stamp[n2,matrix_size+elements[k].inum-1] += -1*n2_en
                stamp[matrix_size+elements[k].inum-1,n1] += 1*n1_en
                stamp[matrix_size+elements[k].inum-1,n2] += -1*n2_en
                rhs[matrix_size+elements[k].inum-1] += float(elements[k].dc_value)
        elif isinstance(elements[k],devices.VCVS):
            sn1 = elements[k].sn1-1
            sn2 = elements[k].sn2-1
            stamp[matrix_size+elements[k].inum-1,n1] += 1*n1_en
            stamp[matrix_size+elements[k].inum-1,n2] += -1*n2_en
            stamp[matrix_size+elements[k].inum-1,sn1] -= float(elements[k].value)
            stamp[matrix_size+elements[k].inum-1,sn2] += float(elements[k].value)
            stamp[n1,matrix_size+elements[k].inum-1] += 1*n1_en
            stamp[n2,matrix_size+elements[k].inum-1] += -1*n2_en

        elif isinstance(elements[k],devices.VCCS):
            sn1 = elements[k].sn1-1
            sn2 = elements[k].sn2-1
            stamp[n1,sn1] += elements[k].value*n1_en*n2_en
            stamp[n1,sn2] -= elements[k].value*n1_en*n2_en
            stamp[n2,sn1] -= elements[k].value*n1_en*n2_en
            stamp[n2,sn2] += elements[k].value*n1_en*n2_en

        elif isinstance(elements[k],devices.CCVS):
            my_inum = netlist_parser.find_vnam(elements[k].vnam)
            stamp[matrix_size+elements[k].inum-1,matrix_size+my_inum-1] -= float(elements[k].value)
            stamp[matrix_size+elements[k].inum-1,n1] += 1*n1_en
            stamp[matrix_size+elements[k].inum-1,n2] += -1*n2_en
            stamp[n1,matrix_size+elements[k].inum-1] += 1*n1_en
            stamp[n2,matrix_size+elements[k].inum-1] += -1*n2_en



        elif isinstance(elements[k],devices.CCCS):
            my_inum = netlist_parser.find_vnam(elements[k].vnam)
            stamp[n1,matrix_size+my_inum-1] += float(elements[k].value)*n1_en
            stamp[n2,matrix_size+my_inum-1] += float(elements[k].value)*n2_en

        elif isinstance(elements[k],devices.Capacitor):
            if i==0:
                v_list = simuValue_tran()
                v_list.lst_append(elements[k].ic)
                simuValue_tran_dic[elements[k].part_id] = v_list
            if simumode==1:
                pass
            elif simumode==2:
                stamp[n1,matrix_size+elements[k].inum-1] += 1*n1_en
                stamp[n2,matrix_size+elements[k].inum-1] += -1*n2_en
                stamp[matrix_size+elements[k].inum-1,n1] += float(elements[k].value)*n1_en/h
                stamp[matrix_size+elements[k].inum-1,n2] -= float(elements[k].value)*n2_en/h
                stamp[matrix_size+elements[k].inum-1,matrix_size+elements[k].inum-1] -= 1
                rhs[matrix_size+elements[k].inum-1] += float(elements[k].value)*simuValue_tran_dic[elements[k].part_id].list_prim[i]/h
            elif simumode==3:
                stamp[n1,matrix_size+elements[k].inum-1] += 1*n1_en
                stamp[n2,matrix_size+elements[k].inum-1] += -1*n2_en
                stamp[matrix_size+elements[k].inum-1,n1] += 2*float(elements[k].value)*n1_en/h
                stamp[matrix_size+elements[k].inum-1,n2] -= 2*float(elements[k].value)*n2_en/h
                stamp[matrix_size+elements[k].inum-1,matrix_size+elements[k].inum-1] -= 1
                rhs[matrix_size+elements[k].inum-1] += 2*float(elements[k].value)*simuValue_tran_dic[elements[k].part_id].list_prim[i]/h


        elif isinstance(elements[k],devices.Inductor):
            if i==0:
                v_list = simuValue_tran()
                v_list.lst_append(elements[k].ic)
                simuValue_tran_dic[elements[k].part_id] = v_list
            if simumode==1:
                pass
            elif simumode==2:
                stamp[n1,matrix_size+elements[k].inum-1] += 1*n1_en
                stamp[n2,matrix_size+elements[k].inum-1] += -1*n2_en
                stamp[matrix_size+elements[k].inum-1,n1] += 1*n1_en
                stamp[matrix_size+elements[k].inum-1,n2] -= 1*n2_en
                stamp[matrix_size+elements[k].inum-1,matrix_size+elements[k].inum-1] -= elements[k].value/h
                rhs[matrix_size+elements[k].inum-1] -= float(elements[k].value)*simuValue_tran_dic[elements[k].part_id].list_prim[i]/h
            elif simumode==3:
                stamp[n1,matrix_size+elements[k].inum-1] += 1*n1_en
                stamp[n2,matrix_size+elements[k].inum-1] += -1*n2_en
                stamp[matrix_size+elements[k].inum-1,n1] += 1*n1_en
                stamp[matrix_size+elements[k].inum-1,n2] -= 1*n2_en
                stamp[matrix_size+elements[k].inum-1,matrix_size+elements[k].inum-1] -= (2*elements[k].value)/h
                rhs[matrix_size+elements[k].inum-1] -= 2*float(elements[k].value)*simuValue_tran_dic[elements[k].part_id].list_prim[i]/h
        elif isinstance(elements[k],devices.Diode):
            stamp[n1,n1] += elements[k].alpha*exp(elements[k].alpha*elements[k].vn)*n1_en*elements[k].isat
            stamp[n2,n2] += elements[k].alpha*exp(elements[k].alpha*elements[k].vn)*n2_en*elements[k].isat
            stamp[n1,n2] -= elements[k].alpha*exp(elements[k].alpha*elements[k].vn)*n1_en*n2_en*elements[k].isat
            stamp[n2,n1] -= elements[k].alpha*exp(elements[k].alpha*elements[k].vn)*n1_en*n2_en*elements[k].isat
            rhs[n1] -= n1_en*(exp(elements[k].alpha * elements[k].vn)- 1 - elements[k].alpha * exp(elements[k].alpha * elements[k].vn) * elements[k].vn) * elements[k].isat
            rhs[n2] += n2_en*(exp(elements[k].alpha * elements[k].vn)- 1 - elements[k].alpha * exp(elements[k].alpha * elements[k].vn) * elements[k].vn) * elements[k].isat
            # print "G"
            # print(elements[k].alpha*exp(elements[k].alpha*elements[k].vn)*n1_en*elements[k].isat)
            # print "I"
            # print (exp(elements[k].alpha * elements[k].vn)- 1 - elements[k].alpha * exp(elements[k].alpha * elements[k].vn) * elements[k].vn) * elements[k].isat
    # print stamp
    # print rhs

def solve_stamps(i,h,simumode):
    global simuValue_tran_dic
    global stamp
    global rhs
    global vlist
    global res_tran
    global elements
    global solved
    global res
    global inum
    global matrix_size
    matrix_size = netlist_parser.matrix_size-1
    inum = netlist_parser.inum
    elements = netlist_parser.circ.elements
    build_stamps(elements,matrix_size,i,h,simumode)
    # print stamp
    # print rhs
    #
    # print stamp
    # print rhs
    for j in xrange(len(elements)):
        if isinstance(elements[j],devices.Diode):
            solved = 0
            while not solved:
                n1_en = 1
                n2_en = 1
                n1 = elements[j].n1-1
                n2 = elements[j].n2-1
                if n1==-1:
                    n1_en = 0
                if n2==-1:
                    n2_en = 0
                solve_nonlinear(elements[j], n1, n2, n1_en, n2_en, i, h)
    res = np.linalg.solve(stamp,rhs)
    print res
    for j in xrange(len(elements)):
        if elements[j].islinear == 0:
            n1_en = 1
            n2_en = 1
            n1 = elements[j].n1-1
            n2 = elements[j].n2-1
            if n1 == -1:
                n1_en = 0
            if n2 == -1:
                n2_en = 0
            # print res[n1]*n1_en-res[n2]*n2_en
            if isinstance(elements[j],devices.Capacitor):
                simuValue_tran_dic[elements[j].part_id].lst_append(res[n1]*n1_en-res[n2]*n2_en)
            elif isinstance(elements[j],devices.Inductor):
                simuValue_tran_dic[elements[j].part_id].lst_append(res[matrix_size+elements[j].inum-1])


         # res_plot = res_tran()
         # if not globals().has_key('res_plot'):

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

