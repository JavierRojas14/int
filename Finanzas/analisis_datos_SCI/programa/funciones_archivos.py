def obtener_full_path(directorio):
    return [os.path.join(directorio, file) for file in os.listdir(directorio)]

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

def guardar_dfs(dfs_a_guardar, carpeta_a_guardar):
    for intervalo_df, lista_dfs in dfs_a_guardar.items():
        diccionario_intervalos = {'Global': 'Global', 0: 'INTERVALO_1_min_Q1',
                                  1: 'INTERVALO_2_Q1_Q2', 2: 'INTERVALO_3_Q2_Q3',
                                  3: 'INTERVALO_4_Q3_max'}

        path_nueva_carpeta = os.path.join(carpeta_a_guardar, diccionario_intervalos[intervalo_df])
        try:
            os.makedirs(path_nueva_carpeta)
        except FileExistsError:
            pass

        for df in lista_dfs:
            nombre_archivo = f'{diccionario_intervalos[intervalo_df]}.xlsx'
            ruta_archivo = os.path.join(path_nueva_carpeta, nombre_archivo)
            df.to_excel(ruta_archivo, index=False)