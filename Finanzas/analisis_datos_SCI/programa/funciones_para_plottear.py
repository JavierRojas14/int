def rankear_y_plottear(df, eje_x, eje_y, titulo_grafico, numero_ranking):
    '''Esta función ordena los datos segun el eje y que se quiere plottear'''
    df_ordenada = df.sort_values(eje_y)
    diez_mas_altos = df_ordenada.head(numero_ranking)
    diez_mas_bajos = df_ordenada.tail(numero_ranking)

    mosaico = '''
    AB
    AC
    '''
    plot_args = [df, eje_x, eje_y, titulo_grafico]

    fig, axis = plt.subplot_mosaic(mosaico, figsize=(19.2, 20), layout='constrained')
    sns.barplot(data=plot_args[0], x=plot_args[1], y=plot_args[2], ax=axis['A'])

    axis['A'].xaxis.set_major_formatter('{x:,}')
    axis['A'].tick_params(axis='x', rotation=45)
    axis['A'].xaxis.tick_top()

    tabla_mas_altos = axis['B'].table(cellText=diez_mas_altos.values,
                                      colLabels=diez_mas_altos.columns,
                                      loc='center')
    tabla_mas_altos.scale(1, 2.3)
    tabla_mas_altos.auto_set_font_size(False)
    tabla_mas_altos.set_fontsize(10)

    tabla_mas_bajos = axis['C'].table(cellText=diez_mas_bajos.values,
                                      colLabels=diez_mas_bajos.columns,
                                      loc='center')

    tabla_mas_bajos.scale(1, 2.3)
    tabla_mas_bajos.auto_set_font_size(False)
    tabla_mas_bajos.set_fontsize(10)

    axis['B'].set_title('Top 10 gasto Neto')
    axis['C'].set_title('Bottom 10 gasto Neto')
    axis['B'].axis('off')
    axis['C'].axis('off')

    fig.suptitle(plot_args[3])
    plt.close()

    return fig

def analizar_distribucion_de_datos(df, columna_a_analizar, titulo_grafico):
    serie_columna = df[columna_a_analizar]
    descripcion_serie_columna = serie_columna.describe().to_frame().reset_index()
    descripcion_serie_columna = descripcion_serie_columna.rename(columns={'index': 'Estadisticas'})

    mosaico = '''
            AB
            AC
            '''

    fig, axis = plt.subplot_mosaic(mosaico, figsize=(19.2, 10.8), layout='constrained')
    args_plot = [df, columna_a_analizar, titulo_grafico]

    tabla = axis['A'].table(cellText=descripcion_serie_columna.values,
                            colLabels=descripcion_serie_columna.columns, loc='center')
    axis['A'].axis('off')

    sns.histplot(data=args_plot[0], x=args_plot[1], ax=axis['B'])
    sns.boxplot(data=args_plot[0], x=args_plot[1], ax=axis['C'])

    plt.ticklabel_format(style='plain', axis='x')

    axis['B'].tick_params(axis='x', rotation=45)
    axis['C'].tick_params(axis='x', rotation=45)
    axis['B'].xaxis.set_major_formatter('{x:,}')
    axis['C'].xaxis.set_major_formatter('{x:,}')

    fig.suptitle(args_plot[2])
    plt.close()

    return fig

def guardar_imagenes(imagenes_a_guardar, carpeta_a_guardar):
    for intervalo_imagen, lista_imagenes in imagenes_a_guardar.items():
        diccionario_intervalos = {'Global': 'Global', 0: 'INTERVALO_1_min_Q1',
                                  1: 'INTERVALO_2_Q1_Q2', 2: 'INTERVALO_3_Q2_Q3',
                                  3: 'INTERVALO_4_Q3_max'}
        path_nueva_carpeta = os.path.join(
            carpeta_a_guardar, diccionario_intervalos[intervalo_imagen])
        try:
            os.makedirs(path_nueva_carpeta)
        except FileExistsError:
            pass

        for i, imagen in enumerate(lista_imagenes):
            diccionario_nombres = {0: 'ranking', 1: 'distribucion'}
            tipo_archivo = diccionario_nombres[i]
            nombre_archivo = f'{diccionario_intervalos[intervalo_imagen]}_{tipo_archivo}.svg'
            ruta_archivo = os.path.join(path_nueva_carpeta, nombre_archivo)
            imagen.savefig(ruta_archivo)