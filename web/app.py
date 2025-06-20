import streamlit as st
import requests
import re
import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import logging

# Configure logging with file output
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("streamlit_log.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# Initialize Hugging Face client
if not HUGGINGFACE_API_TOKEN:
    logger.error("Hugging Face API token not found in .env")
    st.error("Hugging Face API token not found in .env")
    st.stop()
client = InferenceClient(token=HUGGINGFACE_API_TOKEN)

# Load NASDAQ symbols and company names
SYMBOLS_FILE = "data/nasdaq_symbols.json"
try:
    with open(SYMBOLS_FILE, "r") as f:
        nasdaq_data = json.load(f)
        NASDAQ_SYMBOLS = {item["symbol"]: item["company_name"] for item in nasdaq_data}
    logger.info(f"Loaded {len(NASDAQ_SYMBOLS)} NASDAQ symbols from {SYMBOLS_FILE}")
except FileNotFoundError:
    logger.error(f"Symbols file {SYMBOLS_FILE} not found")
    st.error("NASDAQ symbols file not found. Please run scripts/generate_symbols.py.")
    st.stop()
except Exception as e:
    logger.error(f"Failed to load symbols: {str(e)}")
    st.error("Error loading NASDAQ symbols. Contact support.")
    st.stop()

# Streamlit chat UI
st.title("Stock Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your Stock Chatbot. Ask me about any NASDAQ stock (e.g., 'Price of AAPL' or 'Is TSLA a good buy?')."}
    ]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your question (e.g., 'Price of AAPL')"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Initialize response
    response = "Sorry, something went wrong. Please try again."
    logger.debug(f"Processing query: {prompt}")

    # Common words to exclude
    COMMON_WORDS = {"WHAT", "IS", "THE", "PRICE", "OF", "FOR", "IN", "A", "AN", "AND", "GIVE", "ME", "LATEST", "STOCK", "VALUE"}

    # Parse query using regex for symbol
    logger.debug("Attempting regex-based symbol extraction")
    symbol_match = re.search(r'\b(?:of|for|price|value)\s+([A-Z]{1,5})\b', prompt.upper())
    if not symbol_match:
        words = re.findall(r'\b[A-Z]{1,5}\b', prompt.upper())
        symbol_candidates = [w for w in words if w not in COMMON_WORDS]
        symbol = symbol_candidates[0] if symbol_candidates else None
        logger.debug(f"Regex fallback candidates: {symbol_candidates}, selected: {symbol}")
    else:
        symbol = symbol_match.group(1)
        logger.debug(f"Regex extracted symbol: {symbol}")

    # Fallback to LLM for symbol extraction
    if not symbol or symbol in COMMON_WORDS:
        logger.debug("Falling back to LLM for symbol extraction")
        try:
            llm_symbol_response = client.text_generation(
                prompt=f"Extract the stock symbol from this query: '{prompt}'. Return only the symbol (e.g., AAPL) or 'None' if none found.",
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                max_new_tokens=10
            )
            symbol = llm_symbol_response.strip()
            if symbol == "None":
                symbol = None
            logger.debug(f"LLM extracted symbol: {symbol}")
        except Exception as e:
            logger.error(f"LLM symbol extraction failed: {str(e)}")
            response = "Unable to extract a stock symbol. Please include a valid NASDAQ symbol (e.g., AAPL)."
            symbol = None

    # Validate symbol and get company name
    company_name = None
    if symbol:
        if symbol in NASDAQ_SYMBOLS:
            company_name = NASDAQ_SYMBOLS[symbol]
            logger.debug(f"Valid NASDAQ symbol: {symbol}, company name: {company_name}")
        else:
            response = f"'{symbol}' is not a valid NASDAQ stock symbol. Please try a NASDAQ-listed stock (e.g., AAPL, TSLA)."
            logger.info(f"Invalid NASDAQ symbol: {symbol}")
            symbol = None

    # Parse intent using regex patterns first
    intent = None
    price_patterns = [
        r'\bprice\b', r'\bstock\s*value\b', r'\blow\s*much\s*is\b', 
        r'\bcurrent\s*price\b', r'\blatest\s*price\b', r'\bgive\s*me\s*\w*\s*price\b'
    ]
    if symbol:
        query_lower = prompt.lower()
        if any(re.search(pattern, query_lower) for pattern in price_patterns):
            intent = "price"
            logger.debug(f"Regex-based intent detected: {intent}, symbol: {symbol}")
        
        # Fallback to LLM for other intents
        if intent is None:
            logger.debug(f"Attempting LLM intent parsing for symbol: {symbol}")
            try:
                intent_response = client.text_generation(
                    prompt=f"Classify the intent of this query: '{prompt}'. Possible intents: 'price', 'financials', 'sentiment', 'analysis', 'invalid'. Return only the intent.",
                    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    max_new_tokens=10
                )
                raw_intent = intent_response
                # Clean intent: take first word or line, remove quotes and extra text
                intent = raw_intent.split()[0].strip().replace("'", "").replace("\"", "").strip()
                logger.debug(f"Raw LLM intent: {raw_intent!r}, Cleaned intent: {intent}, symbol: {symbol}")
            except Exception as e:
                logger.error(f"LLM intent parsing failed: {str(e)}")
                intent = "invalid"
                response = "Unable to identify your request. Please try again."

    # Process query
    with st.chat_message("assistant"):
        if not symbol:
            response = "Please include a valid NASDAQ stock symbol (e.g., TSLA, AAPL)."
            logger.info(f"No symbol extracted for query: {prompt}")
        elif intent == "invalid":
            response = "Sorry, I didn't understand your request. Try asking about a stock's price, financials, sentiment, or overall analysis."
            logger.info(f"Invalid intent for query: {prompt}")
        else:
            try:
                # Fetch data from FastAPI with company name
                logger.debug(f"Sending API request for {symbol}, company_name: {company_name}")
                api_response = requests.get(
                    f"http://localhost:8000/stock/{symbol}",
                    params={"companyName": company_name},
                    timeout=10
                )
                api_response.raise_for_status()
                data = api_response.json()
                logger.debug(f"API response: {data}")

                # Validate response
                required_fields = {"price", "financials", "sentiment", "status"}
                if not all(key in data for key in required_fields) or data["status"] != "complete":
                    logger.error(f"Invalid API response for {symbol}: {data}")
                    response = f"Received incomplete data for {symbol}. Please try again."
                else:
                    # Generate conversational response
                    if intent == "price":
                        response = f"The current price of {symbol} is ${data['price']:.2f}."
                    elif intent == "financials":
                        response = (
                            f"Financial metrics for {symbol}:\n"
                            f"- Market Cap: ${int(data['financials']['market_cap']):,}\n"
                            f"- Revenue: ${int(data['financials']['revenue']):,}\n"
                            f"- Earnings: ${int(data['financials']['earnings']):,}"
                        )
                    elif intent == "sentiment":
                        response = (
                            f"The sentiment for {symbol} is {data['sentiment']['summary']}.\n"
                            f"Recent news:\n" +
                            "\n".join(
                                f"- {article['title']} ({article['sentiment']})"
                                for article in data['sentiment']['details'][:3]
                            )
                        )
                    elif intent == "analysis":
                        response = (
                            f"Here's an analysis of {symbol}:\n"
                            f"- **Price**: ${data['price']:.2f}\n"
                            f"- **Financials**:\n"
                            f"  - Market Cap: ${int(data['financials']['market_cap']):,}\n"
                            f"  - Revenue: ${int(data['financials']['revenue']):,}\n"
                            f"  - Earnings: ${int(data['financials']['earnings']):,}\n"
                            f"- **Sentiment**: {data['sentiment']['summary']}\n"
                            f"Recent news:\n" +
                            "\n".join(
                                f"  - {article['title']} ({article['sentiment']})"
                                for article in data['sentiment']['details'][:3]
                            )
                        )
                    logger.debug(f"Generated response: {response}")
            except Exception as e:
                logger.error(f"API call or processing failed for {symbol}: {str(e)}")
                response = f"Error fetching data for {symbol}: {str(e)}"

        # Display and store response
        logger.debug(f"Final response: {response}")
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
