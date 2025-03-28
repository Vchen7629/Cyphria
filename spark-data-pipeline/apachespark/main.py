from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, ArrayType, FloatType, StringType
from pyspark.sql.functions import array, lit
import json, threading, os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dataprocessing import generate_vector_embeddings, sentimentAnalysis, categoryClassifier

class Apache_Spark:
    def __init__(self):
        self.spark = SparkSession.builder.getOrCreate()
        
        self.schema = StructType([
            StructField("post_id", StringType(), True),
            StructField("category", StringType(), True),
            StructField("vector_embedding", ArrayType(FloatType()), True),
            StructField("sentiment_score", FloatType(), True),
            StructField("body", StringType(), True),
            StructField("subreddit", StringType(), True),
            StructField("date", StringType(), True)
        ])
        
        self.vector_embedding_dataframe = self.spark.createDataFrame([], self.schema)
        self.batch_buffer = []
        
        self.lock = threading.Lock()
    
    def inputData(self, query):
        if isinstance(query, dict):
            data = query
        else:
            data = json.loads(query)
                        
        row = (
            data.get("id", ""),
            None,
            None,
            None,
            data.get("body", ""),
            data.get("subreddit", ""),
            data.get("date", "")
        )
        
        with self.lock:
            self.batch_buffer.append(row)
        
    def Process_Batch(self):
        with self.lock:
            batch_data = self.batch_buffer[:]
            self.batch_buffer = []
        
        if not batch_data:
            return 0
        
        batch_df = self.spark.createDataFrame(batch_data, schema=self.schema)
        processed_data = []
        for row in batch_df.collect():
            body = row.body
            category = categoryClassifier.Category.Classify_Category(body)
            vector_embedding = generate_vector_embeddings.Embedding.Generate_Vector_Embeddings(body)
            sentiment_score = sentimentAnalysis.Sentiments.SentimentAnalysis(body)
            
            processed_data.append([
                row.post_id,
                category,
                vector_embedding.tolist(), 
                sentiment_score,
                body, 
                row.subreddit, 
                row.date
            ])

        processed_df = self.spark.createDataFrame(processed_data, self.schema)
        
        with self.lock:
            self.vector_embedding_dataframe = self.vector_embedding_dataframe.union(processed_df) # this creates an entirely new dataframe/doesnt
            self.vector_embedding_dataframe.show()                                                # append to previous ones when processing each batch maybe needs fix
            
        count = len(processed_data)
        print(f"Processing batch with {count} records")
        return count
        
Spark = Apache_Spark()
