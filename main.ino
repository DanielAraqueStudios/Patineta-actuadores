// Generador de Frecuencia ESP32 con Potenciómetro

const int PIN_POT = 34; // Pin ADC para el potenciómetro
const int PIN_OUT = 25; // Pin de salida PWM (LEDC)

const int PWM_CANAL = 0;       // Canal LEDC (0-15)
const int PWM_RESOLUCION = 8;  // Resolución PWM de 8 bits (0-255) - No afecta a ledcWriteTone
const int FREC_INICIAL = 1000; // Frecuencia inicial temporal

unsigned long tiempoAnterior = 0;
const int INTERVALO_MS = 100; // Actualizar cada 100 ms

void setup() {
  Serial.begin(115200);
  
  // Configuración del generador PWM (LEDC)
  ledcSetup(PWM_CANAL, FREC_INICIAL, PWM_RESOLUCION);
  ledcAttachPin(PIN_OUT, PWM_CANAL);
  
  Serial.println("Generador de Frecuencia ESP32 Iniciado.");
}

void loop() {
  unsigned long tiempoActual = millis();
  
  // Ejecución no bloqueante
  if (tiempoActual - tiempoAnterior >= INTERVALO_MS) {
    tiempoAnterior = tiempoActual;
    
    // Leer el potenciómetro (resolución 12 bits de ESP32 = 0 a 4095)
    int valorPot = analogRead(PIN_POT);
    
    // Mapear el valor a una frecuencia útil (ej. 10 Hz a 5000 Hz)
    int frecuencia = map(valorPot, 0, 4095, 10, 5000);
    
    // Actualizar la frecuencia de la señal PWM
    ledcWriteTone(PWM_CANAL, frecuencia);
    
    // Enviar datos por UART
    Serial.print("ADC: ");
    Serial.print(valorPot);
    Serial.print(" | Frecuencia: ");
    Serial.print(frecuencia);
    Serial.println(" Hz");
  }
}
