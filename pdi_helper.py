import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt


# ==============================================================================
# 1. UTILIDADES BÁSICAS Y VALIDACIONES (Aceptan cualquier tipo de imagen)
# ==============================================================================

def normalizar_float(img):
    """
    Asegura que la imagen esté en formato float32 en el rango [0.0, 1.0].
    Funciona tanto si entra en uint8 [0, 255] como si ya está en float [0, 1].
    """
    img_f = np.float32(img)
    if img.dtype == np.uint8 or img_f.max() > 1.0:
        img_f = img_f / 255.0
    return np.clip(img_f, 0.0, 1.0)


def convertir_uint8(img):
    """
    Asegura que la imagen esté en formato uint8 en el rango [0, 255].
    Funciona tanto si entra en float [0.0, 1.0] como en float/int [0, 255].
    """
    if img.dtype != np.uint8:
        if img.max() <= 1.0 and img.min() >= 0.0:
            img = img * 255.0
    return np.clip(img, 0, 255).astype(np.uint8)


def validar_imagen(img, mensaje="Primero debes abrir una imagen."):
    """Verifica que la imagen no sea None. Muestra advertencia si no existe."""
    if img is None:
        messagebox.showwarning("Advertencia", mensaje)
        return False
    return True


def validar_dimensiones(img1, img2):
    """Verifica que dos imágenes existan y tengan el mismo tamaño."""
    if not validar_imagen(img1, "Falta abrir la Imagen 1."):
        return False
    if not validar_imagen(img2, "Falta abrir la Imagen 2."):
        return False
    if img1.shape != img2.shape:
        messagebox.showerror(
            "Error",
            f"Las imágenes no tienen la misma dimensión:\n"
            f"Imagen 1: {img1.shape} vs Imagen 2: {img2.shape}"
        )
        return False
    return True


# ==============================================================================
# 2. FUNCIONES DE INTERFAZ Y ARCHIVOS (Tkinter + PIL)
# ==============================================================================

def abrir_imagen(tamano_max=None, modo="RGB"):
    """
    Abre un cuadro de diálogo para seleccionar una imagen y la devuelve como
    un array de NumPy (uint8). Si el usuario cancela, devuelve None.
    - tamano_max: tupla opcional, ej. (500, 400) para redimensionar al cargar.
    - modo: "RGB" por defecto (evita errores con PNGs de 4 canales RGBA),
            o "L" para abrir directamente en escala de grises.
    """
    ruta = filedialog.askopenfilename(
        title="Seleccionar imagen",
        filetypes=[
            ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"),
            ("Todos los archivos", "*.*")
        ]
    )
    if not ruta:
        return None

    try:
        imagen = Image.open(ruta)
        if modo:
            imagen = imagen.convert(modo)
        if tamano_max is not None:
            imagen.thumbnail(tamano_max)
        return np.array(imagen)
    except Exception as error:
        messagebox.showerror("Error", f"No se pudo abrir la imagen.\n\n{error}")
        return None


def guardar_imagen(imagen_array):
    """
    Abre un cuadro de diálogo para guardar un array de NumPy como archivo de imagen.
    """
    if not validar_imagen(imagen_array, "No hay una imagen procesada para guardar."):
        return False

    ruta = filedialog.asksaveasfilename(
        title="Guardar imagen procesada",
        defaultextension=".png",
        filetypes=[
            ("PNG", "*.png"),
            ("JPEG", "*.jpg"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tif")
        ]
    )
    if not ruta:
        return False

    try:
        img_uint8 = convertir_uint8(imagen_array)
        imagen_pil = Image.fromarray(img_uint8)
        imagen_pil.save(ruta)
        messagebox.showinfo("Guardar", "La imagen se guardó correctamente.")
        return True
    except Exception as error:
        messagebox.showerror("Error", f"No se pudo guardar la imagen.\n\n{error}")
        return False


def mostrar_en_label(label_tk, imagen_array, tamano_vista=None):
    """
    Muestra cualquier array de NumPy (2D gris o 3D RGB, float o uint8) en un Label
    de Tkinter. Si se indica tamano_vista=(ancho, alto), achica solo la vista
    sin modificar los datos reales de tu matriz.
    """
    if imagen_array is None:
        return

    img_uint8 = convertir_uint8(imagen_array)
    imagen_pil = Image.fromarray(img_uint8)

    if tamano_vista is not None:
        imagen_pil = imagen_pil.copy()
        imagen_pil.thumbnail(tamano_vista)

    foto = ImageTk.PhotoImage(imagen_pil)
    label_tk.foto = foto
    label_tk.image = foto
    label_tk.config(image=foto, text="")


# ==============================================================================
# 3. CANALES RGB, ESCALA DE GRISES Y ESPACIO YIQ (TP0 y TP1)
# ==============================================================================

def escala_grises(img, mantener_3d=False):
    """
    Convierte una imagen RGB a escala de grises promediando sus canales.
    Si ya está en 2D, devuelve una copia en uint8.
    """
    img_u8 = convertir_uint8(img)
    if img_u8.ndim == 2:
        gris = img_u8.copy()
    else:
        gris = img_u8.mean(axis=2).astype(np.uint8)

    if mantener_3d and gris.ndim == 2:
        return np.stack((gris, gris, gris), axis=2)
    return gris


def aislar_canal_rgb(img, canal):
    """
    Aísla un canal de una imagen RGB manteniendo la forma 3D (con los demás en 0).
    canal: 0 = Rojo, 1 = Verde, 2 = Azul.
    """
    img_u8 = convertir_uint8(img)
    if img_u8.ndim == 2:
        return img_u8.copy()

    resultado = np.zeros_like(img_u8)
    resultado[:, :, canal] = img_u8[:, :, canal]
    return resultado


def canal_rojo(img):
    return aislar_canal_rgb(img, 0)


def canal_verde(img):
    return aislar_canal_rgb(img, 1)


def canal_azul(img):
    return aislar_canal_rgb(img, 2)


# Matrices oficiales de conversión entre RGB y YIQ
MATRIZ_RGB_A_YIQ = np.array([
    [0.299,     0.587,     0.114],
    [0.595716, -0.274453, -0.321263],
    [0.211456, -0.522591,  0.311135]
], dtype=np.float32)

MATRIZ_YIQ_A_RGB = np.array([
    [1.0,  0.9663,  0.6210],
    [1.0, -0.2721, -0.6474],
    [1.0, -1.1069,  1.7046]
], dtype=np.float32)


def convertir_RGB_a_YIQ(img_rgb):
    """
    Convierte una imagen RGB (uint8 [0,255] o float [0,1]) al espacio YIQ.
    Si recibe una imagen 2D en grises, la convierte primero a 3 canales.
    """
    if img_rgb.ndim == 2:
        img_rgb = np.stack((img_rgb, img_rgb, img_rgb), axis=2)

    rgb_norm = normalizar_float(img_rgb)
    yiq = rgb_norm @ MATRIZ_RGB_A_YIQ.T
    return yiq


def convertir_YIQ_a_RGB(img_yiq, devolver_uint8=True):
    """
    Convierte una matriz YIQ de regreso a RGB aplicando recorte (clip) en [0, 1].
    Por defecto devuelve la imagen en uint8 [0, 255].
    """
    yiq = img_yiq.copy()
    yiq[:, :, 0] = np.clip(yiq[:, :, 0], 0.0, 1.0)
    yiq[:, :, 1] = np.clip(yiq[:, :, 1], -0.5957, 0.5957)
    yiq[:, :, 2] = np.clip(yiq[:, :, 2], -0.5226, 0.5226)

    rgb = yiq @ MATRIZ_YIQ_A_RGB.T
    rgb = np.clip(rgb, 0.0, 1.0)

    if devolver_uint8:
        return (rgb * 255.0).astype(np.uint8)
    return rgb


def modificar_YIQ(img_rgb, a=1.0, b=1.0, mostrar_avisos=False):
    """
    Modifica la luminancia (Y' = a*Y) y crominancia (I' = b*I, Q' = b*Q) (TP1).
    """
    yiq = convertir_RGB_a_YIQ(img_rgb)

    canal_y = yiq[:, :, 0] * a
    canal_i = yiq[:, :, 1] * b
    canal_q = yiq[:, :, 2] * b

    if mostrar_avisos:
        if not np.all(canal_y <= 1.0):
            messagebox.showinfo("Información", "El canal Y supera el máximo permitido (1).")
        if not np.all((canal_i >= -0.5957) & (canal_i <= 0.5957)):
            messagebox.showinfo("Información", "El canal I está fuera del rango permitido.")
        if not np.all((canal_q >= -0.5226) & (canal_q <= 0.5226)):
            messagebox.showinfo("Información", "El canal Q está fuera del rango permitido.")

    yiq[:, :, 0] = np.clip(canal_y, 0.0, 1.0)
    yiq[:, :, 1] = np.clip(canal_i, -0.5957, 0.5957)
    yiq[:, :, 2] = np.clip(canal_q, -0.5226, 0.5226)

    return convertir_YIQ_a_RGB(yiq)


# ==============================================================================
# 4. ARITMÉTICA DE PÍXELES (Suma, Resta, Producto, Cociente - TP2)
# ==============================================================================

def cuasi_suma_RGB_clampeada(A, B):
    resultado = np.float32(A) + np.float32(B)
    return np.clip(resultado, 0, 255).astype(np.uint8)


def cuasi_suma_RGB_promedio(A, B):
    resultado = (np.float32(A) + np.float32(B)) / 2.0
    return np.clip(resultado, 0, 255).astype(np.uint8)


def cuasi_suma_YIQ_clampeada(A, B):
    A_YIQ = convertir_RGB_a_YIQ(A)
    B_YIQ = convertir_RGB_a_YIQ(B)
    C_YIQ = np.zeros_like(A_YIQ)

    YA = A_YIQ[:, :, 0]
    YB = B_YIQ[:, :, 0]
    suma_Y = YA + YB

    C_YIQ[:, :, 0] = np.clip(suma_Y, 0.0, 1.0)

    # Evitamos división por cero cuando YA + YB == 0
    num_I = YA * A_YIQ[:, :, 1] + YB * B_YIQ[:, :, 1]
    num_Q = YA * A_YIQ[:, :, 2] + YB * B_YIQ[:, :, 2]
    np.divide(num_I, suma_Y, out=C_YIQ[:, :, 1], where=(suma_Y != 0))
    np.divide(num_Q, suma_Y, out=C_YIQ[:, :, 2], where=(suma_Y != 0))

    return convertir_YIQ_a_RGB(C_YIQ)


def cuasi_suma_YIQ_promedio(A, B):
    A_YIQ = convertir_RGB_a_YIQ(A)
    B_YIQ = convertir_RGB_a_YIQ(B)
    C_YIQ = np.zeros_like(A_YIQ)

    YA = A_YIQ[:, :, 0]
    YB = B_YIQ[:, :, 0]
    suma_Y = YA + YB

    C_YIQ[:, :, 0] = suma_Y / 2.0

    num_I = YA * A_YIQ[:, :, 1] + YB * B_YIQ[:, :, 1]
    num_Q = YA * A_YIQ[:, :, 2] + YB * B_YIQ[:, :, 2]
    np.divide(num_I, suma_Y, out=C_YIQ[:, :, 1], where=(suma_Y != 0))
    np.divide(num_Q, suma_Y, out=C_YIQ[:, :, 2], where=(suma_Y != 0))

    return convertir_YIQ_a_RGB(C_YIQ)


def cuasi_suma_YIQ_if_lighter(A, B):
    A_YIQ = convertir_RGB_a_YIQ(A)
    B_YIQ = convertir_RGB_a_YIQ(B)
    condicion = A_YIQ[:, :, 0] > B_YIQ[:, :, 0]
    C_YIQ = np.where(condicion[:, :, np.newaxis], A_YIQ, B_YIQ)
    return convertir_YIQ_a_RGB(C_YIQ)


def cuasi_suma_YIQ_if_darker(A, B):
    A_YIQ = convertir_RGB_a_YIQ(A)
    B_YIQ = convertir_RGB_a_YIQ(B)
    condicion = A_YIQ[:, :, 0] < B_YIQ[:, :, 0]
    C_YIQ = np.where(condicion[:, :, np.newaxis], A_YIQ, B_YIQ)
    return convertir_YIQ_a_RGB(C_YIQ)


def restar_RGB_clampeada(A, B):
    resultado = np.float32(A) - np.float32(B)
    return np.clip(resultado, 0, 255).astype(np.uint8)


def restar_RGB_promedio(A, B):
    a = normalizar_float(A)
    b = normalizar_float(B)
    resultado = (a - b + 1.0) / 2.0
    return convertir_uint8(resultado)


def restar_RGB_absoluta(A, B):
    resultado = np.abs(np.float32(A) - np.float32(B))
    return np.clip(resultado, 0, 255).astype(np.uint8)


def restar_YIQ_clampeada(A, B):
    A_YIQ = convertir_RGB_a_YIQ(A)
    B_YIQ = convertir_RGB_a_YIQ(B)
    C_YIQ = np.zeros_like(A_YIQ)

    C_Y = A_YIQ[:, :, 0] - B_YIQ[:, :, 0]
    C_YIQ[:, :, 0] = np.clip(C_Y, 0.0, 1.0)
    C_YIQ[:, :, 1] = np.where(C_Y > 0, A_YIQ[:, :, 1], 0.0)
    C_YIQ[:, :, 2] = np.where(C_Y > 0, A_YIQ[:, :, 2], 0.0)

    return convertir_YIQ_a_RGB(C_YIQ)


def restar_YIQ_promediada(A, B):
    A_YIQ = convertir_RGB_a_YIQ(A)
    B_YIQ = convertir_RGB_a_YIQ(B)
    C_YIQ = np.zeros_like(A_YIQ)

    C_YIQ[:, :, 0] = (A_YIQ[:, :, 0] - B_YIQ[:, :, 0] + 1.0) / 2.0
    C_YIQ[:, :, 1] = (A_YIQ[:, :, 1] - B_YIQ[:, :, 1]) / 2.0
    C_YIQ[:, :, 2] = (A_YIQ[:, :, 2] - B_YIQ[:, :, 2]) / 2.0

    return convertir_YIQ_a_RGB(C_YIQ)


def producto_RGB(A, B):
    a = normalizar_float(A)
    b = normalizar_float(B)
    return convertir_uint8(a * b)


def cociente_RGB(A, B):
    a = normalizar_float(A)
    b = normalizar_float(B)
    resultado = np.zeros_like(a)
    np.divide(a, b, out=resultado, where=(b != 0))
    return convertir_uint8(resultado)


# ==============================================================================
# 5. OPERACIONES DE LUMINANCIA Y FILTROS PUNTUALES (TP3 y Ejercicios Cátedra)
# ==============================================================================

def Y_raiz_cuadrada(img):
    """Filtro raíz cuadrada sobre luminancia Y (soporta imágenes RGB y 2D grises)."""
    if img.ndim == 2:
        gris_norm = normalizar_float(img)
        return convertir_uint8(np.sqrt(gris_norm))

    yiq = convertir_RGB_a_YIQ(img)
    yiq[:, :, 0] = np.sqrt(np.clip(yiq[:, :, 0], 0.0, 1.0))
    return convertir_YIQ_a_RGB(yiq)


def Y_cuadratica(img):
    """Filtro cuadrático sobre luminancia Y (soporta imágenes RGB y 2D grises)."""
    if img.ndim == 2:
        gris_norm = normalizar_float(img)
        return convertir_uint8(gris_norm * gris_norm)

    yiq = convertir_RGB_a_YIQ(img)
    yiq[:, :, 0] = yiq[:, :, 0] * yiq[:, :, 0]
    return convertir_YIQ_a_RGB(yiq)


def Y_lineal_trozos(img, ymin, ymax):
    """
    Estiramiento lineal a trozos de la luminancia entre [ymin, ymax] (en rango [0, 1]).
    Soporta imágenes RGB y 2D en escala de grises.
    """
    if ymin >= ymax:
        messagebox.showwarning("Advertencia", "El valor mínimo de Y debe ser menor al máximo.")
        return img

    if img.ndim == 2:
        y = normalizar_float(img)
        y_mod = np.where(y < ymin, 0.0, np.where(y > ymax, 1.0, (y - ymin) / (ymax - ymin)))
        return convertir_uint8(y_mod)

    yiq = convertir_RGB_a_YIQ(img)
    y = yiq[:, :, 0]
    yiq[:, :, 0] = np.where(
        y < ymin,
        0.0,
        np.where(y > ymax, 1.0, (y - ymin) / (ymax - ymin))
    )
    return convertir_YIQ_a_RGB(yiq)


def invertir_negativo(img):
    """Invierte los niveles de intensidad (negativo de la imagen)."""
    img_u8 = convertir_uint8(img)
    return 255 - img_u8


def binarizar(img, umbral=128):
    """
    Binariza una imagen según un umbral (si el umbral está en [0, 1] lo escala a 255).
    Si la imagen es RGB, la pasa a escala de grises antes de binarizar.
    """
    gris = escala_grises(img)
    if isinstance(umbral, float) and umbral <= 1.0:
        umbral = umbral * 255.0
    return np.where(gris >= umbral, 255, 0).astype(np.uint8)


def mezclar_imagenes(img1, img2, factor=0.5):
    """Interpolación lineal (blending) entre dos imágenes: (1 - factor)*img1 + factor*img2."""
    f = np.clip(float(factor), 0.0, 1.0)
    res = (1.0 - f) * np.float32(img1) + f * np.float32(img2)
    return convertir_uint8(res)


# ==============================================================================
# 6. HISTOGRAMAS (TP0 y TP3)
# ==============================================================================

def mostrar_histograma(img, modo="auto", bins=256, titulo="Histograma"):
    """
    Grafica el histograma de una imagen con Matplotlib:
    - modo="auto": Si es 3D grafica los 3 canales RGB; si es 2D grafica escala de grises.
    - modo="gris": Fuerza el histograma en escala de grises [0, 255].
    - modo="Y": Grafica el histograma del canal de luminancia Y en [0.0, 1.0] (TP3).
    """
    if not validar_imagen(img):
        return

    plt.figure(titulo)
    plt.clf()

    if modo == "Y":
        yiq = convertir_RGB_a_YIQ(img)
        plt.hist(yiq[:, :, 0].ravel(), bins=bins, range=(0.0, 1.0), color="gray")
        plt.title(f"{titulo} - Canal Y (Luminancia)")
        plt.xlabel("Luminancia [0 - 1]")
        plt.ylabel("Frecuencia")
        plt.xlim(0.0, 1.0)

    elif modo == "gris" or img.ndim == 2:
        gris = escala_grises(img)
        plt.hist(gris.ravel(), bins=bins, range=(0, 256), color="gray")
        plt.title(f"{titulo} - Escala de Grises")
        plt.xlabel("Intensidad [0 - 255]")
        plt.ylabel("Cantidad de píxeles")
        plt.xlim(0, 255)

    else:
        img_u8 = convertir_uint8(img)
        colores = [("Rojo", "red"), ("Verde", "green"), ("Azul", "blue")]
        for c, (nombre, color) in enumerate(colores):
            plt.hist(
                img_u8[:, :, c].ravel(),
                bins=bins,
                range=(0, 256),
                alpha=0.5,
                label=nombre,
                color=color
            )
        plt.title(f"{titulo} - Canales RGB")
        plt.xlabel("Intensidad [0 - 255]")
        plt.ylabel("Cantidad de píxeles")
        plt.xlim(0, 255)
        plt.legend()

    plt.grid(True)
    plt.show()




    # ==============================================================================
# 7. CONVOLUCIÓN Y KERNELS (TP4)
# ==============================================================================

def obtener_canal_Y(img):
    """
    Si la imagen es RGB (3D), la convierte a YIQ y devuelve solo el canal Y [0.0, 1.0].
    Si ya está en escala de grises (2D), la devuelve normalizada en [0.0, 1.0].
    """
    if img.ndim == 3:
        yiq = convertir_RGB_a_YIQ(img)
        return yiq[:, :, 0]
    else:
        return normalizar_float(img)


def repetir_bordes(img_2d, pad):
    """
    Técnica de cierre de bordes: repite artificialmente la primera/última fila
    y la primera/última columna 'pad' veces (donde pad = tamano_kernel // 2).
    """
    alto, ancho = img_2d.shape
    expandida = np.zeros((alto + 2 * pad, ancho + 2 * pad), dtype=np.float32)

    # 1. Copiar la imagen original en el centro
    expandida[pad : pad + alto, pad : pad + ancho] = img_2d

    # 2. Repetir primera fila (arriba) y última fila (abajo)
    for p in range(pad):
        expandida[p, pad : pad + ancho] = img_2d[0, :]
        expandida[pad + alto + p, pad : pad + ancho] = img_2d[-1, :]

    # 3. Repetir primera columna (izquierda) y última columna (derecha), incluyendo esquinas
    for p in range(pad):
        expandida[:, p] = expandida[:, pad]
        expandida[:, pad + ancho + p] = expandida[:, pad + ancho - 1]

    return expandida


def convolucionar(img, kernel):
    """
    Aplica filtrado por convolución sobre el canal Y (nivel de gris) de la imagen,
    repitiendo filas y columnas en los bordes. Devuelve la imagen en uint8 [0, 255].
    """
    img_y = obtener_canal_Y(img)
    alto, ancho = img_y.shape
    k_alto, k_ancho = kernel.shape
    pad = k_alto // 2

    # Expandimos la imagen repitiendo filas y columnas en los bordes
    img_ext = repetir_bordes(img_y, pad)
    resultado = np.zeros((alto, ancho), dtype=np.float32)

    # Doble ciclo for recorriendo el kernel y acumulando la suma de productos
    for ki in range(k_alto):
        for kj in range(k_ancho):
            ventana = img_ext[ki : ki + alto, kj : kj + ancho]
            resultado += ventana * kernel[ki, kj]

    # Recortamos al rango válido [0.0, 1.0] y pasamos a uint8 [0, 255]
    resultado = np.clip(resultado, 0.0, 1.0)
    return convertir_uint8(resultado)


# --- 7.1 GENERADORES DE KERNELS PASABAJOS ---

def kernel_plano(tamano):
    """Kernel pasabajos plano (llano) de NxN (todos 1 / N^2)."""
    return np.ones((tamano, tamano), dtype=np.float32) / float(tamano * tamano)


def kernel_bartlett(tamano):
    """
    Kernel pasabajos Bartlett (triangular) de 3x3, 5x5 o 7x7.
    Se construye multiplicando un vector triangular 1D por sí mismo.
    """
    mitad = (tamano + 1) // 2
    # Arma la rampa ej: [1, 2, 1] para 3x3, [1, 2, 3, 2, 1] para 5x5
    creciente = list(range(1, mitad + 1))
    decreciente = list(range(mitad - 1, 0, -1))
    vec_1d = np.array(creciente + decreciente, dtype=np.float32)

    kernel_2d = np.outer(vec_1d, vec_1d)
    return kernel_2d / kernel_2d.sum()


def kernel_gaussiano(tamano):
    """
    Kernel pasabajos Gaussiano basado en el Triángulo de Pascal (3x3, 5x5, 7x7).
    """
    if tamano == 3:
        vec_1d = np.array([1, 2, 1], dtype=np.float32)
    elif tamano == 5:
        vec_1d = np.array([1, 4, 6, 4, 1], dtype=np.float32)
    elif tamano == 7:
        vec_1d = np.array([1, 6, 15, 20, 15, 6, 1], dtype=np.float32)
    else:
        vec_1d = np.ones(tamano, dtype=np.float32)

    kernel_2d = np.outer(vec_1d, vec_1d)
    return kernel_2d / kernel_2d.sum()


# --- 7.2 DETECTORES DE BORDES (LAPLACIANO Y SOBEL 8 ORIENTACIONES) ---

def kernel_laplaciano(vecinos=4):
    """Devuelve el kernel Laplaciano de 4 vecinos (v4) o de 8 vecinos (v8)."""
    if vecinos == 4:
        return np.array([
            [ 0, -1,  0],
            [-1,  4, -1],
            [ 0, -1,  0]
        ], dtype=np.float32)
    else:  # v8
        return np.array([
            [-1, -1, -1],
            [-1,  8, -1],
            [-1, -1, -1]
        ], dtype=np.float32)


def kernel_sobel(orientacion):
    """
    Devuelve el kernel de Sobel 3x3 para cualquiera de las 8 orientaciones:
    'N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO'.
    """
    sobel_dict = {
        "N": np.array([
            [ 1,  2,  1],
            [ 0,  0,  0],
            [-1, -2, -1]
        ], dtype=np.float32),
        "NE": np.array([
            [ 0,  1,  2],
            [-1,  0,  1],
            [-2, -1,  0]
        ], dtype=np.float32),
        "E": np.array([
            [-1,  0,  1],
            [-2,  0,  2],
            [-1,  0,  1]
        ], dtype=np.float32),
        "SE": np.array([
            [-2, -1,  0],
            [-1,  0,  1],
            [ 0,  1,  2]
        ], dtype=np.float32),
        "S": np.array([
            [-1, -2, -1],
            [ 0,  0,  0],
            [ 1,  2,  1]
        ], dtype=np.float32),
        "SO": np.array([
            [ 0, -1, -2],
            [ 1,  0, -1],
            [ 2,  1,  0]
        ], dtype=np.float32),
        "O": np.array([
            [ 1,  0, -1],
            [ 2,  0, -2],
            [ 1,  0, -1]
        ], dtype=np.float32),
        "NO": np.array([
            [ 2,  1,  0],
            [ 1,  0, -1],
            [ 0, -1, -2]
        ], dtype=np.float32)
    }
    return sobel_dict[orientacion]


# --- 7.3 PASABANDA Y PASAALTOS ---

def kernel_pasabanda():
    """
    Filtro Pasabanda por Diferencia de Gaussianas (DoG):
    Resta el kernel Gaussiano 5x5 al Gaussiano 3x3 (insertado en 5x5).
    """
    g3 = np.zeros((5, 5), dtype=np.float32)
    g3[1:4, 1:4] = kernel_gaussiano(3)
    g5 = kernel_gaussiano(5)
    return g3 - g5


def kernel_pasaaltos(frecuencia_corte=0.2):
    """
    Filtro Pasaaltos (Impulso Identidad menos Pasabajos):
    - frecuencia_corte = 0.2 -> Usa kernel 5x5 (Identidad 5x5 - Gaussiano 5x5)
    - frecuencia_corte = 0.4 -> Usa kernel 3x3 (Identidad 3x3 - Gaussiano 3x3)
    """
    if frecuencia_corte == 0.2:
        identidad = np.zeros((5, 5), dtype=np.float32)
        identidad[2, 2] = 1.0
        return identidad - kernel_gaussiano(5)
    else:  # 0.4
        identidad = np.zeros((3, 3), dtype=np.float32)
        identidad[1, 1] = 1.0
        return identidad - kernel_gaussiano(3)



# ==============================================================================
# 8. OPERACIONES MORFOLÓGICAS (TP5) - IMPLEMENTACIÓN CORREGIDA
# ==============================================================================
# Estas operaciones trabajan sobre imágenes 2D. Para escala de grises se espera
# uint8 [0, 255]. Para binario se admite tanto {0, 1} como {0, 255}.
# Se utiliza un elemento estructurante cuadrado de 3x3 y extensión por borde.


def _a_grises_2d(imagen):
    """Devuelve una imagen 2D uint8, convirtiendo RGB a grises si es necesario."""
    if imagen is None:
        raise ValueError("La imagen no puede ser None.")
    arreglo = np.asarray(imagen)
    if arreglo.ndim == 3:
        arreglo = escala_grises(arreglo)
    if arreglo.ndim != 2:
        raise ValueError("La operación morfológica requiere una imagen 2D.")
    return convertir_uint8(arreglo)


def validar_binarizar(imagen):
    """Indica si la matriz es 2D y contiene únicamente 0/1 o 0/255."""
    if imagen is None:
        return False
    arreglo = np.asarray(imagen)
    if arreglo.ndim != 2:
        return False
    valores = np.unique(arreglo)
    return bool(np.all(np.isin(valores, [0, 1])) or np.all(np.isin(valores, [0, 255])))


def binarizar(imagen, umbral=0.5):
    """Binariza una imagen gris. Umbral en [0,1] normalizado o en [0,255].

    Devuelve una matriz uint8 cuyos valores son 0 y 1, manteniendo compatibilidad
    con los ejercicios morfológicos que usan la convención binaria {0, 1}.
    """
    gris = _a_grises_2d(imagen)
    umbral = float(umbral)
    umbral_px = umbral * 255.0 if 0.0 <= umbral <= 1.0 else umbral
    return (gris > umbral_px).astype(np.uint8)


def _extremo_vecindad_3x3(imagen, funcion):
    """Aplica mínimo/máximo local 3x3, repitiendo los valores de los bordes."""
    img = _a_grises_2d(imagen)
    pad = np.pad(img, ((1, 1), (1, 1)), mode="edge")
    ventanas = [pad[i:i + img.shape[0], j:j + img.shape[1]]
                for i in range(3) for j in range(3)]
    resultado = ventanas[0].copy()
    for ventana in ventanas[1:]:
        resultado = funcion(resultado, ventana)
    return resultado.astype(img.dtype, copy=False)


def dilatacion_gris(imagen):
    """Dilatación en escala de grises: máximo de la vecindad 3x3."""
    return _extremo_vecindad_3x3(imagen, np.maximum)


def erocion_gris(imagen):
    """Erosión en escala de grises: mínimo de la vecindad 3x3."""
    return _extremo_vecindad_3x3(imagen, np.minimum)


def erosion_gris(imagen):
    """Alias con ortografía estándar para erocion_gris."""
    return erocion_gris(imagen)


def dilatacion_binarizada(imagen):
    """Dilatación binaria (máximo local 3x3); conserva la escala de entrada."""
    return _extremo_vecindad_3x3(imagen, np.maximum)


def erocion_binarizada(imagen):
    """Erosión binaria (mínimo local 3x3); conserva la escala de entrada."""
    return _extremo_vecindad_3x3(imagen, np.minimum)


def erosion_binarizada(imagen):
    """Alias con ortografía estándar para erocion_binarizada."""
    return erocion_binarizada(imagen)


def erosion(imagen):
    """Erosión morfológica 3x3 (válida para escala de grises o binaria)."""
    return erocion_gris(imagen)


def dilatacion(imagen):
    """Dilatación morfológica 3x3 (válida para escala de grises o binaria)."""
    return dilatacion_gris(imagen)


def apertura_gris(imagen):
    """Apertura: erosión seguida de dilatación."""
    return dilatacion_gris(erocion_gris(imagen))


def cierre_gris(imagen):
    """Cierre: dilatación seguida de erosión."""
    return erocion_gris(dilatacion_gris(imagen))


def gradiente_morfologica_gris(imagen):
    """Borde morfológico (gradiente): dilatación menos erosión."""
    dilatada = dilatacion_gris(imagen).astype(np.int16)
    erosionada = erocion_gris(imagen).astype(np.int16)
    return np.clip(dilatada - erosionada, 0, 255).astype(np.uint8)


def apertura_binarizada(imagen):
    """Apertura binaria: erosión seguida de dilatación."""
    return dilatacion_binarizada(erocion_binarizada(imagen))


def cierre_binarizada(imagen):
    """Cierre binario: dilatación seguida de erosión."""
    return erocion_binarizada(dilatacion_binarizada(imagen))


def gradiente_morfologica(imagen):
    """Gradiente morfológico binario: dilatación menos erosión."""
    dilatada = dilatacion_binarizada(imagen).astype(np.int16)
    erosionada = erocion_binarizada(imagen).astype(np.int16)
    return np.maximum(dilatada - erosionada, 0).astype(np.asarray(imagen).dtype)


def borde_exterior(imagen):
    """Borde exterior: dilatación menos imagen original."""
    img = _a_grises_2d(imagen)
    dilatada = dilatacion_gris(img).astype(np.int16)
    return np.maximum(dilatada - img.astype(np.int16), 0).astype(np.uint8)


def borde_interior(imagen):
    """Borde interior: imagen original menos erosión."""
    img = _a_grises_2d(imagen)
    erosionada = erocion_gris(img).astype(np.int16)
    return np.maximum(img.astype(np.int16) - erosionada, 0).astype(np.uint8)


def gradiente(imagen):
    """Gradiente morfológico: dilatación menos erosión.

    Funciona con imágenes en escala de grises y con binarias representadas
    como {0, 1} o {0, 255}.
    """
    img = _a_grises_2d(imagen)
    dilatada = dilatacion_gris(img).astype(np.int16)
    erosionada = erocion_gris(img).astype(np.int16)
    return np.maximum(dilatada - erosionada, 0).astype(np.uint8)


def apertura(imagen):
    """Apertura morfológica genérica."""
    return apertura_gris(imagen)


def cierre(imagen):
    """Cierre morfológico genérico."""
    return cierre_gris(imagen)


def borde_morfologico(imagen):
    """Alias histórico del gradiente morfológico (por compatibilidad)."""
    return gradiente(imagen)


def mediana_3x3(imagen):
    """Filtro de mediana 3x3. Los bordes se extienden repitiendo sus píxeles."""
    img = _a_grises_2d(imagen)
    pad = np.pad(img, ((1, 1), (1, 1)), mode="edge")
    alto, ancho = img.shape
    ventanas = [pad[i:i + alto, j:j + ancho] for i in range(3) for j in range(3)]
    return np.median(np.stack(ventanas, axis=0), axis=0).astype(img.dtype)
