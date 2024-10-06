from sklearn.metrics.pairwise import pairwise_distances
import pandas as pd
import numpy as np
import rasterio

df = pd.read_csv('BioDinamica_data_2024/Sp_SDM.csv')
df = pd.DataFrame(df)

species_mapping = {'sp_10': 0, 'sp_12': 1, 'sp_127': 1}
df['sp'] = df['sp'].map(species_mapping)

df = df[df['sp'] == 0]

ponto_central = []
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
        raster_features = np.array(raster_features)
        mean = raster_features.mean()
        ponto_central.append(mean)
        pontos_rasters.append(raster_data)

array_4d = np.stack(pontos_rasters, axis=-1)

# Outras distancias podem ser utilizadas trocando metric pela distancia correspondente
dists_manhattan = []
ponto_centralT = pd.DataFrame(ponto_central).T
distancia_manhanttan = pairwise_distances(array_4d.reshape((-1, 4)),ponto_centralT,metric='manhattan')
dists_manhattan.append(distancia_manhanttan)

distancias_array_manhanttan = np.array(dists_manhattan)

# Obter as informações espaciais de um dos arquivos tif
with rasterio.open(tif_file) as src:
    profile = src.profile
    transform = src.transform
    crs = src.crs
    shape = src.shape

with rasterio.open('mapa_resultante_manhattan.tif', 'w', **profile) as dst:
    dst.write(distancias_array_manhanttan.reshape(shape), 1)
