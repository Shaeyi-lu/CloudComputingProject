import os
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
import json

credentials_path = '/Users/yemis/Downloads/CloudProject/NewAccount/valid-oven-382920-26289fe24756.json' #path to json key credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path


timeout = 5.0    # timeout in seconds

subscriber = pubsub_v1.SubscriberClient()#create consumer
subscription_path = 'projects/valid-oven-382920/subscriptions/tracks_predict-sub' #path  to subscription to topic

def callback(message):
    print(f'data: {message.data}')
    message.ack()           


pull_message = subscriber.subscribe(subscription_path, callback=callback) #consume message from producer.
print(f'Listening for messages on {subscription_path}') #listen for incoming messages from producer

# to automatically call close() when done
with subscriber:                                                
    try:
        pull_message.result()                         
    except TimeoutError:
        pull_message.cancel()                         
        pull_message.result()                          
