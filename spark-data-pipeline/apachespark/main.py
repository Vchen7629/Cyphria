from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, ArrayType, FloatType, StringType
from pyspark.sql.functions import array, lit
import json, threading, os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dataprocessing import generate_vector_embeddings

class Apache_Spark:
    def __init__(self):
        self.spark = SparkSession.builder.getOrCreate()
        
        self.schema = StructType([
            StructField("vector_embedding", ArrayType(FloatType()), True),
            StructField("body", StringType(), True),
            StructField("subreddit", StringType(), True),
            StructField("date", StringType(), True)
        ])
        
        #creating batch processing q

        self.vector_embedding_dataframe = self.spark.createDataFrame([], self.schema)
        self.vector_embedding_dataframe
        
        self.lock = threading.Lock()
    
    def inputData(self, query):
        if isinstance(query, dict):
            data = query
        else:
            data = json.loads(query)
            
        post_body = data['body']
        vector_embedding = generate_vector_embeddings.Embedding.Generate_Vector_Embeddings(post_body)
        
        print("Vector Embedding Type:", type(vector_embedding))
        print("Vector Embedding:", vector_embedding)
        print("Vector Embedding Shape:", vector_embedding.shape if hasattr(vector_embedding, 'shape') else "N/A")
                        
        rows = [(
            vector_embedding.tolist(),
            data.get("body", ""),
            data.get("subreddit", ""),
            data.get("date", "")
        )]
        
        new_row_df = self.spark.createDataFrame(rows, self.schema)
        
        with self.lock:
            self.vector_embedding_dataframe = self.vector_embedding_dataframe.union(new_row_df)
        
        return self.vector_embedding_dataframe

    def Process_Batch(self):
        with self.lock:
            batch = self.vector_embedding_dataframe
            data = batch.collect()
            for row in data:
                print(row)
            self.vector_embedding_dataframe = self.spark.createDataFrame([], self.schema)
            self.vector_embedding_dataframe
            
        count = batch.count()
        print(f"Processing batch with {count} records")
        return count
        
Spark = Apache_Spark()
