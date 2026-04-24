import threading
# importamos la clase base para heredar y aprovechar su sistema de logging y estructura de simulación
from .base_simulation import BaseSimulation

class TaquillaSimulation(BaseSimulation):
    """
    Simula la venta concurrente de boletos.
    - Con mutex: contador final = N x M
    - Sin mutex: es probable el valor incorrecto (condición de carrera)
    """
    def __init__(self, n_hilos=50, ventas_por_hilo=100, usar_mutex=True):
        super().__init__("Taquilla")
        self.n_hilos = n_hilos
        self.ventas_por_hilo = ventas_por_hilo
        self.usar_mutex = usar_mutex
        self.contador = 0
        self.lock = threading.Lock()

    def venta_segura(self):
        """Sección crítica protegida por mutex."""
        with self.lock:
            # Solo registramos cada 100 operaciones para no saturar
            if self.contador % 100 == 0:
                self.logger.info(f"Mutex adquirido, contador actual: {self.contador}")
            tmp = self.contador
            tmp += 1
            self.contador = tmp

    def venta_insegura(self):
        """Operación sin protección, susceptible a condición de carrera."""
        if self.contador % 100 == 0:  # Cada 100 incrementos, logueamos el estado actual
            self.logger.info(f"Venta insegura, contador actual: {self.contador}")
        tmp = self.contador
        tmp += 1
        self.contador = tmp

    def run_simulation(self):
        # Barrera para que todos los hilos arranquen simultáneamente
        barrera = threading.Barrier(self.n_hilos + 1)
        hilos = []
        for i in range(self.n_hilos):
            t = threading.Thread(
                target=self._trabajador, args=(barrera,),
                name=f"Taquilla-{i}"
            )
            hilos.append(t)

        import time
        inicio = time.perf_counter()
        for t in hilos:
            t.start()

        barrera.wait()   # todos listos, comienzan

        for t in hilos:
            t.join()
        fin = time.perf_counter()

        esperado = self.n_hilos * self.ventas_por_hilo
        self.results = {
            'contador': self.contador,
            'esperado': esperado,
            'correcto': self.contador == esperado,
            'tiempo': round(fin - inicio, 4),
            'modo': 'mutex' if self.usar_mutex else 'sin_mutex'
        }

    def _trabajador(self, barrera):
        barrera.wait()
        venta = self.venta_segura if self.usar_mutex else self.venta_insegura
        for _ in range(self.ventas_por_hilo):
            venta()