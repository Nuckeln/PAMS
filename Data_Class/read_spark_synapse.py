from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip


def read_delta_v2_local(path: str):


    builder = (
        SparkSession.builder
        .appName("Read Delta v2 (Local)")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        # Speicher
        .config("spark.driver.memory", "12g")
        .config("spark.executor.memory", "12g")
        # Azure JARs (lokal)
        .config(
            "spark.jars",
            "/Users/martinwolf/spark_jars/hadoop-azure-3.3.4.jar,"
            "/Users/martinwolf/spark_jars/hadoop-azure-datalake-3.3.4.jar,"
            "/Users/martinwolf/spark_jars/hadoop-common-3.3.4.jar,"
            "/Users/martinwolf/spark_jars/hadoop-auth-3.3.4.jar,"
            "/Users/martinwolf/spark_jars/azure-storage-8.6.6.jar"
        )
        # ADLS Zugriff
        .config("fs.azure.account.auth.type.storpdnedatalakedev01.dfs.core.windows.net", "SharedKey")
        .config("fs.azure.account.key.storpdnedatalakedev01.dfs.core.windows.net",
                "Nhl9qv4ZP/oFN8mmU+MUn9F+MPcJA0oP/WjpaVBUyf4w7X/2jmAoeSSsK8Wu89QOYOpPaVZAQssV+AStuyZYAg==")
        # Delta Optionen
        .config("spark.databricks.delta.schema.autoMerge.enabled", "true")
        .config("spark.sql.parquet.mergeSchema", "false")
    )

    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    df = spark.read.format("delta").load(path)
    return df

# path = "abfss://synapsefs@storpdnedatalakedev01.dfs.core.windows.net/gold/GERMANY_OrderCuts/"
# df_spark = read_delta_v2_local(path)
# display(df_spark)
