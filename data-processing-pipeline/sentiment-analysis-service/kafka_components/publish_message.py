import numpy as np

class PublishMessage:
    def __init__(self, producer_instance):
        try:
            self.instance = producer_instance
        except Exception as e:
            raise ValueError(f"Instance not initialized for Publish Message class: {e}")
    def Pub_Message(self, message):
        if message is not None:
            try:
                message_list = message.to_dict(orient='records')

                output = []
                for row in message_list:
                    if 'vector_embedding' in row and isinstance(row['vector_embedding'], np.ndarray): 
                            row['vector_embedding'] = row['vector_embedding'].tolist() 
                    output.append(row)
                
                self.instance.producer_config.send('processed_data', output)
                self.instance.producer_config.flush()
            except Exception as e:
                raise ValueError(f"message could not be sent: {e}")
        else:
            print("No processed data to send to Kafka.")