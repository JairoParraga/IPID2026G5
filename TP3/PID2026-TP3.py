
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
from pathlib import Path

from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



ruta_proyecto = Path(__file__).resolve().parent.parent
sys.path.append(str(ruta_proyecto))

import pdi_helper as pdi


img1 = None
img_resultante = None



# ==================================================
# MOSTRAR IMAGEN RESULTANTE
# ==================================================

def mostrar_resultado(imagen_array):
    global img_resultante

    img_resultante = imagen_array.copy()

    imagen_pil = Image.fromarray(
        img_resultante.astype(np.uint8)
    )

    # Redimensionar solamente la vista, no la matriz original
    vista = imagen_pil.copy()
    vista.thumbnail((350, 250))

    foto = ImageTk.PhotoImage(vista)

    imagen2_label.config(image=foto, text="")
    imagen2_label.image = foto

    # Actualizar histograma de la imagen resultante
    mostrar_histograma(img_resultante, ax2, canvas2)


# ==================================================
# HISTOGRAMA DEL CANAL Y EN PORCENTAJES
# ==================================================

def mostrar_histograma(img, ax, canvas):
    yiq=pdi.convertir_RGB_a_YIQ(img)
    luminancia = yiq[:, :, 0].ravel()

    # Cada píxel representa el mismo porcentaje del total
    pesos = np.full(
        luminancia.size,
        100.0 / luminancia.size
    )

    ax.clear()

    ax.hist(
        luminancia,
        bins=50,
        range=(0, 1),
        weights=pesos,
        color="steelblue",
        edgecolor="black"
    )

    ax.set_title("Histograma del canal Y")
    ax.set_xlabel("Luminancia")
    ax.set_ylabel("Aparición (%)")
    ax.set_xlim(0, 1)
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.3)

    ax.figure.tight_layout()
    canvas.draw()


# ==================================================
# ABRIR IMAGEN
# ==================================================

def abrir_imagen():
    global img1

    file_path = filedialog.askopenfilename(
        title="Abrir imagen",
        filetypes=[
            (
                "Archivos de imagen",
                "*.png *.jpg *.jpeg *.bmp *.tiff"
            ),
            ("Todos los archivos", "*.*")
        ]
    )

    if not file_path:
        return

    try:
        # Convertir a RGB para garantizar tres canales
        imagen = Image.open(file_path).convert("RGB")

        # Guardar la imagen completa como matriz NumPy
        img1 = np.array(imagen)

        # Mostrar una vista reducida sin alterar img1
        vista = imagen.copy()
        vista.thumbnail((350, 250))

        imagen_tk = ImageTk.PhotoImage(vista)

        imagen1_label.config(image=imagen_tk, text="")
        imagen1_label.image = imagen_tk

        # Al abrir, la imagen resultante comienza siendo la original
        mostrar_resultado(img1)

        # Actualizar histograma original
        mostrar_histograma(img1, ax1, canvas1)

    except Exception as error:
        messagebox.showerror(
            "Error",
            f"No se pudo abrir la imagen:\n{error}"
        )


# ==================================================
# VALIDACIONES
# ==================================================

def validarImagen(img):
    if img is None:
        messagebox.showwarning(
            "Advertencia",
            "Primero debes abrir una imagen."
        )
        return False

    return True


def validarYs():
    if not validarImagen(img1):
        return

    ymin = y_min.get()
    ymax = y_max.get()

    mostrar_resultado(pdi.Y_lineal_trozos(img1, ymin, ymax))



# ==================================================
# SELECCIÓN DE OPERACIONES
# ==================================================

def operacion(event=None):
    op = operacion_md.get()

    seccion_max_min.pack_forget()

    if op == "Lineal a Trozos":
        if validarImagen(img1):
            seccion_max_min.pack(
                side="top",
                fill="x",
                padx=5,
                pady=5
            )
        return

    if op == "Raiz":
        if validarImagen(img1):
            mostrar_resultado(pdi.Y_raiz_cuadrada(img1))

    elif op == "Cuadrado":
        if validarImagen(img1):
            mostrar_resultado(pdi.Y_cuadratica(img1))


# ==================================================
# INTERFAZ TKINTER
# ==================================================

ventana = tk.Tk()
ventana.geometry("1100x800")
ventana.title("TP 3 - Operaciones de luminancia")

# Distribución principal: dos columnas
contenedor = tk.Frame(ventana)
contenedor.pack(fill="both", expand=True, padx=10, pady=10)

# --------------------------------------------------
# COLUMNA IZQUIERDA: IMAGEN ORIGINAL E HISTOGRAMA
# --------------------------------------------------

card_imagen = tk.Frame(contenedor)
card_imagen.pack(
    side="left",
    fill="both",
    expand=True,
    padx=5
)

tk.Label(
    card_imagen,
    text="Imagen original",
    font=("Arial", 12, "bold")
).pack(pady=5)

imagen1_label = tk.Label(
    card_imagen,
    text="Abrí una imagen",
    bg="lightgray",
    width=40,
    height=12
)
imagen1_label.pack(fill="both", expand=True, pady=5)

tk.Label(
    card_imagen,
    text="Histograma original",
    font=("Arial", 11, "bold")
).pack(pady=5)

figura1, ax1 = plt.subplots(figsize=(5, 2.5))

canvas1 = FigureCanvasTkAgg(
    figura1,
    master=card_imagen
)

canvas1.get_tk_widget().pack(
    fill="both",
    expand=True,
    pady=5
)

abrir_btn = tk.Button(
    card_imagen,
    text="Abrir imagen",
    command=abrir_imagen
)
abrir_btn.pack(pady=5)


# --------------------------------------------------
# COLUMNA DERECHA: IMAGEN RESULTANTE E HISTOGRAMA
# --------------------------------------------------

card_resultado = tk.Frame(contenedor)
card_resultado.pack(
    side="right",
    fill="both",
    expand=True,
    padx=5
)

tk.Label(
    card_resultado,
    text="Imagen resultante",
    font=("Arial", 12, "bold")
).pack(pady=5)

imagen2_label = tk.Label(
    card_resultado,
    text="Sin resultados",
    bg="lightgray",
    width=40,
    height=12
)
imagen2_label.pack(fill="both", expand=True, pady=5)

tk.Label(
    card_resultado,
    text="Histograma resultante",
    font=("Arial", 11, "bold")
).pack(pady=5)

figura2, ax2 = plt.subplots(figsize=(5, 2.5))

canvas2 = FigureCanvasTkAgg(
    figura2,
    master=card_resultado
)

canvas2.get_tk_widget().pack(
    fill="both",
    expand=True,
    pady=5
)


# --------------------------------------------------
# CONTROLES DE OPERACIONES
# --------------------------------------------------

seccion_operacion = tk.Frame(card_resultado)
seccion_operacion.pack(side="bottom", fill="x", pady=5)

operacion_label = tk.Label(
    seccion_operacion,
    text="Operación:"
)
operacion_label.pack(side="left", padx=5)

valores_operaciones = [
    "Raiz",
    "Cuadrado",
    "Lineal a Trozos",
]

operacion_md = ttk.Combobox(
    seccion_operacion,
    values=valores_operaciones,
    state="readonly",
    width=32
)

operacion_md.pack(side="left", padx=5)
operacion_md.set("Seleccionar operación")
operacion_md.bind("<<ComboboxSelected>>", operacion)


# --------------------------------------------------
# CONTROLES PARA LINEAL A TROZOS
# --------------------------------------------------

seccion_max_min = tk.Frame(card_resultado)

seccion_min = tk.Frame(seccion_max_min)
seccion_min.pack(side="left", padx=5)

y_min = tk.DoubleVar(value=0.0)

tk.Label(
    seccion_min,
    text="Valor mínimo de Y"
).pack()

valor_minimo = tk.Scale(
    seccion_min,
    from_=0.0,
    to=1.0,
    resolution=0.1,
    variable=y_min,
    orient="horizontal"
)
valor_minimo.pack()

seccion_max = tk.Frame(seccion_max_min)
seccion_max.pack(side="left", padx=5)

y_max = tk.DoubleVar(value=1.0)

tk.Label(
    seccion_max,
    text="Valor máximo de Y"
).pack()

valor_maximo = tk.Scale(
    seccion_max,
    from_=0.0,
    to=1.0,
    resolution=0.1,
    variable=y_max,
    orient="horizontal"
)
valor_maximo.pack()

calcular_bt = tk.Button(
    seccion_max_min,
    text="Calcular",
    command=validarYs
)
calcular_bt.pack(side="left", padx=10)


# Iniciar la aplicación
ventana.mainloop()
