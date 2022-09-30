import os
import shutil
import time


class GestorArchivos:
    def __init__(self):
        os.chdir('..')

        self.ruta_util = os.getcwd()
        self.directorios_sin_sub_directorios = []

        for directorio in os.listdir():
            for root, dirs, files in os.walk(directorio, topdown = True):
                if not(dirs) and not('PROGRAMA' in root):
                    self.directorios_sin_sub_directorios.append(root)

    
    def copiar_y_pegar_archivos_programa(self):
        for root in self.directorios_sin_sub_directorios:
            shutil.copy('DICCIONARIO_CIM.json', root)
            shutil.copy('DICCIONARIO_CODIGO_NOMBRE_FARMACOS.json', root)
            shutil.copy('ENTEROBACTERIAS_RESISTENTES_NATURALMENTE.json', root)
            shutil.copy('ENTEROBACTERIAS.json', root)
            shutil.copy('formateador_xls_data_only.py', root)
            shutil.copy('GENEROS_ENTEROBACTERIAS.json', root)

    def lanzar_programa(self):
        for root in self.directorios_sin_sub_directorios:
            os.chdir(root)
            os.system('python formateador_xls_data_only.py')
            os.chdir(self.ruta_util)


gestor_archivos = GestorArchivos()
gestor_archivos.copiar_y_pegar_archivos_programa()
start = time.time()
gestor_archivos.lanzar_programa()
termino = time.time()

print(f'El programa se demoro {termino - start}s en terminar')
