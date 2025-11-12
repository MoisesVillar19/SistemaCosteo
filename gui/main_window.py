# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from gui.views import import_view, costeo_view, reports_view, dashboard_view


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Costeo y Dashboard")
        self.geometry("1100x650")

        # Variables globales
        self.path_maestro = None
        self.path_kardex = None
        self.dataframes = {}  # Aquí se guardarán todos los DataFrames generados

        # Crear las pestañas principales
        self.tab_control = ttk.Notebook(self)
        self.tab_import = ttk.Frame(self.tab_control)
        self.tab_costeo = ttk.Frame(self.tab_control)
        self.tab_reports = ttk.Frame(self.tab_control)
        self.tab_dashboard = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab_import, text="📂 Importar")
        self.tab_control.add(self.tab_costeo, text="⚙️ Costeo")
        self.tab_control.add(self.tab_reports, text="📊 Reportes")
        self.tab_control.add(self.tab_dashboard, text="📈 Dashboard")
        self.tab_control.pack(expand=1, fill="both")

        # Inicializar pestañas
        self._init_import_tab()
        self._init_costeo_tab()
        self._init_reports_tab()
        self._init_dashboard_tab()

    # ---------------------- IMPORTAR ----------------------
    def _init_import_tab(self):
        btn_select = tk.Button(
            self.tab_import, text="Seleccionar Archivos", font=("Arial", 12),
            command=self.seleccionar_archivos, width=25, height=2
        )
        btn_select.pack(pady=40)

    def seleccionar_archivos(self):
        self.path_maestro, self.path_kardex = import_view.seleccionar_archivos()
        if self.path_maestro and self.path_kardex:
            # Extraer nombre del archivo maestro sin extensión
            import os
            nombre_archivo = os.path.splitext(os.path.basename(self.path_maestro))[0]

            # Actualizar la entrada de empresa
            self.entry_empresa.delete(0, tk.END)
            self.entry_empresa.insert(0, nombre_archivo)

            messagebox.showinfo("Archivos Seleccionados", "Maestro y Kardex seleccionados correctamente.")

    # ---------------------- COSTEO ----------------------
    def _init_costeo_tab(self):
        frame = tk.Frame(self.tab_costeo)
        frame.pack(pady=20)

        tk.Label(frame, text="Empresa:").grid(row=0, column=0)
        self.entry_empresa = tk.Entry(frame)
        self.entry_empresa.grid(row=0, column=1)
        self.entry_empresa.insert(0, "empresa1")

        tk.Label(frame, text="Año:").grid(row=1, column=0)
        self.entry_anno = tk.Entry(frame)
        self.entry_anno.grid(row=1, column=1)
        self.entry_anno.insert(0, "2025")

        tk.Label(frame, text="Meses (1,2,3 o 'anual'):").grid(row=2, column=0)
        self.entry_meses = tk.Entry(frame)
        self.entry_meses.grid(row=2, column=1)
        self.entry_meses.insert(0, "1,2,3")  # valor por defecto


        btn_run = tk.Button(
            frame, text="Ejecutar Costeo y Generar Reportes",
            command=self.ejecutar_costeo, bg="#007acc", fg="white",
            font=("Arial", 10), width=35, height=2
        )
        btn_run.grid(row=3, column=0, columnspan=2, pady=15)

    def ejecutar_costeo(self):
        if not self.path_maestro or not self.path_kardex:
            messagebox.showerror("Error", "Primero selecciona los archivos en la pestaña Importar")
            return

        empresa = self.entry_empresa.get()
        anno = int(self.entry_anno.get())
        # Convertir entrada de meses, acepta 'anual' o lista separada por comas
        entrada = self.entry_meses.get().strip().lower()
        if entrada == "anual":
            meses = list(range(1, 13))
        else:
            meses = list(map(int, entrada.split(",")))


        # Ejecutar proceso principal
        archivo_salida, dfs = costeo_view.ejecutar_costeo(self.path_maestro, self.path_kardex, empresa, anno, meses)

        if archivo_salida:
            self.dataframes = dfs
            messagebox.showinfo(
            "✅ Éxito",
            f"Archivo Excel generado:\n{archivo_salida}\n\n"
            "Puedes revisar los reportes y gráficos en sus pestañas."
        )

        # Limpiar frames previos
        for frame in (self.frame_reports, self.frame_dashboard):
            for widget in frame.winfo_children():
                widget.destroy()

         # Mostrar reportes individuales
        if "Consolidado" in dfs:
            reports_view.mostrar_reporte(self.frame_reports, dfs["Consolidado"], "Consolidado")

        # Mostrar dashboard completo (todos los reportes + análisis de relevancia)
        dashboard_view.mostrar_dashboard_completo(self.frame_dashboard, dfs)


    # ----------------- Mostrar Reportes -----------------
        if "Consolidado" in dfs:
            reports_view.mostrar_reporte(self.frame_reports, dfs["Consolidado"], "Consolidado")

    # ----------------- Mostrar Dashboard Completo -----------------
    # Aquí se muestran automáticamente:
    # Gastos, Margen, Analisis de Relevancia, Comparativo, EstadoResultados, KPIs
        dashboard_view.mostrar_dashboard_completo(self.frame_dashboard, dfs)


    # ---------------------- REPORTES ----------------------
    def _init_reports_tab(self):
        self.frame_reports = tk.Frame(self.tab_reports)
        self.frame_reports.pack(fill="both", expand=True)

        # Menú de selección de reporte
        menu_frame = tk.Frame(self.tab_reports)
        menu_frame.pack(pady=10)

        tk.Label(menu_frame, text="Seleccionar Reporte:", font=("Arial", 11, "bold")).pack(side="left", padx=5)

        opciones = [
            "Consolidado", "Hoja de Costeo", "Analisis Gastos",
            "Comparativo Periodos", "Estado Resultados", "KPIs", "Margen Utilidad"
        ]
        self.reporte_var = tk.StringVar(value=opciones[0])
        menu = ttk.Combobox(menu_frame, textvariable=self.reporte_var, values=opciones, width=25, state="readonly")
        menu.pack(side="left", padx=10)

        btn_ver = tk.Button(menu_frame, text="Mostrar", command=self.mostrar_reporte)
        btn_ver.pack(side="left", padx=10)

    def mostrar_reporte(self):
        reporte = self.reporte_var.get()
        if reporte in self.dataframes:
            reports_view.mostrar_reporte(self.frame_reports, self.dataframes[reporte], reporte)
        else:
            messagebox.showwarning("Aviso", f"No se encontró el DataFrame para '{reporte}'.")

    # ---------------------- DASHBOARD ----------------------
    def _init_dashboard_tab(self):
        self.frame_dashboard = tk.Frame(self.tab_dashboard)
        self.frame_dashboard.pack(fill="both", expand=True)

        # Menú de selección de gráfico
        menu_frame = tk.Frame(self.tab_dashboard)
        menu_frame.pack(pady=10)

        tk.Label(menu_frame, text="Seleccionar Gráfico:", font=("Arial", 11, "bold")).pack(side="left", padx=5)

        opciones = ["Gastos", "Margen", "KPIs"]
        self.grafico_var = tk.StringVar(value=opciones[0])
        menu = ttk.Combobox(menu_frame, textvariable=self.grafico_var, values=opciones, width=25, state="readonly")
        menu.pack(side="left", padx=10)

        btn_ver = tk.Button(menu_frame, text="Mostrar", command=self.mostrar_dashboard)
        btn_ver.pack(side="left", padx=10)

    def mostrar_dashboard(self):
        grafico = self.grafico_var.get()

        if grafico == "Gastos" and "Gastos" in self.dataframes:
            dashboard_view.mostrar_grafico_gastos(self.frame_dashboard, self.dataframes["Gastos"])
        elif grafico == "Margen" and "Margen" in self.dataframes:
            dashboard_view.mostrar_grafico_margen(self.frame_dashboard, self.dataframes["Margen"])
        elif grafico == "KPIs" and "KPIs" in self.dataframes:
            dashboard_view.mostrar_grafico_kpis(self.frame_dashboard, self.dataframes["KPIs"])
        else:
            messagebox.showwarning("Aviso", f"No hay datos para el gráfico '{grafico}'.")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
