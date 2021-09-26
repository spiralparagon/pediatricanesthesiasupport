import pandas as pd
import numpy as np
from st_aggrid import AgGrid
import streamlit as st


#
# This little dashboard fetches pediatric anesthesia drug data from a Google Sheets
# and then displays them as doses in unit/kg or volume (mililiters) to lessen mental load during 
# anesthesia induction on pediatric cases
# This is still an BETA and being developed, please do not use in live enviroment
# No liability will be assumed, every dosage/volume/concentration has to be double checked

sheet_id = "1MCvX4xt4IQaFePdrBn-xoCFBw1DiIVqS2FVQgmdIUVU"
sheet_name = "Drugsperkg"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

dl = pd.read_csv(url)

st.set_page_config(page_title="BarnAnestesi Läkemedel", page_icon=None, layout='wide', initial_sidebar_state='auto', menu_items=None)
st.title('BarnAnestesi Läkemedel 2')
st.write("""
Du kan också välja att använda den mer uppdaterade Google Sheets versionen på:
  https://docs.google.com/spreadsheets/d/1xiBoyy-YyNT0KiVGM4BVH8W0K-Oziw4MnZrlbl9fRvg/edit#gid=0

Båda filerna är BETA-versioner!. Ansvarig anestesiolog har till syvende och sist ansvaret för korrekta ordinationer!
Fel kan finnas beräkningarna!
""")

#print("Beta version 1. Not to be used in production! No liability will be assumed!")
#print("Fyll i vikt nedan")

@st.cache
def calculate_drugs(vikt):
    df = dl.copy()
    df['Lowdose'] = df['Lowdose']*vikt
    df['Highdose'] = df['Highdose']*vikt
    
    #Support for Minimum dose and Maximum dose, e.g Atropin
    df['Lowdose'] = df[['Lowdose', "Mindose"]].apply(lambda x: x['Mindose'] if x['Lowdose'] < x['Mindose'] else x['Lowdose'], axis=1)
    df['Lowdose'] = df[['Lowdose', "Maxdose"]].apply(lambda x: x['Maxdose'] if x['Lowdose'] > x['Maxdose'] else x['Lowdose'], axis=1)
    df['Highdose'] = df[['Highdose', "Mindose"]].apply(lambda x: x['Mindose'] if x['Highdose'] < x['Mindose'] else x['Highdose'], axis=1)
    df['Highdose'] = df[['Highdose', "Maxdose"]].apply(lambda x: x['Maxdose'] if x['Highdose'] > x['Maxdose'] else x['Highdose'], axis=1)

    df['Mililiters_Low'] = df['Lowdose']/df['Concentration_per_ml']
    df['Mililiters_High'] = df['Highdose']/df['Concentration_per_ml']
    #Round to nearest decimal 2
    df = df.round(decimals=2)
    df = df[['Drug', "Concentration_per_ml", "Formula", "Lowdose", "Highdose", "Unit", "Mililiters_Low", "Mililiters_High", "Mindose", "Maxdose", "Category", "Comment"]]
    df['Highdose'] = df['Highdose'].fillna(" ")
    df['Mililiters_Low'] = df['Mililiters_Low'].fillna(" ")
    df['Mililiters_High'] = df['Mililiters_High'].fillna(" ")
    df['Comment'] = df['Comment'].fillna(" ")
    
    

    #Last row to format
    df['Formula'] = df['Formula'].astype(str)
    df['Category'] = df['Category'].astype(str)
    df['Lowdose'] = df['Lowdose'].astype(str) + " " + df['Unit'].astype(str)
    df['Highdose'] = df['Highdose'].astype(str) + " " + df['Unit'].astype(str)
    df['Concentration_per_ml'] = df['Concentration_per_ml'].astype(str) + " " + df['Unit'].astype(str) + "/ml"
    df['Mililiters_Low'] = df['Mililiters_Low'].astype(str) + " ml"
    df['Mililiters_High'] = df['Mililiters_High'].astype(str) + " ml"
    df.drop(columns=["Unit", "Mindose", "Maxdose"], inplace=True)
    df.rename(columns={"Mililiters_Low": "ml_Low", "Mililiters_High": "ml_High", "Concentration_per_ml": "Conc"}, inplace=True)

    #display(df[df['Highdose'] == "  mg"]) ### display ceritan drug
    df['Highdose'].replace({"  Ã‚Âµg": ''}, inplace=True)
    df['Highdose'].replace({"  mg": ''}, inplace=True)
    df['Highdose'].replace({"  ml": ''}, inplace=True)
    df['Highdose'].replace({"  Joule": ''}, inplace=True)
    df['ml_High'].replace({"  ml": ''}, inplace=True)
    df['ml_Low'].replace({"  ml": ''}, inplace=True)
    df['Conc'].replace({"nan nan/ml": ''}, inplace=True)
    df['Conc'].replace({"nan mg/ml": ''}, inplace=True)
    df['Conc'].replace({"nan ml/ml": ''}, inplace=True)
    df['Conc'].replace({"nan Joule/ml": ''}, inplace=True)
    df['Conc'].replace({"nan mg FE/ml": ''}, inplace=True)
    df['Lowdose'].replace({"nan nan": ''}, inplace=True)
    df['Highdose'].replace({"  nan": ''}, inplace=True)
    df['Category'].replace({"nan": ''}, inplace=True)
    df['Formula'].replace({"nan": ''}, inplace=True)
    print("Kontrollera att vikten som valts syns pÃƒÂ¥ raden nedan (tryck nÃƒÂ¥gonstans pÃƒÂ¥ dokumentet)")
    print(f"Visar fÃƒÂ¶r vikten: {vikt} kg")
    return df

vikt = st.slider("VÃƒÂ¤lj en vikt")
st.write("Du har valt", vikt, "kg")

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
df = calculate_drugs(vikt)
# Notify the reader that the data was successfully loaded.
data_load_state.text("Calculations complete!")

AgGrid(df, height=800, fit_columns_on_grid_load=True)
#st.table(df)

#df['new column name'] = df['column name'].apply(lambda x: 'value if condition is met' if x condition else 'value if condition is not met')
#frame[['b','c']].apply(lambda x: x['c'] if x['c']>0 else x['b'], axis=1)


#display(df)
