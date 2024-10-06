import pandas as pd
import numpy as np
import rasterio
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, accuracy_score

df = pd.read_csv('BioDinamica_data_2024/Sp_SDM.csv')
df = pd.DataFrame(df)

species_mapping = {'sp_10': 1, 'sp_12': 0, 'sp_127': 0}
df['sp'] = df['sp'].map(species_mapping)

# df = df[df['sp'] == 1]
df = df[df['sp'].notnull()]

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

# Dividir os dados em conjuntos de treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Normalizar os dados
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)

X_test = scaler.transform(X_test)

# Criar e treinar o modelo ANN 
# Tentar mudar os parametros para nao ter overfitting
model = MLPClassifier(hidden_layer_sizes=(50, 30), activation='relu', solver='adam', max_iter=500, random_state=42)
model.fit(X,y)#X_train, y_train)

X_pred = []
for i in range(array_4d.shape[0]):
    for j in range(array_4d.shape[1]):
        X_pred.append(array_4d[i, j, :])
X_pred = np.array(X_pred)

previsao = model.predict_proba(X_pred)[:,1]
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

with rasterio.open('mapa_resultante_ann.tif', 'w', **profile) as dst:
    dst.write(previsao, 1)
