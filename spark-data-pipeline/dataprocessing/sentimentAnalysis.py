from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class VaderSentimentAnalysis:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def SentimentAnalysis(self, input):
        score = self.analyzer.polarity_scores(input)            
        return score['compound']
    
Sentiments = VaderSentimentAnalysis()
