import tkinter as tk
from tkinter import ttk, messagebox
import registro
import lista
import venta  # Importamos el nuevo módulo de venta

class MenuPrincipal:
    def __init__(self, root):
        # Configuración de la ventana principal
        self.root = root
        self.root.title("Sistema de Gestión")
        self.root.geometry("800x600")

        # Crear barra de menú
        self.barra_menu = tk.Menu(root)
        root.config(menu=self.barra_menu)

        # Menú Archivo
        self.menu_archivo = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Archivo", menu=self.menu_archivo)
        self.menu_archivo.add_command(label="Salir", command=root.quit)

        # Menú Registro
        self.menu_registro = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Registro", menu=self.menu_registro)
        self.menu_registro.add_command(label="Abrir Registro", command=self.abrir_registro)

        # Menú Lista
        self.menu_lista = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Lista", menu=self.menu_lista)
        self.menu_lista.add_command(label="Abrir Lista", command=self.abrir_lista)

        # Menú Venta
        self.menu_venta = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Venta", menu=self.menu_venta)
        self.menu_venta.add_command(label="Abrir Venta", command=self.abrir_venta)

        # Menú Ayuda
        self.menu_ayuda = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Ayuda", menu=self.menu_ayuda)
        self.menu_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)

        # Área de contenido
        self.contenido = tk.Frame(root, bg='white')
        self.contenido.pack(fill=tk.BOTH, expand=True)

        # Etiqueta de bienvenida
        bienvenida = tk.Label(
            self.contenido, 
            text="Bienvenido al Sistema de Gestión", 
            font=('Arial', 14), 
            bg='white'
        )
        bienvenida.pack(expand=True)

    def abrir_registro(self):
        """Abrir la ventana de Registro"""
        try:
            registro.abrir_ventana_registro()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la ventana de Registro: {e}")

    def abrir_lista(self):
        """Abrir la ventana de Lista"""
        try:
            lista.abrir_ventana_lista()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la ventana de Lista: {e}")

    def abrir_venta(self):
        """Abrir la ventana de Venta"""
        try:
            venta.abrir_ventana_venta()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la ventana de Venta: {e}")

    def mostrar_acerca_de(self):
        """Mostrar información sobre la aplicación"""
        messagebox.showinfo("Acerca de", "Sistema de Gestión\nVersión 1.0\nDesarrollado con Tkinter")

def main():
    root = tk.Tk()
    app = MenuPrincipal(root)
    root.mainloop()

if __name__ == "__main__":
    main()