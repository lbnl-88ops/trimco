from dataclasses import dataclass
from pydoc import text
from typing import Dict, Optional, List

import ttkbootstrap as ttk

@dataclass
class CoilSettings:
    entry: ttk.Entry
    setting: ttk.StringVar
    use_trim_coil: Optional[ttk.BooleanVar] = None
    checkbox: Optional[ttk.Checkbutton] = None
    min_current: Optional[ttk.StringVar] = None
    max_current: Optional[ttk.StringVar] = None


class CoilSettingsFrame(ttk.Frame):
    def __init__(self, owner, is_calculated = False):
        super().__init__(owner)
        self.main_current = ttk.StringVar(value = '1000')
        self.coil_settings: Dict[int, CoilSettings] = {}
        self.frame_padding = 5
        self.entry_padding = 5
        self.create_widgets(is_calculated)
        
    def create_widgets(self, is_calculated):

        if not is_calculated:
            main_current_frame = ttk.Frame(self)
            ttk.Label(main_current_frame, text='Main').pack(side='left', padx=self.entry_padding)
            self.entMainCurrent = ttk.Entry(main_current_frame, textvariable=self.main_current,
                                            width=5)
            self.entMainCurrent.pack(side='right', padx=self.entry_padding)
            main_current_frame.grid(column = 0, row = 0)

        self.coil_frames = []
        for i in range(17):
            self.coil_frames.append(ttk.Frame(self))
            coil_frame = self.coil_frames[-1]
            coil_frame.grid(column=int(i/4), row=int(i % 4) + 1, padx=self.frame_padding, sticky='W')

            coil_setting = ttk.StringVar(value = '0')
            ttk.Label(coil_frame, text=f'Coil {i+1}', width=6).pack(side='left', padx=self.entry_padding)
            coil_entry = ttk.Entry(coil_frame, textvariable=coil_setting, width=5,
                                   state='normal' if not is_calculated else 'disable')
            coil_entry.pack(side='right', padx=self.entry_padding)
            self.coil_settings[i] = CoilSettings(coil_entry, coil_setting)

    def current(self, i: int) -> float:
        return self.currents()[i]

    def currents(self) -> Dict[int, float]:
        return {n: float(s.entry.get()) for n, s in self.coil_settings.items()}


class CoilSettingsCalculatedFrame(CoilSettingsFrame):
    def __init__(self, owner):
        super().__init__(owner, is_calculated=True)

    def use_trim_coils(self) -> List[int]:
        return [n + 1 for n, c in self.coil_settings.items() if c.use_trim_coil is not None 
                and c.use_trim_coil.get()]

    def create_widgets(self, is_calculated):
        super().create_widgets(is_calculated)
        for i, coil_frame in enumerate(self.coil_frames):
            coil_setting = self.coil_settings[i]
            coil_setting.use_trim_coil = ttk.BooleanVar(value=False)
            coil_setting.max_current = ttk.StringVar()
            coil_setting.checkbox = ttk.Checkbutton(coil_frame, variable=coil_setting.use_trim_coil)
            # Packing and repacking
            coil_setting.entry.pack_forget()
            coil_setting.checkbox.pack(side='left', padx=self.entry_padding)
            ttk.Entry(coil_frame, textvariable=coil_setting.max_current, width=5).pack(side='right')
            ttk.Label(coil_frame, text='Max', width=4).pack(side='right', padx=self.entry_padding)
            if i == 0:
                coil_setting.min_current = ttk.StringVar()
                ttk.Entry(coil_frame, textvariable=coil_setting.min_current, width=5).pack(side='right')
                ttk.Label(coil_frame, text='Min', width=4).pack(side='right', padx=self.entry_padding)
            coil_setting.entry.pack(side='right')



