import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import datetime 
"""
Import the data using tf.image_dataset_from_directory.
"""
@step(enable_cache=False)
def data_loader(path: str='data', daydelta: int=3) -> int:
    logging.info("Loading raw data")
    url="https://cwfis.cfs.nrcan.gc.ca/downloads/activefires/activefires.csv"
    canada_wilfires=pd.read_csv(url)
    cut_date = datetime.datetime.today() - datetime.timedelta(days=1)
    canada_wilfires = canada_wilfires.drop(canada_wilfires[canada_wilfires[' startdate'] == " "].index)
    canada_wilfires[' startdate'] = pd.to_datetime(canada_wilfires[' startdate'])
    relevant = canada_wilfires[canada_wilfires[' startdate']> cut_date]
    url = 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{},{},15,0/350x350'
    access_token = 'pk.eyJ1IjoibTNuZGVsIiwiYSI6ImNsajV5a2syMjAxOW8zam9ibXp4dGFkNmQifQ.PA3LPn0Ihn_xJ-tOnEUsWg'
    ending = '&attribution=false&logo=false'
    count = 0
    for index, row in relevant.iterrows():
        count += 1
        response = requests.get(url.format(row[' lon'],row[' lat']) + '?access_token=' + access_token + ending)
        img = Image.open(BytesIO(response.content))
        img.save(f"data/additional/wildfire/{row[' lon']},{row[' lat']}.jpg")
    return count


    
