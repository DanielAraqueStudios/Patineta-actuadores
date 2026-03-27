# Generador de Frecuencia Variable ESP32 + Interfaz PyQt6 🎛️

Un sistema de hardware y software en tiempo real diseñado para generar señales cuadradas de frecuencia variable mediante un ESP32-WROOM. Transforma la lectura analógica de un potenciómetro en una señal PWM por hardware (LEDC), la cual es monitoreada en tiempo real a través de un moderno y minimalista Dashboard de escritorio en Python.

---

## ✨ Características Principales

*   **Firmware Minimalista y Eficiente:** Código de Arduino estructurado sin bloqueos (`delay()`) aplicando `millis()` para mantener un ciclo principal ultrarrápido.
*   **PWM por Hardware (LEDC):** Generación de onda limpia y estable directa desde los periféricos de hardware del ESP32, ajustada dinámicamente de **10 Hz a 5000 Hz**.
*   **Interfaz Gráfica (GUI) Oscura y Moderna:** Aplicación de escritorio creada en `PyQt6` con diseño inspirado en la paleta Catppuccin Mocha.
*   **Monitoreo Concurrente:** Comunicación Serial por UART en un hilo independiente (QThread) para asegurar que la interfaz visual nunca se congele.

---

## 🛠️ Requisitos del Hardware

| Componente | Descripción / Conexión |
| :--- | :--- |
| **ESP32-WROOM** | Microcontrolador principal. |
| **Potenciómetro** | 10kΩ preferiblemente. Pin central conectado al **GPIO 34**. |
| **Salida Actuador** | Pin **GPIO 25**. Conecta aquí un zumbador, osciloscopio o multímetro. |

### Diagrama de Conexión Básico

*   **Potenciómetro VCC** ➔ ESP32 `3.3V`
*   **Potenciómetro GND** ➔ ESP32 `GND`
*   **Potenciómetro Señal (Medio)** ➔ ESP32 `Pin 34` (Entrada ADC)
*   **Salida de Frecuencia** ➔ ESP32 `Pin 25` (Salida PWM/LEDC)

#### Pinout Visual (Conexiones Activas)

```text
                      ESP32 DEVKIT V1 (WROOM)
                       _________________
                      |                 |
                 3v3 -| 3.3V            |
                 GND -| GND             |
                      |            D34  |- Señal Potenciómetro (ADC)
                      |                 |
   Salida PWM/ Hz -   | D25             |
                      |                 |
                      |_________________|
```

---

## 💻 Instalación y Configuración

### 1. Despliegue del Firmware (ESP32)

1. Abre el archivo `main.ino` en el **Arduino IDE** (o VS Code con la extensión de Arduino).
2. Instala / Selecciona la placa **ESP32 Dev Module**.
3. Compila y sube el código al microcontrolador.
4. *(Opcional)* Abre el Monitor Serie a `115200 baudios` para verificar que imprime el estado en formato: `ADC: XXXX | Frecuencia: YYYY Hz`.

### 2. Configuración del Entorno Python (Dashboard)

Asegúrate de contar con **Python 3.8+** instalado en tu sistema.

1. Abre tu terminal de comandos (CMD, PowerShell o Bash).
2. Instala las dependencias necesarias ejecutando:
   ```bash
   pip install PyQt6 pyserial
   ```

---

## 🚀 Uso del Sistema

1. Conecta tu ESP32 mediante USB al computador.
2. Ejecuta la interfaz gráfica mediante la terminal:
   ```bash
   python interface.py
   ```
3. En el Dashboard:
   *   Haz clic en el ícono de recargar `↻` si no ves tu puerto COM.
   *   Selecciona el puerto serial correspondiente a tu placa ESP32.
   *   Haz clic en el botón **Conectar**.
4. ¡Gira el potenciómetro! Observarás cómo los valores, tanto del ADC de 12-bits (0-4095) como la Frecuencia en Hercios (10-5000), cambian instantáneamente sin *lag*.

---

## 📁 Estructura del Proyecto

```text
├── main.ino        # Firmware principal en C++ para el ESP32
├── interface.py    # Código fuente de la interfaz gráfica y comunicación Serial
└── README.md       # Documentación del proyecto
```

---

## 📝 Notas de Diseño

*   **¿Por qué el Pin 34?**: El Pin 34 en el ESP32 es únicamente de entrada, libre de resistencias pull-up/pull-down internas e ideal para lecturas en crudo del ADC sin interferir con las radios Wi-Fi/Bluetooth de la placa.
*   **Ajustes de Interfaz**: Si se llegase a alterar el mapeo de frecuencia en el archivo `main.ino`, recuerda actualizar el valor de `.setMaximum(5000)` en el archivo `interface.py` para visualizar bien la barra de progreso.