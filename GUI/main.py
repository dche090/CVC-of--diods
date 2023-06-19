from tkinter import *
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

counter1 = 0
ser = serial.Serial()
serFlag = 0
data2 = []


Root = Tk()
Root.title("Serial Console")
Root.iconbitmap('icon.ico')
Root.geometry('1000x800')
Root.resizable(width=False, height=False)

sty = ttk.Style()
sty.theme_use("alt")

fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=Root)
canvas.get_tk_widget().place(x=10, y=250)
plt.xlabel('Voltage (U)')
plt.grid()


toolbar = NavigationToolbar2Tk(canvas, Root, pack_toolbar=False)
toolbar.update()
toolbar.place(x=10, y=740)


Frame = ttk.LabelFrame(Root, text="Connection Setting", padding=10)
Frame.place(x=20, y=20)
Frame21 = ttk.Frame(Root, padding=10)
Frame21.place(x=325, y=20)


label1 = ttk.Label(Frame, text="Serial Console")
label1.grid(column=2, row=0)

Frame.rowconfigure(0, weight=2)


ports = serial.tools.list_ports.comports()
com_port_list = [com[0] for com in ports]
com_port_list.insert(0, "Select an Option")


com_value_inside = StringVar()
baud_value_inside = StringVar()
baud_menu = ttk.OptionMenu(Frame, baud_value_inside, "select baud rate", "9600",
                           '19200', '28800', '38400', '57600', '76800',
                           '115200', '128000', '153600', '230400', '256000', '460800', '921600')
baud_menu.grid(column=3, row=1, sticky=E)


def com_port_list_update():
    global ports
    global com_port_list

    ports = serial.tools.list_ports.comports()
    com_port_list = [com[0] for com in ports]
    com_port_list.insert(0, "Select an Option")

    com_menu = ttk.OptionMenu(Frame, com_value_inside, *com_port_list)
    com_menu.grid(column=2, row=1, sticky=E)

    Root_com_list = Toplevel(Root)
    x = Root.winfo_x()
    y = Root.winfo_y()
    Root_com_list.geometry("+%d+%d" % (x + 200, y + 200))
    Frame01 = ttk.Frame(Root_com_list, padding=10)
    Frame01.grid(column=0, row=1, sticky=W)

    scrollbar = ttk.Scrollbar(Frame01, orient='horizontal')
    scrollbar.grid(column=1, row=2, sticky=W + E)

    Lb1 = Listbox(Frame01, xscrollcommand=1, width=50, font=('Helvetica 8 bold'))
    counter = 0
    for x in ports:
        Lb1.insert(counter, str(x))

    counter += 1
    Lb1.grid(column=1, row=1, sticky=W + E)
    Lb1.config(xscrollcommand=scrollbar.set)

    scrollbar.config(command=Lb1.xview)


def serial_print():
    global serFlag
    global ser
    global counter1
    global data2

    if (serFlag):
        if (ser.in_waiting > 0):
            try:
                x = ser.readline()
                y = str(counter1) + ": " + " -> " + str(x.decode())
                data2.append(x.decode().strip().split())
                Lb2.insert(counter1, str(y))
                Lb2.see("end")
                counter1 += 1
            except:
                pass
        ser.flush()
        Frame.after(100, serial_print)


def serial_connect(com_port, baud_rate):
    global ser
    ser.baudrate = baud_rate
    ser.port = com_port
    ser.timeout = 1
    ser._xonxoff = 1
    ser.bytesize = serial.EIGHTBITS
    ser.parity = serial.PARITY_NONE
    ser.stopbits = serial.STOPBITS_ONE
    ser.open()
    global serFlag
    serFlag = 1

    t1 = threading.Thread(target=serial_print, args=(), daemon=1)
    t1.start()


def serial_close():
    global ser
    global serFlag
    serFlag = 0
    ser.close()
    data2.clear()


def submit_value():
    serial_connect(com_value_inside.get(), baud_value_inside.get())


def clear_listbox():
    Lb2.delete(0, END)
    data2.clear()
    canvas.close_event()


def avg(x, y):
    min_y = min(y)
    max_y = max(y)
    x_return = []
    y_return = []

    for y_now in np.arange(min_y, max_y, 0.01):
        indexes = np.where(y == y_now)[0]
        temp = np.empty(0)

        for i in indexes:
            temp = np.append(temp, x[i])

        if y_now == 0:
            x_return.append(np.min(temp))
            x_return.append(np.average(temp))

            y_return.append(y_now)
            y_return.append(y_now)
        else:
            x_return.append(np.average(temp))
            y_return.append(y_now)

    return x_return, y_return


def build_cvc():
    ax.clear()

    x = np.empty(0)
    y = []

    for i in range(len(data2)):
        x = np.append(x, float(data2[i][0].split(",")[0]))
        y = np.append(y, float(data2[i][0].split(",")[1]))

    x, y = avg(x, y)

    f = interpolate.interp1d(x, y, kind='quadratic')
    new_x = np.arange(min(x), max(x))
    y = f(new_x)

    plt.xlabel('Voltage (U)')
    plt.grid()

    plt.plot(new_x * 5 / 1024, y * 5 / 1024)
    canvas.draw()


Lb2 = Listbox(Frame21, width=100, xscrollcommand=1)
Lb2.grid(column=1, row=1, sticky=W + E)
Sb2 = ttk.Scrollbar(Frame21, orient='vertical')
Sb2.config(command=Lb2.yview)
Sb2.grid(column=2, row=1, sticky=N + S)
Sb2v = ttk.Scrollbar(Frame21, orient='horizontal')
Sb2v.grid(column=1, row=2, sticky=W + E)
Sb2v.config(command=Lb2.xview)
Lb2.configure(xscrollcommand=Sb2v.set, yscrollcommand=Sb2.set)


subBtn = ttk.Button(Frame, text="submit", command=submit_value)
subBtn.grid(column=4, row=1, sticky=E)

RefreshBtn = ttk.Button(Frame, text="Get List", command=com_port_list_update)
RefreshBtn.grid(column=2, row=2, sticky=E)

closeBtn = ttk.Button(Frame, text="Disconnect", command=serial_close)
closeBtn.grid(column=4, row=2, sticky=E)

clearBtn = ttk.Button(Frame, text="Clear Messages", command=clear_listbox)
clearBtn.grid(column=3, row=2, sticky=E)

cvcBtn = ttk.Button(Frame, text='Build CVC', command=build_cvc)
cvcBtn.grid(column=3, row=3, sticky=E)


Root.mainloop()