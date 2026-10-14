
import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter

# Importar los módulos del proyecto
ruta_proyecto = Path(__file__).resolve().parent.parent
sys.path.append(str(ruta_proyecto))

import pdi_helper as pdi


# ==========================================
# VARIABLES GLOBALES
# ==========================================

img_original_gris = None
img_actual_gris = None
img_filtrada = None

mostrar_histogramas = None

fig_izquierda = None
fig_derecha = None
ax_izquierda = None
ax_derecha = None

canvas_hist_izquierda = None
canvas_hist_derecha = None


# ==========================================
# FUNCIONES DE HISTOGRAMAS
# ==========================================

def actualizar_histograma(imagen, ax, canvas):
    """Actualiza el histograma de una imagen en porcentaje."""

    ax.clear()

    if imagen is None:
        ax.set_title("Histograma")
        ax.set_xlabel("Intensidad")
        ax.set_ylabel("Porcentaje (%)")
        canvas.draw_idle()
        return

    # Asegurar que la imagen sea una matriz de intensidades
    datos = np.asarray(imagen)

    if datos.ndim == 3:
        # Por seguridad, si llega una imagen RGB,
        # se utiliza su primer canal.
        datos = datos[:, :, 0]

    # Convertir a intensidades válidas entre 0 y 255
    datos = np.clip(datos, 0, 255).astype(np.uint8)

   
    # Histograma de 256 niveles de intensidad
    frecuencias, bordes = np.histogram(
        datos.ravel(),
        bins=256,
        range=(0, 256)
    )

    # Convertir las frecuencias a porcentajes
    total_pixeles = datos.size
    porcentajes = frecuencias / total_pixeles * 100

    # Normalizar las intensidades de 0-255 a 0-1
    intensidades = np.arange(256) / 255.0

    # Dibujar el histograma
    ax.bar(
        intensidades,
        porcentajes,
        width=1.0 / 255,
        align="center",
        color="steelblue",
        edgecolor="none"
    )

    # Configurar eje X: rango 0 a 1, intervalos de 0.1
    ax.set_xlim(0, 1)
    ax.set_xticks(np.arange(0, 1.01, 0.1))
    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda valor, _: f"{valor:.1f}")
    )

    # Configurar eje Y en porcentajes
    ax.set_ylabel("Porcentaje (%)")
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda valor, _: f"{valor:.1f}%")
    )

    ax.set_xlabel("Intensidad normalizada")
    ax.set_title("Histograma de intensidades")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

    canvas.figure.tight_layout()
    canvas.draw_idle()




def actualizar_histogramas():
    """Actualiza ambos histogramas según las imágenes mostradas."""

    actualizar_histograma(
        img_actual_gris,
        ax_izquierda,
        canvas_hist_izquierda
    )

    imagen_derecha = (
        img_filtrada if img_filtrada is not None
        else img_actual_gris
    )

    actualizar_histograma(
        imagen_derecha,
        ax_derecha,
        canvas_hist_derecha
    )


def alternar_histogramas():
    """Muestra u oculta ambos histogramas."""

    if mostrar_histogramas.get():
        canvas_hist_izquierda.get_tk_widget().pack(
            side="bottom", fill="x", padx=5, pady=5
        )
        canvas_hist_derecha.get_tk_widget().pack(
            side="bottom", fill="x", padx=5, pady=5
        )
    else:
        canvas_hist_izquierda.get_tk_widget().pack_forget()
        canvas_hist_derecha.get_tk_widget().pack_forget()

    ventana.update_idletasks()


# ==========================================
# FUNCIONES DE LA INTERFAZ
# ==========================================

def btn_abrir():
    global img_original_gris, img_actual_gris, img_filtrada

    img = pdi.abrir_imagen(tamano_max=(450, 380))

    if img is not None:
        # Obtener el canal Y y convertirlo a escala de grises
        canal_y = pdi.obtener_canal_Y(img)
        img_original_gris = pdi.convertir_uint8(canal_y)
        img_actual_gris = img_original_gris.copy()
        img_filtrada = None

        pdi.mostrar_en_label(label_izquierda, img_actual_gris)
        pdi.mostrar_en_label(label_derecha, img_actual_gris)

        actualizar_histogramas()


def btn_restaurar():
    global img_actual_gris, img_filtrada

    if pdi.validar_imagen(img_original_gris):
        img_actual_gris = img_original_gris.copy()
        img_filtrada = None

        pdi.mostrar_en_label(label_izquierda, img_actual_gris)
        pdi.mostrar_en_label(label_derecha, img_actual_gris)

        actualizar_histogramas()


def btn_pasar_a_izquierda():
    global img_actual_gris

    if pdi.validar_imagen(
        img_filtrada,
        "Primero debes aplicar un filtro."
    ):
        img_actual_gris = img_filtrada.copy()

        pdi.mostrar_en_label(label_izquierda, img_actual_gris)

        actualizar_histogramas()


def btn_guardar():
    pdi.guardar_imagen(img_filtrada)


def actualizar_lista_filtros(event=None):
    categoria = combo_categoria.get()

    if categoria == "1- Pasabajos":
        opciones = [
            "Plano 3x3", "Plano 5x5", "Plano 7x7",
            "Bartlett 3x3", "Bartlett 5x5", "Bartlett 7x7",
            "Gaussiano 5x5", "Gaussiano 7x7"
        ]

    elif categoria == "2- Detectores de Bordes":
        opciones = [
            "Laplaciano v4", "Laplaciano v8",
            "Sobel N", "Sobel NE", "Sobel E", "Sobel SE",
            "Sobel S", "Sobel SO", "Sobel O", "Sobel NO"
        ]

    elif categoria == "3- Pasabanda y Pasaaltos":
        opciones = [
            "Pasabanda",
            "Pasaaltos fc = 0.2",
            "Pasaaltos fc = 0.4"
        ]

    else:
        opciones = []

    combo_filtro["values"] = opciones

    if opciones:
        combo_filtro.current(0)


def aplicar_filtro(event=None):
    global img_filtrada

    if not pdi.validar_imagen(img_actual_gris):
        return

    seleccion = combo_filtro.get()
    kernel = None

    # 1. Pasabajos
    if seleccion == "Plano 3x3":
        kernel = pdi.kernel_plano(3)
    elif seleccion == "Plano 5x5":
        kernel = pdi.kernel_plano(5)
    elif seleccion == "Plano 7x7":
        kernel = pdi.kernel_plano(7)

    elif seleccion == "Bartlett 3x3":
        kernel = pdi.kernel_bartlett(3)
    elif seleccion == "Bartlett 5x5":
        kernel = pdi.kernel_bartlett(5)
    elif seleccion == "Bartlett 7x7":
        kernel = pdi.kernel_bartlett(7)

    elif seleccion == "Gaussiano 5x5":
        kernel = pdi.kernel_gaussiano(5)
    elif seleccion == "Gaussiano 7x7":
        kernel = pdi.kernel_gaussiano(7)

    # 2. Detectores de bordes
    elif seleccion == "Laplaciano v4":
        kernel = pdi.kernel_laplaciano(4)
    elif seleccion == "Laplaciano v8":
        kernel = pdi.kernel_laplaciano(8)

    elif seleccion.startswith("Sobel "):
        orientacion = seleccion.split(" ")[1]
        kernel = pdi.kernel_sobel(orientacion)

    # 3. Pasabanda y Pasaaltos
    elif seleccion == "Pasabanda":
        kernel = pdi.kernel_pasabanda()

    elif seleccion == "Pasaaltos fc = 0.2":
        kernel = pdi.kernel_pasaaltos(0.2)

    elif seleccion == "Pasaaltos fc = 0.4":
        kernel = pdi.kernel_pasaaltos(0.4)

    if kernel is not None:
        img_filtrada = pdi.convolucionar(img_actual_gris, kernel)

        pdi.mostrar_en_label(label_derecha, img_filtrada)

        # Actualizar el histograma de la imagen filtrada
        actualizar_histogramas()


# ==========================================
# VENTANA PRINCIPAL
# ==========================================

ventana = tk.Tk()
ventana.title("TP4 - Filtrado por Convolución (PID 2026)")
ventana.geometry("1100x800")
ventana.minsize(850, 650)


# ==========================================
# PANEL SUPERIOR
# ==========================================

panel_superior = tk.Frame(ventana)
panel_superior.pack(
    side="top", fill="x", padx=10, pady=8
)

tk.Button(
    panel_superior,
    text="Abrir Imagen",
    command=btn_abrir
).pack(side="left", padx=5)

tk.Button(
    panel_superior,
    text="Restaurar Original",
    command=btn_restaurar
).pack(side="left", padx=5)

tk.Button(
    panel_superior,
    text="Pasar → Izquierda",
    command=btn_pasar_a_izquierda
).pack(side="left", padx=5)

tk.Button(
    panel_superior,
    text="Guardar Filtrada",
    command=btn_guardar
).pack(side="left", padx=5)

# Checkbox para mostrar u ocultar histogramas
mostrar_histogramas = tk.BooleanVar(value=True)

ttk.Checkbutton(
    panel_superior,
    text="Mostrar histogramas",
    variable=mostrar_histogramas,
    command=alternar_histogramas
).pack(side="right", padx=10)


# ==========================================
# CONTENEDOR DE IMÁGENES E HISTOGRAMAS
# ==========================================

contenedor_imagenes = tk.Frame(ventana)
contenedor_imagenes.pack(
    fill="both", expand=True, padx=10, pady=5
)

# ------------------------------------------
# PANEL IZQUIERDO
# ------------------------------------------

frame_izq = tk.Frame(
    contenedor_imagenes,
    bd=2,
    relief="groove"
)

frame_izq.pack(
    side="left", fill="both", expand=True, padx=5
)

tk.Label(
    frame_izq,
    text="Imagen Original (Canal Y)",
    font=("Arial", 11, "bold")
).pack(side="top", pady=5)

label_izquierda = tk.Label(
    frame_izq,
    text="Abre una imagen",
    bg="#dddddd"
)

label_izquierda.pack(
    side="top", fill="both", expand=True, padx=5, pady=5
)

# Figura del histograma izquierdo
fig_izquierda, ax_izquierda = plt.subplots(figsize=(4.5, 2.0))
fig_izquierda.tight_layout()

canvas_hist_izquierda = FigureCanvasTkAgg(
    fig_izquierda,
    master=frame_izq
)

canvas_hist_izquierda.draw()

canvas_hist_izquierda.get_tk_widget().pack(
    side="bottom", fill="x", padx=5, pady=5
)


# ------------------------------------------
# PANEL DERECHO
# ------------------------------------------

frame_der = tk.Frame(
    contenedor_imagenes,
    bd=2,
    relief="groove"
)

frame_der.pack(
    side="right", fill="both", expand=True, padx=5
)

tk.Label(
    frame_der,
    text="Imagen Filtrada",
    font=("Arial", 11, "bold")
).pack(side="top", pady=5)

label_derecha = tk.Label(
    frame_der,
    text="Abre una imagen y aplica un filtro",
    bg="#dddddd"
)

label_derecha.pack(
    side="top", fill="both", expand=True, padx=5, pady=5
)

# Figura del histograma derecho
fig_derecha, ax_derecha = plt.subplots(figsize=(4.5, 2.0))
fig_derecha.tight_layout()

canvas_hist_derecha = FigureCanvasTkAgg(
    fig_derecha,
    master=frame_der
)

canvas_hist_derecha.draw()

canvas_hist_derecha.get_tk_widget().pack(
    side="bottom", fill="x", padx=5, pady=5
)

# Dibujar histogramas vacíos al iniciar
actualizar_histogramas()


# ==========================================
# PANEL INFERIOR: CONTROLES DE FILTRADO
# ==========================================

panel_inferior = tk.Frame(ventana)
panel_inferior.pack(
    side="bottom", fill="x", padx=10, pady=12
)

tk.Label(
    panel_inferior,
    text="Categoría:"
).pack(side="left", padx=5)

categorias = [
    "1- Pasabajos",
    "2- Detectores de Bordes",
    "3- Pasabanda y Pasaaltos"
]

combo_categoria = ttk.Combobox(
    panel_inferior,
    values=categorias,
    state="readonly",
    width=25
)

combo_categoria.set("Seleccione categoría...")
combo_categoria.pack(side="left", padx=5)

combo_categoria.bind(
    "<<ComboboxSelected>>",
    actualizar_lista_filtros
)

tk.Label(
    panel_inferior,
    text="Filtro:"
).pack(side="left", padx=5)

combo_filtro = ttk.Combobox(
    panel_inferior,
    values=[],
    state="readonly",
    width=22
)

combo_filtro.set("...")
combo_filtro.pack(side="left", padx=5)

btn_filtrar = tk.Button(
    panel_inferior,
    text="Filtrar ->",
    width=12,
    command=aplicar_filtro
)

btn_filtrar.pack(side="left", padx=15)


# ==========================================
# INICIAR APLICACIÓN
# ==========================================

ventana.mainloop()
