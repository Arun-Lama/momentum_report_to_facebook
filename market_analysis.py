import pandas as pd
from adjusted_price_data import get_adjusted_price_of_all_companies, indices_data
from indicator_calculations import calculate_rsi
from gemini_output import generate_response, dataframe_to_json
import re 

def ai_analysis(indices_dataset):
    # Get historical data
    indices_history_all = indices_dataset

    # Data cleaning, convert numeric columns to float, handle non-numeric values like commas or #NA
    indices_history_all[["Open", "High", "Low", "Close", "Volume"]] = indices_history_all[["Open", "High", "Low", "Close", "Volume"]].apply(pd.to_numeric, errors='coerce')
    indices_history_all.set_index('Date', inplace=True)

    # Pivot the DataFrame to have 'Date' as index and 'Ticker' as columns for Close prices
    pivot_indices_history = indices_history_all.pivot_table(index="Date", columns="Ticker", values="Close")
    pivot_indices_history = pivot_indices_history.sort_values(by="Date", ascending=True)
    pivot_indices_history = pivot_indices_history.bfill()  # Backfill missing values if any

    # Get the latest available date (last date in the index)
    last_date = pivot_indices_history.index[-1]
    previous_day = pivot_indices_history.index[-2]

    # Calculate daily return for the latest date (percentage change from the previous day)
    daily_return = ((pivot_indices_history.loc[last_date] - pivot_indices_history.loc[previous_day]) / pivot_indices_history.loc[previous_day]) * 100

    # Calculate 20-day and 50-day moving averages for all sectors at once
    ma_20_df = pivot_indices_history.rolling(window=20, min_periods=1).mean()
    ma_50_df = pivot_indices_history.rolling(window=50, min_periods=1).mean()

    # Get the 20-day and 50-day moving averages for the latest available date
    ma_20_latest = ma_20_df.loc[last_date]
    ma_50_latest = ma_50_df.loc[last_date]

    # Calculate RSI (assuming RSI is already calculated in 'rsi_df' and it has the same index as pivot_indices_history)
    rsi_df = calculate_rsi(pivot_indices_history)
    rsi_latest = rsi_df.loc[last_date]

    # Pivot the data for Volume to get it in the same format
    volume_pivot = indices_history_all.pivot_table(index="Date", columns="Ticker", values="Volume")
    volume_pivot = volume_pivot.sort_values(by="Date", ascending=True)
    volume_pivot = volume_pivot.bfill()  # Backfill missing values if any

    # Get the latest Volume for each sector
    volume_latest = volume_pivot.loc[last_date]

    # Get the latest Close prices for each sector
    latest_close = pivot_indices_history.loc[last_date]

    # Now, create the final summary DataFrame by concatenating all the indicators
    summary_df = pd.DataFrame({
        'Volume': volume_latest,
        'Daily Return (%)': daily_return,
        'MA 20': ma_20_latest,
        'MA 50': ma_50_latest,
        'RSI': rsi_latest,
        'LTP': latest_close
    })
    # Convert the summary DataFrame to JSON
    summary_json = dataframe_to_json(summary_df)

    # Improved prompt with engaging Nepali greeting, no mention of Gemini
    # Assuming you have a function like this for generating responses from the AI
    def generate_inspirational_quote():
        """
        Generate an inspirational stock market quote in Nepali along with the author/source.
        Returns:
            tuple: (quote_text, author_name)
        """
        # Prompt instructs the model to return both quote and author
        prompt = (
            "Generate an inspirational quote about stock markets and investing in Nepali. "
            "Return the quote and the person behind it (author/source). "
            "Do not add anything else."
        )
        
        # Call your AI model
        response = generate_response(prompt)
        
        # Optional: parse if model returns in 'Quote' – Author format
        if '–' in response:
            quote_text, author_name = map(str.strip, response.split('–', 1))
        else:
            # fallback: unknown author
            quote_text = response.strip()
            author_name = "Unknown"
        
        return quote_text, author_name

    # Generate dynamically
    today_quote, quote_author = generate_inspirational_quote()

    # Use this dynamically generated quote in your prompt text
    prompt_text = f"""
    🌞 नमस्ते Nepse Investors! 🇳🇵🚀

    आजको बजार डेटा तल दिइएको छ:

    {summary_json}

    ---

    🎯 तपाईंको काम:
    यो डेटा प्रयोग गरेर sector-wise बजारको चाल र व्यवहार को स्पष्ट, insight-driven विश्लेषण तयार गर्नुहोस्।

    ---

    ❗ नियमहरू:
    - केवल दिइएको डेटा प्रयोग गर्नुहोस् (कुनै अनुमान नगर्नुहोस्)
    - Buy/Sell सिफारिस नगर्नुहोस् ❌
    - बजारको अवस्था, trend, momentum, risk मात्र वर्णन गर्नुहोस्
    - लामो व्याख्या नगर्नुहोस्, concise र readable insight दिनुहोस्
    - हरेक पटक wording, flow, र structure मा variation ल्याउनुहोस्

    ---

    🧠 Analysis Guidelines:

    तलका बुँदाहरूलाई आधार मानेर विश्लेषण गर्नुहोस् (structure flexible):

    - कुन sector हरूमा momentum बलियो छ (MA20, MA50, RSI, दैनिक return का आधारमा)
    - RSI extremes (७० माथि / ३० तल) भएका sector हरू → potential overbought / oversold संकेत
    - दैनिक return अनुसार उदीयमान वा कमजोर sector हरू
    - Volume र price सम्बन्ध → accumulation, distribution वा divergence संकेत
    - Unusual spikes, outliers वा sudden changes
    - Short-term vs medium-term trend mismatch → possible shift
    - Consistency vs volatility → trend quality

    ---

    📌 समावेश गर्नुपर्ने मुख्य insights:

    - 🔥 प्रमुख वा standout sectors (संक्षिप्त कारण सहित)
    - ⚡ Momentum बदलिएको sector हरू (acceleration / slowdown)
    - 🔍 असामान्य गतिविधि वा attention-worthy observations
    - 📈 Trend quality (consistent vs volatile sectors)
    - 🚨 Risk संकेतहरू (RSI extremes, high volatility, weak confirmation)
    - 🔁 बजारमा rotation / trend shifting observation

    ---

    💡 Interpretation Section:

    - Buy/Sell संकेत नदिनुहोस्
    - बजारको condition कस्तो छ भन्ने स्पष्ट गर्नुहोस्
    - कुन sector हरूमा strength वा weakness छ
    - कहाँ instability वा caution संकेत छ

    👉 Example style (flexible wording):
    - “Momentum केही sector हरूमा केन्द्रित देखिन्छ…”
    - “Volume support बिना भएको move कमजोर देखिन सक्छ…”
    - “RSI extremes ले short-term imbalance संकेत गरिरहेको छ…”

    ---

    📣 प्रेरणादायक उद्धरण:
    “{today_quote}” – {quote_author}

    ---

    🏷️ Hashtags (अन्त्यमा):
    - 5–10 relevant hashtags generate गर्नुहोस्, जस्तै #NEPSE #StockMarketNepal #Momentum #SectorAnalysis #InvestmentInsights
    - Nepali र English mix हुन सक्छ
    - हरेक पटक नयाँ combination प्रयोग गर्नुहोस्
    """

    # Generate the response using Gemini
    gemini_output = generate_response(prompt_text)
    cleaned_response = re.sub(r'\*\*(.*?)\*\*', r'\1', gemini_output)
    return cleaned_response