# ==================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
# Curso: Fundamentos de Programación
# Fase 5 - Evaluación Final POA
# Problema 3 - Auditoría de Inventario
# Estudiante: Larieth Salazar León
# ==================================================

# Matriz de inventario: [codigo, nombre, stock_actual, stock_minimo]
inventario = [
    ["A101", "Teclado", 5, 10],
    ["A102", "Mouse", 15, 10],
    ["A103", "Monitor", 3, 8],
    ["A104", "Memoria USB", 20, 15],
    ["A105", "Impresora", 2, 5],
]


def calcular_pedido(stock_actual, stock_minimo):
    """Calcula cuántas unidades se deben pedir para alcanzar el stock mínimo."""
    if not isinstance(stock_actual, (int, float)) or not isinstance(stock_minimo, (int, float)):
        raise ValueError("El stock actual y el stock mínimo deben ser valores numéricos.")
    if stock_actual < 0 or stock_minimo < 0:
        raise ValueError("Los valores de stock no pueden ser negativos.")

    if stock_actual < stock_minimo:
        return stock_minimo - stock_actual
    return 0


def generar_reporte(matriz_inventario):
    """Muestra el reporte de reabastecimiento para cada artículo del inventario."""
    print("======================================")
    print("       REPORTE DE REABASTECIMIENTO")
    print("======================================")

    for articulo in matriz_inventario:
        codigo = articulo[0]
        nombre = articulo[1]
        stock_actual = articulo[2]
        stock_minimo = articulo[3]

        cantidad_pedir = calcular_pedido(stock_actual, stock_minimo)

        print("Código:", codigo)
        print("Artículo:", nombre)
        print("Stock actual:", stock_actual)
        print("Stock mínimo:", stock_minimo)
        print("Cantidad a pedir:", cantidad_pedir)
        print("--------------------------------------")


if __name__ == "__main__":
    generar_reporte(inventario)
