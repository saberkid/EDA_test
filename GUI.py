# import win32com
# from win32com.client import Dispatch, constants
# w = win32com.client.Dispatch('Word.Application')
# w.Visible = 1
# w.DisplayAlerts = 0
# doc = w.Documents.Add()
# myRange = doc.Range(0,0)
# myRange.InsertBefore('Hello from Python!')
# doc.Save()
# doc.Close()
# w.Quit()
from Tkinter import *
import netlist_parser
import tran
import dc
import ac
import sys
import tkFileDialog


reload(sys)
sys.setdefaultencoding('utf-8')


class SimulatorError(Exception):
    def __init__(self, arg):
        self.arg = arg


def submit():
    text = str(netlist.get(0.0, END))
    netlist_parser.parse_lines(text)


def reset():
    netlist.delete(0.0, END)


def simulation_init():
    try:
        if CheckVar_simutype.get() == 1:
            if CheckVar_simumode.get():
                simumode = int(CheckVar_simumode.get())
            else:
                simumode = 3
            t = netlist_parser.T_STOP
            h = netlist_parser.T_STEP
            if time.get() != "" and interval.get() != "":
                t = netlist_parser.units_converter(time.get())
                h = netlist_parser.units_converter(interval.get())
            tran.tran(t, h, simumode)
        elif CheckVar_simutype.get() == 2:
            vsrc = netlist_parser.DC_SRC
            v0 = netlist_parser.DC_V0
            vt = netlist_parser.DC_VT
            vstep = netlist_parser.DC_VSTEP
            dc.dc(vsrc, v0, vt, vstep)

        elif CheckVar_simutype.get() == 3:
            n = netlist_parser.N
            fstart = netlist_parser.FSTART
            fstop = netlist_parser.FSTOP
            ac.ac(n, fstart, fstop)
        # tran.build_stamps()
    except SimulatorError, e:
        print e.arg


def open_file():
    global netlist
    global open_status
    global filename
    filename = tkFileDialog.askopenfilename(initialdir='C:/Python27')
    if filename != "":
        file_object = open(filename)
        try:

            all_the_text = file_object.read()
        finally:
            file_object.close()
        reset()
        netlist.insert(INSERT, all_the_text)
        open_status = 1


def save_file():
    global open_status
    global filename
    if open_status:
        try:
            file_object = open(filename, 'w')
            text = netlist.get(0.0, END)
            file_object.write(text)
        finally:
            file_object.close()

    else:
        filename = tkFileDialog.asksaveasfilename()
        try:
            file_object = open(filename, 'w')
            text = netlist.get(0.0, END)
            file_object.write(text)
        finally:
            file_object.close()


def saveas_file():
    global filename
    global open_status
    filename = tkFileDialog.asksaveasfilename()
    try:
        file_object = open(filename, 'w')
        text = netlist.get(0.0, END)
        file_object.write(text)
        open_status = 1
    finally:
        file_object.close()


def win_simu_init():
    global CheckVar_simutype
    global CheckVar_simumode
    global time, interval
    global v0, vt, vstep
    global fstart, fstop, n
    global type
    global time_entry, time_label, h_label, h_entry
    global fstart_label, fstop_label, fstart_entry, fstop_entry, n_label, n_entry
    global v0_label, v0_entry, vt_label, vt_entry, vstep_label, vstep_entry


    win_simu = Toplevel(root)
    win_simu.title("simulation")
    win_simu.geometry("300x300")
    CheckVar_simumode = IntVar()
    CheckVar_simutype = IntVar()
    time = StringVar()
    interval = StringVar()
    v0 = StringVar()
    vt = StringVar()
    vstep = StringVar()
    fstart = StringVar()
    fstop = StringVar()
    n = StringVar()

    type = 0
    Radiobutton(win_simu, text="tran", variable=CheckVar_simutype, value=1, command=show_tran).grid(sticky=W)
    Radiobutton(win_simu, text="dc", variable=CheckVar_simutype, value=2, command=show_dc).grid(sticky=W)
    Radiobutton(win_simu, text="ac", variable=CheckVar_simutype, value=3, command=show_ac).grid(sticky=W)
#tran
    time_label = Label(win_simu, text="time(s):")
    time_entry = Entry(win_simu, textvariable=time)
    h_label = Label(win_simu, text="interval(s):")
    h_entry = Entry(win_simu, textvariable=interval)
#dc
    v0_label = Label(win_simu, text="V0(v):")
    v0_entry = Entry(win_simu, textvariable=v0)
    vt_label = Label(win_simu, text="Vt(v):")
    vt_entry = Entry(win_simu, textvariable=vt)
    vstep_label = Label(win_simu, text="Vstep(v):")
    vstep_entry = Entry(win_simu, textvariable=vstep)
#ac
    fstart_label = Label(win_simu, text="f start(HZ):")
    fstop_label = Label(win_simu, text="f stop(HZ):")
    n_label = Label(win_simu, text="    n:")
    fstart_entry = Entry(win_simu, textvariable=fstart)
    fstop_entry = Entry(win_simu, textvariable=fstop)
    n_entry = Entry(win_simu, textvariable=n)

    Label(win_simu, text="Simulation type").grid(row=6, column=0)
    Radiobutton(win_simu, text="fe", variable=CheckVar_simumode, value=1).grid(sticky=W)
    Radiobutton(win_simu, text="be", variable=CheckVar_simumode, value=2).grid(sticky=W)
    Radiobutton(win_simu, text="tr", variable=CheckVar_simumode, value=3).grid(sticky=W)
    Button(win_simu, text="OK", command=simulation_init).grid(sticky=W)

    win_simu.mainloop()


def win_root_init():
    global root
    global netlist
    root = Tk()
    m = Menu(root)
    root.config(menu=m)
    filemenu = Menu(m)
    simulate = Menu(m)
    m.add_cascade(label="File", menu=filemenu)
    m.add_cascade(label="Simulate", menu=simulate)
    filemenu.add_command(label="open", command=open_file)
    filemenu.add_command(label="save", command=save_file)
    filemenu.add_command(label="save as", command=saveas_file)

    simulate.add_command(label="parse and run", command=win_simu_init)

    netlist = Text(root)
    netlist.pack()
    Button(root, text='submit', command=submit).pack(side = "left")
    Button(root, text='reset', command=reset).pack(side = "left")
    root.mainloop()


def show_ac():
    global type
    if type == 1:
        time_label.grid_forget()
        time_entry.grid_forget()
        h_label.grid_forget()
        h_entry.grid_forget()

    elif type == 2:
        v0_label.grid_forget()
        v0_entry.grid_forget()
        vt_label.grid_forget()
        vt_entry.grid_forget()

    fstart_label.grid(row=3, column=0)
    fstart_entry.grid(row=3, column=1)
    fstop_label.grid(row=4, column=0)
    fstop_entry.grid(row=4, column=1)
    n_label.grid(row=5, column=0)
    n_entry.grid(row=5, column=1)
    type = 3


def show_dc():
    global type
    # global time_label
    # global time_entry
    # global h_entry
    # global h_label
    # global v0_label
    # global v0_entry
    # global vt_label
    # global vt_entry
    if type == 1:
        time_label.grid_forget()
        time_entry.grid_forget()
        h_label.grid_forget()
        h_entry.grid_forget()
    elif type == 3:
        fstart_label.grid_forget()
        fstart_entry.grid_forget()
        fstop_label.grid_forget()
        fstop_entry.grid_forget()
        n_label.grid_forget()
        n_entry.grid_forget()

    v0_label.grid(row=3, column=0)
    v0_entry.grid(row=3, column=1)
    vt_label.grid(row=4, column=0)
    vt_entry.grid(row=4, column=1)
    vstep_label.grid(row=5, column=0)
    vstep_entry.grid(row=5, column=1)
    type = 2


def show_tran():
    global type
    if type == 3:
        fstart_label.grid_forget()
        fstart_entry.grid_forget()
        fstop_label.grid_forget()
        fstop_entry.grid_forget()
        n_label.grid_forget()
        n_entry.grid_forget()
    elif type == 2:
        v0_label.grid_forget()
        v0_entry.grid_forget()
        vt_label.grid_forget()
        vt_entry.grid_forget()

    time_label.grid(row=3, column=0)
    time_entry.grid(row=3, column=1)
    h_label.grid(row=4, column=0)
    h_entry.grid(row=4, column=1)
    type = 1




