from dataclasses import dataclass, field
from pydoc import text
from typing import Dict, Optional, List, Tuple

import numpy as np
import ttkbootstrap as ttk


@dataclass
class CoilSettings:
    entry: ttk.Entry
    setting: ttk.StringVar
    use_trim_coil: Optional[ttk.BooleanVar] = None
    checkbox: Optional[ttk.Checkbutton] = None
    current_entries: List[ttk.Entry] = field(default_factory=list)
    min_current: Optional[ttk.StringVar] = None
    max_current: Optional[ttk.StringVar] = None


class CoilSettingsFrame(ttk.Frame):
    def __init__(self, owner, is_calculated=False):
        super().__init__(owner)
        self.main_current = ttk.StringVar(value="1000")
        self.coil_settings: Dict[int, CoilSettings] = {}
        self.frame_padding = 5
        self.entry_padding = 5
        self.entry_width = 7
        self.label_width = 7
        self.create_widgets(is_calculated)

    def create_widgets(self, is_calculated):
        if not is_calculated:
            main_current_frame = ttk.Frame(self)
            ttk.Label(main_current_frame, text="Main").pack(
                side="left", padx=self.entry_padding
            )
            self.entMainCurrent = ttk.Entry(
                main_current_frame, textvariable=self.main_current, width=7
            )
            self.entMainCurrent.pack(side="right", padx=self.entry_padding)
            main_current_frame.grid(column=0, row=0)

        self.coil_frames = []
        for i in range(17):
            self.coil_frames.append(ttk.Frame(self))
            coil_frame = self.coil_frames[-1]
            coil_frame.grid(
                column=int(i / 4),
                row=int(i % 4) + 1,
                padx=self.frame_padding,
                sticky="W",
            )

            coil_setting = ttk.StringVar(value="0")
            ttk.Label(
                coil_frame, text=f"{i + 1}", width=self.label_width, anchor="e"
            ).pack(side="left", padx=self.entry_padding)
            coil_entry = ttk.Entry(
                coil_frame,
                textvariable=coil_setting,
                width=self.entry_width,
                state="normal" if not is_calculated else "disable",
            )
            coil_entry.pack(side="right", padx=self.entry_padding)
            self.coil_settings[i] = CoilSettings(coil_entry, coil_setting)

        self.unbalance_frame = ttk.Frame(self)
        (
            col,
            _,
        ) = self.grid_size()
        self.unbalance_frame.grid(
            column=col - 1, row=2, padx=self.frame_padding, sticky="W"
        )  # , columnspan=int(17/4))
        self.unbalance_setting = ttk.StringVar(value="0")
        ttk.Label(
            self.unbalance_frame, text="TC1 Unb", anchor="e", width=self.label_width
        ).pack(side="left", padx=self.entry_padding)
        self.entUnbalance = ttk.Entry(
            self.unbalance_frame,
            textvariable=self.unbalance_setting,
            width=self.entry_width,
            state="normal" if not is_calculated else "disable",
        )
        self.entUnbalance.pack(side="right", padx=self.entry_padding)

    def current(self, i: int) -> float:
        return self.currents()[i]

    def currents(self) -> Dict[int, float]:
        return {n: float(s.entry.get()) for n, s in self.coil_settings.items()}

    @property
    def unbalance(self) -> float:
        return float(self.unbalance_setting.get())


class CoilSettingsCalculatedFrame(CoilSettingsFrame):
    def __init__(self, owner):
        super().__init__(owner, is_calculated=True)

    def use_trim_coils(self) -> Dict[int, float]:
        return {
            n: c.use_trim_coil.get()
            for n, c in self.coil_settings.items()
            if c.use_trim_coil is not None
        }

    def set_current_limits(self, to_set: Dict[int, Tuple[float | None, float]]):
        for i, setting in self.coil_settings.items():
            min, max = to_set[i]
            setting.max_current.set(f"{max:.0f}")
            if min is not None and setting.min_current is not None:
                setting.min_current.set(f"{min:.0f}")

    def clear_current_settings(self) -> None:
        for coil_setting in self.coil_settings.values():
            coil_setting.setting.set("0")

    def set_current_settings(
        self, to_set: Dict[int, float], unbalance: float = 0
    ) -> None:
        self.unbalance_setting.set(f"{np.round(unbalance, decimals=0):.0f}")
        for i, current in to_set.items():
            self.coil_settings[i].setting.set(f"{np.round(current, decimals=0):.0f}")

    @property
    def max_currents(self) -> Dict[int, float]:
        return {
            n: float(c.max_current.get())
            for n, c in self.coil_settings.items()
            if c.max_current is not None
        }

    @property
    def min_currents(self) -> Dict[int, float | None]:
        return {
            n: None if c.min_current is None else float(c.min_current.get())
            for n, c in self.coil_settings.items()
        }

    def current_limits(self):
        return {n: (self.min_currents[n], self.max_currents[n]) for n in range(17)}

    @property
    def unbalance(self) -> float:
        return float(self.unbalance_desired.get())

    def create_widgets(self, is_calculated):
        super().create_widgets(is_calculated)
        for i, coil_frame in enumerate(self.coil_frames):
            coil_setting = self.coil_settings[i]
            coil_setting.use_trim_coil = ttk.BooleanVar(value=False)
            coil_setting.max_current = ttk.StringVar()
            coil_setting.checkbox = ttk.Checkbutton(
                coil_frame, variable=coil_setting.use_trim_coil
            )
            # Packing and repacking
            coil_setting.entry.pack_forget()
            coil_setting.checkbox.pack(side="left", padx=self.entry_padding)
            max_current_entry = ttk.Entry(
                coil_frame,
                textvariable=coil_setting.max_current,
                width=self.entry_width,
            )
            max_current_entry.pack(side="right")
            ttk.Label(coil_frame, text="Max", width=4).pack(
                side="right", padx=self.entry_padding
            )
            coil_setting.current_entries.append(max_current_entry)
            coil_setting.entry.pack(side="right")

        self.entUnbalance.pack_forget()
        self.unbalance_desired = ttk.StringVar(value="0")
        self.entUnbalanceDesired = ttk.Entry(
            self.unbalance_frame,
            width=self.entry_width,
            textvariable=self.unbalance_desired,
        )
        self.entUnbalanceDesired.pack(side="right")
        ttk.Label(self.unbalance_frame, text="Desired").pack(side="right")
        self.entUnbalance.pack(side="right")
