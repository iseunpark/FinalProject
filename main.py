# Standard library imports
import os
import datetime
import requests

# Third-party imports
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel

# Load environment variables
load_dotenv()  

# API configuration constants
API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
SPORTS_API_KEY = os.getenv("SPORTS_API_KEY")
SPORTS_BASE_URL = os.getenv("SPORTS_BASE_URL")

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize FastAPI application and templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configure static file serving
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allow requests from all origins
    allow_credentials=True,   # Allow credentials in requests
    allow_methods=["*"],      # Allow all HTTP methods
    allow_headers=["*"],      # Allow all headers
)

def make_api_request(endpoint):
    """
    Make authenticated requests to the Football API.
    
    Args:
        endpoint (str): API endpoint to query
    
    Returns:
        dict: JSON response data or None if request fails
    """
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers={"X-Auth-Token": API_KEY})
        response.raise_for_status()
        print(f"API Response for {url}: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request error for {url}: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    """
    Render homepage with upcoming matches.
    """
    try:
        matches_data = make_api_request("/matches")
        upcoming_matches = matches_data.get("matches", []) if matches_data else []
    except Exception as e:
        print(f"Error fetching matches: {e}")
        upcoming_matches = []

    return templates.TemplateResponse("index.html", {
        "request": request,
        "upcoming_matches": upcoming_matches,
        "error": "Failed to load matches data." if not upcoming_matches else None,
    })

@app.get("/matches", response_class=HTMLResponse)
def matches_page(request: Request, date: str = None):
    """
    Display matches for a specific date.
    
    Args:
        date (str): Date to filter matches (YYYY-MM-DD format)
    """
    if not date:
        date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    
    data = make_api_request("/matches")
    
    if not data:
        print("Error: No data received from the API.")
        return JSONResponse(status_code=500, content={"message": "Failed to fetch matches."})
    
    # Process and filter matches for the specified date
    filtered_matches = [
        {
            "homeTeamId": match["homeTeam"]["id"],
            "homeTeam": match["homeTeam"]["name"],
            "homeTeamCrest": match["homeTeam"]["crest"],
            "awayTeamId": match["awayTeam"]["id"],
            "awayTeam": match["awayTeam"]["name"],
            "awayTeamCrest": match["awayTeam"]["crest"],
            "formattedTime": match["utcDate"].split("T")[1][:5],
            "status": match["status"]
        }
        for match in data.get("matches", [])
        if match["utcDate"].startswith(date)
    ]

    return templates.TemplateResponse("matches.html", {
        "request": request,
        "matches": filtered_matches,
        "date": date
    })

@app.get("/premier-league-teams", response_class=HTMLResponse)
def premier_league_teams(request: Request):
    """Display all Premier League teams."""
    data = make_api_request("/competitions/PL/teams")
    if not data:
        return JSONResponse(status_code=500, content={"message": "Failed to fetch teams."})

    return templates.TemplateResponse("premier_league_teams.html", {
        "request": request,
        "teams": data.get("teams", [])
    })

@app.get("/team/{team_id}", response_class=HTMLResponse)
def get_team_details(request: Request, team_id: int):
    """
    Display detailed information about a specific team.
    
    Args:
        team_id (int): ID of the team to display
    """
    team_data = make_api_request(f"/teams/{team_id}")
    if not team_data:
        return JSONResponse(status_code=500, content={"message": "Failed to fetch team details."})

    return templates.TemplateResponse("team_details.html", {
        "request": request,
        "team": team_data,
        "squad": team_data.get("squad", [])
    })

@app.get("/search", response_class=HTMLResponse)
def search_team(request: Request, team_name: str):
    """
    Search for a team by name and redirect to team details.
    
    Args:
        team_name (str): Name of team to search for
    """
    data = make_api_request("/competitions/PL/teams")
    if not data:
        return JSONResponse(status_code=500, content={"message": "Failed to fetch teams."})

    teams = data.get("teams", [])
    matching_team = next((team for team in teams if team_name.lower() in team["name"].lower()), None)
    
    if matching_team:
        return RedirectResponse(url=f"/team/{matching_team['id']}")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "upcoming_matches": [],
        "error": f"No team found matching '{team_name}'. Please try again."
    })

# Chatbot
class ChatRequest(BaseModel):
    message: str

@app.post("/chatbot")
async def chatbot_endpoint(request: ChatRequest):
    """
    Handle chatbot interactions using OpenAI API.
    
    Args:
        request (ChatRequest): Chat message from user
    """
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a chatbot answering questions for a football (or soccer in the United States) website."},
                {"role": "user", "content": request.message},
            ],
        )

        return {"response": response.choices[0].message.content}

    except (client.APIStatusError, client.APIConnectionError) as e:
        print(f"OpenAI API error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.exception_handler(404)
def custom_404(request, exc):
    """Custom 404 error handler"""
    return JSONResponse(status_code=404, content={"message": "Resource not found."})

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)