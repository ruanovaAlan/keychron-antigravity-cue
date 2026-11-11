import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys

# Add directory to sys.path to import keychron_notifier
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

import keychron_notifier as kn

CONFIG_FILE = os.path.join(CURRENT_DIR, "config.json")

class KeychronApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Keychron K17 Max - Selector de Efectos")
        self.root.geometry("680x780")
        self.root.minsize(640, 720)
        self.root.configure(bg="#181825")

        self.config = kn.load_config()
        self.selected_preview_mode = tk.IntVar(value=self.config.get("working_mode", 9))
        self.brightness_var = tk.IntVar(value=255)

        self.working_mode_var = tk.IntVar(value=self.config.get("working_mode", 9))
        self.input_mode_var = tk.IntVar(value=self.config.get("input_mode", 14))
        self.done_mode_var = tk.IntVar(value=self.config.get("done_mode", 1))
        self.idle_mode_var = tk.IntVar(value=self.config.get("idle_mode", 12))
        self.duration_var = tk.IntVar(value=self.config.get("done_duration", 15))

        self.mode_buttons = {}
        self.setup_styles()
        self.build_ui()
        self.check_connection()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure custom colors
        self.style.configure(".", background="#181825", foreground="#cdd6f4")
        self.style.configure("TLabel", background="#181825", foreground="#cdd6f4", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#89b4fa")
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 11, "bold"), foreground="#f5c2e7")
        self.style.configure("Card.TFrame", background="#1e1e2e")
        self.style.configure("TFrame", background="#181825")

    def build_ui(self):
        main_frame = ttk.Frame(self.root, padding=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 12))

        title_lbl = ttk.Label(header_frame, text="⚡ Keychron K17 Max - Configuración de Luces", style="Header.TLabel")
        title_lbl.pack(side=tk.LEFT)

        self.status_lbl = tk.Label(header_frame, text="Detectando...", font=("Segoe UI", 9, "bold"), bg="#313244", fg="#f38ba8", padx=10, pady=4)
        self.status_lbl.pack(side=tk.RIGHT)

        # 2. Live Preview Section
        preview_card = tk.LabelFrame(main_frame, text=" 🔍 1. Explorar y Probar Modos en Vivo (Haz clic para ver el efecto) ", bg="#1e1e2e", fg="#89b4fa", font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        preview_card.pack(fill=tk.X, pady=(0, 12))

        grid_frame = tk.Frame(preview_card, bg="#1e1e2e")
        grid_frame.pack(fill=tk.X, pady=6)

        # 18 mode buttons (3 rows of 6)
        for i in range(1, 19):
            row = (i - 1) // 6
            col = (i - 1) % 6
            btn = tk.Button(
                grid_frame,
                text=f"Modo {i}",
                font=("Segoe UI", 9, "bold"),
                width=10,
                pady=6,
                bg="#313244",
                fg="#cdd6f4",
                activebackground="#89b4fa",
                activeforeground="#11111b",
                relief=tk.FLAT,
                cursor="hand2",
                command=lambda m=i: self.preview_mode(m)
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            self.mode_buttons[i] = btn
            grid_frame.columnconfigure(col, weight=1)

        # Brightness & Off controls
        ctrl_frame = tk.Frame(preview_card, bg="#1e1e2e")
        ctrl_frame.pack(fill=tk.X, pady=(8, 2))

        b_lbl = tk.Label(ctrl_frame, text="Brillo:", bg="#1e1e2e", fg="#a6adc8", font=("Segoe UI", 9))
        b_lbl.pack(side=tk.LEFT, padx=(0, 8))

        self.bright_slider = tk.Scale(
            ctrl_frame,
            from_=0,
            to=255,
            orient=tk.HORIZONTAL,
            variable=self.brightness_var,
            bg="#1e1e2e",
            fg="#cdd6f4",
            troughcolor="#313244",
            highlightthickness=0,
            length=250,
            command=self.on_brightness_change
        )
        self.bright_slider.pack(side=tk.LEFT, padx=5)

        off_btn = tk.Button(
            ctrl_frame,
            text="Apagar Luces (Modo 0)",
            font=("Segoe UI", 9),
            bg="#45475a",
            fg="#f38ba8",
            relief=tk.FLAT,
            padx=10,
            cursor="hand2",
            command=lambda: self.preview_mode(0)
        )
        off_btn.pack(side=tk.RIGHT)

        # 3. Mode Assignment Section
        assign_card = tk.LabelFrame(main_frame, text=" ⚙️ 2. Asignar Modos a los Estados del Asistente ", bg="#1e1e2e", fg="#a6e3a1", font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        assign_card.pack(fill=tk.X, pady=(0, 12))

        self.create_assignment_row(assign_card, "🔨 Mientras Trabajo (Pensando/Herramientas):", self.working_mode_var, "#fab387", "Asignar a 'Trabajar'")
        self.create_assignment_row(assign_card, "❓ Necesito Confirmación / Input tuyo:", self.input_mode_var, "#f9e2af", "Asignar a 'Input'")
        self.create_assignment_row(assign_card, "✅ Tarea Terminada (Luz de éxito):", self.done_mode_var, "#a6e3a1", "Asignar a 'Terminado'")
        self.create_assignment_row(assign_card, "💤 Modo Reposo (Tras terminar la alerta):", self.idle_mode_var, "#94e2d5", "Asignar a 'Reposo'")

        # Duration slider
        dur_frame = tk.Frame(assign_card, bg="#1e1e2e")
        dur_frame.pack(fill=tk.X, pady=(6, 2))

        dur_lbl = tk.Label(dur_frame, text="⏱️ Duración de luz de 'Terminado':", bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 9, "bold"), width=34, anchor="w")
        dur_lbl.pack(side=tk.LEFT)

        dur_scale = tk.Scale(
            dur_frame,
            from_=3,
            to=60,
            orient=tk.HORIZONTAL,
            variable=self.duration_var,
            bg="#1e1e2e",
            fg="#cdd6f4",
            troughcolor="#313244",
            highlightthickness=0,
            length=200
        )
        dur_scale.pack(side=tk.LEFT, padx=5)

        dur_val_lbl = tk.Label(dur_frame, textvariable=tk.StringVar(value=f"{self.duration_var.get()} s"), bg="#1e1e2e", fg="#a6e3a1", font=("Segoe UI", 9, "bold"))
        self.duration_var.trace_add("write", lambda *args: dur_val_lbl.config(text=f"{self.duration_var.get()} seg"))
        dur_val_lbl.pack(side=tk.LEFT, padx=5)

        # 4. Simulation / Testing Section
        sim_card = tk.LabelFrame(main_frame, text=" 🧪 3. Probar Flujo Completo ", bg="#1e1e2e", fg="#cba6f7", font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        sim_card.pack(fill=tk.X, pady=(0, 12))

        sim_btns_frame = tk.Frame(sim_card, bg="#1e1e2e")
        sim_btns_frame.pack(fill=tk.X)

        test_work_btn = tk.Button(sim_btns_frame, text="Probar 'Trabajar'", bg="#fab387", fg="#11111b", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=5, cursor="hand2", command=self.test_working)
        test_work_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        test_input_btn = tk.Button(sim_btns_frame, text="Probar 'Input'", bg="#f9e2af", fg="#11111b", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=5, cursor="hand2", command=self.test_input)
        test_input_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        test_done_btn = tk.Button(sim_btns_frame, text="Probar 'Terminado'", bg="#a6e3a1", fg="#11111b", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=5, cursor="hand2", command=self.test_done)
        test_done_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # 5. Save Button
        save_btn = tk.Button(
            main_frame,
            text="💾 Guardar Cambios para Antigravity",
            font=("Segoe UI", 12, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            activebackground="#b4befe",
            relief=tk.FLAT,
            pady=10,
            cursor="hand2",
            command=self.save_configuration
        )
        save_btn.pack(fill=tk.X, pady=(4, 0))

        # Initial button highlight
        self.highlight_button(self.selected_preview_mode.get())

    def create_assignment_row(self, parent, label_text, var, color, btn_text):
        row = tk.Frame(parent, bg="#1e1e2e")
        row.pack(fill=tk.X, pady=3)

        lbl = tk.Label(row, text=label_text, bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 9, "bold"), width=34, anchor="w")
        lbl.pack(side=tk.LEFT)

        val_box = tk.Spinbox(row, from_=0, to=20, textvariable=var, width=4, font=("Segoe UI", 10, "bold"), bg="#313244", fg=color, buttonbackground="#45475a")
        val_box.pack(side=tk.LEFT, padx=6)

        assign_btn = tk.Button(
            row,
            text=f"⬅ Usar Modo Seleccionado",
            font=("Segoe UI", 8),
            bg="#313244",
            fg="#cdd6f4",
            activebackground=color,
            activeforeground="#11111b",
            relief=tk.FLAT,
            padx=8,
            cursor="hand2",
            command=lambda v=var: v.set(self.selected_preview_mode.get())
        )
        assign_btn.pack(side=tk.LEFT, padx=5)

    def highlight_button(self, mode):
        for m, btn in self.mode_buttons.items():
            if m == mode:
                btn.config(bg="#89b4fa", fg="#11111b")
            else:
                btn.config(bg="#313244", fg="#cdd6f4")

    def preview_mode(self, mode):
        self.selected_preview_mode.set(mode)
        self.highlight_button(mode)
        kn.set_mode(mode, self.brightness_var.get(), force=True)

    def on_brightness_change(self, val):
        kn.set_mode(self.selected_preview_mode.get(), int(val), force=False)

    def check_connection(self):
        h = kn.get_keyboard_device()
        if h:
            h.close()
            self.status_lbl.config(text="● Teclado Conectado (Cable)", bg="#065f46", fg="#a6e3a1")
        else:
            self.status_lbl.config(text="▲ Teclado no detectado", bg="#7f1d1d", fg="#f38ba8")
        self.root.after(3000, self.check_connection)

    def test_working(self):
        kn.set_mode(self.working_mode_var.get(), self.brightness_var.get(), force=True)

    def test_input(self):
        kn.set_mode(self.input_mode_var.get(), self.brightness_var.get(), force=True)

    def test_done(self):
        kn.set_mode(self.done_mode_var.get(), self.brightness_var.get(), force=True)
        # Revert after 3 seconds for test
        self.root.after(3000, lambda: kn.set_mode(self.idle_mode_var.get(), self.brightness_var.get(), force=True))

    def save_configuration(self):
        new_config = {
            "working_mode": self.working_mode_var.get(),
            "input_mode": self.input_mode_var.get(),
            "done_mode": self.done_mode_var.get(),
            "idle_mode": self.idle_mode_var.get(),
            "done_duration": self.duration_var.get()
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(new_config, f, indent=2)
            messagebox.showinfo("Configuración Guardada", "¡Configuración guardada correctamente!\n\nAntigravity usará estos modos automáticamente a partir de ahora.")
        except Exception as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar la configuración: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KeychronApp(root)
    root.mainloop()
