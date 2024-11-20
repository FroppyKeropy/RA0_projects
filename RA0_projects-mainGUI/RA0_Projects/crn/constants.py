import numpy as np

lab1_data = {
    550 : 0,
    600 : 0,
    625 : 0,
    650 : 695,
    675 : 1537,
    700 : 1592.333,
    750 : 1590,
    775 : 1626,
    825 : 1759.333,
    850 : 2037.666
}

lab2_data = {
    "Co60" : {
        False : 2861,
        "Papel" : 2632,
        "45mg" : 1773,
        "290mg" : 572.2,
        "1100mg" : 28.61
    },
    "Na22" : {
        False : 16962,
        "Papel" : 15605,
        "45mg" : 10516,
        "290mg" : 3392,
        "1100mg" : 169.62
    }
}

lab3_data = {
    "Co60" : {
        False : 2899.666,
        "Aluminio" : 3276.622,
        "Hierro" : 3537.59,
        "Zinc" : 3624.582,
        "Cadmio" : 3914,
        "Plomo" : 4204
    }
}


"""07/06/2024 - 6/11/2024: Creacion e implementacion del lab4 -Mariano Ceballos y Facundo Ceballos"""


def interpolate_values(data, step=1):
    x_vals = list(data.keys())
    y_vals = list(data.values())

    # Creacion de valores intermedios
    x_new = np.round(np.arange(min(x_vals), max(x_vals) + step, step),3)

    # Interpolación lineal ded valores
    y_new = np.round(np.interp(x_new, x_vals, y_vals),3)

    # Creacion del diccionario con valores aproximados
    interpolated_data = dict(zip(x_new, y_new))
    return interpolated_data


lab4_data = {
    # deciSegundo:Counts(microSievert/hora)
    0: 0,
    20: 0.336,
    40: 0.367,
    60: 0.195,
    80: 0.069,
    100: 0.018,
    120: 0.004,
    140: 0.001
}

interpolated_lab4_data = interpolate_values(lab4_data)
