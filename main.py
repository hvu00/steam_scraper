from pipeline.extraction import get_config, extract_raw_data
from pipeline.transform import transform
from pipeline.output import save_to_csv
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    config = get_config()
    logging.debug(f"config={config}")

    raw_data_extract = extract_raw_data(config)
    logging.debug(f"raw_data_extract={raw_data_extract}")
    
    transformed_data = transform(raw_data_extract)
    logging.debug(f"transformed_data={transformed_data}")

    logging.debug("saving data to disk")
    save_to_csv(transformed_data, "save_data.csv")