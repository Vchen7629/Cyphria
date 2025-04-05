import sys, os, time
from pyspark.sql.functions import from_json, explode, col
from pyspark.sql.types import StructType, StructField, StringType, FloatType, ArrayType, IntegerType

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from apachespark.main import Spark
from dataprocessing.categoryClassifier import Category_Classifier_Pandas_Udf
from dataprocessing.generate_vector_embeddings import Generate_Vector_Embeddings_udf
from dataprocessing.sentimentAnalysis import Sentiment_Analysis_Pandas_Udf
from dataprocessing.keywordextraction import Keyword_Extraction_Pandas_UDF

class Kafka_Consumer:
    def __init__(self):
        self.producer_config = Spark.spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", "localhost:9092") \
                .option("subscribe", "test-topic") \
                .load() 
        
        reddit_message_struct = ArrayType(StructType([
            StructField("post_id", StringType(), True),
            StructField("category", StringType(), True),
            StructField("keywords", ArrayType(StringType()), True),
            StructField("vector_embedding", ArrayType(FloatType()), True),
            StructField("sentiment_score", FloatType(), True),
            StructField("body", StringType(), True),
            StructField("subreddit", StringType(), True),
            StructField("upvotes", IntegerType(), True),
            StructField("downvotes", IntegerType(), True),
            StructField("created_utc", StringType(), True),
            StructField("title", StringType(), True),
        ]))
        
        start = time.time()
        parsed_df = self.producer_config \
            .select(from_json(col("value").cast("string"), reddit_message_struct).alias("data")) \
            .select(explode("data").alias("data")) \
            .select("data.*") \
            .withColumn("vector_embedding", Generate_Vector_Embeddings_udf(col("body"))) \
            .withColumn("category", Category_Classifier_Pandas_Udf(col("vector_embedding"))) \
            .withColumn("sentiment_score", Sentiment_Analysis_Pandas_Udf(col("body"))) \
            .withColumn("keywords", Keyword_Extraction_Pandas_UDF(col("body")))
        
        print(f"--- Process_Batch: Defined processing transformations in {time.time() - start:.4f} seconds ---")

                
        query = parsed_df \
            .writeStream \
            .outputMode("append") \
            .format("console") \
            .start()
        

        
        # Keep the application running until manually terminated
        print("Stream started. Waiting for messages...")
        query.awaitTermination()

kafka = Kafka_Consumer()

if __name__ == "__main__":
    kafka()
    