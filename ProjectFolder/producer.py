import os
from google.cloud import pubsub_v1
import json
import time
import random 
import numpy as np
import pandas as pd

credentials_path = '/Users/yemis/Downloads/CloudProject/NewAccount/valid-oven-382920-26289fe24756.json' #path to json key credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path


publisher = pubsub_v1.PublisherClient() #create publisher
topic_path = 'projects/valid-oven-382920/topics/tracks_data' #path to topic 

df = pd.read_csv('test.csv')
data = df.to_json(orient = 'records')

data_json = json.loads(data) #converts json string to json object

#
for i in data_json:
    topic_data = str(i)
    topic_data = topic_data.replace("\'", "\"")
    topic_data = topic_data.encode('utf-8')

    msgPublish = publisher.publish(topic_path, topic_data)
    print(f'published message id {msgPublish.result()}')
    print(topic_data)
    time.sleep(.5)








