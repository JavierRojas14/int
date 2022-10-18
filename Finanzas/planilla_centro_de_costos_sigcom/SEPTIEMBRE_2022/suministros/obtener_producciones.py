import pandas as pd
import numpy as np

def obtener_porcentaje_de_produccion(mask, produccion):
    df_mask = produccion[mask].to_frame()
    df_mask['porcentajes'] = df_mask / df_mask.sum()
    return df_mask

produccion = pd.read_excel('input\\Producción para PERC septiembre 2022 A.xlsx', header = 3)
produccion_septiembre = produccion.copy()
produccion_septiembre['EGRESOS'] = produccion_septiembre['EGRESOS'].fillna('PLACEHOLDER')
produccion_septiembre = produccion_septiembre.set_index('EGRESOS')
produccion_septiembre = produccion_septiembre['SEPTIEMBRE']

mask_imagenologia = produccion_septiembre.index.str.contains('IMAGENOLOGIA') | produccion_septiembre.index.str.contains('TOMOGRAFIA')

mask_pabellon = produccion_septiembre.index.str.contains('QUIROFANOS CARDIOVASCULAR') | produccion_septiembre.index.str.contains('QUIROFANOS CIRUGIA TORACICA')

mask_desglose_medicina_interna = produccion_septiembre.index.str.contains('HOSPITALIZACION MEDICINA INTERNA') | produccion_septiembre.index.str.contains('HOSPITALIZACION QUIRURGICA')

mask_desglose_lab_clinico = produccion_septiembre.index.str.contains('LABORATORIO CLINICO') | produccion_septiembre.index.str.contains('BANCO DE SANGRE')

mask_desglose_procedimientos_hemodinamia = produccion_septiembre.index.str.contains('HEMODINAMIA') | produccion_septiembre.index.str.contains('TAVI') | \
                            produccion_septiembre.index.str.contains('EBUS') | produccion_septiembre.index.str.contains('NEUMOLOGIA')

mask_desglose_procedimientos_cardiologia = produccion_septiembre.index.str.contains('CARDIOLOGIA') | produccion_septiembre.index.str.contains('ECMO') | \
                            produccion_septiembre.index.str.contains('CIRUGIA CARDIACA') | produccion_septiembre.index.str.contains('CIRUGIA GENERAL')

mask_desglose_uci = produccion_septiembre.index.str.contains('UNIDAD DE CUIDADOS INTENSIVOS') | produccion_septiembre.index.str.contains('UNIDAD DE TRATAMIENTO INTENSIVO ADULTO')

mask_desglose_onco = produccion_septiembre.index.str.contains('ONCOLOGIA') | produccion_septiembre.index.str.contains('MANEJO')

mask_desglose_admin = produccion_septiembre.index.str.contains('NUTRICION')

mask_consultas = produccion_septiembre.index.str.contains('CONSULTA')

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