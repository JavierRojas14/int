'''
Este programa permite obtener el formato 1 de RRHH del SIGCOM. Unidad de Finanzas.
Javier Rojas Benítez.'''

import pandas as pd
import json
import os


class ModuloRecursosHumanosSIGCOM:
    def __init__(self):
        pass

    def correr_programa(self):
        df_leyes_juntas, honorarios = self.cargar_archivos_y_formatearlos()
        suma_por_funcionario = self.agrupar_dfs(df_leyes_juntas, honorarios, 'funcionario')
        suma_por_unidad = self.agrupar_dfs(df_leyes_juntas, honorarios, 'unidad')

        guardar_archivos(suma_por_funcionario, suma_por_unidad)

    def cargar_archivos_y_formatearlos(self):
        '''
        Este función permite obtener los archivos de RRHH, tanto para los funcionarios contratados
        por Leyes, como los funcionarios que prestan servicios por Honorarios.

        En este caso, las 3 leyes del Hospital son juntadas en una única tabla.

        Las Columnas que se dejan tanto en Leyes, como Honorario, son:
         - ['RUT-DV', 'NOMBRE', 'UNIDAD', 'CARGO', 'TOTAL HABER']'''

        print(f'{"SE ESTÁN CARGANDO LOS ARCHIVOS":-^40}')
        leyes = self.cargar_leyes()
        honorarios = self.cargar_honorarios()
        leyes_procesada, honorarios_procesada = self.unificar_formatos(leyes, honorarios)

        return leyes_procesada, honorarios_procesada

    def cargar_leyes(self):
        '''
        Esta función permite cargar los archivos de funcionarios contratados por Leyes.
        - Los archivos considerados como leyes, son todos los que tengan el string "TODOS" en su
        nombre.

        - En esta función, primero se cargan todas las leyes a un DataFrame. Luego, se filtran
        sus columnas por las columnas útiles (además, entre archivos tienen distintas cantidades
        de columnas). Finalmente, se concatenan entre sí a lo largo.
        '''

        print(f'{"SE ESTÁN CARGANDO LAS LEYES":^40}')
        nombres_leyes = [os.path.join('input', nombre) \
                        for nombre in os.listdir('input') if 'TODOS' in nombre]

        leyes_crudas = map(lambda x: pd.read_excel(x, header = 2), nombres_leyes)

        columnas_contrato = ['RUT-DV', 'NOMBRE', 'UNIDAD', 'CARGO', 'TOTAL HABER']

        leyes_columnas_utiles = list(map(lambda x: x[columnas_contrato], leyes_crudas))
        leyes_juntas = pd.concat(leyes_columnas_utiles)

        return leyes_juntas

    def cargar_honorarios(self):
        '''
        Esta función carga el archivo de funcionarios que trabajan por honorarios.

        - Se agrega la columna RUT-DV, ya que esta ausente en el archivo original
        - Se cambian los nombres de las columnas para que tengan el mismo nombre que las columnas
        de leyes.
        '''

        print(f'{"SE ESTÁN CARGANDO LOS HONORARIOS":^40}')
        nombre_archivo_honorarios = [nom for nom in os.listdir('input') if 'PERC' in nom][0]
        nombre_archivo_honorarios = os.path.join('input', nombre_archivo_honorarios)
        honorarios = pd.read_excel(nombre_archivo_honorarios)

        honorarios['RUT-DV'] = honorarios['RUT'].astype(str) + '-' + honorarios['DV'].astype(str)
        columnas_honorario = ['RUT-DV', 'NOMBRE', 'UNIDAD O SERVICIO DONDE SE DESEMPEÑA',
                              'CARGO', 'VALOR TOTAL O BRUTO']

        honorarios = honorarios[columnas_honorario].rename(
                                columns = {'UNIDAD O SERVICIO DONDE SE DESEMPEÑA': 'UNIDAD',
                                            'VALOR TOTAL O BRUTO': 'TOTAL HABER'})
        return honorarios

    def unificar_formatos(self, *args):
        '''
        Esta función es un pasador para aplicar la funcion self.formatear_df() a los argumentos
        de la función.
        '''

        lista_dfs_formateadas = list(map(self.formatear_df, args))
        return lista_dfs_formateadas

    def formatear_df(self, df_funcionarios):
        '''
        Esta función unifica las columnas "NOMBRE" y "RUT-DV" de la DataFrame que le llegue.
        Además, pone a la columna RUT-DV como índice.
        '''

        df_funcionarios['NOMBRE'] = df_funcionarios['NOMBRE'].str.strip().str.upper()
        df_funcionarios['RUT-DV'] = df_funcionarios['RUT-DV'].str.strip().str.upper()

        df_funcionarios = df_funcionarios.set_index('RUT-DV')

        return df_funcionarios

############################################################################################
    def juntar_leyes_y_honorarios(self, df_leyes_juntas, honorarios, tipo_agrupacion):
        print(f'{"SE ESTÁN JUNTANDO LEYES Y HONORARIOS":-^40}')

        suma_leyes_por_tipo_agrupacion = consolidar_informacion_dfs(df_leyes_juntas, tipo_agrupacion,
                                                                    False)
        suma_leyes_por_tipo_agrupacion['TIPO_CONTRATA'] = '1'

        print(f"{'ANALIZANDO HONORARIOS':-^40}")
        suma_honorarios_por_tipo_agrupacion = consolidar_informacion_dfs(honorarios, tipo_agrupacion,
                                                                        False)
        suma_honorarios_por_tipo_agrupacion['TIPO_CONTRATA'] = '2'

        print(f"{'ANALIZANDO LEYES Y HONORARIOS JUNTOS':-^40}")
        juntos_por_tipo_agrupacion = pd.concat([suma_leyes_por_tipo_agrupacion,
                                                    suma_honorarios_por_tipo_agrupacion])

        juntos_por_tipo_agrupacion = formatear_df(juntos_por_tipo_agrupacion)

        suma_juntos_por_tipo_agrupacion = consolidar_informacion_dfs(juntos_por_tipo_agrupacion,
                                                                    tipo_agrupacion, True)



        suma_juntos_por_tipo_agrupacion.to_excel(f'por_{tipo_agrupacion}.xlsx')
        return suma_juntos_por_tipo_agrupacion

    def juntar_leyes_y_honorarios(self, df_leyes_juntas, honorarios):
        '''
        Esta función permite unir los funcionarios por leyes y los por honorario.

        '''
        informacion_a_consolidar = ['NOMBRE', 'CARGO', 'UNIDAD']
        leyes_modificada = df_leyes_juntas.copy()
        honorarios_modificada = honorarios.copy()

        for info in informacion_a_consolidar:
            leyes_modificada = self.unificar_redundancias(leyes_modificada, info)
            honorarios_modificada = self.unificar_redundancias(honorarios_modificada, info)
        
        leyes_modificada['TIPO_CONTRATA'] = '1'
        honorarios_modificada['TIPO_CONTRATA'] = '2'

        ley_honorario = pd.concat([leyes_modificada, honorarios_modificada])
    

    def unificar_redundancias(self, df_funcionarios, redundancia_a_identificar):
        '''
        Esta función permite identificar, crear un cambiador y unificar una característica
        de un df.

        - Retorna el df con la característica unificada!
        '''
        df_repetidos = self.identificar_redundancias(df_funcionarios, redundancia_a_identificar)
        caract_seleccionadas = self.seleccionar_caract_a_unificar(df_repetidos,
                                                                  redundancia_a_identificar)

        df_funcionarios_unificados = self.cambiar_redundancias(df_funcionarios,
                                                               caract_seleccionadas,
                                                               redundancia_a_identificar)

        return df_funcionarios_unificados

    def identificar_redundancias(self, df_funcionarios, caracteristica_a_identificar):
        '''
        Esta función permite identificar las redundancias en la caracteristica señalada

        - Retorna un DataFrame con el formato RUT-DV; caracteristica_a_identificar; TOTAL HABER
        - Los grupos están ordenados de forma descendente (La caract que gana más al principio).
        '''

        agrupado = df_funcionarios.groupby(by = ['RUT-DV', caracteristica_a_identificar]).sum()

        duplicados = agrupado[agrupado.index.get_level_values(0).duplicated(keep = False)]
        duplicados_ordenados = duplicados.reset_index().sort_values(by = ['RUT-DV', 'TOTAL HABER'],
                                                                    ascending = False)
        return duplicados_ordenados

    def seleccionar_caract_a_unificar(self, df_con_duplicados, caracteristica):
        '''
        - Esta función permite seleccionar las características que se dejarán finalmente para
        ese funcionario.
        - Esta función asume que el df proporcionado solamente tiene 2 registros por funcionario.
        - Selecciona la primera característica del funcionario (o sea, en donde gana más).
        - Si la característica a seleccionar es CONTRATO, entonces para ese funcionario siempre
        se dejará el tipo de contrato 1 (por ley).

        '''
        a_dejar = df_con_duplicados.iloc[::2]
        if caracteristica != 'CONTRATO':
            diccionario = dict(zip(a_dejar['RUT-DV'], a_dejar[caracteristica]))

        else:
            diccionario = dict(map(lambda x: (x, '1'), a_dejar['RUT-DV']))

        return diccionario


    def cambiar_redundancias(self, df_funcionarios, dict_a_cambiar, caracteristica_a_cambiar):
        '''
        - Esta función toma el DataFrame original de los funcionarios y aplica la consolidación
        a cada funcionario presente en el diccionario.
        '''

        df_funcionarios_unificados = df_funcionarios.copy()
        for rut, caracteristica in dict_a_cambiar.items():
            df_funcionarios_unificados.loc[rut, caracteristica_a_cambiar] = caracteristica

        return df_funcionarios_unificados

    def guardar_archivos(self, suma_por_funcionario, suma_por_unidad):
        with pd.ExcelWriter('output.xlsx') as writer:
            suma_por_funcionario.to_excel(writer, index = False, sheet_name = 'suma_por_funcionario')
            suma_por_unidad.to_excel(writer, index = False, sheet_name = 'suma_por_unidad')

modulo_rrhh_sigcom = ModuloRecursosHumanosSIGCOM()
modulo_rrhh_sigcom.correr_programa()
