import numpy as np
import pandas as pd

from constantes import DICCIONARIO_UNIDADES_A_DESGLOSAR

df = pd.read_excel('item_cc_rellenados_completos.xlsx')
tabla_din = pd.pivot_table(df, values = 'Neto Total', index = 'CC SIGCOM', columns = 'Item SIGCOM', aggfunc=np.sum)



total = pd.DataFrame()
for item_desglose, a_desglosar in DICCIONARIO_UNIDADES_A_DESGLOSAR.items():
    if item_desglose in tabla_din.index:
        filas_a_agregar = []
        valores_antiguos = tabla_din.loc[item_desglose]
        for desglose in a_desglosar:
            print(f'El item {item_desglose} lo estamos desglosando en {desglose}')
            porcentaje = input('¿Qué porcentaje tiene este item?: ')
            porcentaje = porcentaje.replace(',', '.')
            porcentaje = float(porcentaje)
            porcentaje_cantidad = valores_antiguos * porcentaje
            porcentaje_cantidad.name = desglose

            filas_a_agregar.append(porcentaje_cantidad)

        valores_antiguos.name = 'Total'
        filas_a_agregar.append(valores_antiguos)
        df_super = pd.DataFrame(filas_a_agregar)

    else:
        print('No hubo gastos en este item.')

    total = pd.concat([total, df_super])
    total.to_excel('desgloses.xlsx')
    