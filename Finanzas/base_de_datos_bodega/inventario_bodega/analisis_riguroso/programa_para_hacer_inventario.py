import pandas as pd
import os

def limpiar_columnas_identificadoras(df):
    df['CODIGO'] = df['CODIGO'].astype(str).apply(lambda x: x.strip())
    df['LOTE'] = df['LOTE'].astype(str).apply(lambda x: x.strip())
    df['FECHA VENCIMIENTO'] = pd.to_datetime(df['FECHA VENCIMIENTO'], errors = 'coerce')

    return df

def hacer_inventario():
    contenido_input = os.listdir('input')
    print(list(enumerate(contenido_input)))

    archivo_movimientos = contenido_input[int(input(f'¿Cuál archivo de movimientos quieres ocupar? '))]
    archivo_inventario_inicial = contenido_input[int(input(f'¿Cuál archivo de inventario inicial quieres ocupar? '))]

    df_movimientos = pd.read_excel(f'input\\{archivo_movimientos}')
    df_movimientos.rename(columns = {'CODIGO ARTICULO': 'CODIGO', 'NUMERO LOTE': 'LOTE', 'NUMERO SERIE': 'SERIE', 'CANTIDAD MOVIDA': 'CANTIDAD', 'NOMBRE ARTICULO': 'NOMBRE'}, inplace = True)
    df_movimientos = df_movimientos[['CODIGO', 'NOMBRE', 'CANTIDAD', 'SERIE', 'LOTE', 'FECHA VENCIMIENTO', 'TIPO MOVIMIENTO', 'FECHA MOVIMIENTO']]

    df_inventario = pd.read_excel(f'input\\{archivo_inventario_inicial}')

    df_movimientos = limpiar_columnas_identificadoras(df_movimientos)
    df_inventario = limpiar_columnas_identificadoras(df_inventario)

    df_entradas = df_movimientos[df_movimientos['TIPO MOVIMIENTO'] == 'ENTRADA']
    df_salidas = df_movimientos[df_movimientos['TIPO MOVIMIENTO'] == 'SALIDA']

    inventario_inicial = df_inventario.groupby(by = ['CODIGO', 'LOTE']).sum()
    movimientos_entrada = df_entradas.groupby(by = ['CODIGO', 'LOTE']).sum()
    movimientos_salida = df_salidas.groupby(by = ['CODIGO', 'LOTE']).sum()

    # Primero se suman las entradas al inventario
    inventario_mas_entradas = inventario_inicial.add(movimientos_entrada, fill_value = 0)
    # luego, se restan las salidas al inventario
    inventario_total = inventario_mas_entradas.sub(movimientos_salida, fill_value = 0)

    inventario_inicial.reset_index(inplace = True)
    movimientos_entrada.reset_index(inplace = True)
    movimientos_salida.reset_index(inplace = True)
    inventario_total.reset_index(inplace = True)

    with pd.ExcelWriter('resumen_inventario.xlsx', 'openpyxl') as writer:
        inventario_total.to_excel(writer, sheet_name = 'Inventario_total')
        inventario_inicial.to_excel(writer, sheet_name = 'Inventario_inicial')
        movimientos_entrada.to_excel(writer, sheet_name = 'Movimientos_entrada')
        movimientos_salida.to_excel(writer, sheet_name = 'Movimientos_salida')


hacer_inventario()