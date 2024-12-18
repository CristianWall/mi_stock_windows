import tkinter as tk
from tkinter import ttk, messagebox
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from PIL import Image, ImageTk
from io import BytesIO

# Configuración de Firebase
try:
    # Inicializar Firebase solo si no está ya inicializado
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate("./credencial.json")
    firebase_admin.initialize_app(cred)

# Cliente de Firestore
db = firestore.client()

class VentanaListaProductos:
    def __init__(self, master=None):
        # Ventana principal
        self.ventana = tk.Toplevel(master)
        self.ventana.title("Tienda Virtual")
        self.ventana.geometry("800x600")

        # Título
        titulo = tk.Label(self.ventana, text="Nuestros Productos", font=('Arial', 20, 'bold'))
        titulo.pack(pady=20)

        # Frame para contener la lista y detalles
        self.frame_principal = tk.Frame(self.ventana)
        self.frame_principal.pack(padx=10, pady=10, fill='both', expand=True)

        # Frame para la lista de productos
        self.frame_lista = tk.Frame(self.frame_principal)
        self.frame_lista.pack(side='left', fill='both', expand=True)

        # Crear Treeview para mostrar lista
        columnas = ('ID', 'Nombre', 'Precio', 'Stock', 'Categoría')
        self.tabla = ttk.Treeview(self.frame_lista, columns=columnas, show='headings')

        # Configurar encabezados
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100, anchor='center')

        self.tabla.pack(padx=10, pady=10, fill='both', expand=True)

        # Botón de actualización
        self.boton_actualizar = tk.Button(self.ventana, text="Actualizar", command=self.cargar_productos)
        self.boton_actualizar.pack(pady=10)

        # Frame para detalles del producto
        self.frame_detalles = tk.Frame(self.frame_principal, width=300)
        self.frame_detalles.pack(side='right', fill='y', padx=10)

        # Etiqueta para mostrar imagen
        self.imagen_label = tk.Label(self.frame_detalles)
        self.imagen_label.pack(pady=10)

        # Etiquetas para mostrar detalles
        self.detalle_nombre = tk.Label(self.frame_detalles, font=('Arial', 14, 'bold'))
        self.detalle_nombre.pack(pady=5)

        self.detalle_precio = tk.Label(self.frame_detalles, font=('Arial', 12))
        self.detalle_precio.pack(pady=5)

        self.detalle_stock = tk.Label(self.frame_detalles, font=('Arial', 12))
        self.detalle_stock.pack(pady=5)

        self.detalle_categoria = tk.Label(self.frame_detalles, font=('Arial', 12))
        self.detalle_categoria.pack(pady=5)

        # Botones de Editar y Eliminar
        self.boton_editar = tk.Button(self.frame_detalles, text="Editar", command=self.editar_producto)
        self.boton_editar.pack(pady=10)

        self.boton_eliminar = tk.Button(self.frame_detalles, text="Eliminar", command=self.eliminar_producto)
        self.boton_eliminar.pack(pady=10)

        # Enlazar evento de selección
        self.tabla.bind('<<TreeviewSelect>>', self.mostrar_detalles)

        # Cargar productos
        self.cargar_productos()

    def cargar_productos(self):
        """Cargar productos desde Firestore"""
        # Limpiar tabla
        for i in self.tabla.get_children():
            self.tabla.delete(i)

        # Obtener productos
        productos_ref = db.collection('productos')
        productos = productos_ref.stream()

        # Insertar productos en la tabla
        for producto in productos:
            datos = producto.to_dict()

            # Insertar los productos en la tabla
            self.tabla.insert('', 'end', values=( 
                datos.get('id_producto', ''), 
                datos.get('nombre', ''), 
                f"${datos.get('precio', 0):.2f}", 
                datos.get('stock', 0), 
                datos.get('categoria', '') 
            ), tags=(datos.get('id_producto', ''),))

    def mostrar_detalles(self, event):
        """Mostrar detalles del producto seleccionado"""
        # Obtener selección
        seleccion = self.tabla.selection()
        if not seleccion:
            return

        # Obtener ID del producto
        self.id_producto = self.tabla.item(seleccion[0])['tags'][0]

        # Convertir ID de producto a cadena
        self.id_producto = str(self.id_producto)

        # Buscar producto en Firestore
        producto_ref = db.collection('productos').document(self.id_producto).get()
        if not producto_ref.exists:
            return

        datos = producto_ref.to_dict()

        # Actualizar detalles
        self.detalle_nombre.config(text=datos.get('nombre', ''))
        self.detalle_precio.config(text=f"Precio: ${datos.get('precio', 0):.2f}")
        self.detalle_stock.config(text=f"Stock: {datos.get('stock', 0)}")
        self.detalle_categoria.config(text=f"Categoría: {datos.get('categoria', '')}")

        # Mostrar imagen de forma progresiva
        try:
            # Descargar imagen solo si el usuario selecciona un producto
            url_imagen = datos.get('url_imagen', '')
            if url_imagen:
                response = requests.get(url_imagen)
                img = Image.open(BytesIO(response.content))

                # Redimensionar imagen
                img = img.resize((250, 250), Image.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)

                # Mostrar imagen
                self.imagen_label.config(image=img_tk)
                self.imagen_label.image = img_tk
            else:
                self.imagen_label.config(image='', text="Imagen no disponible")
        except Exception as e:
            print(f"Error al cargar imagen: {e}")
            self.imagen_label.config(image='', text="Imagen no disponible")

    def editar_producto(self):
        """Función para editar un producto"""
        if not hasattr(self, 'id_producto'):
            messagebox.showerror("Error", "Selecciona un producto para editar.")
            return
        
        # Abre una ventana para editar
        self.ventana_editar = tk.Toplevel(self.ventana)
        self.ventana_editar.title("Editar Producto")
        
        # Cargar datos actuales del producto
        producto_ref = db.collection('productos').document(self.id_producto).get()
        if not producto_ref.exists:
            messagebox.showerror("Error", "Producto no encontrado.")
            return
        datos = producto_ref.to_dict()

        # Crear campos de edición
        self.nombre_label = tk.Label(self.ventana_editar, text="Nombre")
        self.nombre_label.pack(pady=5)
        self.nombre_entry = tk.Entry(self.ventana_editar)
        self.nombre_entry.insert(0, datos.get('nombre', ''))
        self.nombre_entry.pack(pady=10)

        self.precio_label = tk.Label(self.ventana_editar, text="Precio")
        self.precio_label.pack(pady=5)
        self.precio_entry = tk.Entry(self.ventana_editar)
        self.precio_entry.insert(0, str(datos.get('precio', '')))
        self.precio_entry.pack(pady=10)

        self.stock_label = tk.Label(self.ventana_editar, text="Stock")
        self.stock_label.pack(pady=5)
        self.stock_entry = tk.Entry(self.ventana_editar)
        self.stock_entry.insert(0, str(datos.get('stock', '')))
        self.stock_entry.pack(pady=10)

        self.categoria_label = tk.Label(self.ventana_editar, text="Categoría")
        self.categoria_label.pack(pady=5)
        self.categoria_entry = tk.Entry(self.ventana_editar)
        self.categoria_entry.insert(0, datos.get('categoria', ''))
        self.categoria_entry.pack(pady=10)

        # Botón para guardar cambios
        self.boton_guardar = tk.Button(self.ventana_editar, text="Guardar cambios", command=self.guardar_edicion)
        self.boton_guardar.pack(pady=10)

    def guardar_edicion(self):
        """Guardar cambios del producto"""
        nombre = self.nombre_entry.get()
        precio = float(self.precio_entry.get())
        stock = int(self.stock_entry.get())
        categoria = self.categoria_entry.get()

        # Actualizar el documento en Firestore
        db.collection('productos').document(self.id_producto).update({
            'nombre': nombre,
            'precio': precio,
            'stock': stock,
            'categoria': categoria
        })

        messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
        self.ventana_editar.destroy()
        self.cargar_productos()

    def eliminar_producto(self):
        """Eliminar un producto"""
        if not hasattr(self, 'id_producto'):
            messagebox.showerror("Error", "Selecciona un producto para eliminar.")
            return

        # Confirmar eliminación
        confirmacion = messagebox.askyesno("Confirmación", "¿Estás seguro de que quieres eliminar este producto?")
        if confirmacion:
            # Eliminar producto de Firestore
            db.collection('productos').document(self.id_producto).delete()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
            self.cargar_productos()

# Función principal para abrir la ventana
def abrir_ventana_lista():
    ventana_lista = VentanaListaProductos()
    ventana_lista.ventana.mainloop()

# Llamar la función para abrir la ventana
abrir_ventana_lista()
