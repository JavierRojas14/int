import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import json


df = pd.read_excel('asociacion_bodega_sigfe.xlsx', header = 3)
df['Código'] = df['Código'].astype(str).str.strip().str.upper()
df['Descripción'] = df['Descripción'].astype(str).str.strip().str.upper()
df = df.sort_values('Descripción')

with open('strings_similares.txt', 'w', encoding = 'utf-8') as writer:    
    for descripcion in df['Descripción'].unique():
        resultados = process.extract(descripcion, df['Descripción'].unique(), limit = 5)

        print(f'\nSe está procesando la descripción: {descripcion} \n')
        print(str(resultados))

        writer.write(f'\nSe está procesando la descripción: {descripcion} \n')
        writer.writelines(str(resultados))
