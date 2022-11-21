import os
import pandas as pd
import sys 


def cargar_archivo_produccion():
    mes_a_analizar = sys.argv[1]

    nombre_archivo = [nombre for nombre in os.listdir('input') if 'Producción' in nombre][0]
    nombre_archivo = os.path.join('input', nombre_archivo)
    producciones = pd.read_excel(nombre_archivo)

    producciones = producciones.loc[:, 'SERVICIOS FINALES':'TOTAL AÑO']
    producciones.columns = [
        'SERVICIOS FINALES', 'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO',
        'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE', 'TOTAL AÑO']

    producciones['SERVICIOS FINALES'] = producciones['SERVICIOS FINALES'].fillna('PLACEHOLDER')

    df_hospitalizaciones = producciones.loc[0:2, ['SERVICIOS FINALES', mes_a_analizar]]
    df_producciones = producciones.loc[3:, ['SERVICIOS FINALES', mes_a_analizar]]

    return df_hospitalizaciones, df_producciones


if __name__ == '__main__':
    hospitalizaciones_mes, producciones_mes = cargar_archivo_produccion()
    print(hospitalizaciones_mes)
    print(producciones_mes)
