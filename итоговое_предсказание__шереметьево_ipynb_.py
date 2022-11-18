pip install catboost >> none

import datetime
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

from catboost import CatBoostRegressor, CatBoostClassifier

from sklearn.model_selection import *
from sklearn.metrics import *

pd.options.display.float_format = "{:.1f}".format
sns.set_style("whitegrid")
plt.style.use("fivethirtyeight") 

import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split

"""# загрузка датасетов"""

df_Union = pd.read_excel("df_Union.xlsx")

df_pas = pd.read_excel("Пассажиропоток.xlsx")

df_table = pd.read_excel("Расписание рейсов 05-06.2022 (1).xlsx")

pd.set_option('display.max_columns', None)

"""# Данные входные новые"""

df_Union.head(3)

df_Union.shape

df_Union.info()

df_pas.head(3)

df_pas.shape

df_pas.info()

df_table.head(3)

df_table.shape

df_table.info()

"""# Анализ"""

df_Union.head(3)

print(f"Данные лежат в следующем промежутке времени: от {df_Union['TimeThirty2'].min()} до {df_Union['TimeThirty2'].max()}")

(df_Union["TotalSumm"]/60).describe(percentiles=np.linspace(0.1, 0.999, 10))

TotalSumm = df_Union["TotalSumm"]
TotalSumm.plot.hist(bins=100);

th = np.percentile(df_Union["TotalSumm"], 99.5)
th

TotalSumm = df_Union.loc[df_Union["TotalSumm"]<th, "TotalSumm"]
TotalSumm.plot.hist(bins=100);

df = df_Union.copy()

df["day_of_week"] = df["TimeThirty2"].dt.day_of_week
df["hour"] = df["TimeThirty2"].dt.hour
df["month"] = df["TimeThirty2"].dt.month
df["day_of_year"] = df["TimeThirty2"].dt.date

"""Зависимость продаж от часа"""

sns.countplot(data=df, x="hour");

plt.figure(figsize=(15,30))
sns.countplot(data=df.sort_values(by='day_of_year'), y='day_of_year');

sns.countplot(data=df, x="day_of_year");

sns.countplot(data=df, x="day_of_week");

sns.countplot(data=df, x="month");

"""# Models catboost"""

df_Union.isnull().sum()

"""## удаление и пустоты"""

df = df.fillna(0)

# df.fillna(df.mean())

df = df.drop(['TimeThirty', 'DAT'], axis = 1)

df = df.drop(['Суммарное время ожидания в часах', 'Суммарное время ожидания в часах между прилет и вылет'], axis = 1)

df = df.drop(['Среднее время ожидания в часах между прилет и вылет'], axis = 1)

df = df.drop(['Среднее время ожидания в часах'], axis = 1)

df = df.drop(['День недели'], axis = 1)

df = df.drop(['day_of_year'], axis = 1)

df = df.drop(['month'], axis = 1)

df.columns

df.head(3)

df['hour'] = df['hour'].astype(str)

df['day_of_week'] = df['day_of_week'].astype(str)

df['Касса'] = df['Касса'].astype(str)

cat_features = ['Торговая точка', 'Касса', 'orgtype', 'terminal', 'tzone', 'DD', 'WW', "W'W'", 'c', 'VV', 'day_of_week', 'hour']

df.info()

df.columns

cat_columns = df.select_dtypes(include=['object']).columns
cat_columns

df[['Торговая точка', 'Касса', 'orgtype', 'terminal', 'tzone', 'DD', 'WW', "W'W'", 'c', 'VV', 'day_of_week', 'hour']] = df[['Торговая точка', 'Касса', 'orgtype', 'terminal', 'tzone', 'DD', 'WW', "W'W'", 'c', 'VV', 'day_of_week', 'hour']].astype('category')

df[ 'VV' ] = df[ 'VV' ].cat.codes

# df[cat_columns].apply(lambda x: x.cat.codes)

df.head(3)

df.info()

df_train = df[df['TimeThirty2']<'2022-06-01']

df_test = df[df['TimeThirty2']>='2022-06-01']

"""### Преобразованиие данных в X и y"""

X = df_train.drop(['TotalSumm', 'TimeThirty2'], axis=1)
y_regression = df_train['TotalSumm']

cat_features = ['Торговая точка', 'Касса', 'orgtype', 'terminal', 'tzone', 'DD', 'WW', "W'W'", 'c', 'VV', 'day_of_week', 'hour']

X_test = df_test.drop(['TotalSumm', 'TimeThirty2'], axis=1)
y_test_regression = df_test['TotalSumm']

"""## Обучение и тестирование моделей

### Подход №1: Регрессия
"""

X_train, X_val, y_train, y_val = train_test_split(X, y_regression, test_size=0.2, random_state=42)

model_regression = CatBoostRegressor(
    verbose=100,
    cat_features=cat_features
)

model_regression.fit(X_train, y_train, eval_set=(X_val, y_val))

preds_test_regression = model_regression.predict(X_test[model_regression.feature_names_])

# print('Test MAE:', mean_absolute_error(y_test_regression, preds_test_regression))

print('Test MAE:', mean_absolute_error(y_test_regression, preds_test_regression))

"""## Предсказание"""

df_test['pred'] = preds_test_regression

df_test.head(3)

df_test.to_csv('pred.csv', sep=';', index=None)

df_test.to_excel("pred.xlsx")

"""# feature_importance"""

feature_importance = model_regression.feature_importances_
sorted_idx = np.argsort(feature_importance)
fig = plt.figure(figsize=(3, 6))
plt.barh(range(len(sorted_idx)), feature_importance[sorted_idx], align='center')
plt.yticks(range(len(sorted_idx)), np.array(X_test.columns)[sorted_idx])
plt.title('Feature Importance')

feature_importance = model_regression.feature_importances_
sorted_idx = np.argsort(feature_importance)
fig = plt.figure(figsize=(12, 6))
plt.barh(range(len(sorted_idx)), feature_importance[sorted_idx], align='center')
plt.yticks(range(len(sorted_idx)), np.array(X_test.columns)[sorted_idx])
plt.title('Feature Importance')

"""# Gradient Boosting lightgbm"""

df[['Торговая точка', 'Касса', 'orgtype', 'terminal', 'tzone', 'DD', 'WW', "W'W'", 'c', 'VV', 'day_of_week', 'hour']] = df[['Торговая точка', 'Касса', 'orgtype', 'terminal', 'tzone', 'DD', 'WW', "W'W'", 'c', 'VV', 'day_of_week', 'hour']].astype('category')

df[ 'VV' ] = df[ 'VV' ].cat.codes

cat_columns = df.select_dtypes(['category']).columns
cat_columns

df[cat_columns] = df[cat_columns].apply(lambda x: x.cat.codes)

df.head(3)

params = {
    "task":"train", 
    "boosting":"gbdt", 
    "objective":"regression", 
    "num_leaves":8, 
    "n_estimators":1000,
    "learning_rate":0.03, 
    "metric": {"l2"}, 
    "verbose": -1
}

df_train = df[df['TimeThirty2']<'2022-06-01']

df_test = df[df['TimeThirty2']>='2022-06-01']

X = df_train.drop(['TotalSumm', 'TimeThirty2'], axis=1)
y = df_train['TotalSumm']

X_test = df_test.drop(['TotalSumm', 'TimeThirty2'], axis=1)
y_test = df_test['TotalSumm']

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.15, random_state=17)

import lightgbm as lgb

lgb_train = lgb.Dataset(X_train, y_train)
lgb_eval = lgb.Dataset(X_val, y_val, reference=lgb_train)

model = lgb.train(params, 
                  train_set=lgb_train, 
                  valid_sets=lgb_eval,
                  early_stopping_rounds=30)

y_pred = model.predict(X_test)
print("RMSLE: ", mean_squared_error(y_test, y_pred)**0.5)

print('Test MAE:', mean_absolute_error(y_test, y_pred))

"""## Output Analysis"""

fig, ax = plt.subplots(figsize=(3, 6))
lgb.plot_importance(model, ax=ax)

fig, ax = plt.subplots(figsize=(5, 8))
lgb.plot_importance(model, ax=ax)

# lgb.plot_importance(model, height=1);

"""## Предсказание"""

df_test['pred'] = y_pred

df_test.head(3)

df_test.to_csv('pred_lgb.csv', sep=';', index=None)

df_test.to_excel("pred_lgb.xlsx")
