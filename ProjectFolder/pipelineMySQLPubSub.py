# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import json
import logging
import os
import pickle
from sklearn.neighbors import KNeighborsClassifier

import apache_beam as beam
from beam_nuggets.io import relational_db
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

model = pickle.load(open('model.pkl', 'rb')) #loads model from pickle file

class PredictDoFn(beam.DoFn):
    def process(self, element):
        width = element["width"]
        height = element["height"]
        predict_result = model.predict([[width, height]])

        return str(predict_result)

            
def run(argv=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input', dest='input', required=True,
                            help='Input topic to process.')
    parser.add_argument('--output', dest='output', required=True,
                            help='Output topic to write results to.')
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True;
    
    with beam.Pipeline(options=pipeline_options) as p:
        source_config = relational_db.SourceConfiguration(
        drivername='CloudProject',
        host='localhost',
        port=3306,
        username='usr',
        password='sofe4630u',
        database='Predictions',)

        table_config = relational_db.TableConfiguration(
        name='vehicle_predictions',
        create_if_missing=True,  # automatically create the table if not there
        primary_key_columns=['num'])  # and use 'num' column as primary key

        given_data = (p | "Read from Pub/Sub" >> beam.io.ReadFromPubSub(topic=known_args.input)
                        | "toDict" >> beam.Map(lambda x: json.loads(x)))
            
        predictions = given_data | 'Prediction' >> beam.ParDo(PredictDoFn())
        
        (predictions | 'Writing to DB' >> relational_db.Write(source_config=source_config, table_config=table_config)) #writes prediction to database
        (predictions | 'to byte' >> beam.Map(lambda x: json.dumps(x).encode('utf8'))
            |   'to Pub/sub' >> beam.io.WriteToPubSub(topic=known_args.output)); #write prediction to pub/sub

        
if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()