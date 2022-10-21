'''
Este es un archivo para hacer un resumen de las producciones por Unidad'''

import json
from math import prod
from operator import mod
import os

import pandas as pd

from constantes import DICCIONARIO_UNIDADES_A_DESGLOSAR


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
            suma_producciones = df_unidad['SEPTIEMBRE'].sum()
            df_unidad.loc[len(df_unidad.index)] = [unidad_a_desglosar, suma_producciones]
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
                              (~df_prod['EGRESOS'].str.contains('(Egresos)') |
                               ~df_prod['EGRESOS'].str.contains('(Traslados)')),

                               "166-UNIDAD DE CUIDADOS INTENSIVOS":
                               df_prod['EGRESOS'].str.contains('UNIDAD DE CUIDADOS INTENSIVOS') &
                              (~df_prod['EGRESOS'].str.contains('(Egresos)') |
                               ~df_prod['EGRESOS'].str.contains('(Traslados)')),

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


    def obtener_porcentaje_de_produccion(self, mask, produccion):
        df_mask = produccion[mask].to_frame()
        df_mask['porcentajes'] = df_mask / df_mask.sum()
        return df_mask

    def guardar_archivos(self, produccion_por_unidad):
        with pd.ExcelWriter('output.xlsx') as writer:
            produccion_por_unidad.to_excel(writer, sheet_name = 'produccion_por_unidad')


modulo_producciones = ModuloProducciones()
modulo_producciones.correr_programa()