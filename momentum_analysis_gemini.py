from gemini_output import generate_response, dataframe_to_json
import re 
import os
from collections import OrderedDict
import pandas as pd
from adjusted_price_data import get_adjusted_price_of_all_companies


def gemini_momentum_analysis(dataset):
    def prepare_pivot(adjusted_pivot_adjusted_pivot_df, column_name="Ticker"):
        adjusted_pivot_adjusted_pivot_df = adjusted_pivot_adjusted_pivot_df.copy()
        adjusted_pivot_adjusted_pivot_df[["Open", "High", "Low", "Close", "Volume"]] = (
            adjusted_pivot_adjusted_pivot_df[["Open", "High", "Low", "Close", "Volume"]]
            .apply(pd.to_numeric, errors="coerce")
            .astype(float)
        )
        adjusted_pivot_adjusted_pivot_df["Date"] = pd.to_datetime(adjusted_pivot_adjusted_pivot_df["Date"], errors="coerce")
        return adjusted_pivot_adjusted_pivot_df.pivot_table(index="Date", columns=column_name, values="Close", aggfunc="first")


    adjusted_data = dataset
    adjusted_pivot_adjusted_pivot_adjusted_pivot_df = prepare_pivot(adjusted_data, column_name="Ticker")
    df = adjusted_pivot_adjusted_pivot_adjusted_pivot_df


    # 1. Updated periods: Added Daily and stopped at 6-Months
    periods = [
        ("1-D", 1), ("2-D", 2), ("3-D", 3), ("4-D", 4),
        ("1-W", 5), ("2-W", 10), ("3-W", 15), 
        ("1-M", 21), ("2-M", 42), ("3-M", 63), ("6-M", 126)
    ]

    def get_short_term_summary(df):
        # Data Cleaning: Convert index to datetime and fill missing prices
        df.index = pd.to_datetime(df.index)
        df = df.sort_index().ffill()
        
        summary_data = {}
        
        for label, days in periods:
            # Check if we have enough historical data for the period
            if len(df) > days:
                # Formula: (Latest Price / Price N days ago) - 1
                # .iloc[-1] is today, .iloc[-(days + 1)] is 'days' ago
                returns = ((df.iloc[-1] / df.iloc[-(days + 1)]) - 1) * 100
                
                # Sort and pick top 10 performers
                top_10 = returns.sort_values(ascending=False).head(10)
                
                # Create the string format "Ticker | Return%"
                summary_data[label] = [f"{t} | {r:.2f}%" for t, r in top_10.items()]
            else:
                summary_data[label] = ["Data N/A"] * 10
                
        return pd.DataFrame(summary_data)

    summary_df = get_short_term_summary(df)


    prompt_text = f"""
    🌞 नमस्ते, Nepse Traders! 🇳🇵🚀

    तपाईंलाई विभिन्न समय अवधिहरूमा आधारित momentum डेटा दिइएको छ:

    {dataframe_to_json(summary_df)}

    ---

    🎯 तपाईंको काम:
    यो डेटा प्रयोग गरेर **insightful momentum analysis** तयार गर्नुहोस् जसले बजारको अवस्था स्पष्ट रूपमा बुझाउँछ।

    ---

    ❗ मुख्य नियमहरू:
    - केवल दिइएको डेटा प्रयोग गर्नुहोस् (कुनै अनुमान नगर्नुहोस्)
    - Buy/Sell सिफारिस नगर्नुहोस् ❌
    - बजारका **conditions, behavior, trend structure** मात्र वर्णन गर्नुहोस्
    - छोटो तर meaningful insight दिनुहोस् (no unnecessary explanation)
    - Output Facebook पोस्ट जस्तो natural र readable हुनुपर्छ
    - हरेक पटक एउटै शैली follow नगर्नुहोस् — wording, flow, structure मा variation ल्याउनुहोस्

    ---

    🧠 Analysis Guidelines (Flexible, Not Strict):

    तपाईं तलका विचारहरूलाई आधार मानेर analysis गर्नुहोस्, तर rigid structure follow गर्न जरुरी छैन:

    - Multi-timeframe मा बारम्बार देखिने स्टकहरू → strong momentum संकेत
    - Short-term vs long-term performance फरक छ भने → momentum shift / rotation संकेत
    - छोटो समयमा धेरै बढेका स्टकहरू → overextension वा volatility संकेत
    - Single timeframe मा मात्र देखिएका स्टकहरू → weak conviction वा spike हुन सक्छ
    - Consistent presence भएका स्टकहरू → sustained trend संकेत

    ---

    📌 तपाईंले समेट्नुपर्ने key insights:
    (सबै समावेश गर्नुपर्छ, तर order र presentation flexible छ)

    - 🔥 प्रमुख momentum stocks (with reason)
    - ⚡ acceleration वा slowdown भएका stocks
    - 🔁 market rotation / shifting trends
    - 📈 trend quality (consistent vs weak moves)
    - 🚨 risk संकेतहरू (overextension, instability, etc.)

    ---

    💡 Strategy Section (IMPORTANT CHANGE):

    - कुनै पनि Buy/Sell signal नदिनुहोस्
    - यसको सट्टा:
        - बजारको वर्तमान अवस्था कस्तो छ भन्ने explain गर्नुहोस्
        - कुन प्रकारका stocks मा momentum देखिन्छ (e.g., multi-timeframe, short-term burst, etc.)
        - कुन अवस्थामा caution आवश्यक छ भन्ने बताउनुहोस्

    👉 Example style (not fixed, vary wording):
    - “Momentum हाल multi-timeframe stocks मा केन्द्रित देखिन्छ…”
    - “Short-term spikes बढी देखिँदा volatility बढ्न सक्छ…”
    - “Consistent trend भएका stocks ले stability देखाइरहेका छन्…”

    ---

    📝 Output Style:

    - Facebook-friendly format
    - bullet points / sections प्रयोग गर्न सक्नुहुन्छ, तर structure fix छैन
    - emojis प्रयोग गर्न सक्नुहुन्छ तर overuse नगर्नुहोस्
    - repetition avoid गर्नुहोस्
    - flow natural हुनुपर्छ (robotic नदेखियोस्)

    At the end give overall bigger picture summmary. 

    ---

    🌐 भाषा नियम:
    - सम्पूर्ण उत्तर Nepali (देवनागरी) मा लेख्नुहोस्
    - English प्रयोग नगर्नुहोस् (stock ticker बाहेक)
    """

    # Generate the response using Gemini
    gemini_output = generate_response(prompt_text)
    cleaned_response = re.sub(r'\*\*(.*?)\*\*', r'\1', gemini_output)
    return cleaned_response