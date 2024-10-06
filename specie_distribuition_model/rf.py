# Importando as bibliotecas necessárias
import pandas as pd
import numpy as np
import rasterio
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

df = pd.read_csv('BioDinamica_data_2024/Sp_SDM.csv')
df = pd.DataFrame(df)

species_mapping = {'sp_10': 1, 'sp_12': 0, 'sp_127': 0}
df['sp'] = df['sp'].map(species_mapping)

# df = df[df['sp'] == 1]
df = df[df['sp'].notnull()]

pontos_rasters = []
nodata_value = -9999  # Ou o valor específico que você deseja usar para dados ausentes
extreme_negative_value = -1.7e+308  # Valor extremo a ser substituído

# Extraindo características dos rasters
for i in range(1, 5):
    tif_file = 'BioDinamica_data_2024/Predictors/PCA' + str(i) + '.tif'
    
    with rasterio.open(tif_file) as src:
        raster_data = src.read(1)
        raster_nodata = src.nodata
        
        if raster_nodata is None:
            raster_nodata = nodata_value
        
        raster_features = []
        for idx, row in df.iterrows():
            row_idx, col_idx = src.index(row['x'], row['y'])
            if 0 <= row_idx < raster_data.shape[0] and 0 <= col_idx < raster_data.shape[1]:
                value = raster_data[row_idx, col_idx]
                if value == raster_nodata or value == extreme_negative_value:
                    value = np.nan  # Ou outro valor que você escolha para representar ausência de dados
            else:
                value = np.nan
            raster_features.append(value)
        
        newcolumn = 'raster_feature' + str(i)
        df[newcolumn] = raster_features
        pontos_rasters.append(raster_data)

# Empilhando os dados raster em uma matriz 4D
array_4d = np.stack(pontos_rasters, axis=-1)

# Substituindo NaN e valores extremos por um valor específico (por exemplo, zero) para a modelagem
array_4d[np.isnan(array_4d)] = 0.0
array_4d[array_4d == extreme_negative_value] = 0.0

X = df[['raster_feature1','raster_feature2','raster_feature3','raster_feature4']]
y = df['sp']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Criando o modelo Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Treinando o modelo
model.fit(X,y)#X_train, y_train)

X_pred = []
for i in range(array_4d.shape[0]):
    for j in range(array_4d.shape[1]):
        X_pred.append(array_4d[i, j, :])
X_pred = np.array(X_pred)

# Fazendo previsões
previsao = model.predict_proba(X_pred)
previsao = previsao[:, 1]  # Assumindo que estamos interessados na probabilidade da classe positiva
previsao = previsao.reshape(array_4d.shape[0], array_4d.shape[1])

print(previsao[300])  # Verificar um valor de previsão

# Criar o raster de saída
with rasterio.open('BioDinamica_data_2024/Predictors/PCA1.tif') as src:
    profile = src.profile
    transform = src.transform
    crs = src.crs
    nodata = src.nodata

mask = array_4d[:, :, 0] == nodata  # Considerando que a ausência de dados é marcada por nodata
previsao[mask] = nodata  # Atribuir valor nodata para regiões sem dados

with rasterio.open('mapa_resultante_rf.tif', 'w', **profile) as dst:
    dst.write(previsao, 1)


