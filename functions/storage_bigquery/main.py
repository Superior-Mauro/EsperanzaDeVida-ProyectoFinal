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
    
    # Obtener el nombre de la tabla a partir del nombre del archivo CSV
    table_name = os.path.splitext(file_name)[0]
    
    # Configurar el dataset de destino
    dataset_id = 'limpiezatotal'
    
    # Crear la tabla en BigQuery si no existe
    dataset_ref = bigquery_client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_name)
    
    try:
        # Verificar si la tabla ya existe
        table = bigquery_client.get_table(table_ref)
        print(f'La tabla {table_name} ya existe en BigQuery.')
    except Exception as e:
        # Si la tabla no existe, crearla con la misma estructura que el archivo CSV
        job_config = bigquery.LoadJobConfig(
            autodetect=True,
            skip_leading_rows=1,  # Saltar la primera fila, ya que son los encabezados
            source_format=bigquery.SourceFormat.CSV,
            schema_update_options=[
                bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
            ],
        )
        
        table = bigquery.Table(table_ref)
        load_job = bigquery_client.load_table_from_uri(
            file_path,
            table_ref,
            job_config=job_config
        )
        
        load_job.result()  # Esperar a que se complete la carga
        
        print(f'Tabla {table_name} creada en BigQuery.')
    
    # Cargar los datos del archivo CSV en la tabla
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        skip_leading_rows=1,  # Saltar la primera fila, ya que son los encabezados
        source_format=bigquery.SourceFormat.CSV,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,  # Agregar los datos a la tabla existente
    )
    
    load_job = bigquery_client.load_table_from_uri(
        file_path,
        table_ref,
        job_config=job_config
    )
    
    load_job.result()  # Esperar a que se complete la carga
    
    print(f'Datos del archivo {file_name} cargados correctamente en la tabla {table_name}.')
    
    # Eliminar el archivo CSV después de la carga (opcional)
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.delete()
        print(f'Archivo {file_name} eliminado del bucket.')
    except Exception as e:
        print(f'Error al eliminar el archivo {file_name} del bucket: {str(e)}')