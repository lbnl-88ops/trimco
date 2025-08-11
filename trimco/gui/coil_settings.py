from dataclasses import dataclass
from typing import Dict, Optional, List

import ttkbootstrap as ttk

@dataclass
class CoilSettings:
    entry: ttk.Entry
    setting: ttk.StringVar
    use_trim_coil: Optional[ttk.BooleanVar] = None
    checkbox: Optional[ttk.Checkbutton] = None

class CoilSettingsFrame(ttk.Frame):
    def __init__(self, owner, is_calculated = False):
        super().__init__(owner, borderwidth=1, relief=ttk.RAISED)
        self.main_current = ttk.StringVar(value = '1000')
        self.coil_settings: Dict[int, CoilSettings] = {}
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

        self.coil_frames = []
        for i in range(17):
            self.coil_frames.append(ttk.Frame(self))
            coil_frame = self.coil_frames[-1]
            coil_frame.grid(column=int(i/4), row=int(i % 4) + 1, padx=frame_padding, sticky='E')

            coil_setting = ttk.StringVar(value = '0')
            ttk.Label(coil_frame, text=f'Coil {i+1}').pack(side='left', padx=entry_padding)
            coil_entry = ttk.Entry(coil_frame, textvariable=coil_setting,
                                   state='normal' if not is_calculated else 'disable')
            coil_entry.pack(side='right', padx=entry_padding)
            self.coil_settings[i] = CoilSettings(coil_entry, coil_setting)

    def current(self, i: int) -> float:
        return self.currents()[i]

    def currents(self) -> Dict[int, float]:
        return {n: float(s.entry.get()) for n, s in self.coil_settings.items()}


class CoilSettingsCalculatedFrame(CoilSettingsFrame):
    def __init__(self, owner):
        super().__init__(owner, is_calculated=True)

    def use_trim_coils(self) -> List[int]:
        return [n for n, c in self.coil_settings.items() if c.use_trim_coil is not None 
                and c.use_trim_coil.get()]

    def create_widgets(self, is_calculated):
        super().create_widgets(is_calculated)
        for i, coil_frame in enumerate(self.coil_frames):
            coil_setting = self.coil_settings[i]
            coil_setting.use_trim_coil = ttk.BooleanVar(value=False)
            coil_setting.checkbox = ttk.Checkbutton(coil_frame, variable=coil_setting.use_trim_coil)
            coil_setting.checkbox.pack(side='left')



