import pyspark
from pyspark.ml import Pipeline
from pyspark.sql.types import StructType,StructField, StringType, IntegerType, FloatType, DoubleType
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, MinMaxScaler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
import sqlite3
import pandas as pd


#Create spark session
spark = pyspark.sql.SparkSession.builder.getOrCreate()

#Connect and read SQL Database
path = '/home/stephen/Desktop/Data_Engineering/house_price.db'
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
filtered_df = df[df.notnull().all(1)]

#Construct schema for pyspark dataframe
schema = StructType([ \
    StructField("price",IntegerType(),True), \
    StructField("beds",FloatType(),True), \
    StructField("baths",FloatType(),True), \
    StructField("sqft", FloatType(), True), \
    StructField("sqftlot", FloatType(), True), \
    StructField("address", StringType(), True), \
    StructField("zip", IntegerType(), True) \
  ])

#Construct pyspark dataframe
df_spark = spark.createDataFrame(data = filtered_df, schema=schema)

#Split data into train, validation, test
train, valid, test = df_spark.randomSplit([0.6, 0.2, 0.2])

#Final feature list for analysis
features = ['beds','baths','sqft','sqftlot','encoded_zip']

#Construct data pipline for encoding and model creation
indexer = StringIndexer(inputCol='zip', outputCol="indexed_zip")
encoder = OneHotEncoder(inputCol='indexed_zip',outputCol='encoded_zip')
assembler = VectorAssembler(inputCols=features, outputCol='features')
minmaxscale = MinMaxScaler(inputCol='features', outputCol='features_scaled')
lr = LinearRegression(featuresCol = 'features_scaled', labelCol='price', maxIter=100, regParam=0.3, elasticNetParam=0.8)

pipeline = Pipeline(stages=[indexer, encoder, assembler, minmaxscale,lr])

#Fit and save pyspark pipeline for later use
lr_model = pipeline.fit(train)
lr_model.write().overwrite().save('/home/stephen/Desktop/Data_Engineering/Models/lr')

#Construct r^2 and root mean squared error model evaluators
lr_r2_evaluator = RegressionEvaluator(predictionCol="prediction", \
                 labelCol="price",metricName="r2")

lr_rmse_evaluator = RegressionEvaluator(predictionCol="prediction", \
                 labelCol="price",metricName="rmse")

#Pass data into pipeline for analysis
lr_train_pred = lr_model.transform(train)
lr_val_pred = lr_model.transform(valid)
lr_test_pred = lr_model.transform(test)

#Evaluate model
print(f"LR Train r2: %.4f" % lr_r2_evaluator.evaluate(lr_train_pred))
print(f"LR Train rmse: %.4f" % lr_rmse_evaluator.evaluate(lr_train_pred))
print(f"LR Val r2: %.4f" % lr_r2_evaluator.evaluate(lr_val_pred))
print(f"LR Train rmse: %.4f" % lr_rmse_evaluator.evaluate(lr_val_pred))
print(f"LR Test r2: %.4f" % lr_r2_evaluator.evaluate(lr_test_pred))
print(f"LR Test rmse: %.4f" % lr_rmse_evaluator.evaluate(lr_test_pred))
lr_test_pred.select("prediction","price","features_scaled").show(5)













