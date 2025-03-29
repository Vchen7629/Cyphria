import pandas as pd
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import ArrayType, FloatType
import time

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

vader_instance = None

def Get_Vader_Analyzer():
    global vader_instance
    if vader_instance is None:
        vader_instance = VaderSentimentAnalysis()
    return vader_instance

class VaderSentimentAnalysis:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def SentimentAnalysis(self, input: pd.Series) -> pd.Series:
        input_len = len(input)
        results = []
        try:
            for text in input:
                score = self.analyzer.polarity_scores(text)            
                overall = score['compound']
                results.append(overall)
            
            output = pd.Series(results, dtype=float)
            output_len = len(output)
            
            if input_len != output_len:
                print(f"SENTIMENT UDF LENGTH MISMATCH: Input={input_len}, Output={output_len}")
                return pd.Series([None] * input_len)
            
            return output
        except Exception as e:
            print(f"Error generating embedding batch. Error: {e}")
            return pd.Series([None] * len(input))
    
@pandas_udf(FloatType())
def Sentiment_Analysis_Pandas_Udf(texts: pd.Series) -> pd.Series:
    start_time = time.time()
    vader = Get_Vader_Analyzer()
    print(f"Sentiment analysis in: {time.time() - start_time:.4f} seconds")
    return vader.SentimentAnalysis(texts)