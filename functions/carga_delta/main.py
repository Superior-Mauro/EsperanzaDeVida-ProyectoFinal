import os
from google.cloud import bigquery
from google.cloud import storage

def load_csv_to_bigquery(data, context):
    # Obtener información del archivo cargado
    bucket_name = data['bucket']
    file_name = data['name']
    
    # Verificar que el archivo sea un archivo CSV
    if not file_name.endswith('.csv'):
        print(f'El archivo {file_name} no es un archivo CSV. No se realizará la carga a BigQuery.')
        return
    
    # Configurar el cliente de Storage
    storage_client = storage.Client()
    
    # Obtener la ruta del archivo CSV
    file_path = f'gs://{bucket_name}/{file_name}'
    
    # Configurar el cliente de BigQuery
    bigquery_client = bigquery.Client()
    
    # Configurar el dataset y tabla de destino
    dataset_id = 'datos'
    table_id = 'tabla21'
    
    # Cargar el archivo CSV a BigQuery
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        skip_leading_rows=1,  # Saltar la primera fila, ya que son los encabezados
        source_format=bigquery.SourceFormat.CSV,
    )
    
    dataset_ref = bigquery_client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    
    try:
        load_job = bigquery_client.load_table_from_uri(
            file_path,
            table_ref,
            job_config=job_config
        )
        
        load_job.result()  # Esperar a que se complete la carga
        
        print(f'Archivo {file_name} cargado correctamente a BigQuery.')
    
    except Exception as e:
        print(f'Error al cargar el archivo {file_name} a BigQuery: {str(e)}')
    
    # Eliminar el archivo CSV después de la carga (opcional)
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.delete()
        print(f'Archivo {file_name} eliminado del bucket.')
    except Exception as e:
        print(f'Error al eliminar el archivo {file_name} del bucket: {str(e)}')