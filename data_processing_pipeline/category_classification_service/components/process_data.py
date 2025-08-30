from preprocessing import (
    remove_noise,
)


class RedditPosts:
    def __init__(self):
        self.filter_instance = remove_noise.removeNoise()
        #self.sub_age_instance = substitute_time.ReplaceText()
        #self.sub_money_instance = substitute_money.ReplaceText()
        #self.sub_stock_instance = stock_ticker.ReplaceText()
        #self.sub_prog_instance = tool.ReplaceText()
        #self.sub_gpu_instance = substitute_gpu.ReplaceText()
        #self.sub_vehicle_instance = name.ReplaceText()
        #self.sub_drug_instance = drug.ReplaceText()

    def substituteLexicon(self, rawtext):
        #sub_age = self.sub_age_instance.age(rawtext)
        #sub_money = self.sub_money_instance.numerical(sub_age)
        #sub_stock_name = self.sub_stock_instance.substitute(sub_money)
        #sub_programming_name = self.sub_prog_instance.substitute(sub_stock_name)
        #sub_gpu_name = self.sub_gpu_instance.substitute(sub_programming_name)
        #sub_vehicle_name = self.sub_vehicle_instance.substitute(sub_gpu_name)
        #sub_drug = self.sub_drug_instance.drug(sub_vehicle_name)

        #return sub_drug
        pass

    def removeNoise(self, rawtext):
        filter_url = self.filter_instance.url(rawtext)
        filter_stopwords = self.filter_instance.stopWords(filter_url)
        #filter_commas = self.filter_instance.punctuation(filter_stopwords)
        #filter_brackets = self.filter_instance.brackets(filter_commas)

        #return filter_brackets
        return filter_stopwords
    
    #def checkValid(self, text):
    #    if language_filter.isEnglish(text) and self.filter_instance.oldRedditPosts(text):
     #       return True
     #   else:
     #       return False
#