import os

direcciones_sin_sub_directorios = []
for (root,dirs,files) in os.walk('7 SENS_ JULIO 22', topdown=True):
        if not(dirs):
            direcciones_sin_sub_directorios.append(root)
    
directorio_antiguo = os.getcwd()
for directorio in direcciones_sin_sub_directorios:
    os.chdir(directorio)
    os.system('python formateador_xls_data_only.py')
    os.chdir(directorio_antiguo)