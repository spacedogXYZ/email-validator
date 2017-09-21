# Email Validation Service
based on mailgun/flanker API and client

run on your own server, for privacy and performance

## Usage
- request `/address/validate?address=test@example.com`
- get json response with `is_valid`, `parts` and `did_you_mean`

## Form Integration
- include `/static/validate.js`
- attach to your email input `$('form input[name=email]').email_validator` and define your own success and error callbacks
- or use ActionKit.forms validation with ```actionkit.emailValidation.init({
    api_url: 'https://YOUR_APP.herokuapp.com/address/validate',
    stop_on_invalid: true
});```

## Nightly Batch Processing
- run at least one worker process `python manager.py rq worker`
- trigger nightly batches via cron or Heroku scheduler with `python manager.py queue_nightly_tasks`
- new emails will be downloaded from configured CRM and checked with Flanker
- old emails which have not taken an action will be double checked with Briteverify (if BRITEVERIFY_API_KEY is provided)
- emails which fail their second validation can be unsubscribed
- nightly reports are sent via email to admins and optional Slack channel

## Deployment
- caches mail server responses in Redis, or thread-local dictionary
- warm cache with `python manager.py warm_cache -f REMOTE_FILE` or `python manager.py warm_cache -f - < LOCAL_FILE`
- when running in Heroku, you may want to run `python manager.py warm_cache` before `uwsgi uwsgi.ini`, to ensure flanker.address_lib parser is run successfully
- when running in Heroku, you may run multiple workers in one dyno with `supervisord -c supervisor.conf -n`

## Development
- create python virtual environment `virtualenv .venv`    
- install pip requirements `pip install -r requirements.txt`
- start local server `python manager.py runserver`
- open test form `http://localhost:5000/test`