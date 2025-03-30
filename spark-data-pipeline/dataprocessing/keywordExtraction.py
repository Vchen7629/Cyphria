from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import time

Model_Instance = None

def Get_Model():
    global Model_Instance
    if Model_Instance is None:
        start_time = time.time()
        tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
        Model_Instance = pipeline("ner", model=model, tokenizer=tokenizer)
        print(f"Initialized in: {time.time() - start_time:.4f} seconds")


    return Model_Instance

class Keyword_Extraction:
    model_instance = Get_Model()

    def __init__(self):
        self.model = self.model_instance
        
    def Extract_Keywords(self, query):
        ner_results = self.model(query)
        print(ner_results)
        return ner_results

keyword = Keyword_Extraction()
start_time = time.time()
keyword.Extract_Keywords(
    "In PySpark, using withColumn inside a loop causes a huge performance hit. This is not a bug, it is just the way Spark's optimizer applies rules and prunes the logical plan. The problem is so common that it is mentioned directly in the PySpark documentation:This method introduces a projection internally. Therefore, calling it multiple times, for instance, via loops in order to add multiple columns can generate big plans which can cause performance issues and even StackOverflowException. To avoid this, use select() with multiple columns at once. Nevertheless, I'm still confronted with this problem very often, especially from people not experienced with PySpark. To make life easier for both junior devs who call withColumn in loops and then spend a lot of time debugging and senior devs who review code from juiniors, I created a tiny (about 50 LoC) flake8 plugin that detects the use of withColumn in loop or reduce. I published it to PyPi, so all that you need to use it is just run pip install flake8-pyspark-with-column To lint your code run flake8 --select PSPRK001,PSPRK002 your-code and see all the warnings about misusing of withColumn! You can check the source code here (Apache 2.0): https://github.com/SemyonSinchenko/flake8-pyspark-with-column")
print(f"Classified Category in: {time.time() - start_time:.4f} seconds")
