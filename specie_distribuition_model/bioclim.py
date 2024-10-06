import pandas as pd
import rasterio
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('BioDinamica_data_2024/Sp_SDM.csv')
df = pd.DataFrame(df)

df = df[df['sp'] == 'sp_10']
species_mapping = {'sp_10': 0, 'sp_12': 1, 'sp_127': 1}
df['sp'] = df['sp'].map(species_mapping)

result_arrays = []

for i in range(1,5):
    tif_file = 'BioDinamica_data_2024/Predictors/PCA'+str(i)+'.tif'

    with rasterio.open(tif_file) as src:
        # Ler os dados raster
        raster_data = src.read(1)
        transform = src.transform
        raster_shape = raster_data.shape
        profile = src.profile

    raster_features = []
    for idx, row in df.iterrows():
        row, col = src.index(row['x'], row['y'])
        value = raster_data[row, col]
        raster_features.append(value)

    # df['raster_feature'] = raster_features
    raster_features = np.array(raster_features)
    max_1 = raster_features.max()
    min_1 = raster_features.min()

    indices_1 = np.where((raster_data >= min_1) & (raster_data <= max_1))
    result_array = np.zeros(raster_shape, dtype=np.uint8)
    result_array[indices_1] = 1
    # Adicione o array resultante à lista
    result_arrays.append(result_array)

# Combine os arrays resultantes de cada raster em um único array somando-os
final_result_array = sum(result_arrays)

# Normalize os valores do array final para 0 e 1
final_result_array = np.where(final_result_array > 3, 1, 0)

# Salve o novo array como um arquivo .tif
with rasterio.open('mapa_resultante_bioclim.tif', 'w', **profile) as dst:
    dst.write(final_result_array, 1)
