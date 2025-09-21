import numpy as np


class PublishMessage:
    def __init__(
        self,
        producer_instance,
    ):
        try:
            self.instance = producer_instance
        except Exception as e:
            raise ValueError(f"Instance not initialized for Publish Message class: {e}")

    def Pub_Message(
        self,
        message,
    ):
        if message is not None and not message.empty:
            try:
                message_list = message.to_dict(orient="records")
                messages_sent = 0

                for row in message_list:
                    processed_row = {}
                    for (
                        key,
                        value,
                    ) in row.items():
                        if isinstance(
                            value,
                            np.ndarray,
                        ):
                            processed_row[key] = value.tolist()
                        else:
                            processed_row[key] = value
                    self.instance.producer_config.send(
                        "reddit-data",
                        value=processed_row,
                    )
                    messages_sent += 1
                print(
                    "output",
                    processed_row,
                    "sent amount: ",
                    messages_sent,
                )
                self.instance.producer_config.flush()
            except Exception as e:
                raise ValueError(f"message could not be sent: {e}")
        else:
            print("No processed data to send to Kafka.")
