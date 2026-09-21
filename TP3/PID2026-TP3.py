import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt

img1=None
img_resultante=None

# Funciones de operaciones en luminicidad
def Y_raizcuadrada():
    yiq = convertirRGB_YIQ((np.float32(img1))/255.0)
    yiq[:,:,0] = np.sqrt(yiq[:,:,0])
    mostrar_resultado(convertir_YIQ_RGB(yiq))
    
def Y_cuadratica():
    yiq = convertirRGB_YIQ((np.float32(img1))/255.0)
    yiq[:,:,0] = yiq[:,:,0]*yiq[:,:,0]
    mostrar_resultado(convertir_YIQ_RGB(yiq))

def Y_lineal_trozo(ymin,ymax):
    yiq = convertirRGB_YIQ((np.float32(img1))/255.0)
    y = yiq[:,:,0]

    y = np.where(
        y < ymin,
        0,
        np.where(
            y > ymax,
            1,
            (y - ymin) / (ymax - ymin)
        )
    )

    yiq[:, :, 0] = y

    mostrar_resultado(convertir_YIQ_RGB(yiq))

def mostrar_resultado(imagen_array):
    if imagen_array.ndim == 2:
        imagen_pil = Image.fromarray(
            imagen_array.astype(np.uint8)
        )
    else:
        imagen_pil = Image.fromarray(
            imagen_array.astype(np.uint8)
        )
    global img_resultante
    img_resultante=imagen_array
    foto = ImageTk.PhotoImage(imagen_pil)
    imagen2_label.foto = foto
    imagen2_label.config(
        image=foto,
        text=""
    )


def convertir_YIQ_RGB(_im):
    MAT_YIQ = np.array([[0.299, 0.595716, 0.211456],
                        [0.587, -0.274453, -0.522591],
                        [0.114, -0.321263, 0.311135]])
    imagen_rgb = (_im.reshape((-1, 3)) @ np.linalg.inv(MAT_YIQ)).reshape(_im.shape)
    imagen_rgb = np.clip(imagen_rgb, 0, 1)
    return (imagen_rgb * 255).astype(np.uint8)


def convertirRGB_YIQ(rgb):
    yiq = np.zeros(rgb.shape)
    yiq[:,:,0] = 0.299*rgb[:,:,0] + 0.587*rgb[:,:,1] + 0.114*rgb[:,:,2]
    yiq[:,:,1] = 0.595716*rgb[:,:,0] - 0.274453*rgb[:,:,1] - 0.321263*rgb[:,:,2]
    yiq[:,:,2] = 0.211456*rgb[:,:,0] - 0.522591*rgb[:,:,1] + 0.311135*rgb[:,:,2]
    #yiq[:,:,3]=rgb[:,:,3]
    return yiq

def mostrar_hitograma(img ,estado):
    yiq=convertirRGB_YIQ(((np.float32(img))/255.0))
    if (estado):
        plt.figure("Hitograma de la imagen original")
    else:
        plt.figure("Hitograma de la imagen resultante")
    plt.hist(yiq[:,:,0].ravel(),bins=50)

    plt.title("Canal Y")
    plt.xlabel("Luminancia")
    plt.ylabel("Frecuencia")
    
    plt.show()

# Funciones de la interfaz
def abrir_imagen():
    file_path = filedialog.askopenfilename(
        title=f"Abrir Imagen",
        filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff"), ("Todos los archivos", "*.*")]
    )
    if file_path:
        imagen = Image.open(file_path)
        imagen.thumbnail((200, 200))
        imagen_tk = ImageTk.PhotoImage(imagen)

        imagen1_label.config(image=imagen_tk)
        imagen1_label.image = imagen_tk
        global img1
        img1 = np.array(imagen)
       
def validarImagen(img):
    if img is None:
        messagebox.showwarning(
            "Advertencia",
            "Primero debes abrir una imagen."
        )
        return False
    return True

def validarYs():
    ymin=y_min.get()
    ymax=y_max.get()
    if ymax==ymin:
        return None
    if ymin<ymax:
        Y_lineal_trozo(float(ymin),float(ymax))
    else:
        messagebox.showwarning(
                    "Advertencia",
                    "Los valores de minimo y maximo esta mal."
                )
        return False        

def operacion(event=None):    
    op = operacion_md.get()
    seccion_max_min.pack_forget()
    if op == "Raiz" and validarImagen(img1):
        Y_raizcuadrada()
    elif op == "Cuadrado" and validarImagen(img1):
        Y_cuadratica()
    elif op == "Lineal a Trozos" and validarImagen(img1):
        seccion_max_min.pack(side="right", padx=10)
        validarYs()
    elif op == "Hitograma del canal Y Original" and validarImagen(img1):
        mostrar_hitograma(img1,True)
    elif op == "Hitograma del canal Y Modificado" and validarImagen(img_resultante):
        mostrar_hitograma(img_resultante, False)
# Intefaz 
ventana = tk.Tk()
ventana.geometry("850x450")
ventana.title("TP 3 Operaciones de luminancia")

card_imagen = tk.Frame(ventana)
card_imagen.pack(side="left",fill="both",expand=True)

imagen1_label = tk.Label(card_imagen, text="Imagen 1",bg="lightgray")
imagen1_label.pack(side="top",fill="both",expand=True,pady=20,padx=10)
abrir_btn = tk.Button(card_imagen,text="Abrir imagen",command= abrir_imagen )
abrir_btn.pack(side="bottom")
card_operacion=tk.Frame(ventana)
card_operacion.pack(side="right",fill="both",expand=True)

imagen2_label = tk.Label(card_operacion, text="Imagen Resultante",bg="lightgray")
imagen2_label.pack(side="top",fill="both",expand=True,pady=20,padx=10)

seccion_operacion = tk.Frame(card_operacion)
seccion_operacion.pack(side="bottom")

operacion_label = tk.Label(seccion_operacion,text="Operacion: ")
operacion_label.pack(side="left",padx=10)

seccion_max_min=tk.Frame(seccion_operacion)


seccion_min=tk.Frame(seccion_max_min)
seccion_min.pack(side="left",padx=10)


y_min=tk.DoubleVar()
label_min=tk.Label(seccion_min,text="Valor minimo de Y")
label_min.pack(side="top")
valor_minimo = tk.Scale(seccion_min,from_=0.0, to=1.0,resolution=0.1,variable=y_min,orient="horizontal")
valor_minimo.pack(side="bottom",)

seccion_max=tk.Frame(seccion_max_min)
seccion_max.pack(side="left",padx=10)

y_max=tk.DoubleVar()
label_max=tk.Label(seccion_max,text="Valor maximo de Y")
label_max.pack(side="top")
valor_maximo = tk.Scale(seccion_max,from_=0.0, to=1.0,resolution=0.1,variable=y_max,orient="horizontal")
valor_maximo.pack(side="bottom",padx=10)

calcular_bt=tk.Button(seccion_max_min,text="Calcular",command=validarYs)
calcular_bt.pack(side="right",padx=10)


valores_operaciones = ["Raiz", "Cuadrado", "Lineal a Trozos","Hitograma del canal Y Original","Hitograma del canal Y Modificado"]
operacion_md=ttk.Combobox(seccion_operacion,values=valores_operaciones,state="readonly")
operacion_md.pack(side="left",padx=10)
operacion_md.set("...")
operacion_md.bind("<<ComboboxSelected>>", operacion )



ventana.mainloop()