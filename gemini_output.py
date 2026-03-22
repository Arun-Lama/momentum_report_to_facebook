from google import genai
import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("GEMINI_API")

# Initialize the client
client = genai.Client(api_key=API_KEY)

def generate_response(prompt_text):
    try:
        # Use the latest stable model
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt_text
        )
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")

def dataframe_to_json(df):
    """
    Convert the summary DataFrame to a JSON format.
    This function will format the DataFrame as a JSON string that can be passed to Gemini.
    """
    # Convert the DataFrame to JSON (keeping the index as part of the JSON)
    return df.to_json(orient="index", date_format="iso")  # Using 'index' to maintain sector names as keys

