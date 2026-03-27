import sys
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QPushButton, 
                             QProgressBar, QMessageBox, QFrame)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont

# --- DARK MODERN STYLESHEET (Catppuccin Mocha inspired) ---
DARK_THEME = """
QMainWindow {
    background-color: #1e1e2e;
}
QLabel {
    color: #cdd6f4;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QFrame#Card {
    background-color: #313244;
    border-radius: 10px;
}
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #b4befe;
}
QPushButton:disabled {
    background-color: #45475a;
    color: #a6adc8;
}
QComboBox {
    background-color: #45475a;
    color: #cdd6f4;
    border: 1px solid #585b70;
    border-radius: 6px;
    padding: 8px;
    font-size: 14px;
}
QComboBox::drop-down {
    border: none;
}
QProgressBar {
    background-color: #45475a;
    border: none;
    border-radius: 8px;
    text-align: center;
    color: transparent; /* Hide text to make it cleaner */
    height: 16px;
}
QProgressBar::chunk {
    background-color: #a6e3a1;
    border-radius: 8px;
}
"""

class SerialWorker(QThread):
    data_received = pyqtSignal(int, int) # ADC, Freq
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        self.running = False

    def connect_port(self, port):
        try:
            self.serial_port.port = port
            self.serial_port.timeout = 1
            self.serial_port.open()
            self.running = True
            self.start()
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False

    def disconnect_port(self):
        self.running = False
        self.wait(500) # Wait for thread to finish safely
        if self.serial_port.is_open:
            self.serial_port.close()

    def run(self):
        while self.running and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    # Expected format: "ADC: 1234 | Frecuencia: 2500 Hz"
                    if "ADC:" in line and "Frecuencia:" in line:
                        parts = line.split("|")
                        adc_val = int(parts[0].split(":")[1].strip())
                        freq_val = int(parts[1].split(":")[1].replace("Hz", "").strip())
                        self.data_received.emit(adc_val, freq_val)
            except Exception as e:
                pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ESP32 Control Interface")
        self.setMinimumSize(500, 400)
        
        self.worker = SerialWorker()
        self.worker.data_received.connect(self.update_ui)
        self.worker.error_occurred.connect(self.show_error)

        self.setup_ui()
        self.refresh_ports()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # TITLE
        title = QLabel("Dashboard Generador de Frecuencia")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # TOP BAR: Connection
        conn_layout = QHBoxLayout()
        
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedWidth(40)
        self.refresh_btn.clicked.connect(self.refresh_ports)

        self.connect_btn = QPushButton("Conectar")
        self.connect_btn.clicked.connect(self.toggle_connection)

        conn_layout.addWidget(QLabel("Puerto Serial:"))
        conn_layout.addWidget(self.port_combo)
        conn_layout.addWidget(self.refresh_btn)
        conn_layout.addWidget(self.connect_btn)
        main_layout.addLayout(conn_layout)

        # DATA CARDS
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # ADC Card
        adc_card = QFrame()
        adc_card.setObjectName("Card")
        adc_layout = QVBoxLayout(adc_card)
        adc_title = QLabel("Nivel ADC")
        adc_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.adc_label = QLabel("0")
        self.adc_label.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        self.adc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.adc_label.setStyleSheet("color: #fab387;")
        
        self.adc_bar = QProgressBar()
        self.adc_bar.setMaximum(4095)
        
        adc_layout.addWidget(adc_title)
        adc_layout.addWidget(self.adc_label)
        adc_layout.addWidget(self.adc_bar)
        cards_layout.addWidget(adc_card)

        # Frequency Card
        freq_card = QFrame()
        freq_card.setObjectName("Card")
        freq_layout = QVBoxLayout(freq_card)
        freq_title = QLabel("Frecuencia (Hz)")
        freq_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.freq_label = QLabel("0")
        self.freq_label.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        self.freq_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.freq_label.setStyleSheet("color: #89b4fa;")
        
        self.freq_bar = QProgressBar()
        self.freq_bar.setMaximum(5000) # Maximum map value
        
        freq_layout.addWidget(freq_title)
        freq_layout.addWidget(self.freq_label)
        freq_layout.addWidget(self.freq_bar)
        cards_layout.addWidget(freq_card)

        main_layout.addLayout(cards_layout)
        main_layout.addStretch()

    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)

    def toggle_connection(self):
        if not self.worker.running:
            port = self.port_combo.currentText()
            if port:
                if self.worker.connect_port(port):
                    self.connect_btn.setText("Desconectar")
                    self.connect_btn.setStyleSheet("background-color: #f38ba8; color: #1e1e2e;")
                    self.port_combo.setEnabled(False)
                    self.refresh_btn.setEnabled(False)
        else:
            self.worker.disconnect_port()
            self.connect_btn.setText("Conectar")
            self.connect_btn.setStyleSheet("")
            self.port_combo.setEnabled(True)
            self.refresh_btn.setEnabled(True)
            self.adc_label.setText("0")
            self.freq_label.setText("0")
            self.adc_bar.setValue(0)
            self.freq_bar.setValue(0)

    def update_ui(self, adc, freq):
        self.adc_label.setText(str(adc))
        self.freq_label.setText(str(freq))
        self.adc_bar.setValue(adc)
        self.freq_bar.setValue(freq)

    def show_error(self, message):
        QMessageBox.critical(self, "Error Serial", message)
        self.toggle_connection() # Reset UI state

    def closeEvent(self, event):
        self.worker.disconnect_port()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
