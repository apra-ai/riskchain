#!/usr/bin/env python3
"""
Social Media Risk Tool – Twitter/X Location Monitoring

This tool uses the Twitter API v2 to retrieve recent tweets mentioning specific
locations (cities, regions, countries) in combination with keywords indicating
disruptive events such as strikes, natural disasters, political unrest, or infrastructure failures.

It enables risk detection in global supply chains by analyzing open-source
social media content, filtering relevant disruptions, and providing structured
risk entries to support decision-making and monitoring.

Example use cases:
- Detect protests or strikes in urban centers
- Identify natural disasters affecting logistics regions
- Monitor political or civil unrest in high-risk areas
"""
import traceback
import requests
from langchain_core.tools import tool
from supplychains.models import Risk, Node, Edge


@tool
def search_twitter(location: str) -> list:
    """
    Search Twitter for recent tweets mentioning a location or disruption keyword.
    
    Args:
        location: City, region, or country name (e.g. "Hamburg", "Rotterdam").
        
    Returns:
        List of tweets (text + date) mentioning disruptions near that location.
    """
    try:
        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}"
        }

        query = f"{location} (strike OR protest OR delay OR blocked OR riot OR storm OR flooding OR blackout OR shutdown) -is:retweet lang:en"

        url = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            "query": query,
            "max_results": 10,
            "tweet.fields": "created_at,text"
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        tweets = []
        for tweet in data.get("data", []):
            tweets.append({
                "text": tweet["text"],
                "date": tweet["created_at"]
            })

        return tweets or [{"message": "No relevant tweets found."}]

    except Exception as e:
        return [{"error": f"Failed to search tweets: {str(e)}"}]

@tool
def search_reddit(location: str) -> list:
    """
    Search Reddit for recent posts mentioning a location with disruption-related context.
    
    Args:
        location: City, region, or country to look for (e.g. "Berlin", "Suez", "India").
    
    Returns:
        A list of relevant Reddit posts (title + snippet + timestamp).
    """
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="supply_chain_disruption_detector"
        )

        keywords = [
            "strike", "protest", "riot", "shutdown", "storm", "flooding",
            "earthquake", "blockade", "fire", "blackout", "logistics delay"
        ]

        query = f"{location} {' OR '.join(keywords)}"

        submissions = reddit.subreddit("all").search(query, sort="new", limit=10)

        results = []
        for submission in submissions:
            results.append({
                "title": submission.title,
                "text": submission.selftext[:300],
                "created_utc": submission.created_utc,
                "url": submission.url
            })

        return results or [{"message": "No relevant Reddit posts found."}]

    except Exception as e:
        return [{"error": f"Failed to search Reddit: {str(e)}"}]


@tool
def create_risk_entry_log(name: str,
                          description: str,
                          risk_level: str,
                          risk_score: float = 0.0,
                          source: str = None,
                          node_id: int = None,
                          edge_id: int = None
                          ) -> dict:
    """
    Create a new Social Media Risk entry in the database.

    Args:
        name: Short title of the risk (e.g. "Protest in Berlin").
        description: Explanation of what was found on social media.
        risk_level: One of 'low', 'medium', or 'high'.
        risk_score: Optional numeric score from 0.0 to 1.0.
        source: A permanent URL to the original post or tweet.
        node_id: ID of the node this risk is associated with.
        edge_id: Optional edge ID (used for route-level risks).

    Returns:
        Dictionary with the created risk ID or error message.
    """
    try:
        risk = Risk.objects.create(
            name=name[:255],
            description=description,
            risk_level=risk_level.lower(),
            risk_score=risk_score,
            source=source,  # <- Jetzt wird die URL direkt gespeichert
            url=source,     # <- Auch das 'url'-Feld übernimmt die Linkadresse
            risk_type=1     # 1 = Social Media (z. B. Twitter, Reddit)
        )

        if risk.id is None:
            return {"message": f"Risk: {description} is too similar to an existing one, not created."}

        if node_id is not None:
            node = Node.objects.get(id=node_id)
            node.risks.add(risk)
            node.save()

        if edge_id is not None:
            edge = Edge.objects.get(id=edge_id)
            edge.risks.add(risk)
            edge.save()

        return {
            "status": "success",
            "risk_id": risk.id,
            "name": risk.name,
            "risk_level": risk.risk_level,
            "risk_score": risk.risk_score,
            "source": source
        }

    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
