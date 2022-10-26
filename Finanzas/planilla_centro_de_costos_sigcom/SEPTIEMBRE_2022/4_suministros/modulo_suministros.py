'''
Programa para obtener el formato 4 de Suministros del SIGCOM. Unidad de Finanzas.
Javier Rojas Benítez'''

import numpy as np
import os
import pandas as pd

from constantes import BODEGA_SIGFE_SIGCOM, DESTINO_INT_CC_SIGCOM

pd.options.mode.chained_assignment = None  # default='warn'


class AnalizadorSuministros:
    def __init__(self):
        pass

    def correr_programa(self):
        df_cartola = self.leer_archivo()
        df_cartola = self.dejar_movimientos_de_salida(df_cartola)
        df_cartola = self.filtrar_destinos_de_farmacia(df_cartola)
        df_cartola = self.asociar_codigo_articulo_a_sigcom(df_cartola)
        df_cartola = self.asociar_destino_int_a_sigcom(df_cartola)
        df_cartola = self.filtrar_items_de_farmacia(df_cartola)
        df_cartola = self.filtrar_motivos(df_cartola)

        df_completa = self.rellenar_destinos(df_cartola)

        if not 'item_cc_rellenados_completos.xlsx' in os.listdir():
            df_sin_cc_rellenados = self.rellenar_destinos(df_final)

        else:
            df_consolidada = pd.read_excel('item_cc_rellenados_completos.xlsx')

        formato_relleno = self.convertir_a_tabla_din_y_rellenar_formato(
            df_consolidada)
        formato_relleno.to_excel('output_formato.xlsx')

    def leer_archivo(self):
        df_cartola = pd.read_csv('input\\Cartola valorizada.csv')
        return df_cartola
    
    def dejar_movimientos_de_salida(self, df_cartola):
        df_filtrada = df_cartola.copy()
        return df_filtrada.query('Movimiento == "Salida"')

    def filtrar_destinos_de_farmacia(self, df_cartola):
        df_filtrada = df_cartola.copy()

        mask_farmacia = ~(df_filtrada['Destino'].str.contains('FARMACIA')) | \
                         (df_filtrada['Destino'].str.contains('SECRE. FARMACIA'))

        return df_filtrada[mask_farmacia]
    
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
    
    def filtrar_items_de_farmacia(self, df_cartola):
        df_filtrada = df_cartola.copy()
        df_filtrada = df_filtrada.query('Tipo_Articulo_SIGFE != "Farmacia"')

        return df_filtrada

    def filtrar_motivos(self, df_cartola):
        df_filtrada = df_cartola.copy()
        motivos_a_filtrar = ['Merma', 'Préstamo', 'Devolución al Proveedor']
        df_filtrada = df_filtrada[~df_filtrada['Motivo'].isin(motivos_a_filtrar)]

        return df_filtrada

    def rellenar_destinos(self, df_cartola):
        if 'cartola_valorizada_con_cc_completos.xlsx' in os.listdir('input'):
            df_cartola = pd.read_excel('input\\cartola_valorizada_con_cc_completos.xlsx')
        
        sin_cc = df_cartola[df_cartola['CC SIGCOM'].isna()]
        print('\n- Se rellenarán los centros de costo NO ASIGNADOS asociados a cada artículo - \n')
        print(f'{sin_cc.to_markdown()}')
        

        # for tupla in sin_cc.itertuples():
        #     print('\n', tupla)
        #     while True:
        #         destino = input(
        #             'Qué destino crees que es? (están en constantes.py) ')

        #         if destino in TRADUCTOR_DESTINO_INT_CC_SIGCOM_JSON:
        #             cc = TRADUCTOR_DESTINO_INT_CC_SIGCOM_JSON[destino]
        #             sin_cc.loc[tupla.Index, 'Destino'] = destino
        #             sin_cc.loc[tupla.Index, 'CC SIGCOM'] = cc
        #             break

        #         else:
        #             print('Debes ingresar un destino válido.')
        
        # df_cartola_completa.to_excel('input\\cartola_valorizada_con_cc_completos.xlsx')

        return sin_cc

    def convertir_a_tabla_din_y_rellenar_formato(self, df_consolidada):
        tabla_dinamica = pd.pivot_table(df_consolidada, values='Neto Total', index='CC SIGCOM',
                                        columns='Item SIGCOM', aggfunc=np.sum)

        formato = pd.read_excel(
            'input\\Formato 4_Distribución Suministro 2022-10.xlsx')
        formato = formato.set_index('Centro de Costo')

        for cc in tabla_dinamica.index:
            for item_sigcom in tabla_dinamica.columns:
                formato.loc[cc,
                            item_sigcom] = tabla_dinamica.loc[cc, item_sigcom]

        return formato


analizador = AnalizadorSuministros()
analizador.correr_programa()
