import pandas as pd
import numpy as np
import requests
import io


# --------------------------------------------------
# Adjusted price data (RAW GitHub CSV)
# --------------------------------------------------
def get_adjusted_price_of_all_companies():
    import os
    import requests
    import pandas as pd
    import io
    from dotenv import load_dotenv

    if os.path.exists(".env"):
        load_dotenv()

    token = os.getenv("HUB_TOKEN")
    if not token:
        raise RuntimeError("HUB_TOKEN missing")

    api_url = (
        "https://api.github.com/repos/"
        "Arun-Lama/Adjusted-price-to-sheet/"
        "contents/adjusted price/all_adj_companies_data.csv"
        "?ref=main"
    )

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "price-adjuster"
    }

    meta = requests.get(api_url, headers=headers)
    meta.raise_for_status()

    download_url = meta.json()["download_url"]

    csv_resp = requests.get(download_url, headers=headers)
    csv_resp.raise_for_status()

    df = pd.read_csv(io.StringIO(csv_resp.text))
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values("Date", inplace=True)

    return clean_price_data(df)



def clean_price_data(df: pd.DataFrame) -> pd.DataFrame:
    price_cols = ["Open", "High", "Low", "Close"]

    df = df.copy()
    df[price_cols] = df[price_cols].replace(0, np.nan)
    df = df.dropna(subset=["Open", "Close"])
    df = df[(df[price_cols] > 0).all(axis=1)]

    return df


# --------------------------------------------------
# Indices data (RAW GitHub CSV)
# --------------------------------------------------
def indices_data():
    url = (
        "https://raw.githubusercontent.com/"
        "Arun-Lama/download-nepse-indices/main/"
        "indices/indices_data.csv"
    )

    response = requests.get(url)
    response.raise_for_status()

    df = pd.read_csv(io.StringIO(response.text))
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values(by="Date", ascending=True, inplace=True)

    return df


# --------------------------------------------------
# Debug / local test only
# --------------------------------------------------
if __name__ == "__main__":
    print(get_adjusted_price_of_all_companies().head())
    print(indices_data().head())
