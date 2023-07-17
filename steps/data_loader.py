import pandas as pd
import requests
from PIL import Image
import io
import datetime 
import logging
from zenml import step

@step()
def data_loader(path: str='data', timedelta: int=3) -> int:
    """
    The function loads data from the Canada Wildfire Service and saves the wildfire images.
    
    Parameters:
    path (str): The base path where the images will be saved.
    timedelta (int): The number of days prior to the current date for which the data is considered.

    Returns:
    int: The number of images saved.
    """
    logging.info("Loading raw data")
    
    canada_wilfires=pd.read_csv("https://cwfis.cfs.nrcan.gc.ca/downloads/activefires/activefires.csv")
    
    # Filter out entries without a start date and entries older than 'daydelta' days
    canada_wilfires = canada_wilfires.drop(canada_wilfires[canada_wilfires[' startdate'] == " "].index)
    canada_wilfires[' startdate'] = pd.to_datetime(canada_wilfires[' startdate'])
    cut_date = datetime.datetime.today() - datetime.timedelta(days=timedelta)
    relevant = canada_wilfires[canada_wilfires[' startdate']> cut_date]
    
    # Prepare URL string components for Mapbox API
    url = 'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{},{},15,0/350x350'
    access_token = 'pk.eyJ1IjoidGltbGFjaG5lciIsImEiOiJjbGp5MGE0MmcwMGFrM3FsbGFxd2FwMmJvIn0.nP8b9q2owgwoCStcCnGL7Q'
    ending = '&attribution=false&logo=false'
    
    count = 0
    for index, row in relevant.iterrows():
        count += 1
        lon = row[' lon']
        lat = row[' lat']
        
        # Request image from Mapbox API and save it
        response = requests.get(url.format(lon,lat) + '?access_token=' + access_token + ending)
        img = Image.open(io.BytesIO(response.content))
        img.save(f"{path}/additional/wildfire/{lon},{lat}.jpg")
    
    logging.info(f"Added {count} new images to the dataset.")
    return count
