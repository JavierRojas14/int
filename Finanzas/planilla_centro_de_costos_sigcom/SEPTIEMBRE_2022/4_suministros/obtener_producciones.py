'''
Este es un archivo para hacer un resumen de las producciones por Unidad
'''
import os

import pandas as pd

from constantes import (DICCIONARIO_UNIDADES_A_DESGLOSAR, PORCENTAJES_A_CONSULTAS_ONCOLOGIA, 
                        PORCENTAJES_A_PROCEDIMIENTOS_ONCOLOGIA, 
                        UNIDADES_PROPORCIONALES_A_LA_PRODUCCION,
                        VALOR_TAVI_SUMINISTROS, VALOR_EBUS_SUMINISTROS, VALOR_ECMO_SUMINISTROS,
                        PORCENTAJES_A_CONSULTAS_CARDIOLOGIA, PORCENTAJES_A_CONSULTAS_ONCOLOGIA,
                        PORCENTAJES_A_PROCEDIMIENTOS_CARDIOLOGIA,
                        PORCENTAJES_A_PROCEDIMIENTOS_ONCOLOGIA,
                        VALOR_CONSULTAS_ADMIN_SUMINISTROS)

pd.options.mode.chained_assignment = None  # default='warn'

class ModuloProducciones:
    def __init__(self):
        pass

    def correr_programa(self):
        df_prod = self.cargar_archivo()
        producciones_por_unidad = self.obtener_desglose_por_unidad(df_prod)
        self.guardar_archivos(producciones_por_unidad)

    def cargar_archivo(self):
        nombre_archivo = [nombre for nombre in os.listdir('input') if 'Producción' in nombre][0]
        nombre_archivo = os.path.join('input', nombre_archivo)
        df_producciones = pd.read_excel(nombre_archivo, header = 3)
        df_producciones['EGRESOS'] = df_producciones['EGRESOS'].fillna('PLACEHOLDER')
        df_producciones = df_producciones[['EGRESOS', 'SEPTIEMBRE']]
        return df_producciones

    def obtener_desglose_por_unidad(self, df_prod):
        producciones_por_unidad = pd.DataFrame()
        for unidad_a_desglosar, lista_subunidades in DICCIONARIO_UNIDADES_A_DESGLOSAR.items():
            for i, produccion_a_pedir in enumerate(lista_subunidades):
                mask_consulta = self.obtener_mask_de_unidad(df_prod, produccion_a_pedir)
                if i == 0:
                    mask_total = mask_consulta

                else:
                    mask_total = mask_total | mask_consulta

            df_unidad = df_prod[mask_total]
            df_unidad = df_unidad.groupby('EGRESOS').sum().reset_index()
            df_unidad['PORCENTAJES'] = self.obtener_porcentajes(df_unidad, unidad_a_desglosar)

            suma_producciones = df_unidad['SEPTIEMBRE'].sum()
            df_unidad.loc[len(df_unidad.index)] = [unidad_a_desglosar, suma_producciones, '1']

            df_unidad['AGRUPACION'] = unidad_a_desglosar

            producciones_por_unidad = pd.concat([producciones_por_unidad, df_unidad])

        return producciones_por_unidad

    def obtener_mask_de_unidad(self, df_prod, produccion_pedida):
        diccionario_unidad = {"41107-TOMOGRAFÍA":
                              df_prod['EGRESOS'].str.contains('TOMOGRAFIA'),

                              "41108-IMAGENOLOGÍA":
                              df_prod['EGRESOS'].str.contains('IMAGENOLOGIA'),

                              "464-QUIRÓFANOS CARDIOVASCULAR":
                              df_prod['EGRESOS'] == 'QUIROFANOS CARDIOVASCULAR',

                              "484-QUIRÓFANOS TORACICA":
                              df_prod['EGRESOS'] == 'QUIROFANOS CIRUGIA TORACICA',

                              "51001-BANCO DE SANGRE":
                              df_prod['EGRESOS'] == 'BANCO DE SANGRE',

                              "518-LABORATORIO CLÍNICO":
                              df_prod['EGRESOS'] == 'LABORATORIO CLINICO',

                              "90-HOSPITALIZACIÓN QUIRÚRGICA":
                              df_prod['EGRESOS'].str.contains('HOSPITALIZACION QUIRURGICA'),

                              "66-HOSPITALIZACIÓN MEDICINA INTERNA":
                              df_prod['EGRESOS'].str.contains('HOSPITALIZACION MEDICINA INTERNA'),

                              "270-PROCEDIMIENTOS TAVI":
                              df_prod['EGRESOS'].str.contains('TAVI'),

                              "264-PROCEDIMIENTOS EBUS":
                              df_prod['EGRESOS'] == 'PROCEDIMIENTO EBUS',

                              "15022-PROCEDIMIENTO DE NEUMOLOGÍA":
                              df_prod['EGRESOS'] == 'PROCEDIMIENTO DE NEUMOLOGIA (apnea del sueño)',

                              "253-PROCEDIMIENTOS DE HEMODINAMIA":
                              df_prod['EGRESOS'] == 'PROCEDIMIENTOS DE HEMODINAMIA',

                              "265-PROCEDIMIENTOS ECMO":
                              df_prod['EGRESOS'].str.contains('PROCEDIMIENTO ECMO'),

                              "15105-CONSULTA CARDIOLOGÍA":
                              df_prod['EGRESOS'] == 'CONSULTA CARDIOLOGIA',

                              "15220-CONSULTA CIRUGIA CARDIACA":
                              df_prod['EGRESOS'] == 'CONSULTA CIRUGIA CARDIACA',

                              "15201-CONSULTA CIRUGÍA GENERAL":
                              df_prod['EGRESOS'] == 'CONSULTA CIRUGIA GENERAL (cirugía torax)',

                              "15026-PROCEDIMIENTOS DE CARDIOLOGÍA":
                              df_prod['EGRESOS'] == 'PROCEDIMIENTO DE CARDIOLOGIA',

                              "195-UNIDAD DE TRATAMIENTO INTENSIVO ADULTO":
                              df_prod['EGRESOS'].str.contains('UNIDAD DE TRATAMIENTO INTENSIVO') &
                              (~df_prod['EGRESOS'].str.contains('(Egresos)', regex = False) |
                               ~df_prod['EGRESOS'].str.contains('(Traslados)', regex = False)),

                               "166-UNIDAD DE CUIDADOS INTENSIVOS":
                               df_prod['EGRESOS'].str.contains('UNIDAD DE CUIDADOS INTENSIVOS') &
                              (~df_prod['EGRESOS'].str.contains('(Egresos)', regex = False) |
                               ~df_prod['EGRESOS'].str.contains('(Traslados)', regex = False)),

                               "15123-PROGRAMA MANEJO DEL DOLOR":
                               df_prod['EGRESOS'] == 'CONSULTA MANEJO DEL DOLOR',

                               "15107-CONSULTA ONCOLOGÍA":
                               df_prod['EGRESOS'] == 'CONSULTA ONCOLOGIA',

                               "15038-PROCEDIMIENTO ONCOLOGÍA":
                               df_prod['EGRESOS'] == 'PROCEDIMIENTO ONCOLOGIA',

                               "15008-CONSULTA NUTRICIÓN":
                               df_prod['EGRESOS'] == 'CONSULTA NUTRICION'
                              }
        mask = diccionario_unidad[produccion_pedida]
        return mask

    def obtener_porcentajes(self, produccion_unidad, unidad_a_desglosar):
        if unidad_a_desglosar in UNIDADES_PROPORCIONALES_A_LA_PRODUCCION:
            return produccion_unidad['SEPTIEMBRE'] / produccion_unidad['SEPTIEMBRE'].sum()

        else:
            if unidad_a_desglosar == '253-PROCEDIMIENTOS DE HEMODINAMIA':
                # Aislar los procedimientos
                series_hemodinamia = produccion_unidad.copy()
                mask_procedimientos = (produccion_unidad['EGRESOS'].str.contains('NEUMOLOGIA') |
                                       produccion_unidad['EGRESOS'].str.contains('HEMODINAMIA'))

                procedimientos_hemo = produccion_unidad[mask_procedimientos]

                porcentajes_hemo = (procedimientos_hemo['SEPTIEMBRE'] /
                                                   procedimientos_hemo['SEPTIEMBRE'].sum())

                tavi = produccion_unidad.query('EGRESOS == "PROCEDIMIENTO TAVI (4 horas c/u)"')
                ebus = produccion_unidad.query('EGRESOS == "PROCEDIMIENTO EBUS"')
                valor_total_tavi = tavi['SEPTIEMBRE'] * VALOR_TAVI_SUMINISTROS
                valor_total_ebus = ebus['SEPTIEMBRE'] * VALOR_EBUS_SUMINISTROS

                series_hemodinamia.loc[porcentajes_hemo.index, 'PORCENTAJES'] = porcentajes_hemo
                series_hemodinamia.loc[valor_total_tavi.index, 'PORCENTAJES'] = valor_total_tavi
                series_hemodinamia.loc[valor_total_ebus.index, 'PORCENTAJES'] = valor_total_ebus

                print(f'Hemodinamia se desglosó en:\n{series_hemodinamia.to_markdown()}')

                return series_hemodinamia['PORCENTAJES']

            elif unidad_a_desglosar == '15026-PROCEDIMIENTOS DE CARDIOLOGÍA':
                series_cardiologia = produccion_unidad.copy()

                ecmo = produccion_unidad.query('EGRESOS == "PROCEDIMIENTO ECMO (1,5 horas c/u/)"')
                valor_total_ecmo = ecmo['SEPTIEMBRE'] * VALOR_ECMO_SUMINISTROS

                mask_consultas_cardio = produccion_unidad['EGRESOS'].str.contains('CONSULTA')
                consultas_cardio = produccion_unidad[mask_consultas_cardio]

                porcentajes_consultas_cardio = (consultas_cardio['SEPTIEMBRE'] /
                                                consultas_cardio['SEPTIEMBRE'].sum()) * \
                                                PORCENTAJES_A_CONSULTAS_CARDIOLOGIA

                procedimientos_cardio = produccion_unidad.query('EGRESOS == '
                                                                '"PROCEDIMIENTO DE CARDIOLOGIA"')
                porcentajes_proc_cardio = (procedimientos_cardio['SEPTIEMBRE'] / 
                                           procedimientos_cardio['SEPTIEMBRE'].sum()) * \
                                           PORCENTAJES_A_PROCEDIMIENTOS_CARDIOLOGIA

                series_cardiologia.loc[valor_total_ecmo.index, 'PORCENTAJES'] = valor_total_ecmo
                series_cardiologia.loc[porcentajes_consultas_cardio.index, 'PORCENTAJES'] = \
                                       porcentajes_consultas_cardio

                series_cardiologia.loc[porcentajes_proc_cardio.index, 'PORCENTAJES'] = \
                                       porcentajes_proc_cardio

                print(f'Cardiología se desglosó en:\n{series_cardiologia.to_markdown()}')

                return series_cardiologia['PORCENTAJES']

            elif unidad_a_desglosar == '15038-PROCEDIMIENTO ONCOLOGÍA':
                series_oncologia = produccion_unidad.copy()

                mask_consultas_onco = produccion_unidad['EGRESOS'].str.contains('CONSULTA')
                consultas_onco = produccion_unidad[mask_consultas_onco]

                porcentajes_consultas_onco = (consultas_onco['SEPTIEMBRE'] /
                                              consultas_onco['SEPTIEMBRE'].sum()) * \
                                              PORCENTAJES_A_CONSULTAS_ONCOLOGIA

                procedimientos_onco = produccion_unidad.query('EGRESOS == '
                                                              '"PROCEDIMIENTO ONCOLOGIA"')
                porcentajes_proc_onco = (procedimientos_onco['SEPTIEMBRE'] /
                                         procedimientos_onco['SEPTIEMBRE'].sum()) * \
                                         PORCENTAJES_A_PROCEDIMIENTOS_ONCOLOGIA

                series_oncologia.loc[porcentajes_consultas_onco.index, 'PORCENTAJES'] = \
                                     porcentajes_consultas_onco

                series_oncologia.loc[porcentajes_proc_onco.index, 'PORCENTAJES'] = \
                                     porcentajes_proc_onco

                print(f'Oncologia se desglosó en:\n{series_oncologia.to_markdown()}')

                return series_oncologia['PORCENTAJES']

            elif unidad_a_desglosar == '670-ADMINISTRACIÓN':
                series_admin = produccion_unidad.copy()

                mask_consultas_admin = produccion_unidad['EGRESOS'].str.contains('CONSULTA')
                consultas_admin = produccion_unidad[mask_consultas_admin]

                valor_total_consultas_admin = consultas_admin['SEPTIEMBRE'] * \
                                              VALOR_CONSULTAS_ADMIN_SUMINISTROS

                series_admin.loc[valor_total_consultas_admin.index, 'PORCENTAJES'] = \
                                 valor_total_consultas_admin

                print(f'Administración se desglosó en:\n{series_admin.to_markdown()}')

                return series_admin['PORCENTAJES']

    def guardar_archivos(self, produccion_por_unidad):
        with pd.ExcelWriter('output.xlsx') as writer:
            produccion_por_unidad.to_excel(writer, sheet_name = 'produccion_por_unidad', index =
                                                                                         False)


modulo_producciones = ModuloProducciones()
modulo_producciones.correr_programa()
