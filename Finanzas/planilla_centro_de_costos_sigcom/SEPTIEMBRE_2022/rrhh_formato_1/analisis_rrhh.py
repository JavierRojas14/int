import pandas as pd
import json

def identificar_redundancias(df, caracteristica_a_identificar):
    agrupar_por = ['RUT-DV'] + caracteristica_a_identificar
    agrupado = df.groupby(by = agrupar_por).sum()
    duplicados = agrupado[agrupado.index.get_level_values(0).duplicated(keep = False)]
    return duplicados

def hacer_cambiador_de_caracteristica_redundante(df_con_duplicados, caracteristica):
    if caracteristica == 'CONTRATO':
        diccionario = {rut[0]: '1' for rut in df_con_duplicados.index[::2]}

    else:
        diccionario = dict(df_con_duplicados.index[::2])

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

def tratar_dfs(df, cambiar_tipo_contrato):
    df = cambiar_redundancias(df, 'NOMBRE')
    df = cambiar_redundancias(df, 'CARGO')
    if cambiar_tipo_contrato:
        df = cambiar_redundancias(df, 'TIPO_CONTRATA')

    df_suma = df.groupby(by = ['RUT-DV', 'NOMBRE', 'CARGO']).sum().reset_index()

    return df_suma

df_leyes_juntas, honorarios = cargar_archivos_y_formatearlos()

suma_leyes_juntas = tratar_dfs(df_leyes_juntas, False)
suma_leyes_juntas['TIPO_CONTRATA'] = '1'
print(f'Hay {suma_leyes_juntas.shape[0]} funcionarios por Ley')

suma_honorarios = tratar_dfs(honorarios, False)
suma_honorarios['TIPO_CONTRATA'] = '2'
print(f'Hay {suma_honorarios.shape[0]} funcionarios por Honorarios')

funcionarios_juntos = pd.concat([suma_leyes_juntas, suma_honorarios])
print(f'Todos los funcionarios juntos suman {funcionarios_juntos.shape[0]} juntos')

suma_funcionarios_juntos = tratar_dfs(funcionarios_juntos, True)
print(f'Al consolidar todos los campos, quedaron {suma_funcionarios_juntos.shape[0]} '
      f'funcionarios')
