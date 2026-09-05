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



# Funciones del programa

def convertir_a_YIQ():
    global imagen_actual

    print("convertir_a_YIQ ejecutada")
    print("imagen_actual =", imagen_actual)

    # Verificar que exista una imagen
    if imagen_actual is None:
        messagebox.showwarning(
            "Advertencia",
            "Primero debes abrir una imagen."
        )
        return

    # Obtener valores a y b
    try:
        a = float(entrada_a.get())
        b = float(entrada_b.get())
    except ValueError:
        messagebox.showerror(
            "Error",
            "Los valores a y b deben ser números."
        )
        return

    # Matriz YIQ -> RGB
    matriz_conversion_YIQ_a_RGB = np.array([
        [1,       0.9663,  0.6210],
        [1,      -0.2721, -0.6474],
        [1,      -1.1069,  1.7046]
    ])

    # Matriz RGB -> YIQ
    matriz_conversion_RGB_a_YIQ = np.array([
        [0.299,  0.587,  0.114],
        [0.596, -0.274, -0.322],
        [0.211, -0.523,  0.312]
    ])

    # RGB [0,255] -> RGB [0,1]
    imagen_rgb = imagen_actual.astype(np.float64) / 255.0

    # RGB -> YIQ
    imagen_yiq = imagen_rgb @ matriz_conversion_RGB_a_YIQ.T

    # Modificar canales
    canal_y = imagen_yiq[:, :, 0] * a
    canal_i = imagen_yiq[:, :, 1] * b
    canal_q = imagen_yiq[:, :, 2] * b

    # Verificar límites
    if not np.all(canal_y <= 1):
        messagebox.showerror(
            "Error",
            "El canal Y supera el valor máximo permitido (1)."
        )
        return

    if not np.all(
        (canal_i >= -0.5957) &
        (canal_i <= 0.5957)
    ):
        messagebox.showerror(
            "Error",
            "El canal I está fuera del rango permitido."
        )
        return

    if not np.all(
        (canal_q >= -0.5226) &
        (canal_q <= 0.5226)
    ):
        messagebox.showerror(
            "Error",
            "El canal Q está fuera del rango permitido."
        )
        return

    # Guardar canales modificados
    imagen_yiq[:, :, 0] = canal_y
    imagen_yiq[:, :, 1] = canal_i
    imagen_yiq[:, :, 2] = canal_q

    # YIQ -> RGB
    imagen_rgb_modificada = (
        imagen_yiq @ matriz_conversion_YIQ_a_RGB.T
    )

    # Limitar RGB al rango [0,1]
    imagen_rgb_modificada = np.clip(
        imagen_rgb_modificada,
        0,
        1
    )

    # RGB [0,1] -> RGB [0,255]
    imagen_rgb_modificada *= 255

    imagen_procesada = imagen_rgb_modificada.astype(np.uint8)

    # Mostrar resultado
    mostrar_imagen_derecha(imagen_procesada)

     


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


# Componentes del contenedor de imagenes
componente_imagen_actual = tk.Label(contenedor_imagen,text="Imagen Actual",bg="gray")
componente_imagen_actual.pack(expand=True,fill="both",side="left",padx=5,pady=5)

componente_imagen_procesada = tk.Label(contenedor_imagen,text="Imagen Procesada",bg="gray")
componente_imagen_procesada.pack(expand=True,fill="both",side="right",padx=5,pady=5)
# Componentes del contenedor de botones

label_a = tk.Label(contenedor_botones, text="Valor a:")
label_a.pack(side="left", padx=5, pady=5)
entrada_a = tk.Entry(contenedor_botones)
entrada_a.pack(side="left", padx=5, pady=5)
label_b = tk.Label(contenedor_botones, text="Valor b:")
label_b.pack(side="left", padx=5, pady=5)
entrada_b = tk.Entry(contenedor_botones)
entrada_b.pack(side="left", padx=5, pady=5)
opcion2_btn = tk.Button(contenedor_botones, text="Modificar", command=convertir_a_YIQ)
opcion2_btn.pack(side="left", padx=5, pady=5)


ventana.mainloop()




