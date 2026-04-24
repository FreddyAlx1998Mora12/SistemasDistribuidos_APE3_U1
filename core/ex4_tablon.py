import threading
import time
from .base_simulation import BaseSimulation

class TablonSimulation(BaseSimulation):
    """
    Simula el problema de Lectores-Escritores en un tablón de notas.
    Soporta dos variantes: prioridad a lectores ('lectores') y prioridad a escritores ('escritores').
    """

    def __init__(self, n_lectores=5, n_escritores=2,
                 operaciones_lector=5, operaciones_escritor=3,
                 prioridad='lectores'):
        super().__init__("Tablon")
        self.n_lectores = n_lectores
        self.n_escritores = n_escritores
        self.operaciones_lector = operaciones_lector
        self.operaciones_escritor = operaciones_escritor
        self.prioridad = prioridad   # 'lectores' o 'escritores'

        # Mecanismos de sincronización
        self.cant_lectores = 0
        self.mutex_lectores = threading.Lock()
        self.sem_escritor = threading.Semaphore(1)    # recurso exclusivo
        if prioridad == 'escritores':
            self.turnstile = threading.Semaphore(1)   # torno para prioridad escritor

        # Estadísticas y monitoreo
        self.max_lectores_concurrentes = 0
        self.estadisticas_lock = threading.Lock()
        self.lectores_activos = 0

    def run_simulation(self):
        lectores = [
            threading.Thread(target=self._lector, args=(i,),
                             name=f"Lector-{i}")
            for i in range(self.n_lectores)
        ]
        escritores = [
            threading.Thread(target=self._escritor, args=(i,),
                             name=f"Escritor-{i}")
            for i in range(self.n_escritores)
        ]

        inicio = time.perf_counter()
        for t in lectores + escritores:
            t.start()
        for t in lectores + escritores:
            t.join()
        fin = time.perf_counter()

        self.results = {
            'max_lectores_concurrentes': self.max_lectores_concurrentes,
            'prioridad': self.prioridad,
            'tiempo': round(fin - inicio, 4)
        }

    def _lector(self, lid):
        for _ in range(self.operaciones_lector):
            if self.prioridad == 'lectores':
                # Protocolo con prioridad a lectores
                with self.mutex_lectores:
                    self.cant_lectores += 1
                    if self.cant_lectores == 1:
                        self.sem_escritor.acquire()
                # Lectura
                self._iniciar_lectura(lid)
                # Salida
                with self.mutex_lectores:
                    self.cant_lectores -= 1
                    if self.cant_lectores == 0:
                        self.sem_escritor.release()
            else:  # prioridad a escritores
                self.turnstile.acquire()
                self.turnstile.release()      # paso rápido, no bloquea a lectores detrás
                with self.mutex_lectores:
                    self.cant_lectores += 1
                    if self.cant_lectores == 1:
                        self.sem_escritor.acquire()
                # Lectura
                self._iniciar_lectura(lid)
                # Salida
                with self.mutex_lectores:
                    self.cant_lectores -= 1
                    if self.cant_lectores == 0:
                        self.sem_escritor.release()
            # Simular tiempo de lectura
            time.sleep(0.01)   # pequeño delay para ver concurrencia

    def _iniciar_lectura(self, lid):
        with self.estadisticas_lock:
            self.lectores_activos += 1
            if self.lectores_activos > self.max_lectores_concurrentes:
                self.max_lectores_concurrentes = self.lectores_activos
        self.logger.info(f"{threading.current_thread().name} comienza a leer (lectores activos: {self.lectores_activos})")

        # Simular tiempo de lectura
        time.sleep(0.02)

        with self.estadisticas_lock:
            self.lectores_activos -= 1
        self.logger.info(f"{threading.current_thread().name} termina de leer (lectores activos: {self.lectores_activos})")

    def _escritor(self, eid):
        for _ in range(self.operaciones_escritor):
            if self.prioridad == 'lectores':
                self.sem_escritor.acquire()
                self._escribir(eid)
                self.sem_escritor.release()
            else:  # prioridad a escritores
                self.turnstile.acquire()        # bloquea nuevos lectores
                self.sem_escritor.acquire()     # espera lectores actuales
                self.turnstile.release()        # permite nuevos lectores en turnstile (se bloquearán en sem_escritor)
                self._escribir(eid)
                self.sem_escritor.release()

    def _escribir(self, eid):
        self.logger.info(f"{threading.current_thread().name} comienza a escribir (exclusivo)")
        # Simular tiempo de escritura
        
        time.sleep(0.05)
        self.logger.info(f"{threading.current_thread().name} termina de escribir")