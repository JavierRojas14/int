'''
Programa para obtener el formato 4 de Suministros del SIGCOM. Unidad de Finanzas.
Javier Rojas Benítez'''

import os

import numpy as np
import pandas as pd

from bodega_sigfe_sigcom import BODEGA_SIGFE_SIGCOM
from constantes import (DESTINO_INT_CC_SIGCOM, DICCIONARIO_UNIDADES_A_DESGLOSAR,
                        WINSIG_SERVICIO_FARMACIA_CC_SIGCOM)

pd.options.mode.chained_assignment = None  # default='warn'


class AnalizadorSuministros:
    '''
    Esta clase permite desglosar los suministros de la cartola valorizada del SCI, y generar
    el formato 4 de Suministros del SIGCOM.
    '''

    def __init__(self):
        pass

    def correr_programa(self):
        '''
        Esta es la función principal para correr el programa. Ejecuta las siguientes funciones:

        1 - Leer, Traducir y filtrar la cartola valorizada del SCI.
        2 - Permite rellenar los artículos que NO tengan un destino asociado en el INT.
        3 - Rellena el formato del SIGCOM.
        4 - Guarda los archivos generados
        '''
        df_cartola = self.leer_asociar_y_filtrar_cartola()
        df_completa = self.rellenar_destinos(df_cartola)
        formato_relleno = self.convertir_a_tabla_din_y_rellenar_formato(df_completa)
        formato_con_medicamentos = self.rellenar_columna_medicamentos_winsig(formato_relleno)

        # formato_desglosado = self.desglosar_por_produccion(formato_relleno)

        self.guardar_archivos(formato_con_medicamentos, df_completa)

    def leer_asociar_y_filtrar_cartola(self):
        '''
        Esta función controla el flujo de creación de la cartola traducida.
        Si NO existe la cartola traducida, entonces crea una nueva desde la cartola cruda.
        Si existe una cartola traducida, entonces lee esta y la trata.
        '''
        if 'cartola_valorizada_traducida.xlsx' not in os.listdir('input'):
            df_filtrada = self.leer_cartola_desde_cero()
            df_filtrada.to_excel('input\\cartola_valorizada_traducida.xlsx', index=False)

        else:
            df_filtrada = pd.read_excel('input\\cartola_valorizada_traducida.xlsx')

        return df_filtrada

    def leer_cartola_desde_cero(self):
        '''
        Esta función permite leer el archivo de la Cartola Valorizada del SCI. Luego, trata
        este archivo de la siguiente forma:

        1 - Crea una copia de la cartola.
        2 - Deja solamente los movimientos de salida de los artículos
        3 - Filtra todos los movimientos que NO tengan FARMACIA en su nombre, exceptuando
        SECRE. FARMACIA
        4 - Filtra todos los movimientos que tengan como motivo a "Merma" - "Préstamo" o "Devolución
        al Proveedor".
        5 - Asocia el código de bodega con el código SIGFE y el código SIGCOM.
        6 - Asocia el destino INT (destino del artículo dentro del hospital) con un centro
        de costo.
        7 - Filtra todos los artículos que sean del tipo Farmacia (ya que estos vienen desde
        la planilla de Juan Pablo).
        '''
        df_cartola = pd.read_csv('input\\Cartola valorizada.csv')
        df_filtrada = df_cartola.copy()

        df_filtrada = df_filtrada.query('Movimiento == "Salida"')
        mask_farmacia = ~(df_filtrada['Destino'].str.contains('FARMACIA')) | \
            (df_filtrada['Destino'].str.contains('SECRE. FARMACIA'))
        df_filtrada = df_filtrada[mask_farmacia]
        motivos_a_filtrar = ['Merma', 'Préstamo', 'Devolución al Proveedor']
        df_filtrada = df_filtrada[~df_filtrada['Motivo'].isin(motivos_a_filtrar)]

        df_filtrada = self.asociar_codigo_articulo_a_sigcom(df_filtrada)
        df_filtrada = self.asociar_destino_int_a_sigcom(df_filtrada)
        df_filtrada = df_filtrada.query('Tipo_Articulo_SIGFE != "Farmacia"')
        df_filtrada = df_filtrada.sort_values(['CC SIGCOM', 'Nombre'], na_position='first')

        return df_filtrada

    def asociar_codigo_articulo_a_sigcom(self, df_cartola):
        '''
        Esta función permite relacionar el código de bodega con el código presupuestario
        SIGCOM y SIGFE.
        '''
        df_filtrada = df_cartola.copy()
        df_filtrada['Tipo_Articulo_SIGCOM'] = df_filtrada['Codigo Articulo'].apply(
            lambda x: BODEGA_SIGFE_SIGCOM[x]['Total_SIGCOM'])

        df_filtrada['Tipo_Articulo_SIGFE'] = df_filtrada['Codigo Articulo'].apply(
            lambda x: BODEGA_SIGFE_SIGCOM[x]['Item SIGFE'])

        return df_filtrada

    def asociar_destino_int_a_sigcom(self, df_cartola):
        '''
        Esta función permite asociar el destino INT con el centro de costo SIGCOM.
        '''
        df_filtrada = df_cartola.copy()
        df_filtrada['CC SIGCOM'] = df_filtrada['Destino'].apply(
            lambda x: DESTINO_INT_CC_SIGCOM[x])

        return df_filtrada

    def rellenar_destinos(self, df_cartola):
        '''
        Esta función permite rellenar todos los ítems que tengan algún destino que NO
        tenga relacionado algún centro de costo SIGCOM (Ej: Hospital del Salvador, INT, otros).
        '''
        sin_cc = df_cartola[df_cartola['CC SIGCOM'].isna()]
        a_printear = sin_cc[["Nombre", "Destino", "Tipo_Articulo_SIGFE", "Tipo_Articulo_SIGCOM"]]

        print('\n- Se rellenarán los centros de costo NO ASIGNADOS asociados a cada artículo - \n')
        print(f'{a_printear.to_markdown()}')

        for nombre_articulo in sin_cc['Nombre'].unique():
            while True:
                destino = input(f'\n{nombre_articulo}\n'
                                f'Qué destino crees que es? (están en constantes.py): ')

                if destino in DESTINO_INT_CC_SIGCOM:
                    cc_sigcom = DESTINO_INT_CC_SIGCOM[destino]

                    mask_articulos_mismo_nombre = sin_cc['Nombre'] == nombre_articulo
                    a_cambiar = sin_cc[mask_articulos_mismo_nombre]
                    df_cartola.loc[a_cambiar.index, 'Destino'] = destino
                    df_cartola.loc[a_cambiar.index, 'CC SIGCOM'] = cc_sigcom
                    break

                else:
                    print('Debes ingresar un destino válido.')

            df_cartola.to_excel('input\\cartola_valorizada_traducida.xlsx', index=False)

        return df_cartola

    def convertir_a_tabla_din_y_rellenar_formato(self, df_consolidada):
        '''
        Esta función permite convertir la cartola valorizada en una tabla al estilo wide.
        '''
        tabla_dinamica = pd.pivot_table(df_consolidada, values='Neto Total', index='CC SIGCOM',
                                        columns='Tipo_Articulo_SIGCOM', aggfunc=np.sum)

        formato = pd.read_excel('input\\Formato 4_Distribución Suministro 2022-10.xlsx')
        formato = formato.set_index('Centro de Costo')

        for centro_costo in tabla_dinamica.index:
            for item_sigcom in tabla_dinamica.columns:
                formato.loc[centro_costo, item_sigcom] = tabla_dinamica.loc[centro_costo,
                                                                            item_sigcom]

        return formato

    def desglosar_centro_de_costo(self, desglose, total_dinero):
        con_dinero = desglose.copy()
        con_dinero['TOTAL_X_PORCENTAJE'] = con_dinero['PORCENTAJES'] * total_dinero

        return con_dinero

    def rellenar_columna_medicamentos_winsig(self, formato_relleno):
        df_winsig = pd.read_excel('input\\Informe Winsig Septiembre 2022.xlsx', header=7)
        df_winsig = df_winsig.dropna(axis=1, how='all').dropna(axis=0, how='all')
        archivo_produccion = pd.ExcelFile('input\\output_producciones.xlsx')

        desglose_pabellon = pd.read_excel(archivo_produccion, sheet_name='PABELLÓN')
        total_pabellon = df_winsig.query('SERVICIO == "B. PABELLON"')['Gasto Servicio'].iloc[0]
        con_gastos_pabellon = self.desglosar_centro_de_costo(desglose_pabellon, total_pabellon)

        desglose_policlinico = pd.read_excel(
            archivo_produccion, sheet_name='CONSULTAS SIN MANEJO DEL DOLOR')
        total_policlinico = df_winsig.query('SERVICIO == "POLICLÍNICO"')['Gasto Servicio'].iloc[0]
        con_gastos_policlinico = self.desglosar_centro_de_costo(
            desglose_policlinico, total_policlinico)

        con_gastos_pabellon_para_concatenar = con_gastos_pabellon.iloc[:, [0, 1, 2, -1, 3]]
        con_gastos_pabellon_para_concatenar.iloc[:, [1, 2, -1]] = None
        con_gastos_pabellon_para_concatenar.columns = df_winsig.columns

        con_gastos_policlinico_para_concatenar = con_gastos_policlinico.iloc[:, [0, 1, 2, -1, 3]]
        con_gastos_policlinico_para_concatenar.iloc[:, [1, 2, -1]] = None
        con_gastos_policlinico_para_concatenar.columns = df_winsig.columns

        winsig_concatenado = df_winsig.copy()
        winsig_mas_desglose = pd.concat([winsig_concatenado, con_gastos_pabellon_para_concatenar])
        winsig_mas_desglose = pd.concat(
            [winsig_mas_desglose, con_gastos_policlinico_para_concatenar])
        servicios_a_sacar = ['B. PABELLON', 'PABELLÓN',
                             'POLICLÍNICO', 'CONSULTAS SIN MANEJO DEL DOLOR']
        servicios_a_dejar = ~(winsig_mas_desglose['SERVICIO'].isin(servicios_a_sacar))

        winsig_final = winsig_mas_desglose[servicios_a_dejar]
        winsig_sigcom = winsig_final.copy()
        winsig_sigcom['CC_SIGCOM'] = winsig_sigcom['SERVICIO'].apply(
            lambda x: WINSIG_SERVICIO_FARMACIA_CC_SIGCOM[x])

        agrupado_sigcom = winsig_sigcom.groupby('CC_SIGCOM')['Gasto Servicio'].sum()

        for cc, valor in agrupado_sigcom.items():
            print(f'Imputando {cc} {valor}')
            formato_relleno.loc[cc, '30-MEDICAMENTOS'] = valor

        return formato_relleno

    def desglosar_por_produccion(self, formato_relleno):
        '''
        Esta función permite hacer el desglose, con los montos respectivos, de cada uno de los
        Centros de Costos que lo requieran. Solamente desglosa los que están en el formato.
        '''
        producciones = pd.ExcelFile('input\\output_producciones.xlsx')
        for i, cc_a_desglosar in enumerate(DICCIONARIO_UNIDADES_A_DESGLOSAR):
            if cc_a_desglosar in formato_relleno.index:
                produccion_cc = pd.read_excel(producciones, sheet_name=i)
                total = formato_relleno.loc[cc_a_desglosar, :]

                producciones_a_imputar = producciones
                for desglose in produccion_cc.itertuples():
                    parcelado = total * desglose.PORCENTAJES
                    total_cc_a_desglosar = pd.concat([total_cc_a_desglosar, parcelado], axis=1)

                print(total_cc_a_desglosar)

    def guardar_archivos(self, formato_relleno, df_cartola):
        '''
        Esta función permite guardar los archivos generados en el programa.
        '''
        with pd.ExcelWriter('output_suministros.xlsx') as writer:
            formato_relleno.to_excel(writer, sheet_name='formato_relleno')
            df_cartola.to_excel(writer, sheet_name='cartola_con_cc_sigcom')


analizador = AnalizadorSuministros()
analizador.correr_programa()
