import pandas as pd
import numpy as np
import rasterio
from pygam import GAM,s

df = pd.read_csv('BioDinamica_data_2024/Sp_SDM.csv')
df = pd.DataFrame(df)

species_mapping = {'sp_10': 1, 'sp_12': 0, 'sp_127': 0}
df['sp'] = df['sp'].map(species_mapping)

df = df[df['sp'] == 1]

pontos_rasters = []

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

modelo = GAM(s(0) + s(1) + s(2) + s(3)).fit(X,y)
X_pred = []
for i in range(array_4d.shape[0]):
    for j in range(array_4d.shape[1]):
        X_pred.append(array_4d[i, j, :])
X_pred = np.array(X_pred)

# Normalizar os dados de previsão
# X_pred_scaled = scaler.transform(X_pred)

previsao = modelo.predict(X_pred)

previsao = previsao.reshape(array_4d.shape[0], array_4d.shape[1])

print(previsao[300])

with rasterio.open(tif_file) as src:
    profile = src.profile
    transform = src.transform
    crs = src.crs
    shape = src.shape

with rasterio.open('mapa_resultante_gam.tif', 'w', **profile) as dst:
    dst.write(previsao, 1)
