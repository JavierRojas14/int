import pandas as pd
import json

def identificar_redundancias(df, caracteristica_a_identificar):
    agrupar_por = ['RUT-DV'] + caracteristica_a_identificar
    agrupado = df.groupby(by = agrupar_por).sum()
    duplicados = agrupado[agrupado.index.get_level_values(0).duplicated(keep = False)]
    duplicados_ordenados = duplicados.reset_index().sort_values(by = ['RUT-DV', 'TOTAL HABER'],
                                                                ascending = False)
    return duplicados_ordenados

def hacer_cambiador_de_caracteristica_redundante(df_con_duplicados, caracteristica):
    a_dejar = df_con_duplicados.iloc[::2]
    if caracteristica == 'CONTRATO':
        contratos_1 = ['1' for _ in range(a_dejar.shape[0])]
        diccionario = dict(zip(a_dejar['RUT-DV'], contratos_1))

    else:
        diccionario = dict(zip(a_dejar['RUT-DV'], a_dejar[caracteristica]))

    return diccionario

def cambiar_redundancias(df, caracteristica_a_cambiar):
    df_con_redundancias = identificar_redundancias(df, [caracteristica_a_cambiar])
    print(f'\nEstos son los "{caracteristica_a_cambiar}" redundantes: \n'
          f'{df_con_redundancias.to_markdown()}\n')

    dict_cambiador = hacer_cambiador_de_caracteristica_redundante(df_con_redundancias, 
                                                                  caracteristica_a_cambiar)

    print(f'\nLos ruts quedarán de la siguiente forma:\n'
          f'{json.dumps(dict_cambiador, indent = 1)}\n')

    for rut, caracteristica in dict_cambiador.items():
        df.loc[rut, caracteristica_a_cambiar] = caracteristica

    return df

def formatear_df(df):
    df['NOMBRE'] = df['NOMBRE'].str.strip()
    df['RUT-DV'] = df['RUT-DV'].str.strip().str.upper()

    df = df.set_index('RUT-DV')

    return df

def cargar_archivos_y_formatearlos():
    df_15076 = pd.read_excel('input\\TODOS_15076.xlsx', header = 2)
    df_18834 = pd.read_excel('input\\TODOS_18834.xlsx', header = 2)
    df_19664 = pd.read_excel('input\\TODOS_19664.xlsx', header = 2)

    columnas_contrato = ['RUT-DV', 'NOMBRE', 'UNIDAD', 'CARGO', 'TOTAL HABER']

    df_15076 = df_15076[columnas_contrato]
    df_18834 = df_18834[columnas_contrato]
    df_19664 = df_19664[columnas_contrato]

    df_leyes_juntas = pd.concat([df_15076, df_18834, df_19664])
    ##################################################################################

    honorarios = pd.read_excel('input\\PERC SEPTIEMBRE.xlsx')
    honorarios['RUT-DV'] = honorarios['RUT'].astype(str) + '-' + honorarios['DV'].astype(str)
    columnas_honorario = ['RUT-DV', 'NOMBRE', 'UNIDAD O SERVICIO DONDE SE DESEMPEÑA',
                          'CARGO', 'VALOR TOTAL O BRUTO']

    honorarios = honorarios[columnas_honorario].rename(
                 columns = {'UNIDAD O SERVICIO DONDE SE DESEMPEÑA': 'UNIDAD',
                            'VALOR TOTAL O BRUTO': 'TOTAL HABER'})

    df_leyes_juntas = formatear_df(df_leyes_juntas)
    honorarios = formatear_df(honorarios)

    return df_leyes_juntas, honorarios

def consolidar_informacion_dfs(df, consolidar_por, consolidar_contratos):
    df = df.sort_values('TOTAL HABER', ascending = False)
    if consolidar_por == 'funcionario':
        df = cambiar_redundancias(df, 'NOMBRE')
        df = cambiar_redundancias(df, 'CARGO')

        if consolidar_contratos:
            df = cambiar_redundancias(df, 'TIPO_CONTRATA')

        df_suma = df.groupby(by = ['RUT-DV', 'NOMBRE', 'CARGO']).sum().reset_index()

        return df_suma

    elif consolidar_por == 'unidad':
        df = cambiar_redundancias(df, 'NOMBRE')
        df = cambiar_redundancias(df, 'CARGO')

        if consolidar_contratos:
            df = cambiar_redundancias(df, 'TIPO_CONTRATA')

        df = cambiar_redundancias(df, 'UNIDAD')

        df_suma = df.groupby(by = ['RUT-DV', 'NOMBRE', 'CARGO', 'UNIDAD']).sum().reset_index()

        return df_suma


    return df_suma

df_leyes_juntas, honorarios = cargar_archivos_y_formatearlos()
df_leyes_juntas.to_excel('leyes_juntas.xlsx')

suma_leyes_por_funcionario = consolidar_informacion_dfs(df_leyes_juntas, 'funcionario', False)
suma_leyes_por_funcionario['TIPO_CONTRATA'] = '1'

# suma_honorarios_por_funcionario = consolidar_informacion_dfs(honorarios, 'funcionario', False)
# suma_honorarios_por_funcionario['TIPO_CONTRATA'] = '2'

# ley_y_honorarios_por_funcionario = pd.concat([suma_leyes_por_funcionario,
#                                               suma_honorarios_por_funcionario])

# suma_ley_y_honorarios_por_funcionario = consolidar_informacion_dfs(ley_y_honorarios_por_funcionario,
#                                                               'funcionario', True)

# print(f'Hay {suma_leyes_por_funcionario.shape[0]} funcionarios por Ley')
# print(f'Hay {suma_honorarios_por_funcionario.shape[0]} funcionarios por Honorarios')
# print(f'Todos los funcionarios juntos suman {ley_y_honorarios_por_funcionario.shape[0]} juntos')
# print(f'Al consolidar todos los campos, quedaron {suma_ley_y_honorarios_por_funcionario.shape[0]} '
#       f'funcionarios')


# print('-Analizando Leyes- \n\n')
# suma_leyes_por_unidad = consolidar_informacion_dfs(df_leyes_juntas, 'unidad', False)
# suma_leyes_por_unidad['TIPO_CONTRATA'] = '1'

# print('-Analizando Honorarios- \n\n')
# suma_honorarios_por_unidad = consolidar_informacion_dfs(honorarios, 'unidad', False)
# suma_honorarios_por_unidad['TIPO_CONTRATA'] = '2'

# ley_y_honorarios_por_unidad = pd.concat([suma_leyes_por_unidad,
#                                               suma_honorarios_por_unidad])

# print('-Analizando Leyes y Honorarios juntos- \n\n')
# suma_ley_y_honorarios_por_unidad = consolidar_informacion_dfs(ley_y_honorarios_por_unidad,
#                                                               'unidad', True)

# print(f'Hay {suma_leyes_por_unidad.shape[0]} unidads por Ley')
# print(f'Hay {suma_honorarios_por_unidad.shape[0]} unidads por Honorarios')
# print(f'Todos los unidads juntos suman {ley_y_honorarios_por_unidad.shape[0]} juntos')
# print(f'Al consolidar todos los campos, quedaron {suma_ley_y_honorarios_por_unidad.shape[0]} '
#       f'unidads')
