from util.sbert_model import model


class category_trends:
    def __init__(self):
        self.model_instance = model

    def retrieve_relevant_posts(self, query):
        response = self.model_instance(query)
        print(response)

        return response


category = category_trends()
