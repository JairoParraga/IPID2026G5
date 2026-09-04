import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt

# Variables 
imagen_original = None
imagen_actual = None
imagen_procesada = None

# Función para abrir una imagen
def abrir_imagen():
    global imagen_original, imagen_actual, imagen_procesada
    ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")
            ]
        )
    
    if not ruta:
        return
    try:

        imagen = Image.open(ruta).convert("RGB")
        imagen.thumbnail((500, 400))
        imagen_array = np.array(imagen)
        imagen_original = imagen_array.copy()
        imagen_actual = imagen_array.copy()
        imagen_procesada = None
        
        mostrar_imagen_izquierda(imagen_array)
    except Exception as error:
        messagebox.showerror(
            "Error",
            f"No se pudo abrir la imagen.\n\n{error}"
        )    
       

def mostrar_imagen_izquierda(imagen_array):

    imagen_pil = Image.fromarray(imagen_array)
    foto = ImageTk.PhotoImage(imagen_pil)
    componente_imagen_actual.foto = foto
    componente_imagen_actual.config(
        image=foto,
        text=""
    )
def mostrar_imagen_derecha(imagen_array):
    if imagen_array.ndim == 2:
        imagen_pil = Image.fromarray(
            imagen_array.astype(np.uint8)
        )
    else:
        imagen_pil = Image.fromarray(
            imagen_array.astype(np.uint8)
        )

    foto = ImageTk.PhotoImage(imagen_pil)
    componente_imagen_procesada.foto = foto
    componente_imagen_procesada.config(
        image=foto,
        text=""
    )

def restaurar():

    global imagen_actual

    if imagen_original is None:

        messagebox.showwarning(
            "Advertencia",
            "Primero debes abrir una imagen."
        )

        return
    imagen_actual = imagen_original.copy()
    mostrar_imagen_izquierda(imagen_actual)


# Funciones del programa
def opcion1():
    return
def opcion2():
    return
def opcion3():
    return

def canal_rojo():
    global imagen_actual, imagen_procesada

    if imagen_actual is None:
        messagebox.showwarning(
            "Advertencia",
            "Primero debes abrir una imagen."
        )
        return

    canal_r = imagen_actual[:, :, 0]

    imagen_procesada = canal_r

    mostrar_imagen_derecha(imagen_procesada)
    canal_r = np.zeros_like(imagen_actual)
    canal_r[:, :, 0] = imagen_actual[:, :, 0]
    imagen_procesada = canal_r  

    mostrar_imagen_derecha(canal_r)


ventana = tk.Tk()
ventana.title("TP1 - PID2026")
ventana.geometry("800x600")

cabecera = tk.Frame(ventana)
cabecera.pack(side="top", fill="x")

contenedor_imagen = tk.Frame(ventana)
contenedor_imagen.pack( fill="both", expand=True)

contenedor_botones = tk.Frame(ventana)
contenedor_botones.pack(side="bottom", fill="x")

# Componentes de la cabecera
abrir_btn = tk.Button(cabecera, text="Abrir Imagen", command=abrir_imagen)
abrir_btn.pack(side="left", padx=5, pady=5)
restaurar_btn = tk.Button(cabecera, text="Restaurar Imagen", command=restaurar)
restaurar_btn.pack(side="left", padx=5, pady=5)

# Componentes del contenedor de imagenes
componente_imagen_actual = tk.Label(contenedor_imagen,text="Imagen Actual",bg="gray")
componente_imagen_actual.pack(expand=True,fill="both",side="left",padx=5,pady=5)

componente_imagen_procesada = tk.Label(contenedor_imagen,text="Imagen Procesada",bg="gray")
componente_imagen_procesada.pack(expand=True,fill="both",side="right",padx=5,pady=5)
# Componentes del contenedor de botones
opcion1_btn = tk.Button(contenedor_botones, text="Opcion 1", command=canal_rojo)
opcion1_btn.pack(side="left", padx=5, pady=5)

opcion2_btn = tk.Button(contenedor_botones, text="Opcion 2", command=opcion2)
opcion2_btn.pack(side="left", padx=5, pady=5)

opcion3_btn = tk.Button(contenedor_botones, text="Opcion 3", command=opcion3)
opcion3_btn.pack(side="left", padx=5, pady=5)

ventana.mainloop()

