from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import httpx
import snscrape.modules.twitter as sntwitter
import ssl
import certifi

app = FastAPI()

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nseindia.com/",
    "Accept-Language": "en-US,en;q=0.9",
}

SESSION = httpx.Client(headers=HEADERS, timeout=10.0)


class Tweet(BaseModel):
    content: str
    date: str


@app.get("/api/price/{symbol}")
def get_nse_price(symbol: str, from_date: str, to_date: str):
    try:
        url = f"https://www.nseindia.com/api/historical/cm/equity?symbol={symbol.upper()}&series=[%22EQ%22]&from={from_date}&to={to_date}"
        response = SESSION.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="NSE Unauthorized or blocked.")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tweets/{symbol}", response_model=List[Tweet])
def get_tweets(symbol: str, since: str, until: str):
    tweets = []
    query = f"${symbol} lang:en since:{since} until:{until}"
    try:
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i > 50:
                break
            tweets.append({"content": tweet.content, "date": str(tweet.date)})
        return tweets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"snscrape failed: {e}")
