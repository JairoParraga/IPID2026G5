import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt


# ==========================================
# VARIABLES
# ==========================================

imagen_original = None
imagen_actual_array = None
imagen_procesada = None


# ==========================================
# ABRIR IMAGEN
# ==========================================

def abrir_imagen():

    global imagen_original
    global imagen_actual_array
    global imagen_procesada

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
        imagen_actual_array = imagen_array.copy()
        imagen_procesada = None
        mostrar_imagen_izquierda(imagen_actual_array)
        imagen_modificada.config(
            image="",
            text="Imagen procesada"
        )

    except Exception as error:
        messagebox.showerror(
            "Error",
            f"No se pudo abrir la imagen.\n\n{error}"
        )


# ==========================================
# MOSTRAR IMAGEN IZQUIERDA
# ==========================================

def mostrar_imagen_izquierda(imagen_array):

    imagen_pil = Image.fromarray(imagen_array)
    foto = ImageTk.PhotoImage(imagen_pil)
    imagen_actual.foto = foto
    imagen_actual.config(
        image=foto,
        text=""
    )


# ==========================================
# MOSTRAR IMAGEN DERECHA
# ==========================================

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
    imagen_modificada.foto = foto
    imagen_modificada.config(
        image=foto,
        text=""
    )


# ==========================================
# ESCALA DE GRISES
# ==========================================

def escala_grises():

    global imagen_actual_array
    global imagen_procesada

    if imagen_actual_array is None:

        messagebox.showwarning(
            "Advertencia",
            "Primero debes abrir una imagen."
        )

        return

    gris = imagen_actual_array.mean(axis=2)
    gris = gris.astype(np.uint8)
    imagen_procesada = gris
    mostrar_imagen_derecha(imagen_procesada)


# ==========================================
# PASAR PROCESADA A LA IZQUIERDA
# ==========================================

def pasar_a_izquierda():

    global imagen_actual_array

    if imagen_procesada is None:

        messagebox.showwarning(
            "Advertencia",
            "Primero debes procesar una imagen."
        )

        return
    imagen_actual_array = imagen_procesada.copy()
    mostrar_imagen_izquierda(imagen_actual_array)


# ==========================================
# RESTAURAR ORIGINAL
# ==========================================

def restaurar():

    global imagen_actual_array

    if imagen_original is None:

        messagebox.showwarning(
            "Advertencia",
            "Primero debes abrir una imagen."
        )

        return
    imagen_actual_array = imagen_original.copy()
    mostrar_imagen_izquierda(imagen_actual_array)


# ==========================================
# GUARDAR IMAGEN PROCESADA
# ==========================================

def guardar():

    if imagen_procesada is None:

        messagebox.showwarning(
            "Advertencia",
            "No hay una imagen procesada para guardar."
        )

        return

    ruta = filedialog.asksaveasfilename(
        title="Guardar imagen procesada",
        defaultextension=".png",
        filetypes=[
            ("PNG", "*.png"),
            ("JPEG", "*.jpg"),
            ("BMP", "*.bmp")
        ]
    )

    if not ruta:
        return

    try:

        imagen_pil = Image.fromarray(
            imagen_procesada
        )

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


# ==========================================
# MOSTRAR HISTOGRAMA
# ==========================================

def mostrar_histograma():

    if imagen_actual_array is None:

        messagebox.showwarning(
            "Advertencia",
            "Primero debes abrir una imagen."
        )

        return
    plt.figure("Histograma")
    if imagen_actual_array.ndim == 3:

        # Histograma del canal rojo
        plt.hist(
            imagen_actual_array[:, :, 0].ravel(),
            bins=256,
            range=(0, 256),
            alpha=0.5,
            label="Rojo"
        )

        # Histograma del canal verde
        plt.hist(
            imagen_actual_array[:, :, 1].ravel(),
            bins=256,
            range=(0, 256),
            alpha=0.5,
            label="Verde"
        )

        # Histograma del canal azul
        plt.hist(
            imagen_actual_array[:, :, 2].ravel(),
            bins=256,
            range=(0, 256),
            alpha=0.5,
            label="Azul"
        )

        plt.title("Histograma de la imagen RGB")
        plt.xlabel("Intensidad")
        plt.ylabel("Cantidad de píxeles")
        plt.legend()

    else:
        plt.hist(
            imagen_actual_array.ravel(),
            bins=256,
            range=(0, 256)
        )

        plt.title("Histograma de escala de grises")
        plt.xlabel("Intensidad")
        plt.ylabel("Cantidad de píxeles")

    plt.xlim(0, 255)
    plt.grid()
    plt.show()

# ==========================================
# CANALES RGB
# ==========================================
def canal_rojo():
    global imagen_procesada
    if imagen_actual_array is None:
        messagebox.showwarning(
            "Advertencia",
            "Primero debes abrir una imagen."
        )
        return

    canal_r = np.zeros_like(imagen_actual_array)
    canal_r[:, :, 0] = imagen_actual_array[:, :, 0]
    imagen_procesada = canal_r  

    mostrar_imagen_derecha(canal_r)

def canal_verde():
    global imagen_procesada
    if imagen_actual_array is None:
        messagebox.showwarning(
            "Advertencia",
            "Primero debes abrir una imagen."
        )
        return

    canal_g = np.zeros_like(imagen_actual_array)
    canal_g[:, :, 1] = imagen_actual_array[:, :, 1]
    imagen_procesada = canal_g      
    mostrar_imagen_derecha(canal_g)

def canal_azul():
    global imagen_procesada
    if imagen_actual_array is None:
        messagebox.showwarning(
            "Advertencia",
            "Primero debes abrir una imagen."
        )
        return

    canal_b = np.zeros_like(imagen_actual_array)
    canal_b[:, :, 2] = imagen_actual_array[:, :, 2]
    imagen_procesada = canal_b

    mostrar_imagen_derecha(canal_b)

# ==========================================
# VENTANA PRINCIPAL
# ==========================================

ventana = tk.Tk()

ventana.title("Trabajo Práctico 0")

ventana.geometry("1000x600")


# ==========================================
# PANEL SUPERIOR
# ==========================================

panel_inicio = tk.Frame(ventana)

panel_inicio.pack(
    pady=10,
    padx=10,
    side="top",
    fill="x"
)


# Abrir
boton_abrir = tk.Button(
    panel_inicio,
    text="Abrir imagen",
    command=abrir_imagen
)

boton_abrir.pack(
    pady=2,
    padx=10,
    side="left"
)


# Restaurar
boton_restaurar = tk.Button(
    panel_inicio,
    text="Restaurar original",
    command=restaurar
)

boton_restaurar.pack(
    pady=2,
    padx=10,
    side="left"
)


# ==========================================
# CONTENEDOR DE IMÁGENES
# ==========================================

contenedor_imagen = tk.Frame(ventana)

contenedor_imagen.pack(
    fill="both",
    expand=True
)


# ==========================================
# IMAGEN IZQUIERDA
# ==========================================

imagen_actual = tk.Label(
    contenedor_imagen,
    text="Abrí una imagen para comenzar",
    bg="#dddddd"
)

imagen_actual.pack(
    expand=True,
    padx=10,
    pady=10,
    fill="both",
    side="left"
)


# ==========================================
# IMAGEN DERECHA
# ==========================================

imagen_modificada = tk.Label(
    contenedor_imagen,
    text="Imagen procesada",
    bg="#dddddd"
)

imagen_modificada.pack(
    expand=True,
    padx=10,
    pady=10,
    fill="both",
    side="right"
)


# ==========================================
# PANEL DE OPCIONES
# ==========================================

contenedor_opciones = tk.Frame(ventana)

contenedor_opciones.pack(
    side="bottom",
    fill="x",
    pady=10
)


# Escala de grises
escala_gris = tk.Button(
    contenedor_opciones,
    text="Escala Gris",
    command=escala_grises
)

escala_gris.pack(
    padx=10,
    pady=2,
    side="left"
)


# Pasar procesada a izquierda
pasar_izquierda = tk.Button(
    contenedor_opciones,
    text="Pasar → Izquierda",
    command=pasar_a_izquierda
)

pasar_izquierda.pack(
    padx=10,
    pady=2,
    side="left"
)


# Histograma
boton_histograma = tk.Button(
    contenedor_opciones,
    text="Histograma",
    command=mostrar_histograma
)

boton_histograma.pack(
    padx=10,
    pady=2,
    side="left"
)

# Canal Rojo
boton_canal_rojo = tk.Button(
    contenedor_opciones,
    text="Canal Rojo",
    command=canal_rojo
)
boton_canal_rojo.pack(
    padx=10,
    pady=2,
    side="left"
)

# Canal Grenn
boton_canal_verde = tk.Button(
    contenedor_opciones,
    text="Canal Verde",
    command=canal_verde
)
boton_canal_verde.pack(
    padx=10,
    pady=2,
    side="left"
)
# Canal Blue
boton_canal_azul = tk.Button(
    contenedor_opciones,
    text="Canal Azul",
    command=canal_azul
)
boton_canal_azul.pack(
    padx=10,
    pady=2,
    side="left"
)


# Guardar
guardar_imagen = tk.Button(
    contenedor_opciones,
    text="Guardar procesada",
    command=guardar
)

guardar_imagen.pack(
    padx=10,
    pady=2,
    side="left"
)



ventana.mainloop()