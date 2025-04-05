from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, ArrayType, FloatType, StringType, IntegerType
from pyspark.sql.functions import col
import json, os, time, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataprocessing.categoryClassifier import Category_Classifier_Pandas_Udf
from dataprocessing.generate_vector_embeddings import Generate_Vector_Embeddings_udf
from dataprocessing.sentimentAnalysis import Sentiment_Analysis_Pandas_Udf
from dataprocessing.keywordextraction import Keyword_Extraction_Pandas_UDF

class Apache_Spark:
    def __init__(self):
        project_root = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(project_root, "..", "configs")
        dataprocessing_zip_path = os.path.join(project_root, "..", "dataprocessing.zip")
        components_zip_path = os.path.join(project_root, "..", "components.zip")
        tensor_file = os.path.join(project_root, "..", "precomputed_category_sentences_files", "category_tensor.pt")
        mapping_file = os.path.join(project_root, "..", "precomputed_category_sentences_files", "category_mapping.pkl")
        prometheus_metrics_file = os.path.join(config_dir, "metrics.properties") 

        self.spark = (SparkSession.builder
            .master("local[4]") \
            .config("spark.metrics.conf", prometheus_metrics_file) \
            .config("spark.driver.memory", "4g") \
            .config("spark.executor.memory", "4g") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.streaming.metricsEnabled","true") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .config("spark.python.worker.reuse", "true")
            .getOrCreate()
        )
        
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
        
        print(f"Adding file: {tensor_file}")
        self.spark.sparkContext.addFile(tensor_file)
        print(f"Adding file: {mapping_file}")
        self.spark.sparkContext.addFile(mapping_file)
    
        
        self.input_schema = StructType([
            StructField("post_id", StringType(), True),
            StructField("body", StringType(), True),
            StructField("subreddit", StringType(), True),
            StructField("upvotes", IntegerType(), True),
            StructField("downvotes", IntegerType(), True),
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

            dummy_data = [(f"warmup_id_{i}", f"Warmup text, uc berkeley is cool{i}", "dummy_subreddit", 1, 2, "dummy_date", "dummy_title")
                           for i in range(num_slots)]
            
            dummy_rdd = self.spark.sparkContext.parallelize(dummy_data, numSlices=num_slots)

            dummy_df = self.spark.createDataFrame(dummy_rdd, schema=self.input_schema)
            print(f"--- warm_up_udf: Created dummy DataFrame with {dummy_df.rdd.getNumPartitions()} partitions ---")

            
            processed_dummy_df = (dummy_df
                .withColumn("vector_embedding", Generate_Vector_Embeddings_udf(col("body")))
                .withColumn("sentiment_score", Sentiment_Analysis_Pandas_Udf(col("body")))
                .withColumn("category", Category_Classifier_Pandas_Udf(col("vector_embedding")))
                .withColumn("keywords", Keyword_Extraction_Pandas_UDF(col("body")))
                .select(
                    col("post_id"),
                    col("category"),
                    col("vector_embedding"),
                    col("sentiment_score"),
                    col("keywords"),
                    col("body"),
                    col("created_utc"),
                    col("title"),
                    col("subreddit"),
                    col("upvotes"),
                    col("downvotes")
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
    