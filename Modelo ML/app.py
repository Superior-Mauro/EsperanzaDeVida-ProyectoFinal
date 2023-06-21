import numpy as np
from flask import Flask, request, jsonify, render_template, url_for
import pickle
import streamlit as st


# Path del modelo preentrenado
MODEL_PATH = 'models/pickle_model.pkl'


# Se recibe la imagen y el modelo, devuelve la predicción
def model_prediction(x_in, regressor):

    x = np.asarray(x_in).reshape(1,-1)
    preds=regressor.predict(x)

    return preds

regressor=''

# Se carga el modelo
if regressor=='':
    with open(MODEL_PATH, 'rb') as file:
        regressor = pickle.load(file)
    
def main():

    # Título
    html_temp = """
    <h1 style="color:#181082;text-align:center;">SISTEMA DE RECOMENDACIÓN PARA ESPERANZA DE VIDA </h1>
    </div>
    """
    st.markdown(html_temp,unsafe_allow_html=True)

    # Lectura de datos
    #Datos = st.text_input("Ingrese los valores :")
    GDP_per_capita = st.text_input("GDP per capita:",22303.9613266628)
    GNI = st.text_input("GNI:",1790871642658.27)
    GDP = st.text_input("GDP:",1771671206875.68)
    Urban_population = st.text_input("Urban population:",73.118)
    Rural_population = st.text_input("Rural population:",26.882)
    Military_expenditure = st.text_input("Military expenditure:",2.51843270660831)
    General_government_final_consumption_expenditure = st.text_input("Government final consumption expenditure:",338394845660.332)
    Population_growth = st.text_input("Population growth:",0.861969448764933)
    Access_to_electricity = st.text_input("Access to electricity:",100.0)
    Food_exports = st.text_input("Food exports:",4.78724273053314)
    Food_production_index = st.text_input("Food production index:",100.42)
    Households_and_npish_final_consumption_expenditure = st.text_input("Households final consumption expenditure:",56.3462980039738)

    if st.sidebar.button("test"):
        GDP_per_capita.title =1
        st.write("test" )

    
    # El botón predicción se usa para iniciar el procesamiento
    if st.button("Predicción :"): 
        #x_in = list(np.float_((Datos.title().split('\t'))))
        x_in =[
                    np.float_(GDP_per_capita.title()),
                    np.float_(GNI.title()),
                    np.float_(GDP.title()),
                    np.float_(Urban_population.title()),
                    np.float_(Rural_population.title()),
                    np.float_(Military_expenditure.title()),
                    np.float_(General_government_final_consumption_expenditure.title()),
                    np.float_(Population_growth.title()),
                    np.float_(Access_to_electricity.title()),
                    np.float_(Food_exports.title()),
                    np.float_(Food_production_index.title()),
                    np.float_(Households_and_npish_final_consumption_expenditure.title())
                    ]
        st.write('Esperanza de vida es: ')
        predictS = model_prediction(x_in, regressor)

        st.success('La esperanza de vida es: {}'.format(predictS[0]))


if __name__ == '__main__':
    main()
