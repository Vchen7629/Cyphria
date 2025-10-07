# Todo: code for handling error/info logging
def logger(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()} partition {msg.partition()} offset {msg.offset()}")