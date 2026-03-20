import pandas as pd 

def calculate_rsi(df, window=14):
    """
    Calculate the Relative Strength Index (RSI) for each sector in the dataframe.
    
    :param df: DataFrame with Date as index and sector tickers as columns (Close prices)
    :param window: The period over which RSI is calculated, default is 14 days
    :return: DataFrame with RSI values for each sector
    """
    rsi_df = pd.DataFrame(index=df.index)  # Create a new DataFrame to store RSI values

    for column in df.columns:
        # Calculate the daily price change
        price_change = df[column].diff()

        # Separate the gains and losses
        gain = price_change.where(price_change > 0, 0)
        loss = -price_change.where(price_change < 0, 0)

        # Calculate the rolling average of gains and losses
        avg_gain = gain.rolling(window=window, min_periods=1).mean()
        avg_loss = loss.rolling(window=window, min_periods=1).mean()

        # Calculate the Relative Strength (RS)
        rs = avg_gain / avg_loss

        # Calculate the RSI
        rsi = 100 - (100 / (1 + rs))

        # Add the RSI values to the new DataFrame
        rsi_df[column] = rsi

    return rsi_df