from sklearn.model_selection import train_test_split
import xgboost as xgb
import pandas as pd
import rasterio
import numpy as np

from sklearn.datasets import load_iris

iris = load_iris()
df_iris = pd.DataFrame(data=iris.data, columns=iris.feature_names)
df_iris['species'] = iris.target
df_iris['species'] = df_iris['species'].map({i: name for i, name in enumerate(iris.target_names)})
df_iris['species'] = df_iris['species'].map({'setosa':0,'versicolor':1,'virginica':2})#{i: name for i, name in enumerate(iris.target_names)})

x_iris = df_iris.drop(['species'],axis=1)
y_iris = df_iris['species']

X_iris_train, X_iris_test, y_iris_train, y_iris_test = train_test_split(x_iris, y_iris, random_state=42)

classificador_xgb = xgb.XGBClassifier()
v = classificador_xgb.fit(X_iris_train,y_iris_train)
a = classificador_xgb.predict(X_iris_test)
# print(a)

df = pd.read_csv('BioDinamica_data_2024/Sp_SDM.csv')
df = pd.DataFrame(df)

species_mapping = {'sp_10': 0, 'sp_12': 1, 'sp_127': 1}
df['sp'] = df['sp'].map(species_mapping)

tif_file = 'BioDinamica_data_2024/Predictors/PCA1.tif'

with rasterio.open(tif_file) as src:
    # Ler os dados raster
    raster_data = src.read(1)
    transform = src.transform
    raster_shape = raster_data.shape

raster_features = []
for idx, row in df.iterrows():
    row, col = src.index(row[' x'], row[' y'])
    value = raster_data[row, col]
    raster_features.append(value)

df['raster_feature'] = raster_features
# Definir os recursos (features) e o alvo (target)
X = df.drop(columns=['sp', ' x', ' y'])
y = df['sp']

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = xgb.XGBClassifier(objective='binary:logistic')
a = model.fit(X,y)

raster_data_reshaped = raster_data.reshape(-1, 1)

# Fazer previsões
predicted_probabilities = model.predict(raster_data_reshaped)
# print(predicted_probabilities[253530:253530+300])
predicted_probabilities = predicted_probabilities.reshape(raster_shape)

# print(predicted_probabilities[300])

# Criar um novo arquivo raster para o mapa da distribuição da espécie prevista
output_file = 'predicted_species_distribution.tif'
with rasterio.open(
    output_file,
    'w',
    driver='GTiff',
    height=raster_shape[0],
    width=raster_shape[1],
    count=1,
    dtype=np.float32,
    crs=src.crs,
    transform=transform,
) as dst:
    dst.write(predicted_probabilities, 1)

modelo = xgb.XGBRegressor()
b = modelo.fit(X,y)
c = modelo.predict(raster_data_reshaped)
d = c.reshape(raster_shape)

output_file = 'predicted_species_distribution2.tif'
with rasterio.open(
    output_file,
    'w',
    driver='GTiff',
    height=raster_shape[0],
    width=raster_shape[1],
    count=1,
    dtype=np.float32,
    crs=src.crs,
    transform=transform,
) as dst:
    dst.write(d, 1)