# Stock Chatbot

Welcome to the **Stock Chatbot**! This is a user-friendly web application built with Python that lets you ask about NASDAQ stocks and get conversational, human-like responses. Whether you want to know the current price of a stock, its financial metrics, market sentiment, or an overall analysis, this chatbot has you covered. It uses real-time data from financial APIs and a language model to provide clear and natural answers.

The chatbot is built with:
- **Streamlit** for the web interface (`web/app.py`).
- **FastAPI** for the backend API (`api/main.py`).
- **Pandas** to process NASDAQ stock data (`scripts/generate_symbols.py`).
- **External APIs**: Alpha Vantage (stock prices), NewsAPI (news sentiment), and Hugging Face (language model for intent parsing and response generation).

This README will guide you through setting up and running the project on your local system, step by step. Let's get started!

## Table of Contents
1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Prerequisites](#prerequisites)
4. [Setup Instructions](#setup-instructions)
   - [Clone the Repository](#1-clone-the-repository)
   - [Set Up a Virtual Environment](#2-set-up-a-virtual-environment)
   - [Install Dependencies](#3-install-dependencies)
   - [Download NASDAQ Data](#4-download-nasdaq-data)
   - [Set Up Environment Variables](#5-set-up-environment-variables)
   - [Generate NASDAQ Symbols JSON](#6-generate-nasdaq-symbols-json)
5. [Running the Application](#running-the-application)
   - [Start the FastAPI Backend](#1-start-the-fastapi-backend)
   - [Start the Streamlit Frontend](#2-start-the-streamlit-frontend)
6. [Using the Chatbot](#using-the-chatbot)
7. [Example Queries](#example-queries)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)
10. [License](#license)

## Features
- **Conversational Responses**: Ask questions like "What's the price of AAPL?" or "Is MSFT a good buy?" and get natural, human-like answers.
- **Real-Time Data**: Pulls stock prices and financial metrics from Alpha Vantage and news sentiment from NewsAPI.
- **Smart Intent Detection**: Uses regex and Hugging Face's Mixtral-8x7B model to understand your query (price, financials, sentiment, or analysis).
- **NASDAQ Support**: Handles all valid NASDAQ stocks, validated against a preprocessed list.
- **Error Handling**: Gracefully manages invalid symbols, API errors, and rate limits with fallback responses.

## Project Structure
Here's how the project is organized:
```
real-time-multi-agent-stock-info/
├── api/
│   └── main.py              # FastAPI backend to fetch stock data and sentiment
├── data/
│   ├── nasdaqlisted.txt     # Raw NASDAQ stock data (download required)
│   └── nasdaq_symbols.json  # Processed list of NASDAQ symbols and company names
├── scripts/
│   └── generate_symbols.py  # Script to process nasdaqlisted.txt into JSON
├── web/
│   └── app.py               # Streamlit frontend for the chatbot interface
├── .env                     # Environment variables (API keys)
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## Prerequisites
Before you start, make sure you have:
- **Python 3.8+**: The project uses modern Python features. Check your version with:
  ```bash
  python --version
  ```
- **Git**: To clone the repository. Install from [git-scm.com](https://git-scm.com/).
- **Internet Connection**: Required for downloading dependencies and fetching API data.
- **API Keys**:
  - **Alpha Vantage**: For stock prices and financials. Sign up at [alphavantage.co](https://www.alphavantage.co/support/#api-key).
  - **NewsAPI**: For news sentiment. Get a key at [newsapi.org](https://newsapi.org/register).
  - **Hugging Face**: For language model access. Create an account at [huggingface.co](https://huggingface.co/) and generate an API token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
- **Text Editor**: Like VS Code or PyCharm to edit files (e.g., `.env`).

## Setup Instructions
Follow these steps to set up the project on your local system. Each step is explained in detail to make it easy.

### 1. Clone the Repository
Clone this repository to your local machine using Git.

```bash
git https://github.com/mr-1o1/real-time-multi-agent-stock-info.git
cd real-time-multi-agent-stock-info
```

Replace `your-username` with your GitHub username or the correct repository URL.

### 2. Set Up a Virtual Environment
A virtual environment keeps project dependencies isolated. Create and activate one:

- **On Windows**:
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

- **On macOS/Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

You’ll see `(venv)` in your terminal, indicating the virtual environment is active.

### 3. Install Dependencies
Install the required Python packages listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `pandas`: For processing NASDAQ data.
- `requests`: For API calls.
- `streamlit`: For the web interface.
- `huggingface_hub`: For LLM access.
- `python-dotenv`: For loading environment variables.
- `fastapi`: For the backend API.
- `uvicorn`: For running the FastAPI server.

If you encounter errors, ensure `pip` is up-to-date:
```bash
pip install --upgrade pip
```

### 4. Download NASDAQ Data
The chatbot needs a list of NASDAQ stocks (`nasdaqlisted.txt`) to validate symbols.

1. Download the file from NASDAQ’s FTP server: [ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt](ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt).
2. Save it in the `data/` folder as `nasdaqlisted.txt`. Create the `data/` folder if it doesn’t exist:
   ```bash
   mkdir data
   ```

Alternatively, use `curl` to download directly:
```bash
curl -o data/nasdaqlisted.txt ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt
```

The file is pipe-delimited (`|`) and contains stock symbols, company names, and other metadata.

### 5. Set Up Environment Variables
The project uses API keys stored in a `.env` file for security. Create a `.env` file in the project root:

```bash
touch .env
```

Open `.env` in a text editor and add your API keys:

```env
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
NEWSAPI_KEY=your_newsapi_key
HUGGINGFACE_API_TOKEN=your_huggingface_api_token
```

Replace the placeholders with your actual keys:
- `ALPHA_VANTAGE_KEY`: From [alphavantage.co](https://www.alphavantage.co/support/#api-key).
- `NEWSAPI_KEY`: From [newsapi.org](https://newsapi.org/account).
- `HUGGINGFACE_API_TOKEN`: From [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

Save the file. The `.env` file is ignored by `.gitignore` to keep your keys private.

### 6. Generate NASDAQ Symbols JSON
The chatbot uses `nasdaq_symbols.json` to validate stock symbols and company names. Generate it by running:

```bash
python scripts/generate_symbols.py
```

This script:
- Reads `nasdaqlisted.txt`.
- Filters for valid common stocks (excludes ETFs, warrants, etc.).
- Creates `data/nasdaq_symbols.json` with entries like:
  ```json
  [
    {"symbol": "AAPL", "company_name": "Apple Inc. - Common Stock"},
    {"symbol": "MSFT", "company_name": "Microsoft Corporation - Common Stock"}
  ]
  ```

Check the logs for success:
```
INFO: Read <num> entries from data/nasdaqlisted.txt
INFO: Filtered to <num> valid NASDAQ stock symbols
INFO: Saved <num> records to data/nasdaq_symbols.json
```

If errors occur, ensure `nasdaqlisted.txt` is in `data/` and has the correct format (pipe-delimited).

## Running the Application
The application has two components: the FastAPI backend and the Streamlit frontend. Run them in separate terminal windows.

### 1. Start the FastAPI Backend
The backend (`api/main.py`) fetches stock data and sentiment.

In your virtual environment, run:

```bash
uvicorn api.main:app --reload
```

- `uvicorn`: Runs the FastAPI server.
- `api.main:app`: Points to the FastAPI app in `main.py`.
- `--reload`: Auto-restarts the server on code changes (useful for development).

You’ll see:
```
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

The backend is now running at `http://localhost:8000`.

### 2. Start the Streamlit Frontend
The frontend (`web/app.py`) provides the chatbot interface.

In a new terminal (with the virtual environment activated), run:

```bash
streamlit run web/app.py
```

You’ll see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Open `http://localhost:8501` in your browser to access the chatbot.

## Using the Chatbot
1. Open `http://localhost:8501` in your browser.
2. Type a question in the chat input, like:
   - "What’s the price of AAPL?"
   - "Is MSFT a good buy?"
3. The chatbot responds with a conversational answer, pulling data from the FastAPI backend and formatting it naturally using the Hugging Face LLM.

## Example Queries
Here’s what you can ask and what to expect:

- **Price**:
  - Query: "What is the price of GOOG?"
  - Response: "Alphabet Inc.’s stock (GOOG) is currently trading at $173.98, reflecting strong investor confidence in Google’s market position."

- **Financials**:
  - Query: "Financials of MSFT"
  - Response: "Microsoft Corporation (MSFT) has a massive market capitalization of $3.57 trillion, reflecting its dominance in the tech industry. Its annual revenue stands at $270.01 billion, with earnings of $149.17 billion, highlighting robust financial health."

- **Sentiment**:
  - Query: "What’s the sentiment for GOOG?"
  - Response: "The market sentiment for Alphabet Inc. (GOOG) is positive right now. Recent news highlights the resolution of a multi-year antitrust investigation and optimism about Google’s stock, which boosts confidence in its outlook."

- **Analysis**:
  - Query: "Is MSFT a good buy?"
  - Response: "Let’s dive into Microsoft Corporation (MSFT) to see if it’s a good investment. Its stock is trading at $480.24, reflecting solid market trust in this tech giant. Financially, Microsoft shines with a $3.57 trillion market cap, $270.01 billion in revenue, and $149.17 billion in earnings, showcasing its industry leadership. Sentiment is neutral, with positive buzz about its competitive edge tempered by news of planned job cuts in sales. Given its strong financials, Microsoft could be a solid long-term pick, but keep an eye on those news developments."

## Troubleshooting
If you run into issues, try these solutions:

- **Error: “Symbols file data/nasdaq_symbols.json not found”**
  - Run `python scripts/generate_symbols.py` to create the file.
  - Ensure `nasdaqlisted.txt` is in `data/`.

- **Error: “Hugging Face API token not found in .env”**
  - Check `.env` for `HUGGINGFACE_API_TOKEN`.
  - Verify your token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

- **Error: “LLM humanized response failed: 429 Too Many Requests”**
  - Hugging Face’s free tier has a rate limit (~100 requests/hour). Wait a few minutes and retry.
  - The chatbot falls back to structured responses in this case.

- **Invalid Symbol (e.g., “GOOGL is not a valid NASDAQ symbol”)**:
  - Ensure `nasdaq_symbols.json` includes the symbol. Check `nasdaqlisted.txt` and rerun `generate_symbols.py`.
  - Some symbols (e.g., GOOGL) may be NYSE, not NASDAQ.

- **API Call Fails**:
  - Test the backend:
    ```bash
    curl "http://localhost:8000/stock/AAPL?companyName=Apple%20Inc.+-+Common+Stock"
    ```
  - Verify API keys in `.env`.
  - Check rate limits for Alpha Vantage (5 requests/minute on free tier) or NewsAPI.

- **Slow Responses**:
  - LLM calls may take 1–3 seconds due to network latency or rate limits.
  - Ensure a stable internet connection.

For other issues, check logs in `streamlit_log.log` or the terminal output.

## Contributing
Want to improve the chatbot? Here’s how:
1. Fork the repository.
2. Create a branch: `git checkout -b feature/your-feature`.
3. Make changes and test locally.
4. Commit: `git commit -m "Add your feature"`.
5. Push: `git push origin feature/your-feature`.
6. Open a pull request on GitHub.

Suggestions:
- Normalize company names (e.g., remove “- Common Stock”).
- Add support for NYSE stocks.
- Optimize LLM prompts for faster responses.

## License
This project is licensed under the MIT License.
<!-- See [LICENSE](LICENSE) for details. -->

---

Happy chatting with your Stock Chatbot! If you have questions or need help, open an issue on GitHub. 📈