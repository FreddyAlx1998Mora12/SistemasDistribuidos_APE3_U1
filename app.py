from flask import Flask, render_template, request, jsonify
from core.ex1_taquilla import TaquillaSimulation
from core.ex2_gimnasio import GimnasioSimulation
from core.ex3_panaderia import PanaderiaSimulation
from core.ex4_tablon import TablonSimulation
from core.ex5_barrera import BarreraSimulation

app = Flask(__name__)
# Cargar configuración desde un objeto Config en config.py
app.config.from_object('config.Config')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/run/ex1', methods=['POST'])
def run_ex1():
    data = request.get_json() or {}
    n_hilos = int(data.get('n_hilos', 5))
    m_ventas = int(data.get('ventas_por_hilo', 100000))
    usar_mutex = data.get('usar_mutex', True)

    sim = TaquillaSimulation(
        n_hilos=n_hilos,
        ventas_por_hilo=m_ventas,
        usar_mutex=usar_mutex
    )
    sim.start()
    sim.join()
    results, logs = sim.get_results_and_logs()
    return jsonify({'results': results, 'logs': logs})


@app.route('/api/run/ex2', methods=['POST'])
def run_ex2():
    data = request.get_json() or {}
    n_atletas = int(data.get('n_atletas', 8))
    n_maquinas = int(data.get('n_maquinas', 3))
    repeticiones = int(data.get('repeticiones', 3))

    sim = GimnasioSimulation(
        n_atletas=n_atletas,
        n_maquinas=n_maquinas,
        repeticiones=repeticiones
    )
    sim.start()
    sim.join()
    results, logs = sim.get_results_and_logs()
    return jsonify({'results': results, 'logs': logs})


@app.route('/api/run/ex3', methods=['POST'])
def run_ex3():
    data = request.get_json() or {}
    n_productores = int(data.get('n_productores', 2))
    n_consumidores = int(data.get('n_consumidores', 3))
    capacidad = int(data.get('capacidad', 10))
    items_por_productor = int(data.get('items_por_productor', 5))

    sim = PanaderiaSimulation(
        n_productores=n_productores,
        n_consumidores=n_consumidores,
        capacidad=capacidad,
        items_por_productor=items_por_productor
    )
    sim.start()
    sim.join()
    results, logs = sim.get_results_and_logs()
    return jsonify({'results': results, 'logs': logs})


@app.route('/api/run/ex4', methods=['POST'])
def run_ex4():
    data = request.get_json() or {}
    n_lectores = int(data.get('n_lectores', 5))
    n_escritores = int(data.get('n_escritores', 2))
    op_lector = int(data.get('operaciones_lector', 5))
    op_escritor = int(data.get('operaciones_escritor', 3))
    prioridad = data.get('prioridad', 'lectores')

    sim = TablonSimulation(
        n_lectores=n_lectores,
        n_escritores=n_escritores,
        operaciones_lector=op_lector,
        operaciones_escritor=op_escritor,
        prioridad=prioridad
    )
    sim.start()
    sim.join()
    results, logs = sim.get_results_and_logs()
    return jsonify({'results': results, 'logs': logs})


@app.route('/api/run/ex5', methods=['POST'])
def run_ex5():
    data = request.get_json() or {}
    n_hilos = int(data.get('n_hilos', 5))

    sim = BarreraSimulation(n_hilos=n_hilos)
    sim.start()
    sim.join()
    results, logs = sim.get_results_and_logs()
    return jsonify({'results': results, 'logs': logs})


if __name__ == '__main__':
    app.run(debug=True, threaded=True)

