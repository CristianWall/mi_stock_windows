import tkinter as tk
from tkinter import messagebox, filedialog
from uuid import uuid4
from PIL import Image, ImageTk
import random
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Configuración de Firebase
try:
    # Inicializar Firebase solo si no está ya inicializado
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate("./credencial.json")
    firebase_admin.initialize_app(cred, {'storageBucket': 'ecsaapp4.appspot.com'})

# Referencias de Firestore y Storage
db = firestore.client()
bucket = storage.bucket()

class VentanaRegistro(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Registrar Producto")
        self.geometry("500x600")
        self.configure(bg="#f7f7f7")
        self.imagen_path = None

        self.crear_interfaz()

    def crear_interfaz(self):
        # Título
        titulo = tk.Label(self, text="Registrar Producto", 
                          font=("Arial", 20, "bold"), 
                          bg="#f7f7f7")
        titulo.pack(pady=20)

        # Nombre del Producto
        tk.Label(self, text="Nombre del Producto", font=("Arial", 12), bg="#f7f7f7").pack()
        self.nombre_entry = tk.Entry(self, font=("Arial", 12), width=40)
        self.nombre_entry.pack(pady=5)

        # Precio del Producto
        tk.Label(self, text="Precio del Producto", font=("Arial", 12), bg="#f7f7f7").pack()
        self.precio_entry = tk.Entry(self, font=("Arial", 12), width=40)
        self.precio_entry.pack(pady=5)

        # Stock del Producto
        tk.Label(self, text="Cantidad en Stock", font=("Arial", 12), bg="#f7f7f7").pack()
        self.stock_entry = tk.Entry(self, font=("Arial", 12), width=40)
        self.stock_entry.pack(pady=5)

        # Categoría del Producto
        tk.Label(self, text="Categoría", font=("Arial", 12), bg="#f7f7f7").pack()
        self.categoria_var = tk.StringVar(self)
        categorias = ["Electrónica", "Ropa", "Alimentos", "Otros"]
        self.categoria_menu = tk.OptionMenu(self, self.categoria_var, *categorias)
        self.categoria_menu.config(width=35)
        self.categoria_menu.pack(pady=5)

        # Imagen del Producto
        self.imagen_label = tk.Label(self, text="No se ha seleccionado imagen", 
                                     font=("Arial", 12), 
                                     bg="#f7f7f7")
        self.imagen_label.pack(pady=10)

        # Botón para seleccionar imagen
        btn_imagen = tk.Button(self, text="Seleccionar Imagen", 
                               command=self.seleccionar_imagen,
                               bg="#007BFF", 
                               fg="white")
        btn_imagen.pack(pady=5)

        # Botón para registrar
        btn_registrar = tk.Button(self, text="Registrar Producto", 
                                  command=self.guardar_producto,
                                  bg="#4CAF50", 
                                  fg="white")
        btn_registrar.pack(pady=20)

    def seleccionar_imagen(self):
        """Seleccionar y previsualizar imagen"""
        ruta_imagen = filedialog.askopenfilename(
            title="Selecciona una foto", 
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        
        if ruta_imagen:
            self.imagen_path = ruta_imagen
            img = Image.open(ruta_imagen)
            img = img.resize((150, 150), Image.LANCZOS)  # Redimensionar imagen
            img_tk = ImageTk.PhotoImage(img)
            self.imagen_label.config(image=img_tk, text="")
            self.imagen_label.image = img_tk

    def guardar_producto(self):
        """Guardar producto en Firebase"""
        # Validar campos
        nombre = self.nombre_entry.get().strip()
        precio = self.precio_entry.get().strip()
        stock = self.stock_entry.get().strip()
        categoria = self.categoria_var.get()

        # Validaciones
        if not nombre or not precio or not stock or not categoria:
            messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")
            return

        try:
            # Convertir precio y stock a números
            precio = float(precio)
            stock = int(stock)
        except ValueError:
            messagebox.showwarning("Error", "Precio y stock deben ser números válidos.")
            return

        # Generar ID único de 6 dígitos para el producto
        id_producto = str(random.randint(100000, 999999))

        # Verificar si se seleccionó imagen
        if not self.imagen_path:
            messagebox.showwarning("Advertencia", "Por favor selecciona una imagen.")
            return

        # Subir imagen a Firebase Storage
        url_imagen = self.subir_imagen(self.imagen_path, id_producto)

        # Guardar en Firestore
        producto_ref = db.collection('productos').document(id_producto)
        producto_ref.set({
            'nombre': nombre,
            'precio': precio,
            'stock': stock,
            'categoria': categoria,
            'url_imagen': url_imagen,
            'id_producto': id_producto
        })

        # Mensaje de éxito
        messagebox.showinfo("Éxito", f"Producto registrado con éxito\nID: {id_producto}")
        
        # Limpiar formulario
        self.limpiar_formulario()

    def subir_imagen(self, ruta_imagen, id_producto):
        """Subir imagen a Firebase Storage"""
        blob = bucket.blob(f'productos/{id_producto}.jpg')
        with open(ruta_imagen, 'rb') as img_file:
            blob.upload_from_file(img_file)
        
        # Hacer la imagen públicamente accesible
        blob.make_public()
        return blob.public_url

    def limpiar_formulario(self):
        """Limpiar todos los campos del formulario"""
        self.nombre_entry.delete(0, tk.END)
        self.precio_entry.delete(0, tk.END)
        self.stock_entry.delete(0, tk.END)
        self.categoria_var.set("")
        self.imagen_label.config(image='', text="No se ha seleccionado imagen")
        self.imagen_path = None

def abrir_ventana_registro():
    """Función para abrir la ventana de registro desde otro módulo"""
    VentanaRegistro()

if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    VentanaRegistro()
    root.mainloop()
