from flask import Flask, render_template
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Replace this with your actual API key from football-data.org
API_KEY = 'e5ea053d3ec74fe5803fdb4b57c1f8d5'

@app.route('/')
def index():
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get('https://api.football-data.org/v4/matches', headers=headers)
    matches = response.json().get('matches', [])
    return render_template('index.html', matches=matches)

@app.route('/match/<int:match_id>')
def match_detail(match_id):
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(f'https://api.football-data.org/v4/matches/{match_id}', headers=headers)
    match = response.json()
    return render_template('match.html', match=match)

@app.route('/matches')
@app.route('/matches/<date>')
def matches(date=None):
    if date is None:
        current_date = datetime.now()
    else:
        try:
            requested_date = datetime.strptime(date, '%Y-%m-%d')
            current_date = requested_date
        except ValueError:
            current_date = datetime.now()
    
    prev_date = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
    current_date_str = current_date.strftime('%Y-%m-%d')
    
    # Try to get matches for a wider date range
    headers = {'X-Auth-Token': API_KEY}
    try:
        response = requests.get(
            'https://api.football-data.org/v4/matches',
            headers=headers,
            params={
                'dateFrom': (current_date - timedelta(days=3)).strftime('%Y-%m-%d'),
                'dateTo': (current_date + timedelta(days=3)).strftime('%Y-%m-%d')
            }
        )
        response.raise_for_status()
        
        data = response.json()
        all_matches = data.get('matches', [])
        
        # Filter matches for the current date
        matches = [
            match for match in all_matches 
            if match['utcDate'].split('T')[0] == current_date_str
        ]
        
        if not matches:
            # If no matches on exact date, get closest matches
            matches = all_matches[:5]  # Show up to 5 closest matches
            
    except requests.RequestException as e:
        print(f"Request Exception: {str(e)}")
        matches = []
    except ValueError as e:
        print(f"JSON Parsing Error: {str(e)}")
        matches = []
    
    return render_template('matches.html',
                         matches=matches,
                         current_date=current_date,
                         prev_date=prev_date,
                         next_date=next_date)

@app.route('/profile')
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)