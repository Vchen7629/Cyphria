from util.sbert_model import model


class comparison_trends():
    def __init__(self):
        self.model_instance = model
    
    def retrieve_relevant_posts(self, query):
        response = self.model_instance.encode(query)
        print(response)
        
        #return response

    
comparison = comparison_trends()