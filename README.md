# ⌨️ Keychron Cue para Google Antigravity ✨

> **Avisos visuales en tiempo real para tu teclado Keychron (K17 Max y teclados QMK / VIA compatibles) sincronizados con las acciones de Google Antigravity.**

Convierte la iluminación de tu teclado en un panel de estado físico mientras trabajas en pareja con el asistente de inteligencia artificial:
* 🔨 **Trabajando / Pensando / Herramientas:** Activa una animación continua mientras el agente procesa o ejecuta herramientas (leer, escribir, buscar en la web, ejecutar comandos en terminal).
* ❓ **Esperando Input / Confirmación:** Cambia automáticamente de modo si el agente te hace una pregunta o requiere confirmación.
* ✅ **Tarea Terminada:** Emite una luz sólida fija durante **15 segundos** (configurable) como señal visual de éxito para que sepas cuándo mirar la pantalla.

---

## 📦 Descarga directa

Puedes descargar el paquete listo para usar haciendo clic en:
👉 **[Descargar Keychron-Antigravity-Pack.zip](https://github.com/ruanovaAlan/keychron-antigravity-cue/raw/main/Keychron-Antigravity-Pack.zip)**

---

## 🚀 Instalación en 1 Clic (Windows)

### Requisitos previos:
1. **Python 3.x** instalado en Windows (asegúrate de marcar la casilla *"Add python.exe to PATH"* durante la instalación).
2. Conectar tu teclado Keychron por **Cable USB** con el interruptor lateral/trasero en posición **Cable**. *(Los protocolos de iluminación Raw HID no viajan por el dongle inalámbrico debido a ahorro de batería del firmware)*.

### Pasos:
1. Descarga y descomprime **`Keychron-Antigravity-Pack.zip`**.
2. Haz doble clic en **`instalar.bat`**.

El instalador automatizado se encargará de:
* Instalar la librería requerida (`pip install hidapi`).
* Copiar los scripts a `%USERPROFILE%\.keychron\`.
* Registrar automáticamente los hooks globales de Antigravity en `%USERPROFILE%\.gemini\config\hooks.json`.
* Crear un acceso directo en tu Escritorio: **`Configurar Luces Keychron.bat`**.

---

## 🎨 Selector Visual de Modos (UI con Tkinter)

Abre el acceso directo en tu Escritorio: **`Configurar Luces Keychron.bat`** (o ejecuta `python app_keychron_config.py`).

![UI Preview](https://img.shields.io/badge/Tkinter-UI%20Moderna-89b4fa?style=for-the-badge)

### Características de la app:
1. **Explorador en Vivo:** Haz clic sobre los botones del **Modo 1 al 18** y mira hacia tu teclado: ¡el efecto cambiará instantáneamente en tiempo real! Así podrás ver qué animación te gusta más (olas, respiración, barrido, etc.).
2. **Asignación de Estados:**
   * **Mientras Trabajo:** Modo asignado mientras el agente piensa o ejecuta acciones.
   * **Necesito Confirmación / Input:** Modo asignado cuando espera tu respuesta.
   * **Tarea Terminada:** Modo asignado tras finalizar (por defecto luz sólida).
   * **Modo Reposo:** Modo base al que regresa el teclado tras el aviso de terminado.
   * **Duración de aviso:** Deslizador para ajustar el tiempo que dura la luz de fin (3 a 60 segundos).
3. **Simulador:** Botones para probar cada estado antes de guardar.
4. **Guardar:** Aplica los cambios inmediatamente a tu Antigravity sin reiniciar nada.

---

## ⚙️ ¿Cómo funciona por dentro?

### Comunicación QMK / Raw HID
El script se comunica a nivel de hardware con el chip QMK del teclado a través del canal **Raw HID** (`Vendor ID: 0x3434`, `Usage Page: 0xFF60`, `Usage ID: 0x0061`):
* Utiliza el canal de efectos monocromáticos de QMK (**Channel 5 - LED Matrix**):
  * `Value 1`: Brillo (0 a 255).
  * `Value 2`: Efecto / Modo de iluminación (1 a 18).

### Hooks de Antigravity (`hooks.json`)
Antigravity ejecuta el controlador mediante su sistema de ciclo de vida:
* **`PreInvocation`:** Se dispara cuando el agente empieza a procesar un mensaje del usuario ➔ Activa el modo de trabajo.
* **`PreToolUse`:** Se dispara justo antes de cualquier acción (`read_file`, `write_file`, `search_web`, `run_command`...) ➔ Genera un pulso/cue visual de 80ms sin interrumpir la animación.
* **`Stop`:** Se dispara cuando el agente termina su turno ➔ Inspecciona si la respuesta terminó con una pregunta; si es así, pasa al modo de input; si no, activa el temporizador de luz de éxito.

---

## 📂 Estructura del Proyecto

```text
Keychron-Antigravity-Pack/
│
├── app_keychron_config.py      # Interfaz gráfica moderna en Tkinter
├── keychron_notifier.py        # Controlador de hardware USB y listener de hooks
├── config.json                 # Configuración de modos y tiempos elegidos
├── instalar.bat                # Instalador desatendido en 1 clic para Windows
├── desinstalar.bat             # Desinstalador limpio en 1 clic
├── Keychron-Antigravity-Pack.zip # Paquete comprimido portable
└── README.md                   # Esta guía
```

---

## 🗑️ Desinstalación

Para desinstalar la integración en cualquier momento, simplemente haz doble clic en **`desinstalar.bat`**. Esto eliminará los hooks de Antigravity y el acceso directo del Escritorio sin dejar residuos.

---

## 👤 Autor

Creado por **Alan Ruanova** (@ruanovaalan96).
