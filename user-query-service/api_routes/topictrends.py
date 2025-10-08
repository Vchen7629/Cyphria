from util.sbert_model import model


class topic_trends:
    def __init__(self):
        self.model_instance = model

    def retrieve_relevant_posts(self, query):
        response = self.model_instance.encode(query, convert_to_tensor=True)
        print(response)

        # return response


topic = topic_trends()
