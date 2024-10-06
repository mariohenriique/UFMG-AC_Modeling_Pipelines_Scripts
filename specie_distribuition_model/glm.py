import statsmodels.api as sm
import pandas as pd
import numpy as np
import rasterio

df = pd.read_csv('BioDinamica_data_2024/Sp_SDM.csv')
df = pd.DataFrame(df)

species_mapping = {'sp_10': 1, 'sp_12': 0, 'sp_127': 0}
df['sp'] = df['sp'].map(species_mapping)

df = df[df['sp'] == 1]

pontos_rasters = []

with rasterio.open('BioDinamica_data_2024/Predictors/PCA1.tif') as src:
    # Extrair as dimensões e a extensão geográfica do arquivo TIFF
    xmin, ymin, xmax, ymax = src.bounds
    raster_data_aus = src.read(1)
    
    # Número desejado de pontos de pseudoausência
    num_pseudoausencia = len(df)//4
    
    # Inicializar listas para armazenar as coordenadas dos pontos de pseudoausência
    pseudoausencia_x = []
    pseudoausencia_y = []
    
    # Gerar pontos de pseudoausência aleatórios dentro da extensão geográfica do arquivo TIFF
    while len(pseudoausencia_x) < num_pseudoausencia:
        x = np.random.uniform(xmin, xmax)
        y = np.random.uniform(ymin, ymax)
        
        # Transformar as coordenadas geográficas para coordenadas de pixel
        col, row = src.index(x, y)
        # Verificar se o ponto de pseudoausência está fora da área de presença conhecida
        if not any((df['x'] == x) & (df['y'] == y)) \
            and row >= 0 and row < src.height and col >= 0 and col < src.width and (raster_data_aus[col,row]//0.0000001 > 0):
            pseudoausencia_x.append(x)
            pseudoausencia_y.append(y)

df_aus = pd.DataFrame()
df_aus['x'] = pseudoausencia_x
df_aus['y'] = pseudoausencia_y
df_aus['sp'] = 0
df = pd.concat([df,df_aus])

for i in range(1, 5):
    tif_file = 'BioDinamica_data_2024/Predictors/PCA' + str(i) + '.tif'

    with rasterio.open(tif_file) as src:
        raster_data = src.read(1)
        raster_features = []
        for idx, row in df.iterrows():
            row, col = src.index(row['x'], row['y'])
            value = raster_data[row, col]
            raster_features.append(value)
        newcolumn = 'raster_feature' + str(i)
        df[newcolumn] = raster_features
        pontos_rasters.append(raster_data)

array_4d = np.stack(pontos_rasters, axis=-1)

X = df[['raster_feature1','raster_feature2','raster_feature3','raster_feature4']]
y = df['sp']

modelo = sm.GLM(y, X, family=sm.families.Binomial()).fit()

previsao = modelo.predict(array_4d)
print(previsao[300])
# Obter as informações espaciais de um dos arquivos tif
with rasterio.open(tif_file) as src:
    profile = src.profile
    transform = src.transform
    crs = src.crs
    shape = src.shape

with rasterio.open('mapa_resultante_glm.tif', 'w', **profile) as dst:
    dst.write(previsao, 1)

