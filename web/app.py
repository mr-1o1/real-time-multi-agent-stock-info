import streamlit as st
import requests
import re
import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import logging

# Set up logging to both file and console for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("streamlit_log.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# Initialize the Hugging Face client for AI responses
if not HUGGINGFACE_API_TOKEN:
    logger.error("Hugging Face API token not found in .env")
    st.error("Hugging Face API token not found in .env")
    st.stop()
client = InferenceClient(token=HUGGINGFACE_API_TOKEN)

# Load NASDAQ stock symbols and company names from JSON file
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

# Set up the main chat interface
st.title("Stock Chatbot")

# Initialize chat history with a welcome message
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your Stock Chatbot. Ask me about any NASDAQ stock, like 'What's the price of AAPL?' or 'Is TSLA a good buy?'."}
    ]

# Display all previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Type your question (e.g., 'Price of AAPL')"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Set default error response
    response = "Sorry, something went wrong. Please try again."
    logger.debug(f"Processing query: {prompt}")

    # Define common words to filter out when looking for stock symbols
    COMMON_WORDS = {"WHAT", "IS", "THE", "PRICE", "OF", "FOR", "IN", "A", "AN", "AND", "GIVE", "ME", "LATEST", "STOCK", "VALUE"}

    # Try to extract stock symbol using regex patterns first
    logger.debug("Attempting regex-based symbol extraction")
    symbol_match = re.search(r'\b(?:of|for|price|value)\s+([A-Z]{1,5})\b', prompt.upper())
    if not symbol_match:
        # Fallback: look for any 1-5 letter uppercase words that aren't common words
        words = re.findall(r'\b[A-Z]{1,5}\b', prompt.upper())
        symbol_candidates = [w for w in words if w not in COMMON_WORDS]
        symbol = symbol_candidates[0] if symbol_candidates else None
        logger.debug(f"Regex fallback candidates: {symbol_candidates}, selected: {symbol}")
    else:
        symbol = symbol_match.group(1)
        logger.debug(f"Regex extracted symbol: {symbol}")

    # If regex fails, use AI to extract the stock symbol
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
            response = "I couldn't find a valid stock symbol in your query. Please include a NASDAQ symbol like AAPL or TSLA."
            symbol = None

    # Check if the extracted symbol is valid and get the company name
    company_name = None
    if symbol:
        if symbol in NASDAQ_SYMBOLS:
            company_name = NASDAQ_SYMBOLS[symbol]
            logger.debug(f"Valid NASDAQ symbol: {symbol}, company name: {company_name}")
        else:
            response = f"Sorry, '{symbol}' isn't a valid NASDAQ stock symbol. Try a NASDAQ-listed stock like AAPL or TSLA."
            logger.info(f"Invalid NASDAQ symbol: {symbol}")
            symbol = None

    # Figure out what the user wants to know about the stock
    intent = None
    # Define regex patterns for different types of requests
    price_patterns = [
        r'\bprice\b', r'\bstock\s*value\b', r'\blow\s*much\s*is\b', 
        r'\bcurrent\s*price\b', r'\blatest\s*price\b', r'\bgive\s*me\s*\w*\s*price\b'
    ]
    financials_patterns = [r'\bfinancials?\b', r'\bmarket\s*cap\b', r'\brevenue\b', r'\bearnings\b']
    sentiment_patterns = [r'\bsentiment\b', r'\bnews\b', r'\bmarket\s*mood\b']
    analysis_patterns = [r'\banalysis\b', r'\bmarket\s*analysis\b', r'\bgood\s*(buy|investment)\b']
    
    if symbol:
        query_lower = prompt.lower()
        # Check which type of request this is using regex patterns
        if any(re.search(pattern, query_lower) for pattern in price_patterns):
            intent = "price"
            logger.debug(f"Regex-based intent detected: {intent}, symbol: {symbol}")
        elif any(re.search(pattern, query_lower) for pattern in financials_patterns):
            intent = "financials"
            logger.debug(f"Regex-based intent detected: {intent}, symbol: {symbol}")
        elif any(re.search(pattern, query_lower) for pattern in sentiment_patterns):
            intent = "sentiment"
            logger.debug(f"Regex-based intent detected: {intent}, symbol: {symbol}")
        elif any(re.search(pattern, query_lower) for pattern in analysis_patterns):
            intent = "analysis"
            logger.debug(f"Regex-based intent detected: {intent}, symbol: {symbol}")
        
        # If regex patterns don't match, use AI to figure out the intent
        if intent is None:
            logger.debug(f"Attempting LLM intent parsing for symbol: {symbol}")
            try:
                intent_response = client.text_generation(
                    prompt=f"Classify the intent of this query: '{prompt}'. Possible intents: 'price', 'financials', 'sentiment', 'analysis', 'invalid'. Return only the intent.",
                    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    max_new_tokens=10
                )
                raw_intent = intent_response
                # Clean up the AI response to get a valid intent
                intent = raw_intent.split()[0].strip().replace("'", "").replace("\"", "").strip()
                valid_intents = ["price", "financials", "sentiment", "analysis", "invalid"]
                if intent not in valid_intents:
                    # Search the raw response for valid intent keywords
                    raw_lower = raw_intent.lower()
                    for valid_intent in valid_intents:
                        if valid_intent in raw_lower:
                            intent = valid_intent
                            break
                    else:
                        intent = "invalid"
                logger.debug(f"Raw LLM intent: {raw_intent!r}, Cleaned intent: {intent}, symbol: {symbol}")
            except Exception as e:
                logger.error(f"LLM intent parsing failed: {str(e)}")
                intent = "invalid"
                response = "I couldn't understand your request. Please ask about a stock's price, financials, sentiment, or overall analysis."

    # Generate the response based on the extracted symbol and intent
    with st.chat_message("assistant"):
        if not symbol:
            response = response  # Use error response from symbol extraction
            logger.info(f"No symbol extracted for query: {prompt}")
        elif intent == "invalid":
            response = response  # Use error response from intent parsing
            logger.info(f"Invalid intent for query: {prompt}")
        else:
            try:
                # Get stock data from our FastAPI backend
                logger.debug(f"Sending API request for {symbol}, company_name: {company_name}")
                api_response = requests.get(
                    f"http://localhost:8000/stock/{symbol}",
                    params={"companyName": company_name},
                    timeout=10
                )
                api_response.raise_for_status()
                data = api_response.json()
                logger.debug(f"API response: {data}")

                # Make sure we got all the data we need
                required_fields = {"price", "financials", "sentiment", "status"}
                if not all(key in data for key in required_fields) or data["status"] != "complete":
                    logger.error(f"Invalid API response for {symbol}: {data}")
                    response = f"I received incomplete data for {symbol}. Please try again."
                else:
                    # Use AI to create natural, conversational responses
                    try:
                        if intent == "price":
                            # Generate a friendly response about the stock price
                            llm_prompt = (
                                f"You are a financial assistant. Create a concise, conversational response for {company_name} ({symbol}) using this data:\n"
                                f"- Current price: ${data['price']:.2f}\n"
                                f"Write 1-2 sentences explaining the stock price in a human-friendly way."
                            )
                            humanized_response = client.text_generation(
                                prompt=llm_prompt,
                                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                                max_new_tokens=50
                            ).strip()
                            response = humanized_response
                        elif intent == "financials":
                            # Generate a response about financial metrics
                            llm_prompt = (
                                f"You are a financial assistant. Create a conversational response for {company_name} ({symbol}) using this data:\n"
                                f"- Market Cap: ${int(data['financials']['market_cap']):,}\n"
                                f"- Revenue: ${int(data['financials']['revenue']):,}\n"
                                f"- Earnings: ${int(data['financials']['earnings']):,}\n"
                                f"Write 2-3 sentences summarizing the financial metrics in a human-friendly way."
                            )
                            humanized_response = client.text_generation(
                                prompt=llm_prompt,
                                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                                max_new_tokens=100
                            ).strip()
                            response = humanized_response
                        elif intent == "sentiment":
                            # Generate a response about market sentiment and news
                            llm_prompt = (
                                f"You are a financial assistant. Create a conversational response for {company_name} ({symbol}) using this data:\n"
                                f"- Sentiment: {data['sentiment']['summary']}\n"
                                f"- Recent news: " +
                                "; ".join(
                                    f"{article['title']} ({article['sentiment']})"
                                    for article in data['sentiment']['details'][:3]
                                ) +
                                f"\nWrite 2-3 sentences summarizing the market sentiment and key news in a human-friendly way."
                            )
                            humanized_response = client.text_generation(
                                prompt=llm_prompt,
                                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                                max_new_tokens=100
                            ).strip()
                            response = humanized_response
                        elif intent == "analysis":
                            # Generate a comprehensive analysis response
                            llm_prompt = (
                                f"You are a financial assistant. Create a conversational analysis for {company_name} ({symbol}) using this data:\n"
                                f"- Current price: ${data['price']:.2f}\n"
                                f"- Market Cap: ${int(data['financials']['market_cap']):,}\n"
                                f"- Revenue: ${int(data['financials']['revenue']):,}\n"
                                f"- Earnings: ${int(data['financials']['earnings']):,}\n"
                                f"- Sentiment: {data['sentiment']['summary']}\n"
                                f"- Recent news: " +
                                "; ".join(
                                    f"{article['title']} ({article['sentiment']})"
                                    for article in data['sentiment']['details'][:3]
                                ) +
                                f"\nWrite a concise, natural response (2-3 sentences per section) addressing price, financials, sentiment, and whether it's a good investment. Avoid bullet points."
                            )
                            humanized_response = client.text_generation(
                                prompt=llm_prompt,
                                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                                max_new_tokens=200
                            ).strip()
                            response = humanized_response
                        logger.debug(f"Humanized LLM response: {response}")
                    except Exception as e:
                        logger.error(f"LLM humanized response failed: {str(e)}")
                        # Fallback to structured response if AI fails
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
                response = f"I couldn't fetch data for {symbol} due to an error: {str(e)}."

        # Show the response and save it to chat history
        logger.debug(f"Final response: {response}")
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
