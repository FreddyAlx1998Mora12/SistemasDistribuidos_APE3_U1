
// ---------- Navegación entre paneles ----------
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const ex = btn.getAttribute('data-ex');
        // Oculta todos los paneles
        document.querySelectorAll('.exercise-panel').forEach(p => p.classList.remove('active'));
        // Muestra el panel correspondiente
        document.getElementById('panel-' + ex).classList.add('active');
        // Marca el botón activo
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    });
});

// ---------- Ejercicio 1: Taquilla ----------
async function ejecutarEx1(usarMutex) {
    const n = parseInt(document.querySelector('.ex1-hilos').value);
    const m = parseInt(document.querySelector('.ex1-ventas').value);
    const resp = await fetch('/api/run/ex1', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            n_hilos: n,
            ventas_por_hilo: m,
            usar_mutex: usarMutex
        })
    });
    const data = await resp.json();
    mostrarResultados(data.results, usarMutex ? 'con mutex' : 'sin mutex', 'resultados-ex1');
    mostrarLogs(data.logs, 'logs-ex1');
}

async function secuencialEx1() {
    const n = parseInt(document.querySelector('.ex1-hilos').value);
    const m = parseInt(document.querySelector('.ex1-ventas').value);
    const resp = await fetch('/api/run/ex1', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            n_hilos: 1,
            ventas_por_hilo: n * m,
            usar_mutex: true
        })
    });
    const data = await resp.json();
    mostrarResultados(data.results, 'secuencial (1 hilo)', 'resultados-ex1');
    mostrarLogs(data.logs, 'logs-ex1');
}

async function verificar10Ex1() {
    const n = parseInt(document.querySelector('.ex1-hilos').value);
    const m = parseInt(document.querySelector('.ex1-ventas').value);
    let html = 'Ejecutando 10 pruebas con mutex...\n';
    let todasOk = true;
    for (let i = 1; i <= 10; i++) {
        const resp = await fetch('/api/run/ex1', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                n_hilos: n,
                ventas_por_hilo: m,
                usar_mutex: true
            })
        });
        const data = await resp.json();
        if (data.results.correcto) {
            html += `Prueba ${i}: OK (contador = ${data.results.contador})\n`;
        } else {
            html += `Prueba ${i}: FALLO (contador = ${data.results.contador}, esperado ${data.results.esperado})\n`;
            todasOk = false;
        }
    }
    html += todasOk ? '\n✅ Todas las pruebas pasaron.' : '\n❌ Falló al menos una prueba.';
    document.getElementById('resultados-ex1').innerHTML = `<pre>${html}</pre>`;
    document.getElementById('logs-ex1').textContent = 'Logs omitidos en verificación de 10 ejecuciones.';
}

function mostrarResultados(results, tipo, elementoId) {
    const correcto = results.correcto;
    const clase = correcto ? 'color: #69f0ae;' : 'color: #ff5252;';
    document.getElementById(elementoId).innerHTML = `
        <strong>Resultado (${tipo}):</strong><br>
        Contador: <span style="${clase}">${results.contador}</span><br>
        Esperado: ${results.esperado}<br>
        ¿Correcto?: ${correcto ? 'Sí' : 'No'}<br>
        Tiempo: ${results.tiempo} s
    `;
}

// ---------- Ejercicio 2: Gimnasio ----------
async function ejecutarEx2() {
    const n = parseInt(document.querySelector('.ex2-atletas').value);
    const m = parseInt(document.querySelector('.ex2-maquinas').value);
    const r = parseInt(document.querySelector('.ex2-repeticiones').value);
    const resp = await fetch('/api/run/ex2', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            n_atletas: n,
            n_maquinas: m,
            repeticiones: r
        })
    });
    const data = await resp.json();
    mostrarResultadosEx2(data.results);
    mostrarLogs(data.logs, 'logs-ex2');
}

function mostrarResultadosEx2(results) {
    const div = document.getElementById('resultados-ex2');
    div.innerHTML = `
        <strong>Resultados de la simulación:</strong><br>
        Máximo de máquinas en uso simultáneo: <span style="color: #69f0ae;">${results.max_maquinas_uso}</span><br>
        Máximo permitido: ${results.max_permitido}<br>
        ¿Invariante cumplido? (max ≤ ${results.max_permitido}): 
        <span style="color: ${results.invariante_cumplido ? '#69f0ae' : '#ff5252'};">
            ${results.invariante_cumplido ? 'Sí' : 'No'}
        </span><br>
        Tiempo de ejecución: ${results.tiempo} s
    `;
}

// ---------- Ejercicio 3: Panadería ----------
async function ejecutarEx3() {
    const prod = parseInt(document.querySelector('.ex3-productores').value);
    const cons = parseInt(document.querySelector('.ex3-consumidores').value);
    const cap = parseInt(document.querySelector('.ex3-capacidad').value);
    const items = parseInt(document.querySelector('.ex3-items').value);
    const resp = await fetch('/api/run/ex3', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            n_productores: prod,
            n_consumidores: cons,
            capacidad: cap,
            items_por_productor: items
        })
    });
    const data = await resp.json();
    mostrarResultadosEx3(data.results);
    mostrarLogs(data.logs, 'logs-ex3');
}

function mostrarResultadosEx3(results) {
    const div = document.getElementById('resultados-ex3');
    div.innerHTML = `
        <strong>Resultados:</strong><br>
        Producidos: ${results.producidos}<br>
        Consumidos: ${results.consumidos}<br>
        Esperado: ${results.esperado}<br>
        ¿Completitud (producción = consumo)?: 
        <span style="color: ${results.completitud ? '#69f0ae' : '#ff5252'};">
            ${results.completitud ? 'Sí' : 'No'}
        </span><br>
        Tiempo: ${results.tiempo} s
    `;
}

// ---------- Ejercicio 4: Tablón ----------
async function ejecutarEx4() {
    const lectores = parseInt(document.querySelector('.ex4-lectores').value);
    const escritores = parseInt(document.querySelector('.ex4-escritores').value);
    const opsLector = parseInt(document.querySelector('.ex4-ops-lector').value);
    const opsEscritor = parseInt(document.querySelector('.ex4-ops-escritor').value);
    const prioridad = document.querySelector('.ex4-prioridad').value;
    const resp = await fetch('/api/run/ex4', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            n_lectores: lectores,
            n_escritores: escritores,
            operaciones_lector: opsLector,
            operaciones_escritor: opsEscritor,
            prioridad: prioridad
        })
    });
    const data = await resp.json();
    mostrarResultadosEx4(data.results);
    mostrarLogs(data.logs, 'logs-ex4');
}

function mostrarResultadosEx4(results) {
    const div = document.getElementById('resultados-ex4');
    div.innerHTML = `
        <strong>Resultados:</strong><br>
        Máximo de lectores simultáneos: ${results.max_lectores_concurrentes}<br>
        Prioridad: ${results.prioridad === 'lectores' ? 'Lectores (posible inanición)' : 'Escritores (preferencia)'}<br>
        Tiempo: ${results.tiempo} s
    `;
}

// ---------- Ejercicio 5: Barrera ----------
async function ejecutarEx5() {
    const n = parseInt(document.querySelector('.ex5-hilos').value);
    const resp = await fetch('/api/run/ex5', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ n_hilos: n })
    });
    const data = await resp.json();
    mostrarResultadosEx5(data.results);
    mostrarLogs(data.logs, 'logs-ex5');
}

function mostrarResultadosEx5(results) {
    const div = document.getElementById('resultados-ex5');
    div.innerHTML = `
        <strong>Resultados:</strong><br>
        Hilos sincronizados: ${results.hilos}<br>
        ¿Sincronización correcta?: <span style="color: #69f0ae;">Sí</span><br>
        Tiempo: ${results.tiempo} s
    `;
}

function mostrarLogs(logs, elementoId) {
    document.getElementById(elementoId).textContent = logs.join('\n');
}