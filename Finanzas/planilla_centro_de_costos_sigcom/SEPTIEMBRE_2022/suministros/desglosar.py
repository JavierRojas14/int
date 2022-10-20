import pandas as pd
import numpy as np
import random
from constantes import TRADUCTOR_DESTINO_INT_CC_SIGCOM_JSON, TRADUCTOR_ITEM_SIGFE_ITEM_SIGCOM_JSON

df = pd.read_excel('item_cc_rellenados_completos.xlsx')
tabla_din = pd.pivot_table(df, values = 'Neto Total', index = 'CC SIGCOM', columns = 'Item SIGCOM', aggfunc=np.sum)

diccionario_todos_los_desgloses = {
    '41108-IMAGENOLOGÍA': ['41107-TOMOGRAFÍA', '41108-IMAGENOLOGÍA'],
    'PABELLÓN': ['464-QUIRÓFANOS CARDIOVASCULAR', '484-QUIRÓFANOS TORACICA'],
    '518-LABORATORIO CLÍNICO': ['51001-BANCO DE SANGRE', '518-LABORATORIO CLÍNICO'],
    '66-HOSPITALIZACIÓN MEDICINA INTERNA': ['90-HOSPITALIZACIÓN QUIRÚRGICA', '66-HOSPITALIZACIÓN MEDICINA INTERNA'],
    '253-PROCEDIMIENTOS DE HEMODINAMIA': ['270-PROCEDIMIENTOS TAVI', '264-PROCEDIMIENTOS EBUS', 
                                          '15022-PROCEDIMIENTO DE NEUMOLOGÍA', 
                                          '253-PROCEDIMIENTOS DE HEMODINAMIA'],
    '15026-PROCEDIMIENTOS DE CARDIOLOGÍA': ['15105-CONSULTA CARDIOLOGÍA', '265-PROCEDIMIENTOS ECMO',
                                           '15220-CONSULTA CIRUGIA CARDIACA', '15201-CONSULTA CIRUGÍA GENERAL',
                                           '15026-PROCEDIMIENTOS DE CARDIOLOGÍA'],
    '166-UNIDAD DE CUIDADOS INTENSIVOS': ['195-UNIDAD DE TRATAMIENTO INTENSIVO ADULTO', 
                                          '166-UNIDAD DE CUIDADOS INTENSIVOS'],
    '15038-PROCEDIMIENTO ONCOLOGÍA': ['15123-PROGRAMA MANEJO DEL DOLOR',
                                      '15107-CONSULTA ONCOLOGÍA',
                                      '15038-PROCEDIMIENTO ONCOLOGÍA'],
    '670-ADMINISTRACIÓN': ['15008-CONSULTA NUTRICIÓN', '670-ADMINISTRACIÓN']
    
}

total = pd.DataFrame()
for item_desglose, a_desglosar in diccionario_todos_los_desgloses.items():
    if item_desglose in tabla_din.index:
        filas_a_agregar = []
        valores_antiguos = tabla_din.loc[item_desglose]
        for desglose in a_desglosar:
            print(f'El item {item_desglose} lo estamos desglosando en {desglose}')
            porcentaje = input('¿Qué porcentaje tiene este item?: ')
            porcentaje = porcentaje.replace(',', '.')
            porcentaje = float(porcentaje)
            porcentaje_cantidad = valores_antiguos * porcentaje
            porcentaje_cantidad.name = desglose

            filas_a_agregar.append(porcentaje_cantidad)

        valores_antiguos.name = 'Total'
        filas_a_agregar.append(valores_antiguos)
        df_super = pd.DataFrame(filas_a_agregar)

    else:
        print('No hubo gastos en este item.')

    total = pd.concat([total, df_super])
    total.to_excel('desgloses.xlsx')

    