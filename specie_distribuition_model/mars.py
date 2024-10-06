# Verificar se é possível fazer o código do MARS, ao invés de utilizar bibliotecas
import pandas as pd
import numpy as np
import rasterio

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