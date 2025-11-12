# gui/components/chart_component.py
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd

class Chart(tk.Frame):
    def __init__(self, parent, tipo="bar", datos: pd.DataFrame = None, x=None, y=None, labels=None, values=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.tipo = tipo
        self.datos = datos
        self.x = x
        self.y = y
        self.labels = labels
        self.values = values
        self._draw_chart()

    def _draw_chart(self):
        fig, ax = plt.subplots(figsize=(6,4))
        if self.tipo == "bar":
            # Bar chart
            if isinstance(self.y, list):
                for col in self.y:
                    ax.bar(self.datos[self.x], self.datos[col], label=col)
            else:
                ax.bar(self.datos[self.x], self.datos[self.y], label=self.y)
            ax.set_xlabel(self.x)
            ax.set_ylabel("Costo")
            ax.legend()
        elif self.tipo == "pie":
            # Pie chart
            ax.pie(self.datos[self.values], labels=self.datos[self.labels], autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Circulo perfecto
        else:
            raise ValueError("Tipo de gráfico no soportado: 'bar' o 'pie'.")

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
