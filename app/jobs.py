from flask import render_template, jsonify
from .app import app, rq, mail
from rq import get_current_job
from integrations import base_crm, briteverify
import flanker.addresslib.address
from flask_mail import Message

import logging
from datetime import datetime

log = logging.getLogger(__name__)

def results_hash(type):
    return "{date}-{type}".format(
        date=datetime.now().date(),
        type=type
    )

@rq.job('high')
def validate_new_emails():
    crm_instance = base_crm.get_instance()

    # get newly subscribed addresses from CRM
    to_validate = crm_instance.new_emails()
    if app.config.get('DEBUG') and to_validate:
        import random
        to_validate = random.sample(to_validate, 50)

    log.info('validating {} new emails'.format(len(to_validate)))

    for email in to_validate:
        simple_validation_job = flanker_validate.queue(email=email)
        save_result_job = save_to_crm.queue(stage='flanker', depends_on=simple_validation_job)

    if to_validate:
        # send admin report after last result is done
        admin_report_job = send_admin_report.queue(depends_on=save_result_job)
    else:
        log.error('no new emails to validate')


@rq.job('high')
def validate_old_emails():
    crm_instance = base_crm.get_instance()

    # get addresses from CRM that passed flanker 30 days ago, but have not opened an email
    to_validate = crm_instance.old_emails()

    log.info('validating {} old emails'.format(len(to_validate)))

    for email in to_validate:
        simple_validation_job = briteverify_validate.queue(email=email)
        save_result_job = save_to_crm.queue(stage='briteverify', depends_on=simple_validation_job)

    if to_validate:
        # send admin report after last result is done
        admin_report_job = send_admin_report.queue(depends_on=save_result_job)
    else:
        log.error('no old emails to validate')


@rq.job('high')
def flanker_validate(email):
    # run through flanker
    # a free, rules based validator
    validated = flanker.addresslib.address.validate_address(email, metrics=False, mx_lookup=False)
    if validated:
        status = 'valid'
    else:
        status = 'invalid'
        log.info('invalid {}'.format(email))

    data = {'email':email,
            'status':status}

    # save results to redis hash
    rq.connection.hincrby(results_hash('flanker'), status)

    if status == 'invalid':
        # try to correct hostname for suggestions
        parsed = flanker.addresslib.address.parse(email)
        suggested_hostname = flanker.addresslib.corrector.suggest(parsed.hostname)
        if suggested_hostname != parsed.hostname:
            suggested_email = '%s@%s' % (parsed.mailbox, suggested_hostname)
            log.info('suggestion {}'.format(suggested_email))
            # save suggestion to redis list
            rq.connection.lpush(results_hash('suggestions'), "{},{}".format(email,suggested_email))
            data['suggested_email'] = suggested_email

    return data


@rq.job('high')
def briteverify_validate(email):
    # run through briteverify validation
    # more comprehensive, but expensive check
    status = briteverify.check(email)

    # save results to redis hash
    rq.connection.hincrby(results_hash('briteverify'), status)

    return {'email': email, 'status': status}


@rq.job('low')
def save_to_crm(stage='flanker'):
    crm_instance = base_crm.get_instance()

    # get results from job dependency
    job = get_current_job(rq.connection)
    validation_result = job.dependency.result

    email = validation_result['email']
    status = validation_result['status']

    if app.config.get('DEBUG'):
        return True

    crm_complete = crm_instance.set_user_status(stage, email, status)

    if stage == 'briteverify' and status.lower() == 'invalid':
        crm_unsubscribe = crm_instance.set_user_status('unsubscribe', email, status)

    return crm_complete


@rq.job('low')
def send_admin_report():
    flanker_results = rq.connection.hgetall(results_hash('flanker'))
    briteverify_results = rq.connection.hgetall(results_hash('briteverify'))

    # rehydrate email,suggestion from redis list
    suggestions_list = []
    for l in rq.connection.lrange(results_hash('suggestions'),0,-1):
        suggestions_list.append(l.split(','))

    admin_report = render_template('admin_report.txt',
        new_emails=flanker_results,
        old_emails=briteverify_results,
        suggestions_list=suggestions_list)
    
    if app.config.get('ADMIN_WEBHOOK'):
        import requests
        requests.post(app.config.get('ADMIN_WEBHOOK'),
            jsonify({'text': admin_report})
        )

    ADMIN_EMAILS = app.config.get('ADMIN_EMAILS')
    if ADMIN_EMAILS:
        msg = Message('test subject', sender=ADMIN_EMAILS[0], recipients=ADMIN_EMAILS)
        msg.body = admin_report
        with app.app_context():
            mail.send(msg)

    if app.config.get('DEBUG'):
        # during testing, remove results
        rq.connection.delete(results_hash('flanker'))
        rq.connection.delete(results_hash('briteverify'))
        rq.connection.delete(results_hash('suggestions'))
