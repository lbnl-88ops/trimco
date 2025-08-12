import ttkbootstrap as ttk


class AnalyzeFrame(ttk.Frame):
    def __init__(self, owner):
        super().__init__(owner)
    
    def create_widgets(self):
        ttk.Label(self, text='Analyze')