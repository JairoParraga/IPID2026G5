import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
from pathlib import Path

from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt

ruta_proyecto = Path(__file__).resolve().parent.parent
sys.path.append(str(ruta_proyecto))

import pdi_helper as pdi




img1 = None
img2 = None
img_resultado = None
# Funciones para sumar dos imagenes


# Funcion de de la interfaz

def operacion(event):
    seleccion = opcion_op.get()
    if seleccion == "Suma":
        formato = ["RGB Clampeada", "RGB Promedio", "YIQ Clampeada", "YIQ Promedio", "YIQ If Ligther", "YIQ If Darker"]
    if seleccion == "Resta":
        formato = ["RGB Absoluta", "R-RGB Clampeada","R-YIQ Clampeada","R-RGB Promedio","R-YIQ Promedio"]
    if seleccion == "Producto":
        formato = ["RGB"]
    if seleccion == "Cociente":
        formato = ["C-RGB"]    
    opcion_formato['values'] = formato
    opcion_formato.set("...")


def validar_dimensiones_Imagenes ():
    global img1,img2
    if img1.shape[0] != img2.shape[0] or img1.shape[1] != img2.shape[1]:
        messagebox.showerror(
                "Error",
                f"Las imágenes no son de la misma dimensión.\n\n"
        )

        respuesta = messagebox.askyesno( "Confirmación", "¿Desea redimencionar la imagen con la dimension de la otra para realizar esta acción?")
        if respuesta:
            # Instrucciones si responde Sí
            igualar_dimensiones(img1, img2)
            actualizar_imagenes()
            return True
        return False    
    return True

def igualar_dimensiones(imgen1, imgen2):
    pil1 = Image.fromarray(imgen1)
    pil2 = Image.fromarray(imgen2)

    # Obtener las dimensiones (ancho, alto)
    ancho1, alto1 = pil1.size
    ancho2, alto2 = pil2.size

    # Determinar cuál imagen tiene menor superficie
    if ancho1 * alto1 <= ancho2 * alto2:
        # img1 es la base
        global img2
        img2 = np.array(
            pil2.resize((ancho1, alto1), Image.Resampling.LANCZOS)
        )
    else:
        # img2 es la base
        global img1
        img1 = np.array(
            pil1.resize((ancho2, alto2), Image.Resampling.LANCZOS)
        )

def actualizar_imagenes():
        global img1, img2
        imagen1 = Image.fromarray(img1)
        imagen1.thumbnail((200, 200))
        imagen1_tk = ImageTk.PhotoImage(imagen1)
        imagen1_label.config(image=imagen1_tk)
        imagen1_label.image = imagen1_tk
        imagen2 = Image.fromarray(img2)
        imagen2.thumbnail((200, 200))
        imagen2_tk = ImageTk.PhotoImage(imagen2)
        imagen2_label.config(image=imagen2_tk)
        imagen2_label.image = imagen2_tk


def realizar_operacion():

    seleccion_fo = opcion_formato.get()
    
    if seleccion_fo == "RGB Clampeada" and validar_dimensiones_Imagenes():
         mostrar_imagen_resultado(
             pdi.cuasi_suma_RGB_clampeada(img1, img2)
        )
    elif seleccion_fo == "RGB Promedio"and validar_dimensiones_Imagenes():         
         mostrar_imagen_resultado(
             pdi.cuasi_suma_RGB_promedio(img1, img2)
        )
    elif seleccion_fo == "YIQ Clampeada"and validar_dimensiones_Imagenes():
         mostrar_imagen_resultado(
             pdi.cuasi_suma_YIQ_clampeada(img1, img2)
        )
    elif seleccion_fo == "YIQ Promedio"and validar_dimensiones_Imagenes():
         mostrar_imagen_resultado(
             pdi.cuasi_suma_YIQ_promedio(img1, img2)
        )
    elif seleccion_fo == "YIQ If Ligther"and validar_dimensiones_Imagenes():
         mostrar_imagen_resultado(
             pdi.cuasi_suma_YIQ_if_lighter(img1, img2)
        )
    elif seleccion_fo == "YIQ If Darker"and validar_dimensiones_Imagenes():
         mostrar_imagen_resultado(
             pdi.cuasi_suma_YIQ_if_darker(img1,img2)
        )
    elif seleccion_fo == "RGB Absoluta"and validar_dimensiones_Imagenes():
         mostrar_imagen_resultado(pdi.restar_RGB_absoluta(img1, img2))
    elif seleccion_fo == "R-RGB Clampeada"and validar_dimensiones_Imagenes():
         mostrar_imagen_resultado(pdi.restar_RGB_clampeada(img1,img2))
    elif seleccion_fo == "R-YIQ Clampeada"and validar_dimensiones_Imagenes():
         mostrar_imagen_resultado(pdi.restar_YIQ_clampeada(img1,img2))
    elif seleccion_fo == "R-RGB Promedio"and validar_dimensiones_Imagenes():
         mostrar_imagen_resultado(pdi.restar_RGB_promedio(img1,img2))
    elif seleccion_fo == "R-YIQ Promedio"and validar_dimensiones_Imagenes():
         mostrar_imagen_resultado(pdi.restar_YIQ_promediada(img1,img2))
    elif seleccion_fo == "RGB"and validar_dimensiones_Imagenes():
         mostrar_imagen_resultado(pdi.producto_RGB(img1, img2))
    elif seleccion_fo == "C-RGB"and validar_dimensiones_Imagenes():
         mostrar_imagen_resultado(pdi.cociente_RGB(img1,img2))
    



def mostrar_imagen_resultado(resultado):
    global img_resultado
    if resultado is not None:
        if resultado.dtype == np.float64:
            resultado = (resultado * 255).astype(np.uint8)
        imagen_resultado = Image.fromarray(resultado)
        imagen_resultado.thumbnail((200, 200))
        imagen_tk = ImageTk.PhotoImage(imagen_resultado)
        imagen3_label.config(image=imagen_tk)
        imagen3_label.image = imagen_tk
        img_resultado=resultado


def abrir_imagen(numero):
    file_path = filedialog.askopenfilename(
        title=f"Abrir Imagen {numero}",
        filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff"), ("Todos los archivos", "*.*")]
    )
    if file_path:
        imagen = Image.open(file_path)
        imagen.thumbnail((200, 200))
        imagen_tk = ImageTk.PhotoImage(imagen)

        if numero == 1:
            imagen1_label.config(image=imagen_tk)
            imagen1_label.image = imagen_tk
            global img1
            img1 = np.array(imagen)
        elif numero == 2:
            imagen2_label.config(image=imagen_tk)
            imagen2_label.image = imagen_tk
            global img2
            img2 = np.array(imagen)
    realizar_operacion()
def guardar_imagen():
    global img_resultado
    if img_resultado is None:
        messagebox.showwarning(
            "Advertencia",
            "No hay una imagen procesada para guardar."
        )
        return None
    ruta = filedialog.asksaveasfilename(
        title="Guardar imagen procesada",
        defaultextension=".png",
        filetypes=[
            ("PNG", "*.png"),
            ("JPEG", "*.jpg"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tif"),
        ]
    )

    if not ruta:
        return

    try:
        imagen_pil = Image.fromarray(img_resultado)
        imagen_pil.save(ruta)
        messagebox.showinfo(
            "Guardar",
            "La imagen se guardó correctamente."
        )
    except Exception as error:
    
            messagebox.showerror(
                "Error",
                f"No se pudo guardar la imagen.\n\n{error}"
            )    
def intercambiar_imagenes():
    global img1, img2
    img1, img2 = img2, img1

    if img1 is not None:
        imagen1 = Image.fromarray(img1)
        imagen1.thumbnail((200, 200))
        imagen1_tk = ImageTk.PhotoImage(imagen1)
        imagen1_label.config(image=imagen1_tk)
        imagen1_label.image = imagen1_tk
    else:
        imagen1_label.config(image='', text="Imagen 1", bg="lightgray")

    if img2 is not None:
        imagen2 = Image.fromarray(img2)
        imagen2.thumbnail((200, 200))
        imagen2_tk = ImageTk.PhotoImage(imagen2)
        imagen2_label.config(image=imagen2_tk)
        imagen2_label.image = imagen2_tk
    else:
        imagen2_label.config(image='', text="Imagen 2", bg="lightgray")

    

#Inicio de la intefaz grafica

windows = tk.Tk()
windows.geometry("800x400")
windows.title("Trabajo Práctico 2 - PID2026")

#-----CONTENEDORES-----#
# Contenedor de imagenes
contenedor_imagenes = tk.Frame(windows)
contenedor_imagenes.pack(fill="both", expand=True)

# Contenedor de operaciones
contenedor_botones = tk.Frame(windows)
contenedor_botones.pack(side="bottom", fill="x",  )

# CARD imagenes
imagen1_frame = tk.Frame(contenedor_imagenes, bd=2, relief="groove")
imagen1_frame.pack(side="left", fill="both", expand=True, padx=5)
imagen2_frame = tk.Frame(contenedor_imagenes, bd=2, relief="groove")
imagen2_frame.pack(side="left", fill="both", expand=True, padx=5)
imagen3_frame = tk.Frame(contenedor_imagenes, bd=2, relief="groove")
imagen3_frame.pack(side="left", fill="both", expand=True, padx=5)

imagen1_label = tk.Label(imagen1_frame, text="Imagen 1",bg="lightgray")
imagen1_label.pack(fill="both",expand=True)
abrir_imagen1_button = tk.Button(imagen1_frame, text="Abrir Imagen 1", command=lambda: abrir_imagen(1))
abrir_imagen1_button.pack(side="bottom", pady=5)

imagen2_label = tk.Label(imagen2_frame, text="Imagen 2",bg="lightgray")
imagen2_label.pack(fill="both",expand=True)
abrir_imagen2_button = tk.Button(imagen2_frame, text="Abrir Imagen 2", command=lambda: abrir_imagen(2))
abrir_imagen2_button.pack(side="bottom", pady=5)

imagen3_label = tk.Label(imagen3_frame, text="Imagen Resultado",bg="lightgray")
imagen3_label.pack(fill="both",expand=True)

guardar_imagen_button = tk.Button(imagen3_frame, text="Guardar Imagen", command=lambda: guardar_imagen())
guardar_imagen_button.pack(side="bottom", pady=5)


# menu de operaciones
Operaciones=["Suma","Resta","Producto","Cociente"]
operacion_label = tk.Label(contenedor_botones, text="Operaciones:")
operacion_label.pack(side="left", padx=5, pady=5)
opcion_op = ttk.Combobox(contenedor_botones, values=Operaciones, state="readonly")
opcion_op.set("Seleccione una opcion")
opcion_op.pack(side="left", padx=5, pady=5)
opcion_op.bind("<<ComboboxSelected>>", operacion)

formato=[]
formato_label = tk.Label(contenedor_botones, text="Formato:")
formato_label.pack(side="left", padx=5, pady=5)
opcion_formato = ttk.Combobox(contenedor_botones, values=formato, state="readonly")
opcion_formato.set("...")
opcion_formato.pack(side="left", padx=5, pady=5)
opcion_formato.bind("<<ComboboxSelected>>", lambda event: realizar_operacion())

intercambiar_btn = tk.Button(contenedor_botones, text="Intercambiar Imagenes", command=lambda: intercambiar_imagenes())
#intercambiar_btn.pack(side="right", padx=5, pady=5)


windows.mainloop()