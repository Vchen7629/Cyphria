from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, ArrayType, FloatType, StringType, TimestampNTZType

Vector_Embedding_Schema = StructType([
    StructField("vector_embedding", ArrayType(FloatType()), True),
    StructField("body", StringType(), True),
    StructField("subreddit", StringType(), True),
    StructField("date", TimestampNTZType(), True)
])

class Apache_Spark:
    def __init__(self):
        spark = SparkSession.builder.getOrCreate()

        vector_embedding_dataframe = spark.createDataFrame([], Vector_Embedding_Schema).show()

Spark = Apache_Spark()