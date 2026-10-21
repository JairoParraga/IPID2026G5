import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ruta_proyecto = Path(__file__).resolve().parent.parent
sys.path.append(str(ruta_proyecto))

import pdi_helper as pdi


# Matrices de trabajo. La imagen se carga en gris y se conserva como referencia.
img_original = None
img_actual = None       # imagen de trabajo, ubicada a la izquierda
img_resultante = None


# -----------------------------------------------------------------------------
# Utilidades de visualización e histogramas
# -----------------------------------------------------------------------------
def _a_uint8_visual(imagen):
    """Convierte matrices grises/binarias a uint8 para mostrarlas y guardarlas."""
    if imagen is None:
        return None
    arr = np.asarray(imagen)
    if arr.ndim == 2 and arr.size and arr.min() >= 0 and arr.max() <= 1:
        arr = arr.astype(np.float32) * 255.0
    return np.clip(arr, 0, 255).astype(np.uint8)


def mostrar_en_label(label, imagen, tamano=(440, 250)):
    if imagen is None:
        label.configure(image="", text="Sin imagen")
        label.image = None
        return
    arr = _a_uint8_visual(imagen)
    pil = Image.fromarray(arr, mode="L")
    pil.thumbnail(tamano)
    foto = ImageTk.PhotoImage(pil)
    label.configure(image=foto, text="")
    label.image = foto


def mostrar_histograma(imagen, ax, canvas, titulo):
    """Histograma de intensidad normalizada con eje Y en porcentaje."""
    ax.clear()
    if imagen is None:
        ax.set_title(titulo)
        ax.set_xlabel("Intensidad normalizada")
        ax.set_ylabel("Aparición (%)")
        ax.set_xlim(0, 1)
        canvas.draw_idle()
        return

    arr = np.asarray(imagen)
    if arr.ndim == 3:
        arr = pdi.escala_grises(arr)
    valores = arr.astype(np.float64).ravel()
    if valores.size == 0:
        return
    if valores.min() >= 0 and valores.max() <= 1:
        normalizados = valores
    else:
        normalizados = valores / 255.0
    pesos = np.full(normalizados.size, 100.0 / normalizados.size)

    ax.hist(normalizados, bins=50, range=(0, 1), weights=pesos,
            edgecolor="black", linewidth=0.35)
    ax.set_title(titulo, fontsize=10)
    ax.set_xlabel("Intensidad normalizada (0–1)", fontsize=8)
    ax.set_ylabel("Aparición (%)", fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_ylim(bottom=0)
    ax.tick_params(axis="both", labelsize=8)
    ax.grid(axis="y", alpha=0.25)
    ax.figure.tight_layout(pad=1.2)
    canvas.draw_idle()


def actualizar_panel_izquierdo():
    mostrar_en_label(imagen1_label, img_actual)
    mostrar_histograma(img_actual, ax1, canvas1, "Histograma de la imagen de trabajo")


def mostrar_resultado(imagen):
    global img_resultante
    img_resultante = np.asarray(imagen).copy()
    mostrar_en_label(imagen2_label, img_resultante)
    mostrar_histograma(img_resultante, ax2, canvas2, "Histograma de la imagen resultante")


# -----------------------------------------------------------------------------
# Acciones principales
# -----------------------------------------------------------------------------
def abrir_imagen():
    global img_original, img_actual, img_resultante
    ruta = filedialog.askopenfilename(
        title="Abrir imagen",
        filetypes=[("Archivos de imagen", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
                   ("Todos los archivos", "*.*")],
    )
    if not ruta:
        return
    try:
        with Image.open(ruta) as imagen:
            img_original = np.asarray(imagen.convert("L"), dtype=np.uint8)
        img_actual = img_original.copy()
        tipo_md.set("Imagen en escala grises")
        operacion_md.set("Seleccionar operación")
        mostrar_controles_umbral()
        actualizar_panel_izquierdo()
        mostrar_resultado(img_actual)
    except Exception as error:
        messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{error}")


def restaurar_original():
    global img_actual
    if img_original is None:
        messagebox.showwarning("Advertencia", "Primero debes abrir una imagen.")
        return
    img_actual = img_original.copy()
    tipo_md.set("Imagen en escala grises")
    operacion_md.set("Seleccionar operación")
    mostrar_controles_umbral()
    actualizar_panel_izquierdo()
    mostrar_resultado(img_actual)


def pasar_a_izquierda():
    """Convierte la salida actual en la nueva imagen de trabajo."""
    global img_actual
    if img_resultante is None:
        messagebox.showwarning("Advertencia", "No hay una imagen resultante para pasar.")
        return
    img_actual = img_resultante.copy()
    actualizar_panel_izquierdo()


def guardar_resultado():
    if img_resultante is None:
        messagebox.showwarning("Advertencia", "No hay una imagen procesada para guardar.")
        return
    ruta = filedialog.asksaveasfilename(
        title="Guardar imagen resultante",
        defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"),
                   ("BMP", "*.bmp"), ("TIFF", "*.tif;*.tiff")],
    )
    if not ruta:
        return
    try:
        Image.fromarray(_a_uint8_visual(img_resultante), mode="L").save(ruta)
        messagebox.showinfo("Guardar imagen", "La imagen se guardó correctamente.")
    except Exception as error:
        messagebox.showerror("Error", f"No se pudo guardar la imagen:\n{error}")


# -----------------------------------------------------------------------------
# Selección de tipo y operación morfológica
# -----------------------------------------------------------------------------
OPERACIONES = {
    "Erosión": pdi.erosion,
    "Dilatación": pdi.dilatacion,
    "Apertura": pdi.apertura,
    "Cierre": pdi.cierre,
    "Borde exterior": pdi.borde_exterior,
    "Borde interior": pdi.borde_interior,
    "Gradiente": pdi.gradiente,
    "Mediana 3x3": pdi.mediana_3x3,
}


def mostrar_controles_umbral(event=None):
    if tipo_md.get() == "Binarizar la imagen":
        seccion_umbral.pack(side="left", padx=(14, 4), pady=4)
    else:
        seccion_umbral.pack_forget()
    aplicar_operacion(mostrar_aviso=False)


def aplicar_operacion(event=None, mostrar_aviso=True):
    if img_actual is None:
        if mostrar_aviso:
            messagebox.showwarning("Advertencia", "Primero debes abrir una imagen.")
        return

    modo = tipo_md.get()
    if modo == "Binarizar la imagen":
        # pdi.binarizar devuelve {0,1}; pasar a {0,255} facilita la visualización.
        umbral = float(umbral_var.get())
        base = (pdi.binarizar(img_actual, umbral) * 255).astype(np.uint8)
    else:
        base = pdi.escala_grises(img_actual)

    operacion = operacion_md.get()
    if operacion in OPERACIONES:
        try:
            resultado = OPERACIONES[operacion](base)
            if resultado is None:
                raise ValueError("La operación no devolvió una imagen.")
            mostrar_resultado(resultado)
        except Exception as error:
            if mostrar_aviso:
                messagebox.showerror("Error de procesamiento", str(error))
    else:
        # Si todavía no se seleccionó operación, la salida muestra solo la
        # conversión a grises o la binarización, de modo que el umbral sea visible.
        mostrar_resultado(base)


# -----------------------------------------------------------------------------
# Construcción de la interfaz: arriba acciones, centro imágenes/histogramas,
# abajo controles de procesamiento.
# -----------------------------------------------------------------------------
ventana = tk.Tk()
ventana.title("TP5 - Operaciones morfológicas")
ventana.geometry("1240x940")
ventana.minsize(1080, 800)

estilo = ttk.Style(ventana)
try:
    estilo.theme_use("clam")
except tk.TclError:
    pass

# Barra superior
barra_superior = ttk.Frame(ventana, padding=(10, 8))
barra_superior.pack(side="top", fill="x")

ttk.Button(barra_superior, text="Restaurar imagen original",
           command=restaurar_original).pack(side="left", padx=4)
ttk.Button(barra_superior, text="Pasar a la izquierda",
           command=pasar_a_izquierda).pack(side="left", padx=4)
ttk.Button(barra_superior, text="Guardar imagen",
           command=guardar_resultado).pack(side="left", padx=4)
ttk.Button(barra_superior, text="Abrir imagen",
           command=abrir_imagen).pack(side="right", padx=4)

separador1 = ttk.Separator(ventana, orient="horizontal")
separador1.pack(fill="x", padx=10, pady=(0, 6))

# Zona central: imagen de trabajo (izquierda) e imagen resultante (derecha)
contenedor_imagenes = ttk.Frame(ventana, padding=(8, 0, 8, 4))
contenedor_imagenes.pack(side="top", fill="both", expand=True)
contenedor_imagenes.columnconfigure(0, weight=1, uniform="imagenes")
contenedor_imagenes.columnconfigure(1, weight=1, uniform="imagenes")
contenedor_imagenes.rowconfigure(0, weight=1)

card_imagen = ttk.LabelFrame(contenedor_imagenes, text="Imagen de trabajo (izquierda)", padding=8)
card_imagen.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=4)
card_resultado = ttk.LabelFrame(contenedor_imagenes, text="Imagen resultante (derecha)", padding=8)
card_resultado.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=4)

imagen1_label = tk.Label(card_imagen, text="Abre una imagen", bg="#e8e8e8", relief="groove")
imagen1_label.pack(fill="both", expand=False, pady=(2, 6), ipady=70)
figura1, ax1 = plt.subplots(figsize=(5.0, 2.25), dpi=90)
canvas1 = FigureCanvasTkAgg(figura1, master=card_imagen)
canvas1.get_tk_widget().pack(fill="both", expand=True, pady=(0, 2))
mostrar_histograma(None, ax1, canvas1, "Histograma de la imagen de trabajo")

imagen2_label = tk.Label(card_resultado, text="Sin resultados", bg="#e8e8e8", relief="groove")
imagen2_label.pack(fill="both", expand=False, pady=(2, 6), ipady=70)
figura2, ax2 = plt.subplots(figsize=(5.0, 2.25), dpi=90)
canvas2 = FigureCanvasTkAgg(figura2, master=card_resultado)
canvas2.get_tk_widget().pack(fill="both", expand=True, pady=(0, 2))
mostrar_histograma(None, ax2, canvas2, "Histograma de la imagen resultante")

# Zona inferior de opciones
separador2 = ttk.Separator(ventana, orient="horizontal")
separador2.pack(fill="x", padx=10, pady=(3, 0))

panel_controles = ttk.LabelFrame(ventana, text="Controles de procesamiento", padding=10)
panel_controles.pack(side="bottom", fill="x", padx=10, pady=9)

fila_tipo = ttk.Frame(panel_controles)
fila_tipo.pack(fill="x", pady=(0, 8))
ttk.Label(fila_tipo, text="Transformación:").pack(side="left", padx=(0, 6))
tipo_md = ttk.Combobox(
    fila_tipo,
    values=["Binarizar la imagen", "Imagen en escala grises"],
    state="readonly",
    width=27,
)
tipo_md.pack(side="left", padx=(0, 14))
tipo_md.set("Imagen en escala grises")
tipo_md.bind("<<ComboboxSelected>>", mostrar_controles_umbral)

# Slider binario: se muestra únicamente en modo binario.
seccion_umbral = ttk.Frame(fila_tipo)
umbral_var = tk.DoubleVar(value=0.5)
ttk.Label(seccion_umbral, text="Umbral de binarización:").pack(side="left", padx=(0, 5))
umbral_slider = tk.Scale(
    seccion_umbral,
    from_=0.0,
    to=1.0,
    resolution=0.1,
    orient="horizontal",
    length=250,
    variable=umbral_var,
    showvalue=True,
    command=lambda _valor: aplicar_operacion(mostrar_aviso=False),
)
umbral_slider.pack(side="left")

fila_operacion = ttk.Frame(panel_controles)
fila_operacion.pack(fill="x")
ttk.Label(fila_operacion, text="Operación morfológica:").pack(side="left", padx=(0, 6))
operacion_md = ttk.Combobox(
    fila_operacion,
    values=list(OPERACIONES.keys()),
    state="readonly",
    width=27,
)
operacion_md.pack(side="left", padx=(0, 10))
operacion_md.set("Seleccionar operación")
operacion_md.bind("<<ComboboxSelected>>", aplicar_operacion)
ttk.Button(fila_operacion, text="Aplicar operación",
           command=aplicar_operacion).pack(side="left", padx=4)
ttk.Label(
    panel_controles,
    text="Elemento estructurante: cuadrado 3×3 · Histograma normalizado (0–1) en porcentaje.",
    foreground="#555555",
).pack(anchor="w", pady=(8, 0))


def cerrar_aplicacion():
    plt.close("all")
    ventana.destroy()

ventana.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)
ventana.mainloop()
