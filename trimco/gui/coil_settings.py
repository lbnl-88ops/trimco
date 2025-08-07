from typing import Dict

import ttkbootstrap as ttk

class CoilSettingsFrame(ttk.Frame):
    def __init__(self, owner):
        super().__init__(owner, borderwidth=1, relief=ttk.RAISED)
        self._coil_settings: Dict[int, ttk.StringVar] = {}
        self._main_current = ttk.StringVar(value = '0')
        self.create_widgets()
        
    def create_widgets(self):
        frame_padding = 5
        entry_padding = 5
        main_current_frame = ttk.Frame(self)
        ttk.Label(main_current_frame, text='Main').pack(side='left', padx=entry_padding)
        ttk.Entry(main_current_frame, textvariable=self._main_current).pack(side='right',
                                                                            padx=entry_padding)
        main_current_frame.grid(column = 0, row = 0)
        for i in range(17):
            self._coil_settings[i] = ttk.StringVar(value = '0')
            coil_frame = ttk.Frame(self)
            ttk.Label(coil_frame, text=f'Coil {i+1}').pack(side='left', padx=entry_padding)
            ttk.Entry(coil_frame, textvariable=self._coil_settings[i]).pack(side='right', 
                                                                            padx=entry_padding)
            coil_frame.grid(column=int(i/4), row=int(i % 4) + 1, padx=frame_padding, sticky='E')
