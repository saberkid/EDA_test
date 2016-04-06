import circuit
import devices
import tran
from time_function import sin
import dc
import ac
from string import *
circ = circuit.Circuit()
matrix_size = 0
inum = 0
class NetlistParseError(Exception):
    def __init__(self,arg):
        self.arg = arg
def find_vnam(vnam):
    # nc1 = None
    # nc2 = None
    inum = None
    for i in xrange(len(circ.elements)):
        if circ.elements[i].part_id==vnam:
            # nc1 = circ.elements[i].n1
            # nc2 = circ.elements[i].n2
            inum = circ.elements[i].inum
            return inum
            break
    if inum==None:
        raise NetlistParseError("find_vnam(vnam):No voltage source called %s is found"%vnam)

def units_converter(value_unit):
    # if isinstance(value_unit,(int,float)):
    #     return value_unit
    try:
        number = float(value_unit)
        return number
    except ValueError:
       pass
    if not len(value_unit):
        raise NetlistParseError("")
    for index in xrange(len(value_unit)):
        if not (value_unit[index].isdigit() or value_unit[index] == "." or
                value_unit[index] == "+" or value_unit[index] == "-" or
                value_unit[index] == "E"):
            break
    if index == 0:
        # print value_unit
        raise ValueError("Unable to parse value: %s" % value_unit)
        # return 0
    numeric_value = float(value_unit[:index])
    multiplier = value_unit[index:]
    if len(multiplier) == 0:
        pass # return numeric_value
    elif multiplier == "t":
        numeric_value = numeric_value * 1e12
    elif multiplier == "g":
        numeric_value = numeric_value * 1e9
    elif multiplier == "k":
        numeric_value = numeric_value * 1e3
    elif multiplier == "m":
        numeric_value = numeric_value * 1e-3
    elif multiplier == "u":
        numeric_value = numeric_value * 1e-6
    elif multiplier == "n":
        numeric_value = numeric_value * 1e-9
    elif multiplier == "p":
        numeric_value = numeric_value * 1e-12
    elif multiplier == "f":
        numeric_value = numeric_value * 1e-15
    elif multiplier == "meg":
        numeric_value = numeric_value * 1e6
    elif multiplier == "mil":
        numeric_value = numeric_value * 25.4e-6
    else:
        raise ValueError("Unknown multiplier %s" % multiplier)
    return numeric_value

def parse_equations(eq):
    (label, value) = eq.strip().split("=")
    return (label,value)

def parse_function(fun):
    pass
def to_function():
    pass
def parse_lines(lines):
    global matrix_size
    global inum
    matrix_size=0
    inum=0
    circ.__init__()
    line = (lines.lower().split("\n"))
    parse_function = {
        'c': lambda line: parse_elements_capacitor(line,circ),
        'd': lambda line: parse_elements_diode(line, circ),
        'e': lambda line: parse_elements_vcvs(line, circ),
        'f': lambda line: parse_elements_cccs(line, circ),
        'g': lambda line: parse_elements_vccs(line, circ),
        'h': lambda line: parse_elements_ccvs(line, circ),
        'i': lambda line: parse_elements_isource(line, circ),
        'l': lambda line: parse_elements_inductor(line, circ),
        'r': lambda line: parse_elements_resistor(line, circ),
        # 's': lambda line: parse_elements_switch(line, circ, models),
        'v': lambda line: parse_elements_vsource(line, circ)
            }
    parse_function_command = {
        '.plot': lambda line: parse_command_plot(line, circ),
        '.dc': lambda line: parse_command_dc(line),
        '.ac': lambda line: parse_command_ac(line),
        '.tran': lambda line: parse_command_tran(line)

        }
    try:
        find_ends = 0
        for line_num in xrange(len(line)):
            print line[line_num]
            if line[line_num] == "":
                continue
            elif line[line_num].find(".end") == 0:
                find_ends = 1
                break
            elif line[line_num].find('*') == 0:
                circ.description += ("line %d:"%(line_num+1)+line[line_num].replace('*','') + '\n')
            elif line[line_num].find('.') == 0:
                line_element = line[line_num].split()
                parse_function_command[line_element[0]](line[line_num])
            else:
                # print line[line_num][0]
                circ.elements += parse_function[line[line_num][0]](line[line_num])
        matrix_size += len(circ.nodes_dict)/2
        print matrix_size
        # print circ.description
        if not find_ends:
            raise NetlistParseError(".end not found")
    except NetlistParseError,e:
        print e.arg
    except KeyError, e:
        print "KeyError: no key word is found in line %d" %(line_num+1)

    # print circ.description

# def parse_command(line):
#     line_elements = line.split()
    # if line_elements[0] == '.include':
    #         file_list.append(parse_include_directive(line, netlist_wd))
    # elif line_elements[0] == ".plot":
    #     postproc.append((line, line_n))
                    # elif line_elements[0] == '.four':
                    #     postproc.append((line, line_n))
                    # elif line_elements[0] == '.fft':
     #     postproc.append((line, line_n))
    # elif line_elements[0] == ".model":
    #     model_directives.append((line, line_n))
                    # else:
                    #     directives.append((line, line_n))
                    # continue
def  parse_elements_vcvs(line, circ):
    global matrix_size
    global inum
    line_elements = line.split()
    if not len(line_elements)==6:
        raise NetlistParseError("")

    ext_n1 = line_elements[1]
    ext_n2 = line_elements[2]
    ext_sn1 = line_elements[3]
    ext_sn2 = line_elements[4]
    n1 = circ.add_node(ext_n1)
    n2 = circ.add_node(ext_n2)
    sn1 = circ.add_node(ext_sn1)
    sn2 = circ.add_node(ext_sn2)
    inum += 1
    elem = devices.VCVS(part_id=line_elements[0], n1=n1, n2=n2, sn1=sn1,
                            sn2=sn2, value=units_converter(line_elements[5]), inum=inum)
    # matrix_size += 1
    return [elem]
def  parse_elements_cccs(line, circ):
    line_elements = line.split()
    if not len(line_elements)==5:
        raise NetlistParseError("")

    ext_n1 = line_elements[1]
    ext_n2 = line_elements[2]
    vnam = line_elements[3]

    n1 = circ.add_node(ext_n1)
    n2 = circ.add_node(ext_n2)
    elem = devices.CCCS(part_id=line_elements[0], n1=n1, n2=n2, value=units_converter(line_elements[4]),vnam=vnam,)
    return [elem]
def  parse_elements_vccs(line, circ):
    line_elements = line.split()
    if not len(line_elements)==6:
        raise NetlistParseError("")

    ext_n1 = line_elements[1]
    ext_n2 = line_elements[2]
    ext_sn1 = line_elements[3]
    ext_sn2 = line_elements[4]
    n1 = circ.add_node(ext_n1)
    n2 = circ.add_node(ext_n2)
    sn1 = circ.add_node(ext_sn1)
    sn2 = circ.add_node(ext_sn2)

    elem = devices.VCCS(part_id=line_elements[0], n1=n1, n2=n2, sn1=sn1,
                            sn2=sn2, value=units_converter(line_elements[5]))
    return [elem]
def  parse_elements_ccvs(line, circ):
    global matrix_size
    global inum
    line_elements = line.split()
    if not len(line_elements)==5:
        raise NetlistParseError("")

    ext_n1 = line_elements[1]
    ext_n2 = line_elements[2]
    vnam = line_elements[3]

    n1 = circ.add_node(ext_n1)
    n2 = circ.add_node(ext_n2)

    inum += 1
    elem = devices.CCVS(part_id=line_elements[0], n1=n1, n2=n2, vnam=vnam, value=units_converter(line_elements[4]), inum=inum)
    # matrix_size += 1
    return [elem]

def  parse_elements_isource(line, circ):
    line = line.replace('(',' ')
    line = line.replace(')',' ')
    line_elements = line.split()
    if len(line_elements) < 3:
        raise NetlistParseError("parse_elem_isource(): malformed line")

    dc_value = None
    iac = None
    acp = 0
    function = None

    index = 3
    if line_elements[index][0].isdigit():
        dc_value = units_converter(line_elements[index])
        index += 1
    while True:  # for index in range(3, len(line_elements)):
        if index >= len(line_elements):
            break
        if line_elements[index][0] == '*':
            break
        if '=' in line_elements[index]:
            lable,value = parse_equations(line_elements[index])
            if lable == 'dc':
                dc_value = units_converter(value)
            elif lable == 'ac':
                iac = units_converter(value)
            else:
                raise NetlistParseError("parse_elem_isource(): unknown signal" + "type %s" % lable)
            # elif lable == 'pulse':
            #     param_number = 7
            # elif lable == 'exp':
            #     param_number = 6
            # elif lable == 'sin':
            #     param_number = 5
            # elif lable == 'sffm':
            #     param_number = 5
            # elif lable == 'am':
            #     param_number = 5
        else:
            lable = line_elements[index]
            if lable == 'dc':
                index += 1
                if index<len(line_elements):
                    if units_converter(line_elements[index]):
                        dc_value = units_converter(line_elements[index])
                else:
                    raise NetlistParseError("parse_elem_isource():No DC value is found when it's been defined")
            elif lable == 'ac':
                index += 1
                if index<=len(line_elements):
                    if units_converter(line_elements[index]):
                        iac = units_converter(line_elements[index])
                else:
                    raise NetlistParseError("parse_elem_isource():No AC value is found when it's been defined")
                index += 1
                if index<len(line_elements):
                    if line_elements[index].isdigit():
                        acp = units_converter(line_elements[index])
                else:
                    index -=1
            elif lable =='sin':
                index += 1
                if index<len(line_elements):
                    i0 = units_converter(line_elements[index])
                    index += 1
                    if index<len(line_elements):
                        ia = units_converter(line_elements[index])
                        index += 1
                        if index<len(line_elements):
                            freq = units_converter(line_elements[index])
                        else:
                            raise NetlistParseError("parse_elem_isource():No freq value is found when sin function has been defined")
                    else:
                        raise NetlistParseError("parse_elem_isource():No Ia value is found when sin function has been defined")
                else:
                    raise NetlistParseError("parse_elem_isource():No Io value is found when sin function has been defined")
                function = sin(i0,ia,freq)
        # if param_number and function is None:
        #     function = to_function(value,line_elements[index + 1:index + param_number+ 1],"voltage")
        #     index = index + param_number
                # continue
        # elif function is not None:
        #     raise NetlistParseError("parse_elem_vsource(): only a time function can be defined.")
        index = index + 1

    if dc_value == None and function == None:
        raise NetlistParseError("parse_elem_isource(): neither idc nor a time function are defined.")

    # usual
    ext_n1 = line_elements[1]
    ext_n2 = line_elements[2]
    n1 = circ.add_node(ext_n1)
    n2 = circ.add_node(ext_n2)

    elem = devices.ISource(part_id=line_elements[0], n1=n1, n2=n2,
                           dc_value=dc_value, ac_value=iac, ac_phase=acp)
    print elem.dc_value
    print elem.ac_value
    print elem.ac_phace
    if function is not None:
        elem.is_timedependent = True
        elem.function = function
    return [elem]
def parse_elements_vsource(line, circ):
    global inum
    line = line.replace('(',' ')
    line = line.replace(')',' ')
    line_elements = line.split()
    if len(line_elements) < 3:
        raise NetlistParseError("parse_elem_isource(): malformed line")

    dc_value = None
    vac = None
    acp = None
    function = None

    index = 3
    if line_elements[index][0].isdigit():
        dc_value = units_converter(line_elements[index])
        index += 1
    while True:  # for index in range(3, len(line_elements)):
        if index >= len(line_elements):
            break
        if line_elements[index][0] == '*':
            break
        if '=' in line_elements[index]:
            lable,value = parse_equations(line_elements[index])
            if lable == 'dc':
                dc_value = units_converter(value)
            elif lable == 'ac':
                vsc = units_converter(value)
            else:
                raise NetlistParseError("parse_elem_isource(): unknown signal" + "type %s" % lable)
            # elif lable == 'pulse':
            #     param_number = 7
            # elif lable == 'exp':
            #     param_number = 6
            # elif lable == 'sin':
            #     param_number = 5
            # elif lable == 'sffm':
            #     param_number = 5
            # elif lable == 'am':
            #     param_number = 5
        else:
            lable = line_elements[index]
            if lable == 'dc':
                index += 1
                if index<len(line_elements):
                    if units_converter(line_elements[index]):
                        dc_value = units_converter(line_elements[index])
                else:
                    raise NetlistParseError("parse_elem_Vsource():No DC value is found when it's been defined")
            elif lable == 'ac':
                index += 1
                if index<=len(line_elements):
                    if units_converter(line_elements[index]):
                        vac = units_converter(line_elements[index])
                else:
                    raise NetlistParseError("parse_elem_Vsource():No AC value is found when it's been defined")
                index += 1
                if index<len(line_elements):
                    if line_elements[index].isdigit():
                        acp = units_converter(line_elements[index])
                else:
                    index -=1
            elif lable =='sin':
                index += 1
                if index<len(line_elements):
                    v0 = units_converter(line_elements[index])
                    index += 1
                    if index<len(line_elements):
                        va = units_converter(line_elements[index])
                        index += 1
                        if index<len(line_elements):
                            freq = units_converter(line_elements[index])
                        else:
                            raise NetlistParseError("parse_elem_vsource():No freq value is found when sin function has been defined")
                    else:
                        raise NetlistParseError("parse_elem_vsource():No Va value is found when sin function has been defined")
                else:
                    raise NetlistParseError("parse_elem_vsource():No Vo value is found when sin function has been defined")
                function = sin(v0,va,freq)
        # if param_number and function is None:
        #     function = to_function(value,line_elements[index + 1:index + param_number+ 1],"voltage")
        #     index = index + param_number
                # continue
        # elif function is not None:
        #     raise NetlistParseError("parse_elem_vsource(): only a time function can be defined.")
        index = index + 1

    if dc_value == None and function == None:
        raise NetlistParseError("parse_elem_Vsource(): neither idc nor a time function are defined.")

    # usual
    ext_n1 = line_elements[1]
    ext_n2 = line_elements[2]
    n1 = circ.add_node(ext_n1)
    n2 = circ.add_node(ext_n2)
    inum += 1
    elem = devices.VSource(part_id=line_elements[0], n1=n1, n2=n2,
                           dc_value=dc_value, ac_value=vac, ac_phase=acp, inum=inum)
    print elem.dc_value
    print elem.ac_value
    print elem.ac_phace
    if function is not None:
        elem.is_timedependent = True
        elem.function = function
    # matrix_size += 1
    return [elem]
def parse_elements_capacitor(line,circ):
    global inum
    line_elements = line.split()
    ic = 0
    if len(line_elements) < 4:
        raise NetlistParseError("parse_elem_capacitor(): malformed line")
    elif len(line_elements) == 5:
        (label, value) = parse_equations(line_elements[4])
        if label == "ic":
            ic = units_converter(value)
        else:
            raise NetlistParseError("parse_elem_capacitor(): unknown parameter " + label)

    ext_n1 = line_elements[1]
    ext_n2 = line_elements[2]
    n1 = circ.add_node(ext_n1)
    n2 = circ.add_node(ext_n2)
    inum += 1
    elem = devices.Capacitor(part_id=line_elements[0], n1=n1, n2=n2, value=units_converter(line_elements[3]), ic=ic,inum=inum, islinear=0)
    print elem.ic
    return [elem]
def  parse_elements_inductor(line, circ):
    global inum
    line_elements = line.split()
    ic = None
    if len(line_elements) < 4 or \
       (len(line_elements) > 5 and not line_elements[5][0] == "*" and
        not line_elements[4][0] == "*"):
        raise NetlistParseError("parse_elements_inductor(): malformed line")
    elif len(line_elements) == 5:
        (label, value) = parse_equations(line_elements[4])
        if label == "ic":
            ic = units_converter(value)
        else:
            raise NetlistParseError("parse_elements_inductor(): unknown parameter " + label)

    ext_n1 = line_elements[1]
    ext_n2 = line_elements[2]
    n1 = circ.add_node(ext_n1)
    n2 = circ.add_node(ext_n2)
    inum += 1
    elem = devices.Inductor(part_id=line_elements[0], n1=n1, n2=n2, value=units_converter(line_elements[3]), ic=ic, inum=inum, islinear=0)
    
    print elem.ic
    return [elem]
def  parse_elements_resistor(line, circ):
    line_elements = line.split()
    if len(line_elements) < 4:
        raise NetlistParseError("parse_elements_resistor(): malformed line")
    ext_n1 = line_elements[1]
    ext_n2 = line_elements[2]
    n1 = circ.add_node(ext_n1)
    n2 = circ.add_node(ext_n2)
    if len(line_elements) == 4:
        elem = devices.Resistor(part_id=line_elements[0], n1=n1, n2=n2, value=units_converter(line_elements[3]))
        print elem.value

    return [elem]

def parse_command_dc(line):
    pass
def parse_command_ac(line):
    pass
def parse_command_tran(line):
    pass
def parse_command_plot(line,circ):
    global vlist
    global ilist
    global simu_type
    line_elements = line.split()
    simu_type = 0
    # if not(globals().has_key('vlist') or globals().has_key('ilist')):
    #     vlist = tran.Vlist_tran()
    #     ilist = tran.Ilist_tran()
    vlist = tran.Vlist_tran()
    ilist = tran.Ilist_tran()
    if line_elements[1] == "tran":
        simu_type = 1

        for i in range(2,len(line_elements)):
            str = line_elements[i].replace('(',' ')
            str = str.replace(')',' ')
            str = str.replace(',',' ')
            para = str.split()
            if para[0].find('v')==0:
                if len(para)==3:
                    vlist.lst_append(para[0],circ.add_node(para[1]),circ.add_node(para[2]))
                elif len(para)==2:
                    vlist.lst_append(para[0],circ.add_node(para[1]))
                else:
                    raise NetlistParseError(" parse_command_plot():syntax error")

            elif para[0].find('i')==0:
                if len(para)==2:
                    ilist.lst_append(para[0],para[1])
                else:
                    raise NetlistParseError(" parse_command_plot():syntax error")

        # print vlist.node2
        # print ilist.vid_list
# def parse_elements_c(line):
# def parse_ctr():
def parse_elements_diode(line,circ):
    line_elements = line.split()
    if len(line_elements) < 4:
        raise NetlistParseError("")

    model_label = line_elements[3]

    # for index in range(4, len(line_elements)):
    #     if line_elements[index][0] == '*':
    #         break
    #     param, value = parse_param_value_from_string(line_elements[index])
    #
    #     value = units_converter(value)
    #     if param == "area":
    #         Area = value
    #     elif param == "t":
    #         T = value
    #     elif param == "ic":
    #         ic = value
    #     elif param == "off":
    #         if not len(value):
    #             off = True
    #         else:
    #             off = convert_boolean(value)
    #     else:
    #         raise NetlistParseError("parse_elem_diode(): unknown parameter " + param)

    ext_n1 = line_elements[1]
    ext_n2 = line_elements[2]
    n1 = circ.add_node(ext_n1)
    n2 = circ.add_node(ext_n2)

    # if model_label not in models:
    #     raise NetlistParseError("parse_elem_diode(): Unknown model id: " + model_label)
    elem = devices.diode(part_id=line_elements[0], n1=n1, n2=n2, model_label=model_label, islinear=0)
    return [elem]


