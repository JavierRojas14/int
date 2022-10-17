import pandas as pd
from constantes import TRADUCTOR_DESTINO_INT_CC_SIGCOM_JSON, TRADUCTOR_ITEM_SIGFE_ITEM_SIGCOM_JSON
pd.options.mode.chained_assignment = None  # default='warn'


class AnalizadorSuministros:
    def __init__(self) :
        pass

    def correr_programa(self):
        df_cartola, df_traductor_bodega_sigfe, \
        TRADUCTOR_ITEM_SIGFE_ITEM_SIGCOM, TRADUCTOR_DESTINO_INT_CC_SIGCOM = self.leer_archivos()

        unidas_destino = self.unir_archivos(df_cartola, df_traductor_bodega_sigfe, TRADUCTOR_ITEM_SIGFE_ITEM_SIGCOM, \
                      TRADUCTOR_DESTINO_INT_CC_SIGCOM)

        df_final = self.filtrar_salidas_farmacia(unidas_destino)
        df_final = self.filtrar_motivos(df_final)
        self.rellenar_destinos(df_final)

    def leer_archivos(self):
        df_cartola = pd.read_csv('input\\Cartola valorizada.csv')
        df_traductor_bodega_sigfe = pd.read_excel('input\\asociacion_bodega_sigfe.xlsx', header = 3)

        df_traductor_sigfe_sigcom_cristian = pd.read_excel('input\\Categorías de insumos.xlsx')


        df_traductor_bodega_sigfe = df_traductor_bodega_sigfe.rename(columns = {'Nombre Items': \
                                                                                'Item SIGFE'})
        TRADUCTOR_ITEM_SIGFE_ITEM_SIGCOM = df_traductor_sigfe_sigcom_cristian.iloc[66:83, [0, 1]]
        TRADUCTOR_ITEM_SIGFE_ITEM_SIGCOM = TRADUCTOR_ITEM_SIGFE_ITEM_SIGCOM.rename(columns = 
                                                                        {'Destino INT': 'Item SIGFE',
                                                                        'Unnamed: 1': 'Item SIGCOM'})

        TRADUCTOR_DESTINO_INT_CC_SIGCOM = df_traductor_sigfe_sigcom_cristian.iloc[0:63, [0, 1]]\
                                                .rename(columns = {'Unnamed: 1': 'CC SIGCOM',
                                                                    'Destino INT': 'Destino'})
        
        return df_cartola, df_traductor_bodega_sigfe, \
               TRADUCTOR_ITEM_SIGFE_ITEM_SIGCOM, TRADUCTOR_DESTINO_INT_CC_SIGCOM
    
    def unir_archivos(self, df_cartola, df_traductor_bodega_sigfe, TRADUCTOR_ITEM_SIGFE_ITEM_SIGCOM, \
                      TRADUCTOR_DESTINO_INT_CC_SIGCOM):

        unidas = pd.merge(df_cartola, df_traductor_bodega_sigfe, how = 'left', left_on = 'Codigo Articulo',
                                                                        right_on = 'Código')

        unidas_concepto_presup = pd.merge(unidas, TRADUCTOR_ITEM_SIGFE_ITEM_SIGCOM, how = 'left',
                                                                                    on = 'Item SIGFE')

        unidas_destino = pd.merge(unidas_concepto_presup, TRADUCTOR_DESTINO_INT_CC_SIGCOM, how = 'left',
                                                                                        on = 'Destino')

        print(unidas_destino.columns)
        unidas_destino = unidas_destino[['Codigo Articulo', 'Nombre', 'Movimiento', 'Destino', 'Motivo',
                                        'Neto Total', 'Familia', 'Item SIGFE', 'Item SIGCOM', 'CC SIGCOM']]
        
        return unidas_destino
    
    def filtrar_salidas_farmacia(self, unidas_destino):
        df_final = unidas_destino.copy()
        df_final = df_final.query('Movimiento == "Salida"')

        mask_farmacia = ~(df_final['Destino'].str.contains('FARMACIA')) | \
                        (df_final['Destino'].str.contains('SECRE. FARMACIA'))

        df_final = df_final[mask_farmacia]
        df_final = df_final.query('`Item SIGFE` != "Farmacia"')
        
        return df_final
    
    def filtrar_motivos(self, df_final):
        motivos_a_filtrar = ['Merma', 'Préstamo', 'Devolución al Proveedor']
        df_final = df_final[~df_final['Motivo'].isin(motivos_a_filtrar)]

        df_final.to_excel('Filtrado.xlsx', index = False)

        return df_final
    
    def rellenar_destinos(self, df_final):
        sin_cc = df_final[df_final['CC SIGCOM'].isna()]
        print(f'Las siguientes filas NO tienen CC SIGCOM:\n{sin_cc}')
        print('- Se procederá a rellenarlas -')

        for tupla in sin_cc.itertuples():
            print('\n', tupla)
            while True:
                destino = input('Qué destino crees que es? (están en constantes.py) ')

                if destino in TRADUCTOR_DESTINO_INT_CC_SIGCOM_JSON:
                    cc = TRADUCTOR_DESTINO_INT_CC_SIGCOM_JSON[destino]
                    sin_cc.loc[tupla.Index, 'Destino'] = destino
                    sin_cc.loc[tupla.Index, 'CC SIGCOM'] = cc
                    break

                else:
                    print('Debes ingresar un destino válido.')

analizador = AnalizadorSuministros()
analizador.correr_programa()