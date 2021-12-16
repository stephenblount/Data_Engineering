import streamlit as st
from joblib import load
import pandas as pd
import pathlib
# import pickle


st.title("Seattle Home Value Predictor")

zip_code = st.selectbox("Select Zip Code", 
[98146,98122,98112,98115,98109,98136,98177,98117,98116,98199,
 98103,98102,98101,98118,98107,98125,98106,98178,98168,98119,
 98134,98144,98121,98105,98108,98133,98126,98104,98164,98166])

beds = st.number_input("Number of Bedrooms", min_value=0, max_value=15, value=2)
baths = st.number_input("Number of Bathrooms", min_value=1.0, max_value=10.0, value=1.0, step=0.5)
sqft = st.number_input("Size of Home (sqft)", min_value=100, max_value=10000, value=500, step=10)
sqftlot = st.number_input("Lot Size (sqft)", min_value=100, max_value=1000000, value=5000, step=100)
st.write("If no lot size exists, set equal to Size of Home")
st.write("1 Acre = 43,560 Square Feet")

# lr_model = pickle.load(open('stephenblount/data_engineering/main/App/lr_model.pkl', 'rb'))

PATH = pathlib.Path(__file__).parent
lr_model = load(PATH.joinpath('lr_model.joblib'))

input_data = pd.DataFrame([(beds,baths,sqft,sqftlot,zip_code)], columns = ["beds", "baths","sqft","sqftlot","zip"])

lr_pred = lr_model.predict(input_data)
prediction = "          Predicted Home Value: ${:,.0f}".format(lr_pred[0])

st.title("")
st.header(prediction)
