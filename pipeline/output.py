from datetime import datetime
import pandas as pd
import logging

def save_to_csv(data: list[dict], filename="save_data.csv"):
    if data is None:
        logging.error("called save_to_csv with no data to save")
        return

    df = pd.DataFrame(data)
    filename = f"{datetime.now().strftime('%Y_%m_%d')}_{filename}"
    df.to_csv(filename, index=False)
    logging.debug(f"saved data to {filename}")