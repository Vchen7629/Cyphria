from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, ArrayType, FloatType, StringType
from pyspark.sql.functions import col
import json, os, time, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataprocessing.categoryClassifier import Category_Classifier_Pandas_Udf
from dataprocessing.generate_vector_embeddings import Generate_Vector_Embeddings_udf
from dataprocessing.sentimentAnalysis import Sentiment_Analysis_Pandas_Udf
#from components.kafka_consumer import kafka

class Apache_Spark:
    def __init__(self):
        java_opts = (
            "--add-opens=java.base/java.nio=ALL-UNNAMED "
            "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED "
            "--add-opens=java.base/java.lang=ALL-UNNAMED "
            "--add-opens=java.base/java.util=ALL-UNNAMED "
            "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED" 
        )


        self.spark = (SparkSession.builder
            .master("local[4]") \
            .config("spark.driver.extraJavaOptions", java_opts) \
            .config("spark.executor.extraJavaOptions", java_opts) \
            .config("spark.driver.memory", "4g") \
            .config("spark.executor.memory", "4g") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true")
            .config("spark.python.worker.reuse", "true")
            .getOrCreate()
        )
        
        
        project_root = os.path.dirname(os.path.abspath(__file__))
        dataprocessing_zip_path = os.path.join(project_root, "..", "dataprocessing.zip")
        components_zip_path = os.path.join(project_root, "..", "components.zip")
        
        if os.path.exists(dataprocessing_zip_path):
            print(f"Adding py file: {dataprocessing_zip_path}")
            self.spark.sparkContext.addPyFile(dataprocessing_zip_path)
        else:
            print(f"Warning: {dataprocessing_zip_path} not found. UDFs might fail.")
        
        if os.path.exists(components_zip_path):
             print(f"Adding py file: {components_zip_path}")
             self.spark.sparkContext.addPyFile(components_zip_path)
        else:
             print(f"ERROR: Required zip file not found at {components_zip_path}")
             raise FileNotFoundError(f"Required zip file 'components.zip' not found at {components_zip_path}")

        
        self.input_schema = StructType([
            StructField("post_id", StringType(), True),
            StructField("body", StringType(), True),
            StructField("subreddit", StringType(), True),
            StructField("created_utc", StringType(), True),
            StructField("title", StringType(), True),
        ])
        
        self.output_schema = StructType([
            StructField("post_id", StringType(), True),
            StructField("category", StringType(), True),
            StructField("vector_embedding", ArrayType(FloatType()), True),
            StructField("sentiment_score", FloatType(), True),
            StructField("body", StringType(), True),
            StructField("subreddit", StringType(), True),
            StructField("created_utc", StringType(), True),
            StructField("title", StringType(), True),
        ])
        
        print("Warming up Spark UDFs...")
        self.warm_up_udf()
        print("Warm-up complete.")
        self.batch_buffer = []
    
    def warm_up_udf(self):
        try:
            num_slots = self.spark.sparkContext.defaultParallelism
            print(f"--- warm_up_udf: Target parallelism = {num_slots} ---")

            dummy_data = [(f"warmup_id_{i}", f"Warmup text {i}", "dummy_subreddit", "dummy_date", "dummy_title")
                           for i in range(num_slots)]
            
            dummy_rdd = self.spark.sparkContext.parallelize(dummy_data, numSlices=num_slots)

            dummy_df = self.spark.createDataFrame(dummy_rdd, schema=self.input_schema)
            print(f"--- warm_up_udf: Created dummy DataFrame with {dummy_df.rdd.getNumPartitions()} partitions ---")

            
            processed_dummy_df = (dummy_df
                .withColumn("category", Category_Classifier_Pandas_Udf(col("body")))
                .withColumn("vector_embedding", Generate_Vector_Embeddings_udf(col("body")))
                .withColumn("sentiment_score", Sentiment_Analysis_Pandas_Udf(col("body")))
                .select(
                    col("post_id"),
                    col("category"),
                    col("vector_embedding"),
                    col("sentiment_score"),
                    col("body"),
                    col("created_utc"),
                    col("title"),
                    col("subreddit")
                )
            )
            print("UDFs triggered successfully.")
            count_result =  processed_dummy_df.show()
            print(f"Result: {count_result} ---")

        except Exception as e:
            print(f"WARNING: Spark warm-up failed: {e}")

Spark = Apache_Spark()

if __name__ == "__main__":
    Spark()
    