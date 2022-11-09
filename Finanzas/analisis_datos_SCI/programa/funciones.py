'''
Este programa permite analizar los movimientos de entrada/salida del SCI. El objetivo de este
programa es organizar los artículos según su porcentaje de salida, y así identificar los que tienen
más movimientos. 

Se obtiene un cuociente entre las Salidas/Entradas. Este es un porcentaje de movimientos. Por 
ejemplo:

- Un Valor de 0.86 significa que el 86% de los artículos han salido.

Para este efecto, se genera una tabla del estilo:
Codigo_Articulo | Nombre_Articulo | Entradas | Salidas

Lo anterior se logra agrupando las tablas según su código. Los códigos que SÓlO tienen salidas, y 
0 entradas, significa que en años anteriores tuvieron una entrada. Estos casos serán revisados 
después.
'''

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("darkgrid")
pd.options.display.float_format = '{:,.2f}'.format





def separar_por_cuartil(df_a_separar, columna_a_separar):
    qmin = df_a_separar[columna_a_separar].quantile(0)
    q1 = df_a_separar[columna_a_separar].quantile(0.25)
    q2 = df_a_separar[columna_a_separar].quantile(0.5)
    q3 = df_a_separar[columna_a_separar].quantile(0.75)
    qmax = df_a_separar[columna_a_separar].quantile(1)

    df_min_q1 = df_a_separar.query(
        f'`{columna_a_separar}` >= @qmin and `{columna_a_separar}` < @q1')
    df_q1_q2 = df_a_separar.query(
        f'`{columna_a_separar}` >= @q1 and `{columna_a_separar}` < @q2')
    df_q2_q3 = df_a_separar.query(
        f'`{columna_a_separar}` >= @q2 and `{columna_a_separar}` < @q3')
    df_q3_max = df_a_separar.query(
        f'`{columna_a_separar}` >= @q3 and `{columna_a_separar}` <= @qmax')

    return (df_min_q1, df_q1_q2, df_q2_q3, df_q3_max)








def analisis_global_y_cuartil(df_agrupada, eje_x_agrupado):
    imagenes_a_guardar = {}
    dfs_a_guardar = {}

    fig_rank_global = rankear_y_plottear(
        df_agrupada, 'Porcentaje_salidas', eje_x_agrupado,
        'Gasto por Servicio Global - Porcentaje_salidas', 10)
    fig_distribucion_global = analizar_distribucion_de_datos(
        df_agrupada, 'Porcentaje_salidas',
        'Distribución Gasto Porcentaje_salidas por Servicio Global')
    imagenes_a_guardar['Global'] = [fig_rank_global, fig_distribucion_global]
    dfs_a_guardar['Global'] = [df_agrupada]

    cuartiles = separar_por_cuartil(df_agrupada, 'Porcentaje_salidas')
    for i, cuartil in enumerate(cuartiles):
        if not cuartil.empty:
            fig_rank_cuartil = rankear_y_plottear(
                cuartil, 'Porcentaje_salidas', eje_x_agrupado,
                f'Gasto por Servicio Intervalo Cuartil {i}', 10)
            fig_distribucion_cuartil = analizar_distribucion_de_datos(
                cuartil, 'Porcentaje_salidas', f'Distribución Gasto Neto Intervalo Cuartil {i}')
            imagenes_a_guardar[i] = [fig_rank_cuartil, fig_distribucion_cuartil]
            dfs_a_guardar[i] = [cuartil]

    return imagenes_a_guardar, dfs_a_guardar






