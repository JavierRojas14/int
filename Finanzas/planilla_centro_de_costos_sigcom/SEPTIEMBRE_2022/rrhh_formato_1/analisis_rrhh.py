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
    print(f'Estos son los "{caracteristica_a_cambiar}" redundantes: \n'
          f'{df_con_redundancias.to_markdown()}')

    dict_cambiador = hacer_cambiador_de_caracteristica_redundante(df_con_redundancias, 
                                                                  caracteristica_a_cambiar)

    print(f'Los ruts quedarán de la siguiente forma:\n'
          f'{json.dumps(dict_cambiador, indent = 1)}')

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
    df_leyes_juntas['TIPO CONTRATA'] = 1

    ##################################################################################

    honorarios = pd.read_excel('input\\PERC AGOSTO.xlsx')
    columnas_honorario = ['RUT-DV', 'NOMBRE', 'UNIDAD O SERVICIO DONDE SE DESEMPEÑA',
                          'CARGO', 'VALOR TOTAL O BRUTO']

    honorarios = honorarios[columnas_honorario].rename(
                 columns = {'UNIDAD O SERVICIO DONDE SE DESEMPEÑA': 'UNIDAD',
                            'VALOR TOTAL O BRUTO': 'TOTAL HABER'})

    honorarios['TIPO CONTRATA'] = 2

    df_leyes_juntas = formatear_df(df_leyes_juntas)
    honorarios = formatear_df(honorarios)

    return df_leyes_juntas, honorarios

juntas_contrato = cambiar_redundancias(juntas_contrato, 'NOMBRE')
juntas_contrato = cambiar_redundancias(juntas_contrato, 'CARGO')

honorarios = cambiar_redundancias(honorarios, 'NOMBRE')
honorarios = cambiar_redundancias(honorarios, 'CARGO')