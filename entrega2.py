import datetime
import itertools
from simpleai.search import CspProblem, min_conflicts
from simpleai.search.csp import _find_conflicts


def armar_problema_csp(colores_disponibles, contenidos_parciales):
    nombre = "frasco_"
    dominios = {}
    frascos = []
    lista_colores_disponibles = list(colores_disponibles)
    for i, color in enumerate(colores_disponibles):
        nombre_variable = f"{nombre}{i+1}"
        variable = nombre_variable
        frascos.append(variable)

    for i, frasco in enumerate(frascos):
        dominios[frasco] = []
        if contenidos_parciales and len(contenidos_parciales) > i:
            contenidos_parciales_frasco = contenidos_parciales[i]
            lista_base = []
            lista_base.extend(contenidos_parciales_frasco)
            dominio_frasco = []
            for colores in set(itertools.combinations_with_replacement(lista_base + lista_colores_disponibles, 4)):
                if len(set(colores)) <= 4 and not all(color == colores[0] for color in colores):
                    if colores[:(len(contenidos_parciales_frasco))] == contenidos_parciales_frasco[:(len(contenidos_parciales_frasco))]:
                        dominios[frasco].append(colores)
        else:
            dominio_frasco = []
            for colores in itertools.product(colores_disponibles, repeat=4):
                if len(set(colores)) <= 4 and not all(color == colores[0] for color in colores):
                    dominios[frasco].append(colores)


    def restricciones_capacidad(vars, vals):
        return len(vals) == 4

    def restricciones_colores(vars, vals):
        return len(set(vals)) <= 4 and not all(color == vals[0] for color in vals)

    def restricciones_inicio(vars, vals):
        return len(set(vals)) > 1

    def restricciones_distribucion_colores(vars, vals):
        for color in colores_disponibles:
            if not any(color == segmento for segmento in vals):
                return False
        return True

    def restricciones_adyacencia(vars, vals):
        frasco_i, frasco_j = vals
        var1, var2 = vars
        pos1 = int(var1[-1])
        pos2 = int(var2[-1])
        if (pos1-pos2) == -1 or (pos1-pos2) == 1:
            if frasco_i != frasco_j:
                colores_frasco_i = set(frasco_i)
                colores_frasco_j = set(frasco_j)
                return len(colores_frasco_i.intersection(colores_frasco_j)) >= 1 and len(
                    colores_frasco_i.union(colores_frasco_j)) <= 6

    def restricciones_unicidad(vars, vals):
        frasco_i, frasco_j = vals
        if frasco_i != frasco_j:
            return frasco_i != frasco_j

    def restriccion_max_apariciones_color_con_vals(vars, vals):
        apariciones_colores = {}
        for combinacion in vals:
            for color in combinacion:
                if color not in apariciones_colores:
                    apariciones_colores[color] = 0
                apariciones_colores[color] += 1
                if apariciones_colores[color] > 4:
                    return False
        return True

    def restriccion_color_en_fondo(vars, vals):
        bool = True
        for color in colores_disponibles:
            for frasco in vals:
                segmentos_fondo = 0
                if frasco[0] == color:
                    segmentos_fondo += 1

                if segmentos_fondo == 4:
                    bool = False
        return bool

    def restriccion_contenidos_parciales(vars, vals):
        val = vals
        var = vars
        if contenidos_parciales:
            for i, frasco_parcial in enumerate(contenidos_parciales):
                if var[-1] == i:
                    return val[:(len(frasco_parcial)-1)] == frasco_parcial[:(len(frasco_parcial)-1)]

    restricciones = []

    for frasco in frascos:
        restricciones.append((frasco, restricciones_capacidad))
        restricciones.append((frasco, restricciones_colores))
        restricciones.append((frasco, restricciones_inicio))
        restricciones.append((frasco, restricciones_distribucion_colores))
        restricciones.append((frasco, restriccion_contenidos_parciales))

    restricciones.append((frascos, restriccion_max_apariciones_color_con_vals))
    restricciones.append((frascos, restriccion_color_en_fondo))

    for i, frasco_i in enumerate(frascos):
        for j, frasco_j in enumerate(frascos):
            if abs(i - j) == 1:
                restricciones.append(((frasco_i, frasco_j), restricciones_adyacencia))

    for i in range(len(frascos)):
        for j in range(i + 1, len(frascos)):
            restricciones.append(((frascos[i], frascos[j]), restricciones_unicidad))

    return CspProblem(frascos, dominios, restricciones)


def armar_nivel(colores, contenidos_parciales):
    problema = armar_problema_csp(colores, contenidos_parciales)
    inicio = datetime.datetime.now()
    asignacion = min_conflicts(problema, iterations_limit=100)
    tiempo = (datetime.datetime.now() - inicio).total_seconds()

    conflictos = _find_conflicts(problema, asignacion)
    print("Numero de conflictos en la solucion: {}".format(len(conflictos)))
    print("Tiempo transcurrido: {} segundos".format(tiempo))
    print(asignacion)
    lista_dominios = []
    for clave, valor in asignacion.items():
        lista_dominios.append(valor)
    return lista_dominios


if __name__ == "__main__":
    frascos = armar_nivel(
        colores=["rojo", "verde", "azul", "amarillo"],  # 4 colores, por lo que deberemos armar 4 frascos
        contenidos_parciales=[
            ("verde", "azul", "rojo", "rojo"),  # el frasco 1 ya está completo
            ("verde", "rojo"),  # el frasco 2 ya tiene dos segmentos completos, hay que rellenar el resto
            # los frascos 3 y 4 no vinieron definidos, por lo que tenemos más libertad en ellos
        ],
    )
