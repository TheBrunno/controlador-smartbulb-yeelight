import json
import threading
from pathlib import Path
import tkinter as tk
from tkinter import colorchooser, messagebox, ttk

from discover import discover_yeelight_bulbs
from methods import BulbController


class YeelightApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Controlador Yeelight • Smart UI")
        self.geometry("980x640")
        self.minsize(920, 580)
        self.configure(bg="#0f172a")

        self.controller: BulbController | None = None
        self.discovered_bulbs: list[tuple[str, int]] = []
        self.off_timer: threading.Timer | None = None
        self.presets_file = Path("presets.json")

        self._setup_style()
        self._build_ui()
        self._load_presets()

    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("App.TFrame", background="#0f172a")
        style.configure("Card.TFrame", background="#111827")
        style.configure("CardTitle.TLabel", background="#111827", foreground="#e2e8f0", font=("Segoe UI", 12, "bold"))
        style.configure("Subtle.TLabel", background="#111827", foreground="#94a3b8", font=("Segoe UI", 9))
        style.configure("Value.TLabel", background="#111827", foreground="#f8fafc", font=("Segoe UI", 11, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8)

    def _build_ui(self):
        root = ttk.Frame(self, style="App.TFrame", padding=14)
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=2)
        root.columnconfigure(1, weight=3)
        root.rowconfigure(1, weight=1)

        self._build_header(root)
        self._build_left_panel(root)
        self._build_right_panel(root)

    def _build_header(self, parent):
        header = ttk.Frame(parent, style="Card.TFrame", padding=(14, 10))
        header.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 12))
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Central de Iluminação Yeelight", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="UX focada em ações rápidas: descoberta, cenas, timer e personalização.",
            style="Subtle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.status_var = tk.StringVar(value="Pronto para iniciar")
        ttk.Label(header, textvariable=self.status_var, style="Subtle.TLabel").grid(row=0, column=1, rowspan=2, sticky="e")

    def _build_left_panel(self, parent):
        panel = ttk.Frame(parent, style="Card.TFrame", padding=12)
        panel.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        panel.columnconfigure(0, weight=1)

        ttk.Label(panel, text="Dispositivos", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")

        self.bulb_list = tk.Listbox(panel, height=8, bg="#0b1220", fg="#e2e8f0", selectbackground="#2563eb", borderwidth=0)
        self.bulb_list.grid(row=1, column=0, sticky="nsew", pady=8)

        buttons = ttk.Frame(panel, style="Card.TFrame")
        buttons.grid(row=2, column=0, sticky="ew")
        buttons.columnconfigure((0, 1), weight=1)

        ttk.Button(buttons, text="Descobrir", command=self.discover, style="Accent.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(buttons, text="Conectar", command=self.connect_selected).grid(row=0, column=1, sticky="ew")

        sep = ttk.Separator(panel, orient="horizontal")
        sep.grid(row=3, column=0, sticky="ew", pady=12)

        ttk.Label(panel, text="Cenas rápidas", style="CardTitle.TLabel").grid(row=4, column=0, sticky="w")
        scene_grid = ttk.Frame(panel, style="Card.TFrame")
        scene_grid.grid(row=5, column=0, sticky="ew", pady=(8, 0))
        for i in range(2):
            scene_grid.columnconfigure(i, weight=1)

        ttk.Button(scene_grid, text="Leitura", command=lambda: self.apply_scene("reading")).grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)
        ttk.Button(scene_grid, text="Relax", command=lambda: self.apply_scene("relax")).grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Button(scene_grid, text="Foco", command=lambda: self.apply_scene("focus")).grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=4)
        ttk.Button(scene_grid, text="Noite", command=lambda: self.apply_scene("night")).grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(panel, text="Timer desligar (min)", style="Subtle.TLabel").grid(row=6, column=0, sticky="w", pady=(12, 4))
        timer_row = ttk.Frame(panel, style="Card.TFrame")
        timer_row.grid(row=7, column=0, sticky="ew")
        timer_row.columnconfigure(0, weight=1)

        self.timer_var = tk.IntVar(value=15)
        ttk.Spinbox(timer_row, from_=1, to=240, textvariable=self.timer_var, width=8).grid(row=0, column=0, sticky="w")
        ttk.Button(timer_row, text="Agendar", command=self.schedule_turn_off).grid(row=0, column=1, sticky="e")

    def _build_right_panel(self, parent):
        panel = ttk.Frame(parent, style="Card.TFrame", padding=12)
        panel.grid(row=1, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)

        ttk.Label(panel, text="Controles", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")

        power_row = ttk.Frame(panel, style="Card.TFrame")
        power_row.grid(row=1, column=0, sticky="ew", pady=(8, 6))

        ttk.Button(power_row, text="Ligar", command=self.power_on, style="Accent.TButton").grid(row=0, column=0, padx=(0, 6))
        ttk.Button(power_row, text="Desligar", command=self.power_off).grid(row=0, column=1, padx=(0, 6))
        ttk.Button(power_row, text="Alternar", command=self.toggle).grid(row=0, column=2)

        self.brightness_var = tk.IntVar(value=50)
        ttk.Label(panel, text="Brilho", style="Subtle.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Scale(panel, from_=1, to=100, orient="horizontal", command=self.on_brightness_drag, variable=self.brightness_var).grid(row=3, column=0, sticky="ew")
        self.brightness_value = ttk.Label(panel, text="50%", style="Value.TLabel")
        self.brightness_value.grid(row=4, column=0, sticky="w", pady=(2, 10))

        self.temp_var = tk.IntVar(value=4000)
        ttk.Label(panel, text="Temperatura de Cor (K)", style="Subtle.TLabel").grid(row=5, column=0, sticky="w")
        ttk.Scale(panel, from_=1700, to=6500, orient="horizontal", command=self.on_temp_drag, variable=self.temp_var).grid(row=6, column=0, sticky="ew")
        self.temp_value = ttk.Label(panel, text="4000 K", style="Value.TLabel")
        self.temp_value.grid(row=7, column=0, sticky="w", pady=(2, 10))

        trans_row = ttk.Frame(panel, style="Card.TFrame")
        trans_row.grid(row=8, column=0, sticky="ew")
        ttk.Label(trans_row, text="Transição (ms)", style="Subtle.TLabel").grid(row=0, column=0, sticky="w")
        self.transition_var = tk.IntVar(value=500)
        ttk.Spinbox(trans_row, from_=30, to=5000, increment=50, textvariable=self.transition_var, width=8, command=self.update_transition).grid(row=0, column=1, sticky="e")

        extra_row = ttk.Frame(panel, style="Card.TFrame")
        extra_row.grid(row=9, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(extra_row, text="Escolher cor RGB", command=self.pick_color).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(extra_row, text="Salvar preset atual", command=self.save_current_preset).grid(row=0, column=1)

        ttk.Label(panel, text="Presets salvos", style="Subtle.TLabel").grid(row=10, column=0, sticky="w", pady=(12, 4))
        self.presets_combo = ttk.Combobox(panel, state="readonly")
        self.presets_combo.grid(row=11, column=0, sticky="ew")
        self.presets_combo.bind("<<ComboboxSelected>>", self.apply_saved_preset)

    def _require_controller(self) -> bool:
        if not self.controller:
            messagebox.showwarning("Sem conexão", "Conecte-se a uma lâmpada primeiro.")
            return False
        return True

    def log(self, text: str):
        self.status_var.set(text)

    def discover(self):
        self.log("Procurando dispositivos...")
        self.update_idletasks()
        self.discovered_bulbs = discover_yeelight_bulbs()
        self.bulb_list.delete(0, tk.END)

        for ip, port in self.discovered_bulbs:
            self.bulb_list.insert(tk.END, f"{ip}:{port}")

        if self.discovered_bulbs:
            self.log(f"{len(self.discovered_bulbs)} lâmpada(s) encontrada(s).")
        else:
            self.log("Nenhuma lâmpada encontrada.")

    def connect_selected(self):
        idx = self.bulb_list.curselection()
        if not idx:
            messagebox.showinfo("Seleção", "Escolha uma lâmpada na lista.")
            return

        ip, port = self.discovered_bulbs[idx[0]]
        self.controller = BulbController(ip, port, default_transition=self.transition_var.get())
        self.log(f"Conectado em {ip}:{port}")

    def update_transition(self):
        if self.controller:
            self.controller.set_default_transition(self.transition_var.get())

    def power_on(self):
        if self._require_controller():
            self.update_transition()
            self.controller.turn_on()
            self.log("Lâmpada ligada")

    def power_off(self):
        if self._require_controller():
            self.update_transition()
            self.controller.turn_off()
            self.log("Lâmpada desligada")

    def toggle(self):
        if self._require_controller():
            self.controller.toggle()
            self.log("Estado alternado")

    def on_brightness_drag(self, _):
        value = int(self.brightness_var.get())
        self.brightness_value.configure(text=f"{value}%")
        if self.controller:
            self.controller.set_bright(value)

    def on_temp_drag(self, _):
        value = int(self.temp_var.get())
        self.temp_value.configure(text=f"{value} K")
        if self.controller:
            self.controller.set_ct_abx(value)

    def pick_color(self):
        if not self._require_controller():
            return
        _, hex_color = colorchooser.askcolor(title="Selecione uma cor")
        if hex_color:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            self.controller.set_rgb((r, g, b))
            self.log(f"Cor aplicada: {hex_color}")

    def apply_scene(self, scene: str):
        if not self._require_controller():
            return

        scenes = {
            "reading": {"bright": 75, "temp": 4200},
            "relax": {"bright": 35, "temp": 2700},
            "focus": {"bright": 100, "temp": 5000},
            "night": {"bright": 10, "temp": 1900},
        }
        config = scenes[scene]
        self.controller.turn_on()
        self.controller.set_bright(config["bright"])
        self.controller.set_ct_abx(config["temp"])
        self.brightness_var.set(config["bright"])
        self.temp_var.set(config["temp"])
        self.brightness_value.configure(text=f"{config['bright']}%")
        self.temp_value.configure(text=f"{config['temp']} K")
        self.log(f"Cena aplicada: {scene}")

    def schedule_turn_off(self):
        if not self._require_controller():
            return

        minutes = self.timer_var.get()
        if self.off_timer:
            self.off_timer.cancel()

        self.off_timer = threading.Timer(minutes * 60, self._turn_off_from_timer)
        self.off_timer.daemon = True
        self.off_timer.start()
        self.log(f"Desligamento agendado em {minutes} minuto(s)")

    def _turn_off_from_timer(self):
        try:
            if self.controller:
                self.controller.turn_off()
        finally:
            self.after(0, lambda: self.log("Timer executado: lâmpada desligada"))

    def _load_presets(self):
        if not self.presets_file.exists():
            self.presets = {}
            self._refresh_preset_combo()
            return
        try:
            self.presets = json.loads(self.presets_file.read_text(encoding="utf-8"))
        except Exception:
            self.presets = {}
        self._refresh_preset_combo()

    def _refresh_preset_combo(self):
        names = sorted(self.presets.keys())
        self.presets_combo["values"] = names
        if names:
            self.presets_combo.current(0)

    def save_current_preset(self):
        name = f"Preset {len(self.presets) + 1}"
        self.presets[name] = {
            "bright": int(self.brightness_var.get()),
            "temp": int(self.temp_var.get()),
            "transition": int(self.transition_var.get()),
        }
        self.presets_file.write_text(json.dumps(self.presets, indent=2, ensure_ascii=False), encoding="utf-8")
        self._refresh_preset_combo()
        self.log(f"Preset salvo: {name}")

    def apply_saved_preset(self, _event=None):
        if not self._require_controller():
            return

        name = self.presets_combo.get()
        if not name or name not in self.presets:
            return

        preset = self.presets[name]
        self.transition_var.set(preset["transition"])
        self.update_transition()
        self.controller.turn_on()
        self.controller.set_bright(preset["bright"])
        self.controller.set_ct_abx(preset["temp"])
        self.brightness_var.set(preset["bright"])
        self.temp_var.set(preset["temp"])
        self.brightness_value.configure(text=f"{preset['bright']}%")
        self.temp_value.configure(text=f"{preset['temp']} K")
        self.log(f"Preset aplicado: {name}")


def run_app():
    app = YeelightApp()
    app.mainloop()
