import sys, os, time
from sentence_transformers import util

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components import sbert_model, category_example_sentences

class CategoryClassifier:
    def __init__(self):
        self.model = sbert_model.get_model()
        
        self.technology_embedding = self.model.encode(category_example_sentences.technology, convert_to_tensor=True)
        self.fitness_embedding = self.model.encode(category_example_sentences.fitness, convert_to_tensor=True)
        self.sports_embedding = self.model.encode(category_example_sentences.sports, convert_to_tensor=True)
        self.finance_embedding = self.model.encode(category_example_sentences.finance, convert_to_tensor=True)
        self.food_embedding = self.model.encode(category_example_sentences.food, convert_to_tensor=True)
        self.gaming_embedding = self.model.encode(category_example_sentences.gaming, convert_to_tensor=True)
        self.news_embedding = self.model.encode(category_example_sentences.news, convert_to_tensor=True)
        self.science_embedding = self.model.encode(category_example_sentences.science, convert_to_tensor=True)
        self.animal_embedding = self.model.encode(category_example_sentences.animals, convert_to_tensor=True)
        self.entertainment_embedding = self.model.encode(category_example_sentences.entertainment, convert_to_tensor=True)
        self.education_embedding = self.model.encode(category_example_sentences.education, convert_to_tensor=True)
        self.travel_embedding = self.model.encode(category_example_sentences.travel, convert_to_tensor=True)
        self.housing_embedding = self.model.encode(category_example_sentences.housing, convert_to_tensor=True)
        
    def Classify_Category(self, query):
        start_time = time.time()
        input_vector = self.model.encode(query, convert_to_tensor=True)
        
        technology_sim = util.cos_sim(input_vector, self.technology_embedding).mean().item()
        Sports_sim = util.cos_sim(input_vector, self.sports_embedding).mean().item()
        fitness_sim = util.cos_sim(input_vector, self.fitness_embedding).mean().item()
        finance_sim = util.cos_sim(input_vector, self.finance_embedding).mean().item()
        food_sim = util.cos_sim(input_vector, self.food_embedding).mean().item()
        gaming_sim = util.cos_sim(input_vector, self.gaming_embedding).mean().item()
        news_sim = util.cos_sim(input_vector, self.news_embedding).mean().item()
        science_sim = util.cos_sim(input_vector, self.science_embedding).mean().item()
        animal_sim = util.cos_sim(input_vector, self.animal_embedding).mean().item()
        entertainment_sim = util.cos_sim(input_vector, self.entertainment_embedding).mean().item()
        education_sim = util.cos_sim(input_vector, self.education_embedding).mean().item()
        travel_sim = util.cos_sim(input_vector, self.travel_embedding).mean().item()
        housing_sim = util.cos_sim(input_vector, self.housing_embedding).mean().item()
        
        scores = {
            "technology": technology_sim,
            "sports": Sports_sim,
            "fitness": fitness_sim,
            "finance": finance_sim,
            "food": food_sim,
            "gaming": gaming_sim,
            "news": news_sim,
            "science": science_sim,
            "animal": animal_sim,
            "entertainment": entertainment_sim,
            "education": education_sim,
            "travel": travel_sim,
            "housing": housing_sim
        }
        print(f"Classified in: {time.time() - start_time:.4f} seconds")
        return max(scores, key=scores.get)

Category = CategoryClassifier()

