import pandas as pd

df_movimientos = pd.read_excel('input\\Formato Movimientos - Inventario.xlsx')
df_movimientos['NOMBRE'] = None
df_movimientos.rename(columns = {'Codigo Articulo ': 'CODIGO', 'Lote': 'LOTE', 'Fecha Vencimiento': 'FECHA VENCIMIENTO', 'Numero Serie': 'SERIE', 'Cantidad Movidad': 'CANTIDAD'}, inplace = True)
df_movimientos = df_movimientos[['CODIGO', 'NOMBRE', 'CANTIDAD', 'SERIE', 'LOTE', 'FECHA VENCIMIENTO', 'Tipo Movimiento', 'Fecha Movimiento']]

df_inventario_malo = pd.read_excel('input\\Inventario_A_malo.xlsx')
df_inventario_malo.rename(columns =  {'NOMBRE ARTICULO': 'NOMBRE', 'STOCK': 'CANTIDAD'}, inplace = True)

df_inventario_bueno = pd.read_excel('input\\Inventario_B_bueno.xlsx')

# Antes de comparar y ver si están las llaves, CODIGO, LOTE y FECHA DE VENCIMIENTO DEBEN ESTAR EN FORMATOS IGUALES.
df_movimientos['CODIGO'] = df_movimientos['CODIGO'].astype(str).apply(lambda x: x.strip())
df_inventario_malo['CODIGO'] = df_inventario_malo['CODIGO'].astype(str).apply(lambda x: x.strip())
df_inventario_bueno['CODIGO'] = df_inventario_bueno['CODIGO'].astype(str).apply(lambda x: x.strip())

df_movimientos['LOTE'] = df_movimientos['LOTE'].astype(str).apply(lambda x: x.strip())
df_inventario_malo['LOTE'] = df_inventario_malo['LOTE'].astype(str).apply(lambda x: x.strip())
df_inventario_bueno['LOTE'] = df_inventario_bueno['LOTE'].astype(str).apply(lambda x: x.strip())

df_movimientos['FECHA VENCIMIENTO'] = pd.to_datetime(df_movimientos['FECHA VENCIMIENTO'])
df_inventario_bueno['FECHA VENCIMIENTO'] = pd.to_datetime(df_inventario_bueno['FECHA VENCIMIENTO'], errors = 'coerce')
df_inventario_malo['FECHA VENCIMIENTO'] = pd.to_datetime(df_inventario_malo['FECHA VENCIMIENTO'], errors = 'coerce')


def hacer_inventario(df_movimientos, df_inventario_bueno):
    df_entradas = df_movimientos[df_movimientos['Tipo Movimiento'] == 'ENTRADA']
    df_salidas = df_movimientos[df_movimientos['Tipo Movimiento'] == 'SALIDA']

    inventario_inicial = df_inventario_bueno.groupby(by = ['CODIGO', 'LOTE']).sum()
    movimientos_entrada = df_entradas.groupby(by = ['CODIGO', 'LOTE']).sum()
    movimientos_salida = df_salidas.groupby(by = ['CODIGO', 'LOTE']).sum()

    # Primero se suman las entradas al inventario
    inventario_mas_entradas = inventario_inicial.add(movimientos_entrada, fill_value = 0)
    # luego, se restan las salidas al inventario
    inventario_total = inventario_mas_entradas.sub(movimientos_salida, fill_value = 0)

    with pd.ExcelWriter('resumen_inventario.xlsx', 'openpyxl') as writer:
        inventario_total.to_excel(writer, sheet_name = 'Inventario_total')
        inventario_inicial.to_excel(writer, sheet_name = 'Inventario_inicial')
        movimientos_entrada.to_excel(writer, sheet_name = 'Movimientos_entrada')
        movimientos_salida.to_excel(writer, sheet_name = 'Movimientos_salida')