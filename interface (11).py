from tkinter import *
from tkinter import ttk
import tkinter as tk
import serial
import threading
import time
import math
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

plt.ion()

window = Tk()

txt_consola = Text(window, height=8, bg="black", fg="white")
txt_consola.grid(row=7, column=0, columnspan=7, sticky=N+S+E+W)

def consola(mensaje): # Mostrar consola dentro de la interfaz
    window.after(
        0,
        lambda: (   # para que no de errores cuando el thread recepcion llame la funcion
            txt_consola.insert(END, mensaje + "\n"),
            txt_consola.see(END) # para que se desplace al final
        )
    )


# Variables globales para las graficas
plt.axis([0,100,0,100])
eje_x=[]
eje_xD1=[]
eje_xD2=[]
eje_yD1=[]
eje_yD2=[]
i=0 


# NetID y Frecuencia LoRa: 5 ; 441


periodoHT=1000
periodoDist=40
device = 'COM5' 
mySerial = None
Temperaturas=[]
grafica_temperatura_activa = False

# Variables para el control del servo y la distancia
angulos=[]
currentangulo=0
Distancias1=[]
Distancias2=[]
ultimo_borrado = time.time()
radar_activo = False

#Variables para calcular la media de la temperatura
Medias_Temp = []
eje_x_media = []
i_media = 0
modo_calculo = "TIERRA"
limite_alarma = 30.0
contador_alarma = 0
alarma_activa = False
media_actual = None

running=True

def cerrar():
    global running
    running = False      # detener hilos
    time.sleep(0.2)      # dar tiempo a que terminen
    window.destroy()     # cerrar interfaz
    if mySerial is not None: #· Comprobar si el puerto serie está abierto
        mySerial.close() # cerrar puerto serie

window.protocol("WM_DELETE_WINDOW", cerrar)

def AbrirPuerto():  # Comprueba que el puerto serie esta abierto
    global mySerial
    try:
        mySerial = serial.Serial(device, 9600, timeout=1)
        print("Puerto serie abierto correctamente.")
        consola("Puerto serie abierto correctamente.")
    except serial.SerialException as e:
        mySerial = None
        print(f"No se pudo abrir el puerto serie: {e}")
        consola(f"No se pudo abrir el puerto serie: {e}")

AbrirPuerto()

def reception():
    global running, contador_alarma, alarma_activa, media_actual

    while running:
        if mySerial is None:
            time.sleep(0.1)
            continue

        if mySerial.in_waiting > 0: # Si recibe informacion
            received = str(mySerial.readline().decode('utf-8').rstrip())
            trozos = received.split(':')

            if len(trozos) < 11: # 1:T:temp:H:hum:D1:dist1:D2:dist2:M:media
                if (trozos[0].strip()=="error"):
                    if (trozos[1].strip()=="1"):
                        print("Error de lectura de temperatura/humedad")
                        consola("Error de lectura de temperatura/humedad")
                        alarma_activa = True
                    elif (trozos[1].strip()=="2"):
                        print("Error de lectura del satelite")
                        consola("Error de lectura del satelite")
                        alarma_activa=True
                    elif (trozos[1].strip()=="3"):
                        print("Error de lectura de distancia")
                        consola("Error de lectura de distancia")
                        alarma_activa=True
                    elif (trozos[1].strip()=="31"):
                        print("Error con el sensor de distancia 1")
                        consola("Error con el sensor de distancia 1")
                        alarma_activa=True
                    elif (trozos[1].strip()=="32"):
                        print("Error con el sensor de distancia 2")
                        consola("Error con el sensor de distancia 2")
                        alarma_activa=True
                    elif (trozos[1].strip()=="4"): # No es realmente un error pero no queria añadir otro tipo de mensaje que fuera alarma:123
                        contador_alarma = contador_alarma+1 
                        if contador_alarma >= 3:
                            alarma_activa = True
                            consola("Alerta, temperatura limite superada 3 veces!")
                    elif (trozos[1].strip()=="5"):
                        print("Error de comunicacion con el satelite")
                        consola("Error de comunicacion con el satelite")
                        alarma_activa=True
                    else:
                        print("Error no identificado")
                        consola("Error no identificado")
                else:
                    print(f"Línea inválida recibida: {received}")
                    print(trozos)
                    consola(f"Línea inválida recibida: {received}")
                continue

            if(trozos[1].strip() != "T" or trozos[3].strip() != "H" or trozos[5].strip() != "D1" or trozos[7].strip() != "D2" or trozos[9].strip() != "M"):
                print(f"Formato de línea inválido: {received}")
                consola(f"Formato de línea inválido: {received}")
                continue

            else:
                temp = trozos[2].strip()
                hum = trozos[4].strip()
                dist1 = trozos[6].strip()
                dist2=trozos[8].strip()
                

            try:
                Temperaturas.append(float(temp))
                Distancias1.append(float(dist1))
                Distancias2.append(float(dist2))
                if (modo_calculo=="TIERRA"): # Calculo de la media en Tierra
                    ultimas=Temperaturas[-10:]
                    if (len(ultimas)>0):
                        media_actual=sum(ultimas)/len(ultimas)
                        Medias_Temp.append(media_actual)

                elif (modo_calculo=="SATELITE"):
                    media_actual=float(trozos[10].strip())
                    Medias_Temp.append(media_actual)
                if media_actual is not None:
                    if (media_actual>limite_alarma):
                        contador_alarma = contador_alarma+1
                        if contador_alarma >= 3:
                            alarma_activa = True
                    else: 
                        contador_alarma=0
                        alarma_activa=False
                else:
                    contador_alarma=0
                    alarma_activa=False

            except ValueError:
                print(f"Dato inválido: {received}")
                consola(f"Dato inválido: {received}")
                continue

            print('Temperatura: ' + temp + ' Humedad: ' + hum + ' Distancia1: ' + dist1 + ' Distancia2: ' + dist2 + ' Media:' + str(media_actual))
            consola('Temperatura: ' + temp + ' Humedad: ' + hum + ' Distancia1: ' + dist1 + ' Distancia2: ' + dist2 + ' Media:' + str(media_actual))


def EntrarClick(): # Enviar texto al puerto serie
    orden = fraseEntry.get()

    if mySerial is not None: # Comprobar si el puerto serie está abierto
        mySerial.write((str(orden) + '\n').encode('utf-8'))
        print(orden)
        consola(orden)
    else:
        print("No hay ningún puerto serie conectado.")
        consola("No hay ningún puerto serie conectado.")

threadReception = None

def AClick():
    global threadReception

    print('Has pulsado el botón de inicio.')
    consola('Has pulsado el botón de inicio.')

    if mySerial is None:
        print("No hay puerto serie disponible.")
        consola("No hay puerto serie disponible.")
        return

    if threadReception is None or not threadReception.is_alive():
        threadReception = threading.Thread(
            target=reception,
            daemon=True
        )
        threadReception.start()

def BClick(): # Mostrar gráfica de temperatura
    global grafica_temperatura_activa
    if not grafica_temperatura_activa:
        grafica_temperatura_activa = True
        print('Mostrando gráfica de temperatura')
        consola('Mostrando gráfica de temperatura')
        Grafica_temp()
    else:
        print('La gráfica de temperatura ya está activa.')
        consola('La gráfica de temperatura ya está activa.')
        return

# Protocolo de envio:
# 1:0 o 1:1 -> Parar o Reanudar temperatura y humedad
# 2:currentangulo -> Enviar angulo al servo
# 3:0 o 3:1 -> Parar o Reanudar distancia
# 4:periodoHT -> Cambiar periodo de envio temperatura y humedad
# 5:periodoDist-> Cambiar periodo de envio de distancia
# 6:0 o 6:1 -> Modo Tierra o modo Satelite de la media de la temperatura
# 7:limite_alarma -> Fijar limite de la alarma

def CClick(): # Parar recepción de datos
    if mySerial is not None: # Comprobar si el puerto serie está abierto
            mySerial.write(("1:0\n").encode('utf-8'))
            print("Orden enviada: Parar")
            consola("Orden enviada: Parar")
    else:
        print("No hay ningún puerto serie conectado.")
        consola("No hay ningún puerto serie conectado.")

def DClick(): # Reanudar recepción de datos
    if mySerial is not None: # Comprobar si el puerto serie está abierto
            mySerial.write(("1:1\n").encode('utf-8'))
            print("Orden enviada: Reanudar")
            consola("Orden enviada: Reanudar")
    else:
        print("No hay ningún puerto serie conectado.")
        consola("No hay ningún puerto serie conectado.")

def EClick(): # Mostrar grafica de distancia
    global radar_activo
    if not radar_activo:
        radar_activo = True
        print('Mostrando gráfica de distancia')
        consola('Mostrando gráfica de distancia')
        Grafica_dist()
    else:
        print('La gráfica de distancia ya está activa.')
        consola('La gráfica de distancia ya está activa.')
        return

# FClick y GClick: Codigo de comando de envio de angulos al arduino: 

def FClick(): # Sumar 15 grados al angulo  
    global currentangulo
    if mySerial is not None:
        if currentangulo < 180:
            currentangulo += 15
        else:
            currentangulo = 0
        angulos.append(int(currentangulo))
        mySerial.write(("2:" + str(currentangulo) + "\n").encode('utf-8'))
    else:
        print("No hay ningún puerto serie conectado.")
        consola("No hay ningún puerto serie conectado.")

def GClick(): # Restar 15 grados al angulo
    global currentangulo
    if mySerial is not None:
        if currentangulo > 0:
            currentangulo -= 15
        else:
            currentangulo = 180
        angulos.append(int(currentangulo))
        mySerial.write(("2:" + str(currentangulo) + "\n").encode('utf-8'))
    else:
        print("No hay ningún puerto serie conectado.")
        consola("No hay ningún puerto serie conectado.")

def HClick(): # Modificar intervalo de Temperatura y de Humedad
    global periodoHT
    periodoHT=fraseEntry.get()

    if mySerial is not None: # Comprobar si el puerto serie está abierto
        mySerial.write(("4:"+str(periodoHT) + '\n').encode('utf-8'))
        print(periodoHT)
        consola(periodoHT)
    else:
        print("No hay ningún puerto serie conectado.")
        consola("No hay ningún puerto serie conectado.")

def IClick(): # Cambiar intervalo de envio de la distancia
    global periodoDist
    periodoDist=fraseEntry.get()
    
    if mySerial is not None: # Comprobar si el puerto serie está abierto
        mySerial.write(("5:"+str(periodoDist) + '\n').encode('utf-8'))
        print(periodoDist)
        consola(periodoDist)
    else:
        print("No hay ningún puerto serie conectado.")
        consola("No hay ningún puerto serie conectado.")

def JClick(): # Cambiar a modo Tierra
    global modo_calculo
    modo_calculo="TIERRA"
    if mySerial is not None: # Comprobar si el puerto serie está abierto
        mySerial.write(("6:0" + '\n').encode('utf-8'))
        print(modo_calculo)
        consola("Modo: "+ modo_calculo)
    else:
            print("No hay ningún puerto serie conectado.")
            consola("No hay ningún puerto serie conectado.")

def KClick(): # Cambiar a modo Satelite
    global modo_calculo
    modo_calculo="SATELITE"
    if mySerial is not None: # Comprobar si el puerto serie está abierto
        mySerial.write(("6:1" + '\n').encode('utf-8'))
        print(modo_calculo)
        consola("Modo: "+ modo_calculo)
    else:
            print("No hay ningún puerto serie conectado.")
            consola("No hay ningún puerto serie conectado.")

def fijar_limite():    
    global limite_alarma
    global contador_alarma
    global alarma_activa

    try:
        nuevo_limite = float(fraseEntry.get())

        limite_alarma = nuevo_limite
        contador_alarma = 0
        alarma_activa = False

        print(f"Nuevo límite de alarma establecido en: {limite_alarma} °C")
        consola(f"Nuevo límite de alarma establecido en: {limite_alarma} °C")

        # Enviar al Arduino cuando esté en modo satélite
        if mySerial is not None and modo_calculo == "SATELITE":
            mySerial.write(("7:"+ str(nuevo_limite)+"\n").encode('utf-8'))

    except ValueError:
        print("Error: Por favor, introduce un número válido para el límite.")
        consola("Error: Por favor, introduce un número válido para el límite.")


# Configuración de las gráficas de temperatura y distancia (con frames)

frame_graficaT = Frame(window, bg="grey")
frame_graficaT.grid(row=1, column=1, columnspan=2, rowspan=2, sticky=N + S + E + W)

frame_graficaM = Frame(window, bg="grey")
frame_graficaM.grid(row=3, column=1, columnspan=2, rowspan=1, sticky=N + S + E + W)

frame_graficaD = Frame(window, bg="grey")
frame_graficaD.grid(row=1, column=3, columnspan=2, rowspan=3, sticky=N + S + E + W)

figT = Figure(figsize=(4,3.4), dpi=100)
axT = figT.add_subplot(111)
canvas1 = FigureCanvasTkAgg(figT, master=frame_graficaT)
canvas1.draw()
canvas1.get_tk_widget().pack(expand=False)

figD = Figure(figsize=(5,3.4), dpi=100)
axD = figD.add_subplot(111, projection='polar')
canvas2 = FigureCanvasTkAgg(figD, master=frame_graficaD)
canvas2.draw()
canvas2.get_tk_widget().pack(expand=False)

figM = Figure(figsize=(4, 2.2), dpi=100)
axM = figM.add_subplot(111)
canvas3 = FigureCanvasTkAgg(figM, master=frame_graficaM)
canvas3.draw()
canvas3.get_tk_widget().pack(expand=False)

def Grafica_temp():
    global i, i_media
    #Gráfica de temperaturas instantáneas
    if len(Temperaturas) > i:
        eje_x.append(i)

        axT.clear()  # limpiar la gráfica
        axT.set_title("Grafica de Temperatura")
        axT.set_ylabel("Temperatura (°C)")
        axT.plot(eje_x, Temperaturas[:len(eje_x)], marker=".", color="red")

        axT.set_facecolor("grey")  # fondo gris
        figT.patch.set_facecolor("grey")

        canvas1.draw()  # actualizar la gráfica incrustada
        i += 1

    #Gráfica de la media de los últimos 10 valores
    if len(Medias_Temp) > i_media:
        eje_x_media.append(i_media)

        axM.clear()  # limpiar la gráfica anterior
        axM.set_title(f"Media 10 últimas ({modo_calculo})")  # Muestra en el título si calcula Tierra o Satélite
        axM.set_ylabel("Media (°C)")

        # Dibujamos la evolución de la media en azul
        axM.plot(eje_x_media, Medias_Temp[:len(eje_x_media)], marker="o", markersize=3, color="blue", label="Media")

        # Dibujamos una línea horizontal discontinua en el valor límite de alarma
        axM.axhline(y=limite_alarma, color="darkred", linestyle="--", linewidth=1.2, label="Límite")
        axM.legend(loc="upper left", fontsize=7)  # Leyenda pequeña para distinguir las líneas

        axM.set_facecolor("grey")
        figM.patch.set_facecolor("grey")

        canvas3.draw() # actualizar la gráfica incrustada
        i_media += 1

    window.after(500, Grafica_temp)

def Grafica_dist():
    global currentangulo, ultimo_borrado
    if len(Distancias1) == 0 or len(Distancias2) == 0:
        window.after(100, Grafica_dist)
        return

    # Ángulo frontal (0° a 180°) y trasero (+180° -> 180° a 360°)
    rad1 = math.radians(currentangulo)
    rad2 = math.radians(currentangulo + 180)

    d1 = Distancias1[-1]
    d2 = Distancias2[-1]

    eje_xD1.append(rad1)
    eje_yD1.append(d1)
    eje_xD2.append(rad2)
    eje_yD2.append(d2)

    axD.clear()
    axD.set_title("Radar de Distancia 360°")

    # Configuración circular completa (sin thetamin ni thetamax)
    axD.set_theta_zero_location("W")
    axD.set_theta_direction(-1)

    distancia_max = max(max(eje_yD1), max(eje_yD2), 10)
    axD.set_ylim(0, distancia_max)

    # Dos haces de barrido opuestos (frontal y trasero)
    axD.plot([rad1, rad1], [0, d1], color="lime", linewidth=1)
    axD.plot([rad2, rad2], [0, d2], color="lime", linewidth=1)

    # Estela de barrido independiente para cada sensor
    axD.plot(eje_xD1[-50:], eje_yD1[-50:], color="lime", linewidth=0.75)
    axD.plot(eje_xD2[-50:], eje_yD2[-50:], color="lime", linewidth=0.75)

    # Estética del radar
    axD.set_facecolor("black")
    figD.patch.set_facecolor("grey")
    axD.grid(color="lime", linestyle="--", linewidth=0.5)
    axD.tick_params(colors="lime")
    axD.spines['polar'].set_color('lime')

    # Puntos históricos y actuales de ambos sensores
    axD.scatter(eje_xD1[::5], eje_yD1[::5], color="red", s=8, alpha=0.4)
    axD.scatter(eje_xD2[::5], eje_yD2[::5], color="red", s=8, alpha=0.4)
    axD.scatter([rad1, rad2], [d1, d2], color="red", s=50)

    if time.time() - ultimo_borrado >= 10:
        eje_xD1.clear()
        eje_yD1.clear()
        eje_xD2.clear()
        eje_yD2.clear()
        ultimo_borrado = time.time()

    canvas2.draw()
    window.after(100, Grafica_dist)

window.geometry("1680x840")
window.configure(bg="grey")
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)
window.rowconfigure(3, weight=1)
window.rowconfigure(4, weight=1)
window.rowconfigure(5, weight=1)
window.rowconfigure(6, weight=1)
window.rowconfigure(7, weight=1)
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)
window.columnconfigure(3, weight=1)
window.columnconfigure(4, weight=1)
window.columnconfigure(5, weight=1)
window.columnconfigure(6, weight=1)

tituloLabel = Label(window, text = "Space satellite project Mik-26", font=("Courier", 20, "italic"), bg="grey", fg="black")
tituloLabel.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky=N + S + E + W)

lbl_alarma = Label(window, text="ESTADO: NORMAL (0/3)", font=("Arial", 11, "bold"), bg="lightgreen", fg="black")
lbl_alarma.grid(row=0, column=6, padx=5, pady=5, sticky=N + S + E + W)

fraseEntry = Entry(window)
fraseEntry.grid(row=5, column=3, columnspan = 2, padx=5, pady=5, sticky=N + S + E + W)

EntrarButton = Button(window, text="Entrar", bg='turquoise', fg="black",command=EntrarClick)
EntrarButton.grid(row=5, column=5, padx=5, pady=5, sticky=N + S + E + W)

# Botobn para confirmar y aplicar el nuevo límite
btn_limite = Button(window, text="Fijar Límite", bg="orange", fg="black", command=fijar_limite)
btn_limite.grid(row=6, column=5, columnspan=2, padx=5, pady=5, sticky=N + S + E + W)


def actualizar_alarma_ui():
    global alarma_activa
    if ((alarma_activa) and (contador_alarma >= 3)): # Si la media supera el limite
        lbl_alarma.config(text=f"¡ALARMA! 3 medias > {limite_alarma}°C", bg="red", fg="white")
    elif (alarma_activa): # Cualquier otra alarma (de momento, que el usuario lea la consola para saber que ha pasado)
        lbl_alarma.config(text="ALARMA!!", bg="red", fg="white")
    else:
        lbl_alarma.config(text="ESTADO: NORMAL", bg="lightgreen", fg="black")
    window.after(300, actualizar_alarma_ui)

actualizar_alarma_ui()

AButton = Button(window, text="Iniciar recepcion", bg='turquoise', fg="black",command=AClick) # Iniciar recepción de datos
AButton.grid(row=5, column=0, padx=5, pady=5, sticky=N + S + E + W)
BButton = Button(window, text="Mostrar Temperatura", bg='turquoise', fg="black",command=BClick) # Mostrar gráfica de temperatura
BButton.grid(row=4, column=0, padx=5, pady=5, sticky=N + S + E + W)
CButton = Button(window, text="Parar recepción", bg='turquoise', fg="black", command=CClick) # Parar recepción de datos
CButton.grid(row=3, column=0, padx=5, pady=5, sticky=N + S + E + W)
DButton = Button(window, text="Reanudar recepción", bg='turquoise', fg="black", command=DClick) # Reanudar recepción de datos
DButton.grid(row=2, column=0, padx=5, pady=5, sticky=N + S + E + W)
EButton = Button(window, text="Mostrar Distancia", bg='turquoise', fg="black", command=EClick) # Mostrar gráfica de distancia
EButton.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)        
FButton = Button(window, text="Servo +15º", bg='turquoise', fg="black", command=FClick) # Sumar 15 grados al angulo
FButton.grid(row=5, column=1, padx=5, pady=5, sticky=N + S + E + W)
GButton = Button(window, text="Servo -15º", bg='turquoise', fg="black", command=GClick) # Restar 15 grados al angulo
GButton.grid(row=5, column=2, padx=5, pady=5, sticky=N + S + E + W)
JButton = Button(window, text="Modo Tierra", bg='turquoise', fg="black", command=JClick) # Restar 15 grados al angulo
JButton.grid(row=6, column=2, padx=5, pady=5, sticky=N + S + E + W)
KButton = Button(window, text="Modo Satelite", bg='turquoise', fg="black", command=KClick) # Sumar 15 grados al angulo
KButton.grid(row=6, column=1, padx=5, pady=5, sticky=N + S + E + W)



HButton = Button(window, text="Modificar intervalo H y T", bg="turquoise", fg="black", command=HClick)
HButton.grid(row=5, column=6, padx=5, pady=5, sticky=N + S + E + W)
IButton = Button(window, text="Modificar intervalo Distancia", bg="turquoise", fg="black", command=IClick)
IButton.grid(row=4, column=6, padx=5, pady=5, sticky=N + S + E + W)


window.mainloop()
