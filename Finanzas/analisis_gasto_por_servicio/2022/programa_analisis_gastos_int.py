import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("darkgrid")
pd.options.display.float_format = '{:,.2f}'.format


def correr_programa():
    df = pd.concat(map(lambda x: pd.read_csv(x, parse_dates=[
               0], dayfirst=True), obtener_full_path('input')))
    df = df.sort_values('Fecha')

def obtener_full_path(directorio):
    return [os.path.join(directorio, file) for file in os.listdir(directorio)]


def plottear(df, x, y, titulo):
    fig, axis = plt.subplots(1, 1, figsize=(38.4, 21.6))
    sns.barplot(data=df, x=x, y=y, ax=axis)
    axis.set_xticklabels(axis.get_xticklabels(), rotation=90)
    fig.suptitle(titulo)
    plt.ticklabel_format(style='plain', axis='y')
    plt.show()
    return fig


def obtener_gasto_por_servicio(df_salidas, servicio):
    movimientos_servicio = df_salidas.query('Destino == @servicio and Cantidad > 0')
    articulos_servicio_suma = movimientos_servicio.groupby('Nombre') \
                                                  .sum() \
                                                  .reset_index() \
        .sort_values('Neto Total', ascending=False)

    diez_mas_gastadores = articulos_servicio_suma.sort_values(
        'Neto Total', ascending=False).head(10)
    diez_menos_gastadores = articulos_servicio_suma.sort_values(
        'Neto Total', ascending=False).tail(10)

    print(f'Los 10 artículos que más gastan en {servicio} son:\n'
          f'{diez_mas_gastadores.to_markdown(floatfmt=",.2f")}\n')

    print(f'Los 10 artículos que menos gastan en {servicio} son:\n'
          f'{diez_menos_gastadores.to_markdown(floatfmt=",.2f")}\n')

    figura_articulos_servicio_suma = plottear(
        x='Nombre', y='Neto Total', df=articulos_servicio_suma)

    articulos_qmin, articulos_q1, articulos_q2, articulos_q3, articulos_qmax, \
        figura_df_articulos_min_q1, figura_df_articulos_q1_q2, \
        figura_df_articulos_q2_q3, figura_df_articulos_q3_max = separar_por_cuartil(articulos_servicio_suma)


def separar_por_cuartil(articulos_servicio_suma, eje_x):
    descripcion_neto_total = articulos_servicio_suma['Neto Total'].describe()
    print(f'La distribución de datos de la columna Neto Total es:\n\n'
          f'{descripcion_neto_total}')

    articulos_qmin = articulos_servicio_suma['Neto Total'].quantile(0)
    articulos_q1 = articulos_servicio_suma['Neto Total'].quantile(0.25)
    articulos_q2 = articulos_servicio_suma['Neto Total'].quantile(0.5)
    articulos_q3 = articulos_servicio_suma['Neto Total'].quantile(0.75)
    articulos_qmax = articulos_servicio_suma['Neto Total'].quantile(1)

    df_articulos_min_q1 = articulos_servicio_suma.query(
        '`Neto Total` >= @articulos_qmin and `Neto Total` < @articulos_q1')
    df_articulos_q1_q2 = articulos_servicio_suma.query(
        '`Neto Total` >= @articulos_q1 and `Neto Total` < @articulos_q2')
    df_articulos_q2_q3 = articulos_servicio_suma.query(
        '`Neto Total` >= @articulos_q2 and `Neto Total` < @articulos_q3')
    df_articulos_q3_max = articulos_servicio_suma.query(
        '`Neto Total` >= @articulos_q3 and `Neto Total` <= @articulos_qmax')

    figura_df_articulos_min_q1 = plottear(
        df_articulos_min_q1, eje_x, 'Neto Total', titulo=f'Gasto Total Qmin -> Q1')
    figura_df_articulos_q1_q2 = plottear(
        df_articulos_q1_q2, eje_x, 'Neto Total', titulo=f'Gasto Total Q1 -> Q2')
    figura_df_articulos_q2_q3 = plottear(
        df_articulos_q2_q3, eje_x, 'Neto Total', titulo=f'Gasto Total Q3 -> Q4')
    figura_df_articulos_q3_max = plottear(
        df_articulos_q3_max, eje_x, 'Neto Total', titulo=f'Gasto Total Q4 -> Qmax')

    return articulos_qmin, articulos_q1, articulos_q2, articulos_q3, articulos_qmax, \
        figura_df_articulos_min_q1, figura_df_articulos_q1_q2, \
        figura_df_articulos_q2_q3, figura_df_articulos_q3_max
