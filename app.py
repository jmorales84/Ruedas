from flask import Flask, render_template, request, redirect
import heapq
import itertools

app = Flask(__name__)

# -----------------------------------
# DATOS PRECARGADOS
# -----------------------------------

costos = {

    "Empresa 1": {
        "T": 20,
        "H": 30,
        "V": 20,
        "W": 40
    },

    "Empresa 2": {
        "T": 50,
        "H": 50,
        "V": 40,
        "W": 50
    },

    "Empresa 3": {
        "T": 60,
        "H": 55,
        "V": 50,
        "W": 60
    },

    "Empresa 4": {
        "T": 100,
        "H": 80,
        "V": 60,
        "W": 70
    }

}

tipos_llantas = [
    "T",
    "H",
    "V",
    "W"
]

contador = itertools.count()

# -----------------------------------
# HEURISTICA ADMISIBLE MEJORADA
# -----------------------------------

def heuristica(
    tipos_restantes,
    empresas_restantes
):

    h = 0

    empresas_disponibles = (
        empresas_restantes.copy()
    )

    for tipo in tipos_restantes:

        mejor_costo = float('inf')
        mejor_empresa = None

        for empresa in empresas_disponibles:

            if tipo in costos[empresa]:

                costo = costos[empresa][tipo]

                if costo < mejor_costo:

                    mejor_costo = costo
                    mejor_empresa = empresa

        if mejor_empresa:

            h += mejor_costo

            empresas_disponibles.remove(
                mejor_empresa
            )

    return h

# -----------------------------------
# ALGORITMO A*
# -----------------------------------

def algoritmo_a_estrella():

    empresas = list(costos.keys())

    cola = []

    estado_inicial = {

        "asignaciones": {},
        "empresas_usadas": [],
        "g": 0

    }

    h_inicial = heuristica(
        tipos_llantas,
        empresas
    )

    heapq.heappush(

        cola,

        (
            h_inicial,
            next(contador),
            estado_inicial
        )

    )

    mejor_solucion = None
    mejor_costo = float('inf')

    while cola:

        _, _, estado = heapq.heappop(
            cola
        )

        asignaciones = estado[
            "asignaciones"
        ]

        empresas_usadas = estado[
            "empresas_usadas"
        ]

        g_actual = estado["g"]

        # SI YA ES MAS CARO
        # SE PODA

        if g_actual >= mejor_costo:

            continue

        # META

        if len(asignaciones) == len(
            tipos_llantas
        ):

            if g_actual < mejor_costo:

                mejor_costo = g_actual

                mejor_solucion = (
                    asignaciones.copy()
                )

            continue

        siguiente_tipo = tipos_llantas[
            len(asignaciones)
        ]

        for empresa in empresas:

            if empresa not in empresas_usadas:

                if siguiente_tipo in costos[
                    empresa
                ]:

                    nuevas_asignaciones = (
                        asignaciones.copy()
                    )

                    nuevas_asignaciones[
                        siguiente_tipo
                    ] = empresa

                    nuevas_empresas = (
                        empresas_usadas + [
                            empresa
                        ]
                    )

                    nuevo_g = (

                        g_actual
                        + costos[empresa][
                            siguiente_tipo
                        ]

                    )

                    nuevos_tipos_restantes = [

                        t for t in tipos_llantas
                        if t not in
                        nuevas_asignaciones

                    ]

                    nuevas_empresas_restantes = [

                        e for e in empresas
                        if e not in
                        nuevas_empresas

                    ]

                    nuevo_h = heuristica(

                        nuevos_tipos_restantes,

                        nuevas_empresas_restantes

                    )

                    nuevo_f = (
                        nuevo_g + nuevo_h
                    )

                    nuevo_estado = {

                        "asignaciones":
                        nuevas_asignaciones,

                        "empresas_usadas":
                        nuevas_empresas,

                        "g":
                        nuevo_g

                    }

                    heapq.heappush(

                        cola,

                        (
                            nuevo_f,
                            next(contador),
                            nuevo_estado
                        )

                    )

    return {

        "solucion":
        mejor_solucion,

        "costo_total":
        mejor_costo

    }

# -----------------------------------
# PAGINA PRINCIPAL
# -----------------------------------

@app.route('/')

def index():

    resultado = algoritmo_a_estrella()

    return render_template(

        'index.html',

        costos=costos,

        tipos=tipos_llantas,

        resultado=resultado

    )

# -----------------------------------
# AGREGAR DATOS
# -----------------------------------

@app.route(
    '/agregar',
    methods=['POST']
)

def agregar():

    empresa = request.form[
        'empresa'
    ]

    tipo = request.form[
        'tipo'
    ]

    costo = int(
        request.form['costo']
    )

    if empresa not in costos:

        costos[empresa] = {}

    costos[empresa][tipo] = costo

    return redirect('/')

# -----------------------------------
# NUEVO TIPO
# -----------------------------------

@app.route(
    '/nuevo_tipo',
    methods=['POST']
)

def nuevo_tipo():

    tipo = request.form[
        'nuevo_tipo'
    ]

    tipo = tipo.upper()

    if tipo not in tipos_llantas:

        tipos_llantas.append(tipo)

    return redirect('/')

# -----------------------------------
# ELIMINAR
# -----------------------------------

@app.route(
    '/eliminar/<empresa>/<tipo>'
)

def eliminar(empresa, tipo):

    if empresa in costos:

        if tipo in costos[empresa]:

            del costos[empresa][tipo]

            if len(costos[empresa]) == 0:

                del costos[empresa]

    return redirect('/')

# -----------------------------------

if __name__ == '__main__':

    app.run(debug=True)