import pandas as pd
import numpy as np

from obtener_producciones import DICCIONARIO_UNIDADES_A_DESGLOSAR


class ModuloProducciones:
    def __init__(self):
        pass

    def correr_programa(self):
        pass

    def obtener_desglose_por_unidad(self):
        for unidad_a_desglosar in DICCIONARIO_UNIDADES_A_DESGLOSAR:
            for subunidades_a_desglosar in DICCIONARIO_UNIDADES_A_DESGLOSAR[unidad_a_desglosar]:
                break


    def obtener_mask_de_unidad(self, df_prod, produccion_pedida):
        diccionario_unidad = {"41107-TOMOGRAFÍA": 
                              df_prod['EGRESOS'].str.contains('TOMOGRAFIA'),

                              "41108-IMAGENOLOGÍA": 
                              df_prod['EGRESOS'].str.contains('IMAGENOLOGIA'),

                              "464-QUIRÓFANOS CARDIOVASCULAR": 
                              df_prod['EGRESOS'].str.contains('QUIROFANOS CARDIOVASCULAR'),

                              "84-QUIRÓFANOS TORACICA":
                              df_prod.index.str.contains('QUIROFANOS CIRUGIA TORACICA'),

                              "51001-BANCO DE SANGRE":
                              df_prod['EGRESOS'].str.contains('BANCO DE SANGRE'),

                              "518-LABORATORIO CLÍNICO":
                              df_prod['EGRESOS'].str.contains('LABORATORIO CLINICO'),

                              "90-HOSPITALIZACIÓN QUIRÚRGICA":
                              df_prod['EGRESOS'].str.contains('HOSPITALIZACION QUIRURGICA'),

                              "66-HOSPITALIZACIÓN MEDICINA INTERNA":
                              df_prod['EGRESOS'].str.contains('HOSPITALIZACION MEDICINA INTERNA'),

                              "270-PROCEDIMIENTOS TAVI":
                              df_prod['EGRESOS'].str.contains('TAVI'),

                              "264-PROCEDIMIENTOS EBUS":
                              df_prod['EGRESOS'].str.contains('EBUS'),

                              "15022-PROCEDIMIENTO DE NEUMOLOGÍA":
                              df_prod['EGRESOS'].str.contains('NEUMOLOGIA'),

                              "253-PROCEDIMIENTOS DE HEMODINAMIA":
                              df_prod['EGRESOS'].str.contains('HEMODINAMIA'),

                              "265-PROCEDIMIENTOS ECMO":
                              df_prod['EGRESOS'].str.contains('ECMO'),

                              "15105-CONSULTA CARDIOLOGÍA":
                              df_prod['EGRESOS'].str.contains('CONSULTA CARDIOLOGIA'),

                              "15220-CONSULTA CIRUGIA CARDIACA":
                              df_prod['EGRESOS'].str.contains('CONSULTA CIRUGIA CARDIACA'),

                              "15201-CONSULTA CIRUGÍA GENERAL":
                              df_prod['EGRESOS'].str.contains('CONSULTA CIRUGIA GENERAL'),

                              "15026-PROCEDIMIENTOS DE CARDIOLOGÍA":
                              df_prod['EGRESOS'].str.contains('PROCEDIMIENTO DE CARDIOLOGIA'),
                
                              "195-UNIDAD DE TRATAMIENTO INTENSIVO ADULTO":
                              df_prod['EGRESOS'].str.contains('UNIDAD DE TRATAMIENTO INTENSIVO') &
                              (~df_prod['EGRESOS'].str.contains('(Egresos)') |
                               ~df_prod['EGRESOS'].str.contains('(Traslados)')),
                
                               "166-UNIDAD DE CUIDADOS INTENSIVOS":
                               df_prod['EGRESOS'].str.contains('UNIDAD DE CUIDADOS INTENSIVOS') &
                              (~df_prod['EGRESOS'].str.contains('(Egresos)') |
                               ~df_prod['EGRESOS'].str.contains('(Traslados)')),

                               "15123-PROGRAMA MANEJO DEL DOLOR":
                               df_prod['EGRESOS'].str.contains('CONSULTA MANEJO DEL DOLOR'),

                               "15107-CONSULTA ONCOLOGÍA":
                               df_prod['EGRESOS'].str.contains('CONSULTA ONCOLOGIA'),

                               "15038-PROCEDIMIENTO ONCOLOGÍA":
                               df_prod['EGRESOS'].str.contains('PROCEDIMIENTO ONCOLOGIA'),

                               "15008-CONSULTA NUTRICIÓN":
                               df_prod['EGRESOS'].str.contains('CONSULTA NUTRICION')
                              }



def obtener_porcentaje_de_produccion(mask, produccion):
    df_mask = produccion[mask].to_frame()
    df_mask['porcentajes'] = df_mask / df_mask.sum()
    return df_mask

produccion = pd.read_excel('input\\Producción para PERC septiembre 2022 A.xlsx', header = 3)
produccion_septiembre = produccion.copy()
produccion_septiembre['EGRESOS'] = produccion_septiembre['EGRESOS'].fillna('PLACEHOLDER')
produccion_septiembre = produccion_septiembre.set_index('EGRESOS')
produccion_septiembre = produccion_septiembre['SEPTIEMBRE']

mask_imagenologia = df_prod['EGRESOS'].str.contains('IMAGENOLOGIA') | df_prod['EGRESOS'].str.contains('TOMOGRAFIA')

mask_pabellon = df_prod['EGRESOS'].str.contains('QUIROFANOS CARDIOVASCULAR') | df_prod['EGRESOS'].str.contains('QUIROFANOS CIRUGIA TORACICA')

mask_desglose_medicina_interna = df_prod['EGRESOS'].str.contains('HOSPITALIZACION MEDICINA INTERNA') | df_prod['EGRESOS'].str.contains('HOSPITALIZACION QUIRURGICA')

mask_desglose_lab_clinico = df_prod['EGRESOS'].str.contains('LABORATORIO CLINICO') | df_prod['EGRESOS'].str.contains('BANCO DE SANGRE')

mask_desglose_procedimientos_hemodinamia = df_prod['EGRESOS'].str.contains('HEMODINAMIA') | df_prod['EGRESOS'].str.contains('TAVI') | \
                            df_prod['EGRESOS'].str.contains('EBUS') | df_prod['EGRESOS'].str.contains('NEUMOLOGIA')

mask_desglose_procedimientos_cardiologia = df_prod['EGRESOS'].str.contains('CARDIOLOGIA') | df_prod['EGRESOS'].str.contains('ECMO') | \
                            df_prod['EGRESOS'].str.contains('CIRUGIA CARDIACA') | df_prod['EGRESOS'].str.contains('CIRUGIA GENERAL')

mask_desglose_uci = df_prod['EGRESOS'].str.contains('UNIDAD DE CUIDADOS INTENSIVOS') | df_prod['EGRESOS'].str.contains('UNIDAD DE TRATAMIENTO INTENSIVO ADULTO')

mask_desglose_onco = df_prod['EGRESOS'].str.contains('ONCOLOGIA') | df_prod['EGRESOS'].str.contains('MANEJO')

mask_desglose_admin = df_prod['EGRESOS'].str.contains('NUTRICION')

mask_consultas = df_prod['EGRESOS'].str.contains('CONSULTA')

todas_las_masks = [mask_imagenologia, mask_pabellon, mask_desglose_medicina_interna, 
                   mask_desglose_lab_clinico, mask_desglose_procedimientos_hemodinamia, 
                   mask_desglose_procedimientos_cardiologia, mask_desglose_uci, mask_desglose_onco,
                   mask_desglose_admin, mask_consultas]

total = pd.DataFrame()
for mask in todas_las_masks:
    produccion_desgl = obtener_porcentaje_de_produccion(mask, produccion_septiembre).reset_index()\
                                                                        .groupby('EGRESOS')\
                                                                        .sum()

    total = pd.concat([total, produccion_desgl])
    print('\n\n')

total.to_excel('producciones.xlsx')