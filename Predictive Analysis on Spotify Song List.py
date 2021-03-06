# -*- coding: utf-8 -*-
"""ALY6020_Group_Week6_FinalProject.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17EX9vNiuiK1gOTzSVhxIds2vIhGpbArv
"""

# Libraries
import numpy as np
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, plot_roc_curve, classification_report
from sklearn.svm import SVC

"""# 1. EDA"""

# Set directory
directory = os.getcwd()
dataPath = directory + '/spotify_song.csv' # You can change the file name here or in your directory

# Import data 
try:
    df = pd.read_csv(dataPath)
except FileNotFoundError:
    print(f'File not found. Please make sure the CSV file spotify_song.csv available in your directory {directory}')

df.head()

df.shape

df.artist.value_counts().head(15).plot(kind='barh')
plt.title('TOP 200 Appearances by Frequency')
plt.show()

R_S = ['#19B5FE', '#FFD43B'] 
palette = sns.color_palette(R_S)
sns.set_palette(palette)
sns.set_style('white')

#Visualizing songs tempo together

#calling all tempo values with target == 1, considered as pos tempo, user liked it
p_tempo = df[df['target']==1]['tempo']
#target == 0, considered as pos tempo, user liked it
n_tempo = df[df['target']==0]['tempo']

p_dance = df[df['target']==1]['danceability']
n_dance = df[df['target']==0]['danceability']

p_duration_ms = df[df['target']==1]['duration_ms']
n_duration_ms = df[df['target']==0]['duration_ms']

p_loudness = df[df['target']==1]['loudness']
n_loudness = df[df['target']==0]['loudness']

p_speechiness = df[df['target']==1]['speechiness']
n_speechiness = df[df['target']==0]['speechiness']

p_valence = df[df['target']==1]['valence']
n_valence = df[df['target']==0]['valence']

p_energy = df[df['target']==1]['energy']
n_energy = df[df['target']==0]['energy']

p_acousticness = df[df['target']==1]['acousticness']
n_acousticness = df[df['target']==0]['acousticness']

p_key = df[df['target']==1]['key']
n_key = df[df['target']==0]['key']

p_key = df[df['target']==1]['key']
n_key = df[df['target']==0]['key']

p_instrumentalness = df[df['target']==1]['instrumentalness']
n_instrumentalness = df[df['target']==0]['instrumentalness']

fig1 = plt.figure(figsize=(12,8))
plt.title('song Temp')
p_tempo.hist(alpha=0.7, bins=30, label='positive')
n_tempo.hist(alpha=0.7, bins=30, label='negative')
plt.legend(loc = 'upper right')

df.info()

# Select relevant columns
data = df.iloc[:,1:15]
x_data = data.drop('target', axis = 1)
y_data = data['target']



# Descriptive analysis
data.describe()

# Check null values
data.isnull().sum()

# Check duplicated values
duplicate = df.duplicated()
print(duplicate.sum())

# Select relevant columns
data = df.iloc[:,1:15]

# Calculate Z-score
numerical_features = data.iloc[:,0:13].columns
z = np.abs(stats.zscore(data[numerical_features]))

# Remove outliers
data_outlier_removed = data[(z < 3).all(axis=1)]
data_outlier_removed = data_outlier_removed.reset_index(drop = True)
data_outlier_removed.shape

x_data = data_outlier_removed.drop('target', axis = 1)
y_data = data_outlier_removed['target']

#plt.figure(figsize=(18,12))
sns.set(rc={'figure.figsize':(10,8)})
x_data.hist()
plt.suptitle('Histograms of Numerical Variables')

# Create heatmap of Correlation Matrix
corr = data.corr()
plt.figure(figsize=(18, 6))
ax = sns.heatmap(
    corr, 
    vmin = -1, vmax = 1, center = 0,
    cmap = sns.diverging_palette(20, 220, n = 200),
    square = True
)
ax.set_xticklabels(
    ax.get_xticklabels(),
    rotation = 45,
    horizontalalignment = 'right'
);

# Line graphs for some features of songs 
# Data preparation
# create two separate datasets by targets
like = data['target'] == 1
dislike = data['target'] == 0 
like_list = data.loc[like]
dislike_list = data.loc[dislike]
dislike_list = dislike_list.reset_index(drop = True)

#add the count column of songs 
like_list.loc[:,'song'] = pd.Series(range(1, len(like_list['target']) + 1))
dislike_list.loc[:,'song'] = pd.Series(range(1, len(dislike_list['target']) + 1))

# Plotting with multipleline graphs
fig, ax = plt.subplots(2, 2, figsize=(18, 10))

sns.lineplot(ax = ax[0,0], x = "song", y = "liveness", data = like_list.iloc[0:60, :], label="like", color="coral")
sns.lineplot(ax = ax[0,0], x = "song", y = "liveness", data = dislike_list.iloc[0:60, :], label="dislike", color="steelblue")
ax[0,0].legend(loc='upper right')

sns.lineplot(ax = ax[0,1], x = "song", y = "instrumentalness", data = like_list.iloc[0:60, :], label="like", color="coral")
sns.lineplot(ax = ax[0,1], x = "song", y = "instrumentalness", data = dislike_list.iloc[0:60, :], label="dislike", color="steelblue")
ax[0,1].legend(loc='upper right')

sns.lineplot(ax = ax[1,0], x = "song", y = "acousticness", data = like_list.iloc[0:60, :], label="like", color="coral")
sns.lineplot(ax = ax[1,0], x = "song", y = "acousticness", data = dislike_list.iloc[0:60, :], label="dislike", color="steelblue")
ax[1,0].legend(loc='upper right')

sns.lineplot(ax = ax[1,1], x = "song", y = "danceability", data = like_list.iloc[0:60, :], label="like")
sns.lineplot(ax = ax[1,1], x = "song", y = "danceability", data = dislike_list.iloc[0:60, :], label="dislike")
ax[1,1].legend(loc='upper right')

"""# 2. Data Modeling

### 2.1. First Predictive Model: K-Nearest Neighbors
"""

feature_names = x_data.columns
feature_names

# Data standardization
scaler = StandardScaler()
scaler.fit(x_data)
scaled = scaler.transform(x_data)
x_data_feat = pd.DataFrame(scaled, columns = x_data.columns)

#convert dataframe into numpy array for model fitting 
X = x_data_feat.to_numpy()
y = y_data.to_numpy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

i = 1
print('KNN WITH EUCLIDEAN METRIC')
while i <= 11:
    knn = KNeighborsClassifier(n_neighbors = i, metric = 'euclidean')
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    score = knn.score(X_test, y_test)
    print(f'K-nearest neighbors with k = {i}: \nConfusion Matrix:\n{cm}\nAccuracy: {round(score,4)}\n ')
    i += 2

i = 1
print('KNN WITH MANHATTAN METRIC')
while i <= 11:
    knn = KNeighborsClassifier(n_neighbors = i, metric = 'manhattan')
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    score = knn.score(X_test, y_test)
    print(f'K-nearest neighbors with k = {i}: \nConfusion Matrix:\n{cm}\nAccuracy: {round(score,4)}\n ')
    i += 2

"""### 2.2. Model Comparison and Accuracy Improvement"""

sns.set(rc={'figure.figsize':(8,6)})
# Create Support Vector Classifier curve
svc = SVC(random_state=42)
svc.fit(X_train, y_train)
svc_disp = plot_roc_curve(svc, X_test, y_test)

# Create ROC curve plotting function
def ROC(model):
    ax = plt.gca()
    #Create ROC curve
    rf_disp = plot_roc_curve(model, X_test, y_test, ax=ax, alpha=0.8)
    svc_disp.plot(ax=ax, alpha=0.8)
    #svc_disp.plot(ax=ax, alpha=0.8)
    plt.show()

def create_model(model, x_train, y_train, x_test, y_test): 
    # Fitting
    model = model.fit(x_train, y_train)
    
    # Prediction
    y_pred = model.predict(x_test)
    
    # Accuracy calculation 
    cm = confusion_matrix(y_test, y_pred)
    score = model.score(X_test, y_test)
   
    return model, cm, score

# Fitting three different models and comparison
models = [KNeighborsClassifier(n_neighbors = 9, metric = 'manhattan'), 
          LogisticRegression(), 
          RandomForestClassifier(random_state=42)]
names = ['KNN', 'Logistic Regression', 'Random Forest']
    
for model,name in zip(models,names):
    model, cm, score = create_model(model,X_train,y_train, X_test, y_test)
    print(f'''{name} model
Confusion matrix:\n {cm}
Accuracy: {round(score, 4)}''')
    print("ROC curve:")
    ROC(model)

"""It seems that RF model has the highest accuracy and best ROC curve among these three tested models


"""

# Random Forest Model has the highest accuracy and best ROC curve
# Look at more details in RF model
rf_model, rf_cm, rf_accuracy  = create_model(RandomForestClassifier(random_state=42),
                                             X_train, y_train, X_test, y_test)
y_pred = rf_model.predict(X_test)

report = classification_report(y_test, y_pred, target_names=['0', '1'])
print(f'''Random Forest Classification
Confusion matrix:\n {rf_cm}
Accuracy: {round(rf_accuracy, 4)}\n
Random Forest Classification Report:
{report}''')

# Visualizing important features in Random Forest model
feature_names = x_data.columns
feature_imp = pd.Series(rf_model.feature_importances_, index=feature_names).sort_values(ascending=False)

plt.figure(figsize=(10,6))
# Creating a bar plot
sns.barplot(x=feature_imp, y=feature_imp.index)

# Add labels to your graph
plt.xlabel('Feature Importance Score')
plt.ylabel('Features')
plt.title("Visualizing Important Features")
plt.show()

"""Additional Predictive Model: XGBoost"""

xgbmodel = XGBClassifier()
xgbmodel.fit(X_train, y_train)

xgb_y_pred = xgbmodel.predict(X_test)

xgb_predictions = [round(value) for value in xgb_y_pred]

#evaluate predictions
from sklearn.metrics import accuracy_score
accuracy = accuracy_score(y_test, xgb_predictions)
print("Accuracy: %.2f%%" % (accuracy * 100.0))

