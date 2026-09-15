import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt

img1 = None
img2 = None

def cuasi_suma_RGB_Clampeada(A,B):
    print("A.shape: ", A.shape)
    print("B.shape: ", B.shape)
    #Comprobar si son de la mismsa dimensión
    if A.shape != B.shape:
        messagebox.showerror(
            "Error",
            f"Las imágenes no son de la misma dimensión.\n\n"
        )
        return None
    resultado = A + B
    resultado = np.clip(resultado, 0, 255)
    mostrar_imagen_resultado(resultado)
    

def cuasi_suma_RGB_Promedio(A,B):
    if A.shape != B.shape:
        messagebox.showerror(
            "Error",
            f"Las imágenes no son de la misma dimensión.\n\n"
        )
        return None
    resultado = ((A + B).astype(np.float64))/2
    resultado = resultado.astype(np.uint8)
    mostrar_imagen_resultado(resultado) 

def convertirRGB_YIQ(rgb):
    matriz_conversion_RGB_a_YIQ = np.array([
            [0.299,  0.587,  0.114],
            [0.596, -0.274, -0.322],
            [0.211, -0.523,  0.312]
        ])
    imagen_rgb = rgb.astype(np.float64) / 255.0
    return (imagen_rgb @ matriz_conversion_RGB_a_YIQ.T)


     #Revisar la division 0/0
def cuasi_suma_YIQ_clampeada(A,B):
    if A.shape != B.shape:
        messagebox.showerror(
            "Error",
            f"Las imagenes no son de la misma dimensión.\n\n"
        )
        return None
    C_YIQ=np.zeros(A.shape)
    A_YIQ=convertirRGB_YIQ(A)
    B_YIQ=convertirRGB_YIQ(B)
    C_YIQ[:,:,0]=np.clip(A_YIQ[:,:,0]+B_YIQ[:,:,0],0,1)
    C_YIQ[:,:,1]=(A_YIQ[:,:,0]*A_YIQ[:,:,1]+B_YIQ[:,:,0]*B_YIQ[:,:,1])/(A_YIQ[:,:,0]+B_YIQ[:,:,0])
    C_YIQ[:,:,2]=(A_YIQ[:,:,0]*A_YIQ[:,:,2]+B_YIQ[:,:,0]*B_YIQ[:,:,2])/(A_YIQ[:,:,0]+B_YIQ[:,:,0])

    mostrar_imagen_resultado(convertir_YIQ_RGB(C_YIQ))


def cuasi_suma_YIQ_promedio(A,B):
    if A.shape != B.shape:
        messagebox.showerror(
            "Error",
            f"Las imagenes no son de la misma dimensión.\n\n"
        )
        return None
    C_YIQ=np.zeros(A.shape)
    A_YIQ=convertirRGB_YIQ(A)
    B_YIQ=convertirRGB_YIQ(B)
    C_YIQ[:,:,0]=(A_YIQ[:,:,0]+B_YIQ[:,:,0])/2
    C_YIQ[:,:,1]=(A_YIQ[:,:,0]*A_YIQ[:,:,1]+B_YIQ[:,:,0]*B_YIQ[:,:,1])/(A_YIQ[:,:,0]+B_YIQ[:,:,0])
    C_YIQ[:,:,2]=(A_YIQ[:,:,0]*A_YIQ[:,:,2]+B_YIQ[:,:,0]*B_YIQ[:,:,2])/(A_YIQ[:,:,0]+B_YIQ[:,:,0])
    mostrar_imagen_resultado(convertir_YIQ_RGB(C_YIQ))
    
def cuasi_suma_YIQ_if_ligther(A,B):
    if A.shape != B.shape:
        messagebox.showerror(
            "Error",
            f"Las imagenes no son de la misma dimensión.\n\n"
        )
        return None
    A_YIQ=convertirRGB_YIQ(A)
    B_YIQ=convertirRGB_YIQ(B)
    C_YIQ = np.maximum(A_YIQ, B_YIQ)    
    mostrar_imagen_resultado(convertir_YIQ_RGB(C_YIQ))

def cuasi_suma_YIQ_if_darker(A,B):
    if A.shape != B.shape:
        messagebox.showerror(
            "Error",
            f"Las imagenes no son de la misma dimensión.\n\n"
        )
        return None
    A_YIQ=convertirRGB_YIQ(A)
    B_YIQ=convertirRGB_YIQ(B)
    C_YIQ=np.minimum(A_YIQ,B_YIQ)
    mostrar_imagen_resultado(convertir_YIQ_RGB(C_YIQ))    

# Funciones de restar dos imagenes
def restar_RGB_absoluta(A,B):
    if A.shape != B.shape:
        messagebox.showerror(
            "Error",
            f"Las imagenes no son de la misma dimensión.\n\n"
        )
        return None
    a=A.astype(np.float64)
    b=B.astype(np.float64)
    resultado = np.abs(a-b)
    resultado = np.uint8(resultado)
    mostrar_imagen_resultado(resultado)

# Funciones de producto entre imagenes
def producto_RGB(A,B):
    if A.shape != B.shape:
            messagebox.showerror(
                "Error",
                f"Las imagenes no son de la misma dimensión.\n\n"
            )
            return None
    A_norm = np.float32(A) / 255.0
    B_norm = np.float32(B) / 255.0

    resultado = (A_norm * B_norm) * 255.0

    resultado = np.uint8(resultado)

    mostrar_imagen_resultado(resultado)

# Funcion de de la interfaz

def operacion(event):
    seleccion = opcion_op.get()
    if seleccion == "Suma":
        formato = ["RGB Clampeada", "RGB Promedio", "YIQ Clampeada", "YIQ Promedio", "YIQ If Ligther", "YIQ If Darker"]
    if seleccion == "Resta":
        formato = ["RGB Absoluta"]
    if seleccion == "Producto":
        formato = ["RGB"]    
    opcion_formato['values'] = formato
    opcion_formato.set("...")




def realizar_operacion():
    seleccion_fo = opcion_formato.get()
    if seleccion_fo == "RGB Clampeada":
         cuasi_suma_RGB_Clampeada(img1, img2)
    elif seleccion_fo == "RGB Promedio":
         cuasi_suma_RGB_Promedio(img1, img2)
    elif seleccion_fo == "YIQ Clampeada":
         cuasi_suma_YIQ_clampeada(img1, img2)
    elif seleccion_fo == "YIQ Promedio":
         cuasi_suma_YIQ_promedio(img1, img2)
    elif seleccion_fo == "YIQ If Ligther":
         cuasi_suma_YIQ_if_ligther(img1, img2)
    elif seleccion_fo == "YIQ If Darker":
         cuasi_suma_YIQ_if_darker(img1,img2)
    elif seleccion_fo == "RGB Absoluta":
         restar_RGB_absoluta(img1, img2)
    elif seleccion_fo == "RGB":
         producto_RGB(img1, img2)

def convertir_YIQ_RGB(yiq):
    matriz_conversion_YIQ_a_RGB = np.array([
        [1.0,  0.956,  0.621],
        [1.0, -0.272, -0.647],
        [1.0, -1.106,  1.703]
    ])
    imagen_rgb = yiq @ matriz_conversion_YIQ_a_RGB.T
    imagen_rgb = np.clip(imagen_rgb, 0, 1)
    return (imagen_rgb * 255).astype(np.uint8)

def mostrar_imagen_resultado(resultado):
    if resultado is not None:
        if resultado.dtype == np.float64:
            resultado = (resultado * 255).astype(np.uint8)
        imagen_resultado = Image.fromarray(resultado)
        imagen_resultado.thumbnail((200, 200))
        imagen_tk = ImageTk.PhotoImage(imagen_resultado)
        imagen3_label.config(image=imagen_tk)
        imagen3_label.image = imagen_tk

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
Operaciones=["Suma","Resta","Producto"]
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
intercambiar_btn.pack(side="right", padx=5, pady=5)


windows.mainloop()