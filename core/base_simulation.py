# threading para hilos
# logging para registro de eventos
# queue para almacenar logs de forma segura entre hilos y ya sabemos que es
import threading
import logging
import logging.handlers
import queue

class SimulationLogger:
    """
    Configura un logger independiente que almacena los mensajes
    en una cola segura para su posterior recuperación.
    """
    def __init__(self, name):
        self.log_queue = queue.Queue()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Handler que encola objetos LogRecord
        self.queue_handler = logging.handlers.QueueHandler(self.log_queue)
        self.formatter = logging.Formatter(
            '[%(asctime)s.%(msecs)03d] %(threadName)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        self.queue_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.queue_handler)
        self.logger.propagate = False   # no envía al logger raíz

    def get_logs(self):
        """
        Extrae todos los registros formateados como cadenas.
        Los objetos LogRecord de la cola se convierten usando el formateador.
        """
        logs = []
        while not self.log_queue.empty():
            record = self.log_queue.get()
            logs.append(self.formatter.format(record))
        return logs


class BaseSimulation(threading.Thread):
    """
    Clase abstracta para todas las simulaciones.
    Hereda de Thread para ejecutarse en segundo plano si es necesario.
    """
    def __init__(self, exercise_name):
        super().__init__()
        self.exercise_name = exercise_name
        self.log_manager = SimulationLogger(exercise_name)
        self.logger = self.log_manager.logger
        self._stop_event = threading.Event()
        self.results = {}
        self.logs = []

    def run(self):
        self.logger.info(f"Inicio de simulación: {self.exercise_name}")
        try:
            self.run_simulation()
        except Exception as e:
            self.logger.exception("Error fatal en simulación")
            self.results['error'] = str(e)
        finally:
            self.logger.info(f"Fin de simulación: {self.exercise_name}")
            self.logs = self.log_manager.get_logs()

    def run_simulation(self):
        """
        Método que debe ser implementado por cada ejercicio.
        Dentro de este método se crean los hilos y se ejecuta
        la lógica de sincronización específica.
        """
        raise NotImplementedError("Implementar en subclase")

    def get_results_and_logs(self):
        """Devuelve los resultados y los logs acumulados."""
        return self.results, self.logs