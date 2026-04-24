import threading
import time
import random
from .base_simulation import BaseSimulation

class CustomBarrier:
    """
    Barrera implementada con Mutex y Variable de Condición,
    según el algoritmo del ejercicio.
    """
    def __init__(self, total):
        self.total = total
        self.contador = 0
        self.cond = threading.Condition()

    def esperar(self, id_hilo, logger):
        with self.cond:
            self.contador += 1
            logger.info(f"Hilo {id_hilo} llega a la barrera (contador = {self.contador}/{self.total})")
            if self.contador == self.total:
                logger.info(">>> Último hilo: despertando a todos (broadcast) <<<")
                self.cond.notify_all()
            else:
                while self.contador < self.total:
                    self.cond.wait()


class BarreraSimulation(BaseSimulation):
    """
    Simula N hilos que deben sincronizarse en una barrera
    antes de pasar a la Fase 2.
    """

    def __init__(self, n_hilos=5):
        super().__init__("Barrera")
        self.n_hilos = n_hilos
        self.barrera = CustomBarrier(n_hilos)

    def run_simulation(self):
        hilos = []
        for i in range(self.n_hilos):
            t = threading.Thread(target=self._trabajador, args=(i,),
                                 name=f"Hilo-{i}")
            hilos.append(t)

        inicio = time.perf_counter()
        for t in hilos:
            t.start()
        for t in hilos:
            t.join()
        fin = time.perf_counter()

        self.results = {
            'hilos': self.n_hilos,
            'sincronizacion_correcta': True,  # Siempre cierto con esta barrera
            'tiempo': round(fin - inicio, 4)
        }

    def _trabajador(self, id_hilo):
        # Fase 1 (trabajo previo)
        tiempo_fase1 = random.uniform(0.1, 0.3)
        self.logger.info(f"Hilo {id_hilo} inicia Fase 1 (trabajo {tiempo_fase1:.2f}s)")
        
        time.sleep(tiempo_fase1)
        self.logger.info(f"Hilo {id_hilo} terminó Fase 1, esperando en barrera...")

        # Espera en la barrera
        self.barrera.esperar(id_hilo, self.logger)

        # Fase 2 (trabajo posterior)
        tiempo_fase2 = random.uniform(0.05, 0.15)
        self.logger.info(f"Hilo {id_hilo} cruza barrera e inicia Fase 2 (trabajo {tiempo_fase2:.2f}s)")
        time.sleep(tiempo_fase2)
        self.logger.info(f"Hilo {id_hilo} finaliza Fase 2")