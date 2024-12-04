# FinalProject
# Football Matches Web Application

A FastAPI-based web application that displays football matches, team information, and includes a chatbot assistant for football-related queries.

## Features

- View upcoming football matches
- Search for teams
- Browse Premier League teams
- View detailed team information and squad lists
- AI-powered chatbot for football-related questions

## Prerequisites

- Python 3.8+
- pip (Python package installer)

## Dependencies
pip install -r requirements.txt

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
FOOTBALL_API_KEY=your_football_data_api_key
OPENAI_API_KEY=your_openai_api_key
SPORTS_API_KEY=your_sports_api_key (Negligible)

## Instructions

1. Run main.py with prerequisites installed and .env set up. 
2. Open browser and navigate to http://127.0.0.1:8000

football-matches-app/
├── main.py           # Main application file
├── requirements.txt  # Python dependencies
├── .env             # Environment variables
├── static/          # Static files (CSS, JS)
└── templates/       # HTML templates
    ├── index.html
    ├── matches.html
    ├── premier_league_teams.html
    └── team_details.html

## AI Usage
1. Implementation of OpenAI ChatBot
2. Styles.css formatting
3. Aiding in Comments
4. Debugging Errors
5. Aid in drafting of README.md
6. Aid in drafting of requirements.txt

## Technologies Used
- FastAPI
- Jinja2 Templates
- OpenAI API
- Football-Data.org API

## Acknowledgments
- Football-Data.org for providing the sports data API
- OpenAI for the ChatGPT API integration