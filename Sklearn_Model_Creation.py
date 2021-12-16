from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.pipeline import Pipeline
import sqlite3
import pandas as pd
import numpy as np
import joblib
import sklearn

path = '/home/stephen/Desktop/Data_Engineering/house_price.db'

#Connect and read SQL Database
conn = sqlite3.connect(path)
curs = conn.cursor()
query = """UPDATE house
SET sqftlot = sqft
WHERE sqftlot IS NULL"""
curs.execute(query)
conn.commit()

query = 'SELECT * from house'
df = pd.read_sql_query(query, conn)
conn.close()

#Drop null values from dataframe
filtered_df = df.copy(deep=True)
filtered_df = filtered_df[filtered_df.notnull().all(1)]
filtered_df = filtered_df.drop(['address'], axis=1)

#Split data into train, validation, test
X, y = filtered_df.drop('price',axis=1), filtered_df['price']
X, X_test, y, y_test = train_test_split(X, y, test_size=.2, random_state=1)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=.25, random_state=2)

#Create Pipline
pipe = Pipeline([('encoder', ColumnTransformer(transformers =[('enc', OneHotEncoder(drop ='first',sparse=False),['zip'])], remainder='passthrough')),
                ('regressor', LinearRegression())])


#Fit pipline to traning data
pipe.fit(X_train, y_train)

#Evaluate Model
print(pipe.score(X_train, y_train))
print(pipe.score(X_val, y_val))
print(pipe.score(X_test, y_test))

# Export the regressor to a file
joblib.dump(pipe, 'lr_model.joblib')




