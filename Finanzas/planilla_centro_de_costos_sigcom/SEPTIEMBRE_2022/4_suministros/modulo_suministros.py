'''
Programa para obtener el formato 4 de Suministros del SIGCOM. Unidad de Finanzas.
Javier Rojas Benítez'''

import numpy as np
import os
import pandas as pd

from constantes import DESTINO_INT_CC_SIGCOM
from bodega_sigfe_sigcom import BODEGA_SIGFE_SIGCOM

pd.options.mode.chained_assignment = None  # default='warn'


class AnalizadorSuministros:
    def __init__(self):
        pass

    def correr_programa(self):
        df_cartola = self.leer_asociar_y_filtrar_cartola()
        df_completa = self.rellenar_destinos(df_cartola)

        formato_relleno = self.convertir_a_tabla_din_y_rellenar_formato(df_completa)

        self.guardar_archivos(formato_relleno, df_completa)

    def leer_asociar_y_filtrar_cartola(self):
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
        if not('cartola_valorizada_con_cc.xlsx' in os.listdir('input')):
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

            df_filtrada.to_excel('input\\cartola_valorizada_con_cc.xlsx', index = False)
        
        else:
            df_filtrada = pd.read_excel('input\\cartola_valorizada_con_cc.xlsx')

        return df_filtrada

    def asociar_codigo_articulo_a_sigcom(self, df_cartola):
        df_filtrada = df_cartola.copy()
        df_filtrada['Tipo_Articulo_SIGCOM'] = df_filtrada['Codigo Articulo'].apply(
            lambda x: BODEGA_SIGFE_SIGCOM[x]['Total_SIGCOM'])

        df_filtrada['Tipo_Articulo_SIGFE'] = df_filtrada['Codigo Articulo'].apply(
            lambda x: BODEGA_SIGFE_SIGCOM[x]['Item SIGFE'])

        return df_filtrada

    def asociar_destino_int_a_sigcom(self, df_cartola):
        df_filtrada = df_cartola.copy()
        df_filtrada['CC SIGCOM'] = df_filtrada['Destino'].apply(
            lambda x: DESTINO_INT_CC_SIGCOM[x])

        return df_filtrada

    def rellenar_destinos(self, df_cartola):
        if 'cartola_valorizada_con_cc.xlsx' in os.listdir('input'):
            df_cartola = pd.read_excel('input\\cartola_valorizada_con_cc.xlsx')

        sin_cc = df_cartola[df_cartola['CC SIGCOM'].isna()]
        print('\n- Se rellenarán los centros de costo NO ASIGNADOS asociados a cada artículo - \n')
        print(
            f'{sin_cc[["Nombre", "Destino", "Tipo_Articulo_SIGFE", "Tipo_Articulo_SIGCOM"]].to_markdown()}')

        for fila_sin_cc in sin_cc.itertuples():
            while True:
                destino = input('Qué destino crees que es? (están en constantes.py) ')

                if destino in DESTINO_INT_CC_SIGCOM:
                    centro_de_costo = DESTINO_INT_CC_SIGCOM[destino]
                    df_cartola.loc[fila_sin_cc.Index, 'Destino'] = destino
                    df_cartola.loc[fila_sin_cc.Index, 'CC SIGCOM'] = centro_de_costo
                    break

                else:
                    print('Debes ingresar un destino válido.')

        df_cartola.to_excel('input\\cartola_valorizada_con_cc.xlsx', index = False)

        return df_cartola

    def convertir_a_tabla_din_y_rellenar_formato(self, df_consolidada):
        tabla_dinamica = pd.pivot_table(df_consolidada, values='Neto Total', index='CC SIGCOM',
                                        columns='Tipo_Articulo_SIGCOM', aggfunc=np.sum)

        formato = pd.read_excel(
            'input\\Formato 4_Distribución Suministro 2022-10.xlsx')
        formato = formato.set_index('Centro de Costo')

        for cc in tabla_dinamica.index:
            for item_sigcom in tabla_dinamica.columns:
                formato.loc[cc,
                            item_sigcom] = tabla_dinamica.loc[cc, item_sigcom]

        return formato

    def guardar_archivos(self, formato_relleno, df_cartola):
        with pd.ExcelWriter('output_suministros.xlsx') as writer:
            formato_relleno.to_excel(writer, sheet_name='formato_relleno')
            df_cartola.to_excel(writer, sheet_name='cartola_con_cc_sigcom')


analizador = AnalizadorSuministros()
analizador.correr_programa()
