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
# import dc
# import ac
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
    global time
    global interval

    try:
        simumode = int(CheckVar_simumode.get())
        if time.get() == "" or interval.get() == "":
            t = netlist_parser.T_STOP
            h = netlist_parser.T_STEP
        else:
            t = netlist_parser.units_converter(time.get())
            h = netlist_parser.units_converter(interval.get())
        if CheckVar_tran.get():
            tran.tran(t, h, simumode)
        if CheckVar_ac.get():
            pass
        if CheckVar_dc.get():
            pass
        # tran.build_stamps()
    except SimulatorError,e:
        print e.arg


def open_file():
    global netlist
    global open_status
    global filename
    filename = tkFileDialog.askopenfilename(initialdir = 'C:/Python27')
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
            text = netlist.get(0.0,END)
            file_object.write(text)
        finally:
            file_object.close()


def saveas_file():
    global filename
    global open_status
    filename = tkFileDialog.asksaveasfilename()
    try:
        file_object = open(filename, 'w')
        text = netlist.get(0.0,END)
        file_object.write(text)
        open_status = 1
    finally:
        file_object.close()


def win_simu_init():
    global CheckVar_tran
    global CheckVar_dc
    global CheckVar_ac
    global CheckVar_simumode
    global time
    global interval
    win_simu = Toplevel(root)
    win_simu.title("simulation")
    # win_simu.geometry("200x200")
    CheckVar_tran = IntVar()
    CheckVar_dc = IntVar()
    CheckVar_ac = IntVar()
    CheckVar_simumode = IntVar()
    time = StringVar()
    interval = StringVar()
    Checkbutton(win_simu, text="tran", variable=CheckVar_tran).grid(sticky=W)
    Checkbutton(win_simu, text="dc",variable=CheckVar_ac).grid(sticky=W)
    Checkbutton(win_simu, text="ac",variable=CheckVar_dc).grid(sticky=W)

    Label(win_simu,text="time(s):").grid(row=3,column=0)
    Entry(win_simu,textvariable=time).grid(row=3,column=1)
    Label(win_simu,text="interval(s):").grid(row=4,column=0)
    Entry(win_simu,textvariable=interval).grid(row=4,column=1)
    Button(win_simu,text="OK",command=simulation_init).grid(row=5,column=0,sticky=W)
    Label(win_simu, text="Simulation type").grid()
    Radiobutton(win_simu, text="fe", variable=CheckVar_simumode,value=1).grid(sticky=W)
    Radiobutton(win_simu, text="be",variable=CheckVar_simumode,value=2).grid(sticky=W)
    Radiobutton(win_simu, text="tr",variable=CheckVar_simumode, value=3).grid(sticky=W)
    win_simu.mainloop()


def win_root_init():
    global root
    global netlist
    root = Tk()
    m = Menu(root)
    root.config(menu = m)
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
    Button(root, text='submit', command = submit).pack(side = "left")
    Button(root, text='reset', command = reset).pack(side = "left")
    root.mainloop()



