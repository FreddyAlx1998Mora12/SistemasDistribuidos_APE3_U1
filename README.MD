# 🧵 Arquitectura de Sistemas Distribuidos — Laboratorio de Sincronización Concurrente

## Proyecto integrador que implementa cinco problemas clásicos de sincronización en sistemas multihilo, utilizando **Python** como backend y **Flask** como API REST.

### Mejoras a futuro: La interfaz web (actualmente basada en plantillas Jinja2) está preparada para migrar a **React + Vite** sin modificar la lógica del núcleo.

## 📂 Estructura del proyecto

ArquitecturaSistemasDistribuidos/
├── app.py # Controlador principal – API REST
├── config.py # Configuración centralizada
├── requirements.txt # Dependencias (Flask, Flask-CORS)
│
├── core/ # Núcleo de lógica concurrente
│ ├── init.py
│ ├── base_simulation.py # Clase abstracta base + sistema de logging
│ ├── ex1_taquilla.py # Ejercicio 1: Exclusión mutua (Mutex)
│ ├── ex2_gimnasio.py # Ejercicio 2: Semáforos de conteo
│ ├── ex3_panaderia.py # Ejercicio 3: Productor-Consumidor
│ ├── ex4_tablon.py # Ejercicio 4: Lectores-Escritores
│ └── ex5_barrera.py # Ejercicio 5: Barreras de sincronización
│
├── templates/
│ └── index.html # Frontend SPA con 5 paneles intercambiables
│
├── static/
│ ├── css/
│ │ └── styles.css # Estilos dark y barra lateral
│ └── js/
│ └── app.js # Lógica asíncrona (fetch) para la API
│
└── screenshots/ # Capturas de pantalla (ver sección 📸)

---

## 🧠 Arquitectura del sistema

El proyecto sigue una arquitectura **modular por capas**, con separación clara entre:

- **Capa de presentación** (`templates/`, `static/`): interfaz de usuario tipo SPA con navegación lateral y paneles para cada ejercicio.
- **Capa de API** (`app.py`): endpoints RESTful que ejecutan las simulaciones y devuelven resultados + logs en JSON.
- **Capa de dominio** (`core/`): implementación de las primitivas de sincronización y las simulaciones. Cada ejercicio hereda de `BaseSimulation`, lo que garantiza uniformidad en logging, manejo de errores y recolección de estadísticas.

### 🔍 Subsistema de logging

Cada simulación cuenta con un logger independiente (`SimulationLogger`) que:

- Crea un `logging.Logger` con un `QueueHandler` que envía mensajes a una cola segura.
- Al finalizar la simulación, todos los registros formateados se recuperan como lista de cadenas.
- Los logs viajan en la respuesta JSON para ser visualizados en el frontend, permitiendo **trazar cada evento de sincronización**: adquisiciones/liberaciones de locks, operaciones de semáforos, estados de buffers, etc.

El formato de los mensajes es:  
`[HH:MM:SS.mmm] NombreHilo: mensaje`

---

## 🧪 Ejercicios implementados

### 1. 🎬 Dilema de la Taquilla — Exclusión Mutua (Mutex)

**Contexto:** Miles de usuarios compran boletos simultáneamente. Si dos hilos leen el mismo asiento disponible, hay sobreventa (condición de carrera).

**Solución:** Se usa `threading.Lock` para proteger una sección crítica donde el contador se lee, incrementa y almacena de forma explícita (no atómica). Modos:

- **Con Mutex:** siempre da `N × M`.
- **Sin Mutex:** expone la condición de carrera.
- **Secuencial:** referencia de rendimiento.

**Criterio de verificación:** ejecutar 10 veces con mutex sin variación → ✅.

**Endpoint:** `POST /api/run/ex1`  
**Parámetros:** `n_hilos`, `ventas_por_hilo`, `usar_mutex`

---

### 2. 🏋️ Gimnasio — Semáforos de Conteo

**Contexto:** Un gimnasio con 3 máquinas y 8 atletas. Si todas están ocupadas, los atletas esperan.

**Solución:** Clase `MiSemaforo` implementada con `Condition` y `Lock` (siguiendo el pseudocódigo del enunciado). Controla el acceso a un número limitado de recursos. Se monitoriza el máximo de máquinas en uso simultáneo para verificar que nunca supera el límite.

**Criterio de verificación:** `max_maquinas_uso ≤ n_maquinas` → ✅.

**Endpoint:** `POST /api/run/ex2`  
**Parámetros:** `n_atletas`, `n_maquinas`, `repeticiones`

---

### 3. 🥖 La Vitrina de la Panadería — Productor-Consumidor

**Contexto:** Panaderos colocan pan en una vitrina limitada; clientes los retiran. No se puede poner si está llena ni sacar si está vacía.

**Solución:** Buffer de capacidad fija controlado por:

- Semáforo `espacios_vacios` (capacidad inicial).
- Semáforo `panes_listos` (0 inicial).
- `Lock` para acceso exclusivo al buffer (evitar corrupción).
  Terminación con _píldoras envenenadas_ (objetos `None`) para detener a los consumidores cuando los productores terminan.

**Criterio de verificación:** todos los ítems producidos son consumidos (`producidos == consumidos == esperado`) → ✅.

**Endpoint:** `POST /api/run/ex3`  
**Parámetros:** `n_productores`, `n_consumidores`, `capacidad`, `items_por_productor`

---

### 4. 📋 El Tablón de Notas — Lectores-Escritores

**Contexto:** Varios estudiantes pueden leer al mismo tiempo, pero el profesor escribe con acceso exclusivo. Se incluye política para evitar inanición.

**Solución:** Se implementan dos variantes:

- **Prioridad a lectores:** el primer lector toma el semáforo de escritura, el último lo libera. Riesgo de inanición de escritores.
- **Prioridad a escritores:** se añade un torno (`turnstile`) que los escritores toman antes de solicitar el recurso, impidiendo que nuevos lectores entren.

Se monitoriza el máximo de lectores simultáneos y los logs confirman el patrón de acceso.

**Criterio de verificación:** logs muestran lectores concurrentes y escritor exclusivo → ✅.

**Endpoint:** `POST /api/run/ex4`  
**Parámetros:** `n_lectores`, `n_escritores`, `operaciones_lector`, `operaciones_escritor`, `prioridad` (`'lectores'` o `'escritores'`)

---

### 5. 🚦 El Punto de Encuentro — Barreras de Sincronización

**Contexto:** Varios procesos trabajan en fases. La Fase 2 no puede comenzar hasta que todos hayan terminado la Fase 1.

**Solución:** Clase `CustomBarrier` que implementa el algoritmo del enunciado: contador, mutex y variable de condición. El último hilo que llega despierta a todos (`notify_all`). Se usa una simulación con trabajo aleatorio en cada fase.

**Criterio de verificación:** ningún hilo inicia Fase 2 antes del broadcast → ✅.

**Endpoint:** `POST /api/run/ex5`  
**Parámetros:** `n_hilos`

---

## 🚀 Ejecución del proyecto

1. **Clonar el repositorio** y entrar a la carpeta:

   ```bash
   git clone <url-del-repo>
   cd ArquitecturaSistemasDistribuidos

   ```

2. **Crear un entorno virtual e instalar dependencias:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt

   ```

3. **Ejecutar el servidor Flask**
   ```bash
   python app.py
   ```
