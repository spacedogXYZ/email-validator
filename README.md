# Email Validation Service
based on mailgun/flanker API and client

run on your own server, for privacy and performance

## Usage
- request `/address/validate?address=test@example.com`
- get json response with `is_valid`, `parts` and `did_you_mean`

## Development
- create python virtual environment `virtualenv .venv`    
- install pip requirements `pip install -r requirements.txt`
- start local server `python manager.py runserver`
- open test form `http://localhost:5000/test`