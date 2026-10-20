from tkinter import *
from tkinter import ttk
import tkinter as tk
import serial
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#style = ttk.Style()
#style.configure("Accent.TButton", background="turquoise", foreground="white")

plt.ion()

plt.axis([0,100,0,100])
eje_x=[]
i=0

device = 'COM6'
mySerial = serial.Serial(device, 9600)
Temperaturas=[]

running=True

def cerrar():
    global running
    running = False      # detener hilos
    time.sleep(0.2)      # dar tiempo a que terminen
    window.destroy()     # cerrar interfaz

def reception():
    global running
    while running:
        if mySerial.in_waiting > 0:
            received = str(mySerial.readline().decode('utf-8').rstrip())
            trozos = received.split(':') #trozos[3]=humedad trozos[1]=temperatura
            if len(trozos) < 4:
                print("Línea inválida recibida:", received)
                continue
            temp = trozos[1].strip()
            hum = trozos[3].strip()
            Temperaturas.append(float(temp))
            print('Temperatura: ' + temp + ' Humedad: ' + hum)
            Temperaturas.append(float(temp))


threadReception = threading.Thread (target = reception)
#threads = [threadReception]


def EntrarClick ():
    orden=fraseEntry.get()
    mySerial.write((orden + '\n').encode('utf-8')) # Enviar frase al Arduino
    print(fraseEntry.get()) # comprobacion

def AClick (): # Iniciar recepcion de datos
    print ('Has pulsado el botón de inicio.')
    threadReception.start() 

def BClick(): # Mostrar gráfica de temperatura
    print('Mostrando gráfica de temperatura')
    Grafica_temp()

window = Tk()
window.protocol("WM_DELETE_WINDOW", cerrar)


frame_grafica = Frame(window, bg="white")
frame_grafica.grid(row=1, column=1, columnspan=4, rowspan=3, sticky=N + S + E + W)

fig = Figure(figsize=(4,3), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
canvas.draw()
canvas.get_tk_widget().pack(expand=False)

def Grafica_temp():
    global i
    if len(Temperaturas) > i:
        eje_x.append(i)

        ax.clear()  # limpiar la gráfica
        ax.set_title("Grafica de Temperatura")
        ax.set_ylabel("Temperatura (°C)")
        ax.plot(eje_x, Temperaturas[:len(eje_x)], marker=".", color="red")

        canvas.draw()  # actualizar la gráfica incrustada

        if i == 100:
            i = 0
            eje_x.clear()
            Temperaturas.clear()
        else:
            i += 1

    window.after(500, Grafica_temp)

window.geometry("1280x720")
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)
window.rowconfigure(3, weight=1)
window.rowconfigure(4, weight=1)
window.rowconfigure(5, weight=1)
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)
window.columnconfigure(3, weight=1)
window.columnconfigure(4, weight=1)
window.columnconfigure(5, weight=1)

tituloLabel = Label(window, text = "Space Temperature and Humidity satellite Mik-26", font=("Courier", 20, "italic"))
tituloLabel.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky=N + S + E + W)

fraseEntry = Entry(window)
fraseEntry.grid(row=5, column=3, columnspan = 2, padx=5, pady=5, sticky=N + S + E + W)

EntrarButton = Button(window, text="Entrar", bg='turquoise', fg="black",command=EntrarClick)
EntrarButton.grid(row=5, column=5, padx=5, pady=5, sticky=N + S + E + W)

AButton = Button(window, text="Iniciar recepcion", bg='turquoise', fg="black",command=AClick) # Iniciar recepción de datos
AButton.grid(row=5, column=0, padx=5, pady=5, sticky=N + S + E + W)
BButton = Button(window, text="Mostrar Temperatura", bg='turquoise', fg="black",command=BClick) # Mostrar gráfica de temperatura
BButton.grid(row=4, column=0, padx=5, pady=5, sticky=N + S + E + W)
CButton = Button(window, text="C", bg='turquoise', fg="black")
CButton.grid(row=3, column=0, padx=5, pady=5, sticky=N + S + E + W)
DButton = Button(window, text="D", bg='turquoise', fg="black")
DButton.grid(row=2, column=0, padx=5, pady=5, sticky=N + S + E + W)
EButton = Button(window, text="E", bg='turquoise', fg="black")
EButton.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)        
FButton = Button(window, text="F", bg='turquoise', fg="black")
FButton.grid(row=5, column=1, padx=5, pady=5, sticky=N + S + E + W)
GButton = Button(window, text="G", bg='turquoise', fg="black")
GButton.grid(row=5, column=2, padx=5, pady=5, sticky=N + S + E + W)


window.mainloop()





