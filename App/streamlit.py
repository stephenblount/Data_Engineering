import streamlit as st
import pyspark
from pyspark import SparkConf
from pyspark.ml import PipelineModel
st.title("Seattle House Price Predictor")

zip_code = st.sidebar.selectbox("Select Zip Code", 
[98146,98122,98112,98115,98109,98136,98177,98117,98116,98199,
 98103,98102,98101,98118,98107,98125,98106,98178,98168,98119,
 98134,98144,98121,98105,98108,98133,98126,98104,98164,98166])

beds = st.sidebar.number_input("Number of Bedrooms", min_value=0, max_value=15, value=2)
baths = st.sidebar.number_input("Number of Bathrooms", min_value=1.0, max_value=10.0, value=1.0, step=0.5)
sqft = st.sidebar.number_input("Size of Home (sqft)", min_value=100, max_value=10000, value=500, step=10)
sqftlot = st.sidebar.number_input("Lot Size (sqft)", min_value=100, max_value=1000000, value=5000, step=100)
st.sidebar.write("If no lot size exists, set equal to Size of Home")
st.sidebar.write("1 Acre = 43,560 Square Feet")

# input_data = pd.DataFrame({'beds':[beds], 'baths':[baths],'sqft':[sqft], 'sqftlot':[sqftlot], 'zip':[zip_code]})
# prediction = lr.predict(input_data)[0]

conf = SparkConf().setAppName("lecture-lyon2").setMaster("local")
spark = pyspark.sql.SparkSession.builder.config(conf=conf).getOrCreate()
lr_model = PipelineModel.load('/Models/lr')
input_data = spark.createDataFrame([(beds,baths,sqft,sqftlot,zip_code)], 
                                    ["beds", "baths","sqft","sqftlot","zip"])

lr_pred = lr_model.transform(input_data)
prediction = lr_pred.select('prediction').collect()[0]
prediction = "${:,.0f}".format(prediction[0])
st.write(prediction)
