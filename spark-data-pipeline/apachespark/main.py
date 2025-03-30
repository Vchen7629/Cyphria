from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, ArrayType, FloatType, StringType
from pyspark.sql.functions import col
import json, os, time

from dataprocessing.categoryClassifier import Category_Classifier_Pandas_Udf
from dataprocessing.generate_vector_embeddings import Generate_Vector_Embeddings_udf
from dataprocessing.sentimentAnalysis import Sentiment_Analysis_Pandas_Udf

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
            .config("spark.sql.execution.arrow.pyspark.enabled", "true")
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
            StructField("date", StringType(), True)
        ])
        
        self.output_schema = StructType([
            StructField("post_id", StringType(), True),
            StructField("category", StringType(), True),
            StructField("vector_embedding", ArrayType(FloatType()), True),
            StructField("sentiment_score", FloatType(), True),
            StructField("body", StringType(), True),
            StructField("subreddit", StringType(), True),
            StructField("date", StringType(), True)
        ])
        
        print("Warming up Spark UDFs...")
        self.warm_up_udf()
        print("Warm-up complete.")
        self.batch_buffer = []
    
    def warm_up_udf(self):
        try:
            dummy_data = [("warmup_id", "This is dummy text for warm-up.", "dummy_subreddit", "dummy_date")]
            dummy_df = self.spark.createDataFrame(dummy_data, schema=self.input_schema)
            
            (dummy_df
                .withColumn("category", Category_Classifier_Pandas_Udf(col("body")))
                .withColumn("vector_embedding", Generate_Vector_Embeddings_udf(col("body")))
                .withColumn("sentiment_score", Sentiment_Analysis_Pandas_Udf(col("body")))
                .limit(1)
                .count()
            )
            print("UDFs triggered successfully.")
        except Exception as e:
            print(f"WARNING: Spark warm-up failed: {e}")
    
    def inputData(self, query):
        if isinstance(query, dict):
            data = query
        else:
            data = json.loads(query)
                        
        row = (
            data.get("id", ""),
            data.get("body", ""),
            data.get("subreddit", ""),
            data.get("date", "")
        )
        
        self.batch_buffer.append(row)
        
    def Process_Batch(self):        
        if not self.batch_buffer:
            print("No data in buffer to process.")
            return 0
        
        batch_data = self.batch_buffer[:]
        self.batch_buffer = []
        
        try:
            input_df = self.spark.createDataFrame(batch_data, schema=self.input_schema)
            input_df.cache()
            
            processed_df = (input_df
                .withColumn("category", Category_Classifier_Pandas_Udf(col("body")))
                .withColumn("vector_embedding", Generate_Vector_Embeddings_udf(col("body")))
                .withColumn("sentiment_score", Sentiment_Analysis_Pandas_Udf(col("body")))
                .select(
                    col("post_id"),
                    col("category"),
                    col("vector_embedding"),
                    col("sentiment_score"),
                    col("body"),
                    col("subreddit"),
                    col("date")
                 )
            )
            
            processed_df.cache()
            
            #processed_df.show(5, vertical=True) # this adds 8 seconds
                
            processed_count = processed_df.count()
            
            processed_df.unpersist()
            input_df.unpersist()
            return processed_count
        except Exception as e:
            return 0
Spark = Apache_Spark()
