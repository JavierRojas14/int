import os
import shutil

direcciones_sin_sub_directorios = []
for (root,dirs,files) in os.walk('7 SENS_ JULIO 22', topdown=True):
        if not(dirs):
            direcciones_sin_sub_directorios.append(root)

for directorio in direcciones_sin_sub_directorios:
    shutil.copy('DICCIONARIO_CIM.json', directorio)
    shutil.copy('DICCIONARIO_CODIGO_NOMBRE_FARMACOS.json', directorio)
    shutil.copy('ENTEROBACTERIAS_RESISTENTES_NATURALMENTE.json', directorio)
    shutil.copy('ENTEROBACTERIAS.json', directorio)
    shutil.copy('formateador_xls_data_only.py', directorio)


