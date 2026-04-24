import threading
import random
from .base_simulation import BaseSimulation

class MiSemaforo:
    """
    Implementación de un semáforo general de conteo
    usando Mutex y Variable de Condición, según el algoritmo del ejercicio.
    """
    def __init__(self, valor_inicial):
        self.cond = threading.Condition()       # incluye su propio Lock
        self.contador = valor_inicial

    def esperar(self):
        """Protocolo de entrada: espera si contador==0, luego decrementa."""
        with self.cond:
            while self.contador == 0:
                self.cond.wait()       # libera el lock y se duerme
            self.contador -= 1

    def senial(self):
        """Protocolo de salida: incrementa contador y despierta a un hilo."""
        with self.cond:
            self.contador += 1
            self.cond.notify()


class GimnasioSimulation(BaseSimulation):
    """
    Simula el acceso concurrente de N atletas a M máquinas.
    Usa MiSemaforo para controlar la concurrencia.
    """

    def __init__(self, n_atletas=8, n_maquinas=3, repeticiones=3):
        super().__init__("Gimnasio")
        self.n_atletas = n_atletas
        self.n_maquinas = n_maquinas
        self.repeticiones = repeticiones
        self.semaforo = MiSemaforo(n_maquinas)

        # Seguimiento de máquinas en uso para verificar invariante
        self.en_uso = 0
        self.lock_monitor = threading.Lock()
        self.max_uso = 0

    def run_simulation(self):
        atletas = []
        for i in range(self.n_atletas):
            t = threading.Thread(
                target=self._atleta, args=(i,),
                name=f"Atleta-{i}"
            )
            atletas.append(t)

        import time
        inicio = time.perf_counter()
        for t in atletas:
            t.start()
        for t in atletas:
            t.join()
        fin = time.perf_counter()

        self.results = {
            'max_maquinas_uso': self.max_uso,
            'max_permitido': self.n_maquinas,
            'invariante_cumplido': self.max_uso <= self.n_maquinas,
            'tiempo': round(fin - inicio, 4)
        }

    def _atleta(self, id_atleta):
        for ronda in range(self.repeticiones):
            # Solicitar máquina (puede bloquear)
            self.logger.info(f"Atleta {id_atleta} espera máquina (ronda {ronda})")
            self.semaforo.esperar()

            # Registrar inicio de uso
            with self.lock_monitor:
                self.en_uso += 1
                if self.en_uso > self.max_uso:
                    self.max_uso = self.en_uso
                uso_actual = self.en_uso
            self.logger.info(f"Atleta {id_atleta} ENTRA a entrenar (máquinas ocupadas: {uso_actual})")

            # Simular tiempo de uso (entre 0.2 y 0.5 segundos)
            import time
            time.sleep(random.uniform(0.2, 0.5))

            # Registrar fin de uso
            with self.lock_monitor:
                self.en_uso -= 1
                uso_actual = self.en_uso
            self.logger.info(f"Atleta {id_atleta} SALE (máquinas ocupadas: {uso_actual})")

            # Liberar máquina
            self.semaforo.senial()