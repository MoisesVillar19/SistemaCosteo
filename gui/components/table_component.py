# gui/components/table_component.py
import tkinter as tk
from tkinter import ttk
import pandas as pd

class Table(tk.Frame):
    def __init__(self, parent, dataframe: pd.DataFrame, titulo="Tabla", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.df = dataframe
        self.titulo = titulo
        self._build_table()

    def _build_table(self):
        # Título
        lbl = tk.Label(self, text=self.titulo, font=("Arial", 12, "bold"))
        lbl.pack(side="top", pady=5)

        # Treeview
        self.tree = ttk.Treeview(self, show='headings')
        self.tree.pack(fill="both", expand=True)

        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        # Columnas
        self.tree["columns"] = list(self.df.columns)
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        # Filas
        for _, row in self.df.iterrows():
            self.tree.insert("", "end", values=list(row))
