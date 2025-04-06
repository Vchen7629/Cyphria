import pandas as pd
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
            start_time = time.time()
            for text in input:
                score = self.analyzer.polarity_scores(text)            
                overall = score['compound']
                results.append(overall)
            print(f"Sentiment analysis in: {time.time() - start_time:.4f} seconds")

            output = pd.Series(results, dtype=float)
            output_len = len(output)
            
            if input_len != output_len:
                print(f"SENTIMENT UDF LENGTH MISMATCH: Input={input_len}, Output={output_len}")
                return pd.Series([None] * input_len)
            
            return output
        except Exception as e:
            print(f"Error generating embedding batch. Error: {e}")
            return pd.Series([None] * len(input))
