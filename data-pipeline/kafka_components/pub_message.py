import time
import numpy as np

# this class is responsible for publishing messages onto the processed data kafka topic
class Publish_Messages:
    def __init__(self, publisher_instance):
        try:
            self.instance = publisher_instance
        except Exception as e:
            print(f"Error initializing publisher instance: {e}")
    
    def publish_message(self, message):
        if message is not None:
            try:
                message_list = message.to_dict(orient='records')
                print("message on topic", message_list)

                num_sent = 0
                start_time = time.time()
                for row in message_list:
                    try:
                        if 'vector_embedding' in row and isinstance(row['vector_embedding'], np.ndarray): 
                            row['vector_embedding'] = row['vector_embedding'].tolist() 
                        self.instance.producer_config.send('processed_data', row)
                        num_sent += 1
                    except Exception as e:
                        print(f"Error publishing to topic: {e}")
                
                self.instance.producer_config.flush()
                print(f"Finished publishing in: {time.time() - start_time}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("No processed data to send to Kafka.")

