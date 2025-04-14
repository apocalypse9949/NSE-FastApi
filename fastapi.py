from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import snscrape.modules.twitter as sntwitter
from fastapi.concurrency import run_in_threadpool
import os
import nest_asyncio
from pyngrok import ngrok
import uvicorn

app = FastAPI()

class Tweet(BaseModel):
    content: str
    date: str

@app.get("/")
def root():
    return {"message": "FastAPI is running. Use /docs for Swagger UI."}

@app.get("/api/price/{symbol}")
def get_price(symbol: str, from_date: str, to_date: str):
    if not symbol or not from_date or not to_date:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    return {"symbol": symbol, "from": from_date, "to": to_date}

@app.get("/api/tweets/{symbol}", response_model=List[Tweet])
async def get_tweets(symbol: str, since: str, until: str):
    if not symbol or not since or not until:
        raise HTTPException(status_code=400, detail="Missing required parameters")
    return await run_in_threadpool(_scrape_tweets, symbol, since, until)

def _scrape_tweets(symbol: str, since: str, until: str):
    tweets = []
    query = f"${symbol} lang:en since:{since} until:{until}"
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i > 50:
            break
        tweets.append({"content": tweet.content, "date": str(tweet.date)})
    return tweets


ngrok_auth_token = "your_auth_token"  
ngrok.set_auth_token(ngrok_auth_token)  
public_url = ngrok.connect(8000)
print(" Public URL:", public_url)


nest_asyncio.apply()


try:
    uvicorn.run(app, host="0.0.0.0", port=8000)
except KeyboardInterrupt:
    print("Server manually stopped.")

