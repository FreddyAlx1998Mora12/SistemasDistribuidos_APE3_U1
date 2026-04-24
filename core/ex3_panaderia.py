import threading
from .base_simulation import BaseSimulation

class PanaderiaSimulation(BaseSimulation):
    """
    Simula el problema Productor-Consumidor en una panadería.
    Usa dos semáforos (espacios_vacios, panes_listos) y un mutex para la vitrina.
    """

    def __init__(self, n_productores=2, n_consumidores=3,
                 capacidad=10, items_por_productor=5):
        super().__init__("Panaderia")
        self.n_productores = n_productores
        self.n_consumidores = n_consumidores
        self.capacidad = capacidad
        self.items_por_productor = items_por_productor

        # Sincronización
        self.espacios_vacios = threading.Semaphore(capacidad)  # huecos libres
        self.panes_listos = threading.Semaphore(0)            # items disponibles
        self.mutex_vitrina = threading.Lock()                 # exclusión mutua

        self.buffer = []  # vitrina compartida

        # Contadores para verificación
        self.producidos = 0
        self.consumidos = 0
        self.lock_contadores = threading.Lock()

    def run_simulation(self):
        # Crear hilos productores y consumidores
        productores = [
            threading.Thread(target=self._productor, args=(i,),
                             name=f"Panadero-{i}")
            for i in range(self.n_productores)
        ]
        consumidores = [
            threading.Thread(target=self._consumidor, args=(i,),
                             name=f"Cliente-{i}")
            for i in range(self.n_consumidores)
        ]

        import time
        inicio = time.perf_counter()
        for t in productores + consumidores:
            t.start()

        # Esperar a que todos los productores terminen
        for t in productores:
            t.join()

        # Insertar píldoras envenenadas para detener a los consumidores
        for _ in range(self.n_consumidores):
            self.espacios_vacios.acquire()
            with self.mutex_vitrina:
                self.buffer.append(None)
                self.logger.info("Píldora envenenada añadida a la vitrina")
            self.panes_listos.release()

        # Esperar a que los consumidores terminen
        for t in consumidores:
            t.join()
        fin = time.perf_counter()

        # Cálculo de resultados
        with self.lock_contadores:
            total_prod = self.producidos
            total_cons = self.consumidos

        self.results = {
            'producidos': total_prod,
            'consumidos': total_cons,
            'esperado': self.n_productores * self.items_por_productor,
            'completitud': total_prod == total_cons,
            'tiempo': round(fin - inicio, 4)
        }

    def _productor(self, pid):
        for i in range(self.items_por_productor):
            # Producir un pan
            pan = f"Pan-{pid}-{i}"
            # Esperar un espacio vacío (puede bloquear)
            self.espacios_vacios.acquire()
            # Adquirir mutex para modificar la vitrina
            with self.mutex_vitrina:
                self.buffer.append(pan)
                self.logger.info(
                    f"{threading.current_thread().name} produce {pan} "
                    f"→ vitrina: {len(self.buffer)}/{self.capacidad}"
                )
            # Señalar que hay un nuevo pan listo
            self.panes_listos.release()

            # Registrar producción
            with self.lock_contadores:
                self.producidos += 1

    def _consumidor(self, cid):
        while True:
            # Esperar un pan listo (puede bloquear)
            self.panes_listos.acquire()
            # Adquirir mutex para extraer de la vitrina
            with self.mutex_vitrina:
                pan = self.buffer.pop(0)
                if pan is None:  # Píldora envenenada
                    self.logger.info(
                        f"{threading.current_thread().name} recibe veneno y termina"
                    )
                    # No hay que liberar espacios_vacios, porque la píldora no ocupa lugar real
                else:
                    self.logger.info(
                        f"{threading.current_thread().name} consume {pan} "
                        f"→ vitrina: {len(self.buffer)}/{self.capacidad}"
                    )
            if pan is None:
                # Salimos del bucle sin señalizar espacios_vacios
                break

            # Señalizar que hay un espacio vacío
            self.espacios_vacios.release()

            # Registrar consumo
            with self.lock_contadores:
                self.consumidos += 1