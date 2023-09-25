from datetime import datetime
import re

def reformat_date(input_date,
                  from_format = "%b %d, %Y",
                  to_format = "%Y-%m-%d"
                  ):
    return datetime.strftime(
        datetime.strptime(input_date, from_format),
        to_format
        )

def regex_extract(input_str, regex_str):
    first_match = re.search(regex_str, input_str)

    return first_match.group()

def transform(data: [dict]):
    transformations = {
        "release_date": lambda date: reformat_date(date, "%b %d, %Y", "%Y-%m-%d"),
        "review_category": lambda raw: raw.split("|")[0].strip(),
        "review_count": lambda raw: int(regex_extract(raw.replace(",", ""), r'\d+')),
        "price_currency": lambda raw: re.sub(r'\d+\.\d+', "", raw).strip(),
        "original_price": lambda raw: float(regex_extract(raw, r'\d+\.\d+')),
        "discounted_price": lambda raw: float(regex_extract(raw, r'\d+\.\d+')),
    }

    for entry in data:
        for k, f in transformations.items():
            if k in entry:
                entry[k] = f(entry[k])

    return data