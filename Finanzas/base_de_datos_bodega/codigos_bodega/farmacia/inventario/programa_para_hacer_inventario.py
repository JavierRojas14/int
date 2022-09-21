import pandas as pd

df_traductor = pd.read_excel('input\\asociacion_bodega_sigcom.xlsx')
df_traductor.set_index('Cod. Bodega', inplace = True)

#######################################################################

def realizar_inventario():
    df_movimientos = pd.read_excel('input\\movimientos.xlsx')
    df_movimientos.set_index('CODIGO ARTICULO', inplace = True)

    inventario = pd.DataFrame(df_movimientos.groupby(by = ['CODIGO ARTICULO'])['CANTIDAD'].sum())

    movimientos_traducidos = pd.merge(df_movimientos, df_traductor, how = 'left', left_index = True, right_index = True)
    inventario_traducido = pd.merge(inventario, df_traductor, how = 'left', left_index = True, right_index = True)

    with pd.ExcelWriter('inventario.xlsx') as writer:
        inventario_traducido.to_excel(writer, sheet_name = 'inventario')
        movimientos_traducidos.to_excel(writer, sheet_name = 'movimientos_traducidos')


realizar_inventario()
        