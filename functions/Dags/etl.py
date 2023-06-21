from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from google.cloud import storage
import wbgapi as wb
import pandas as pd
import numpy as np
import time

def etl_extract():
    paises_lista = ['DEU', 'AUS', 'CAN', 'ESP', 'USA', 'ITA', 'JPN', 'GBR', 'RUS', 'SWE',
                   'ALB', 'ARG', 'BRA', 'COL', 'VNM', 'PHL', 'IND', 'IDN', 'MEX', 'PER',
                    'ZAF', 'THA', 'AFG', 'BGD', 'EGY', 'ETH', 'IRQ', 'IRN', 'KEN', 'MAR']

    diccionario_de_datos = {'SP.DYN.LE00.IN': 'Life expectancy at birth, total (years)',
        'NY.GDP.PCAP.CD': 'GDP per capita (current US$)',
        'NY.GNP.MKTP.CD': 'GNI (current US$)',
        'NY.GDP.MKTP.CD': 'GDP (current US$)',
        'SP.URB.TOTL.IN.ZS': 'Urban population (% of total population)',
        'SP.RUR.TOTL.ZS': 'Rural population (% of total population)',
        'MS.MIL.XPND.GD.ZS': 'Military expenditure (% of GDP)',
        'NE.CON.GOVT.CD':'General government final consumption expenditure (current US$)',
        'SP.POP.GROW':'Population growth (annual %)',
        'EG.ELC.ACCS.ZS': 'Access to electricity (% of population)',
        'TX.VAL.FOOD.ZS.UN':'Food exports (% of merchandise exports)',
        'AG.PRD.FOOD.XD':'Food production index (2014-2016 = 100)',
        'NE.CON.PRVT.ZS': 'Households and NPISHs final consumption expenditure (% of GDP)'
        }

    dataset = np.array([])
    tabla_indicadores = pd.DataFrame()

    for i in diccionario_de_datos.items():
        test = wb.data.fetch(i[0], paises_lista)  # Obtener los datos del indicador econÃ³mico para los paÃ­ses dados
        time.sleep(1)  # Esperar 1 segundo (pausa)
        lista_de_paises = []  # Lista para almacenar los nombres de los paÃ­ses
        lista_de_aÃ±os = []  # Lista para almacenar los aÃ±os
        lista_de_indicadores = []  # Lista para almacenar los datos

        for a in test:
            year = int(a['time'][2::])
            if year >= 1990 and year <= 2021:
                lista_de_paises.append(a['economy'])  # Agregar el nombre del paÃ­s a la lista
                lista_de_aÃ±os.append(year)  # Agregar el aÃ±o a la lista
                lista_de_indicadores.append(a['value'])  # Agregar el valor del indicador econÃ³mico a la lista

        add = {'title': i[1], 'economy': lista_de_paises, 'time': lista_de_aÃ±os, 'value': lista_de_indicadores}  # Crear un diccionario con los datos del indicador
        dataset = np.append(dataset, add)  # Agregar el diccionario al dataset

        # ValidaciÃ³n de las dimensiones de los datos
        print('Dimension of data list: ' + str(i[1]))  # Imprimir el tÃ­tulo del indicador econÃ³mico
        print(len(lista_de_indicadores))  # Imprimir la longitud de la lista de valores del indicador

        if len(dataset) > 1:
            if dataset[-1]['time'] == dataset[-2]['time']:
                print('Is equal times')  # Imprimir mensaje si los tiempos son iguales entre indicadores consecutivos
            if dataset[-1]['economy'] == dataset[-2]['economy']:
                print('Is equal countries')  # Imprimir mensaje si los paÃ­ses son iguales entre indicadores consecutivos

        # Crear columna para cada indicador econÃ³mico en el DataFrame
        years = dataset[-1]['time']
        values = dataset[-1]['value']
        filtered_years = []
        filtered_values = []

        for j in range(len(years)):
            year = int(years[j])
            if year >= 1990 and year <= 2021:
                filtered_years.append(years[j])
                filtered_values.append(values[j])

        tabla_indicadores['country'] = dataset[-1]['economy']  # Crear columna 'country' en el DataFrame y asignar los nombres de los paÃ­ses del primer indicador econÃ³mico
        tabla_indicadores['year'] = filtered_years  # Crear columna 'year' en el DataFrame y asignar los aÃ±os del primer indicador econÃ³mico
        tabla_indicadores[i[1]] = filtered_values  # Crear columna para cada indicador econÃ³mico en el DataFrame

    # Especificar el nombre del archivo CSV que se crearÃ¡
    nombre_archivo = 'evn.csv'

    # Guardar el DataFrame como un archivo CSV en el bucket de Google Cloud Storage
    client = storage.Client()
    bucket = client.bucket('limpiezatotal')
    blob = bucket.blob(nombre_archivo)
    blob.upload_from_string(tabla_indicadores.to_csv(index=False, header=True), 'text/csv')

# Definir argumentos del DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 6, 17),
    'email': ['mauroalexanderpimentel@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Definir el DAG
dag = DAG(
    'extraccion_datos_csv_dag',
    default_args=default_args,
    description='ExtracciÃ³n de datos y guardado como CSV en GCS',
    schedule_interval='@daily',
)

# Definir el operador PythonOperator
extraer_datos_operator = PythonOperator(
    task_id='extraer_datos_task',
    python_callable=etl_extract,
    dag=dag
)

# Establecer dependencias del DAG
extraer_datos_operator