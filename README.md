# Email Validation Service
based on mailgun/flanker API and client

run on your own server, for privacy and performance

## Usage
- request `/address/validate?address=test@example.com`
- get json response with `is_valid`, `parts` and `did_you_mean`

## Form Integration
- include `/static/validate.js`
- attach to your email input `$('form input[name=email]').email_validator` and define your own success and error callbacks
- or use ActionKit.forms validation with `actionkit.emailValidation.init(API_URL);`

## Deployment
- caches mail server responses in Redis, or thread-local dictionary
- warm cache with `python manager.py warm_cache -f REMOTE_FILE` or `python manager.py warm_cache -f - < LOCAL_FILE`

## Development
- create python virtual environment `virtualenv .venv`    
- install pip requirements `pip install -r requirements.txt`
- start local server `python manager.py runserver`
- open test form `http://localhost:5000/test`