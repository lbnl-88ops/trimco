from typing import Dict

import ttkbootstrap as ttk

class CoilSettingsFrame(ttk.Frame):
    def __init__(self, owner, is_calculated = False):
        super().__init__(owner, borderwidth=1, relief=ttk.RAISED)
        self.coil_settings: Dict[int, ttk.StringVar] = {}
        self.main_current = ttk.StringVar(value = '0')
        self.create_widgets(is_calculated)
        
    def create_widgets(self, is_calculated):
        frame_padding = 5
        entry_padding = 5
        if not is_calculated:
            main_current_frame = ttk.Frame(self)
            ttk.Label(main_current_frame, text='Main').pack(side='left', padx=entry_padding)
            self.entMainCurrent = ttk.Entry(main_current_frame, textvariable=self.main_current)
            self.entMainCurrent.pack(side='right', padx=entry_padding)
            main_current_frame.grid(column = 0, row = 0)
        self.trim_coil_entries = {}
        self.use_trim_coil = {}
        self.trim_coil_checkboxes = {}
        for i in range(17):
            self.coil_settings[i] = ttk.StringVar(value = '0')
            coil_frame = ttk.Frame(self)
            if is_calculated:
                self.use_trim_coil[i] = ttk.BooleanVar(value=False)
                self.trim_coil_checkboxes[i] = ttk.Checkbutton(coil_frame, variable=self.use_trim_coil[i])
                self.trim_coil_checkboxes[i].pack(side='left')
            ttk.Label(coil_frame, text=f'Coil {i+1}').pack(side='left', padx=entry_padding)
            coil_entry = ttk.Entry(coil_frame, textvariable=self.coil_settings[i])
            coil_entry.pack(side='right', padx=entry_padding)
            self.trim_coil_entries[i] = coil_entry
            coil_frame.grid(column=int(i/4), row=int(i % 4) + 1, padx=frame_padding, sticky='E')

class CoilSettingsCalculatedFrame(CoilSettingsFrame):
    def __init__(self, owner):
        super().__init__(owner, is_calculated=True)