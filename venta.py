import tkinter as tk
from tkinter import ttk, messagebox
import firebase_admin
from firebase_admin import credentials, firestore

# Configuración de Firebase
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate("./credencial.json")
    firebase_admin.initialize_app(cred)

# Referencia a Firestore
db = firestore.client()

def abrir_ventana_venta():
    """Crear y mostrar la ventana de Venta"""
    ventana_venta = tk.Toplevel()
    ventana_venta.title("Ventas")
    ventana_venta.geometry("500x400")
    ventana_venta.configure(bg="#f7f7f7")

    # Título de la ventana
    titulo = tk.Label(
        ventana_venta, 
        text="Registro de Ventas", 
        font=("Arial", 16, "bold"),
        bg="#f7f7f7"
    )
    titulo.pack(pady=20)

    # Marco para los campos de venta
    marco_venta = tk.Frame(ventana_venta, bg="#f7f7f7")
    marco_venta.pack(padx=20, pady=10, fill=tk.X)

    # Campo para ingresar el ID del producto
    tk.Label(marco_venta, text="ID del Producto:", font=("Arial", 12), bg="#f7f7f7").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    id_producto_entry = tk.Entry(marco_venta, font=("Arial", 12), width=30)
    id_producto_entry.grid(row=0, column=1, padx=5, pady=5)

    # Botón para buscar el producto
    def buscar_producto():
        id_producto = id_producto_entry.get().strip()
        if not id_producto:
            messagebox.showwarning("Advertencia", "Por favor, ingresa un ID de producto.")
            return

        # Buscar producto en Firestore
        producto_ref = db.collection("productos").document(id_producto)
        producto = producto_ref.get()

        if producto.exists:
            datos_producto = producto.to_dict()
            nombre_producto.set(datos_producto["nombre"])
            precio_producto.set(datos_producto["precio"])
            stock_disponible.set(datos_producto["stock"])
        else:
            messagebox.showerror("Error", f"No se encontró un producto con ID: {id_producto}")

    btn_buscar = tk.Button(marco_venta, text="Buscar Producto", font=("Arial", 12), bg="#007BFF", fg="white", command=buscar_producto)
    btn_buscar.grid(row=0, column=2, padx=5, pady=5)

    # Información del producto
    nombre_producto = tk.StringVar()
    precio_producto = tk.DoubleVar()
    stock_disponible = tk.IntVar()

    tk.Label(marco_venta, text="Nombre:", font=("Arial", 12), bg="#f7f7f7").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    tk.Label(marco_venta, textvariable=nombre_producto, font=("Arial", 12), bg="#f7f7f7").grid(row=1, column=1, sticky="w", padx=5, pady=5)

    tk.Label(marco_venta, text="Precio Unitario:", font=("Arial", 12), bg="#f7f7f7").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    tk.Label(marco_venta, textvariable=precio_producto, font=("Arial", 12), bg="#f7f7f7").grid(row=2, column=1, sticky="w", padx=5, pady=5)

    tk.Label(marco_venta, text="Stock Disponible:", font=("Arial", 12), bg="#f7f7f7").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    tk.Label(marco_venta, textvariable=stock_disponible, font=("Arial", 12), bg="#f7f7f7").grid(row=3, column=1, sticky="w", padx=5, pady=5)

    # Campo para ingresar la cantidad a comprar
    tk.Label(marco_venta, text="Cantidad a Comprar:", font=("Arial", 12), bg="#f7f7f7").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    cantidad_entry = tk.Entry(marco_venta, font=("Arial", 12), width=30)
    cantidad_entry.grid(row=4, column=1, padx=5, pady=5)

    # Botón para realizar la compra
    def realizar_compra():
        try:
            cantidad_comprar = int(cantidad_entry.get().strip())
        except ValueError:
            messagebox.showwarning("Error", "Por favor, ingresa una cantidad válida.")
            return

        stock_actual = stock_disponible.get()
        if cantidad_comprar > stock_actual:
            messagebox.showerror("Error", "No hay suficiente stock disponible.")
            return

        # Actualizar stock en Firestore
        nuevo_stock = stock_actual - cantidad_comprar
        id_producto = id_producto_entry.get().strip()

        db.collection("productos").document(id_producto).update({"stock": nuevo_stock})

        # Confirmación de compra
        messagebox.showinfo(
            "Compra Exitosa",
            f"Se compraron {cantidad_comprar} unidades de {nombre_producto.get()}.\nStock restante: {nuevo_stock}"
        )
        
        # Limpiar campos del formulario y reiniciar variables
        id_producto_entry.delete(0, tk.END)
        cantidad_entry.delete(0, tk.END)
        nombre_producto.set("")
        precio_producto.set(0.0)
        stock_disponible.set(0)


    btn_comprar = tk.Button(ventana_venta, text="Realizar Compra", font=("Arial", 12), bg="#4CAF50", fg="white", command=realizar_compra)
    btn_comprar.pack(pady=20)

# Si se ejecuta directamente este script
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    abrir_ventana_venta()
    root.mainloop()
