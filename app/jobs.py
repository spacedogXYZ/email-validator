from .app import app, rq
from rq import get_current_job
from integrations import base_crm, briteverify
import flanker.addresslib.address

import logging
from datetime import datetime

log = logging.getLogger(__name__)

def results_hash(type):
    return "{date}-{type}".format(
        date=datetime.now().date(),
        type=type
    )

@rq.job
def validate_new_emails():
    crm_instance = base_crm.get_instance()

    # get newly subscribed addresses from CRM
    to_validate = crm_instance.new_emails()

    for email in to_validate:
        simple_validation_job = flanker_validate.queue(email=email)
        save_result_job = save_to_crm.queue(depends_on=simple_validation_job)

    # send admin report after last result is done
    admin_report_job = send_admin_report.queue(depends_on=save_result_job)


@rq.job
def validate_old_emails():
    crm_instance = base_crm.get_instance()

    # get addresses from CRM that passed flanker 30 days ago, but have not opened an email
    to_validate = crm_instance.old_emails()

    for email in to_validate:
        simple_validation_job = briteverify_validate.queue(email=email)
        save_result_job = save_to_crm.queue(depends_on=simple_validation_job)

        if status in ['invalid', 'disposable']:
            crm_instance.unsubscribe(email)

    # send admin report after last result is done
    admin_report_job = send_admin_report.queue(depends_on=save_result_job)

@rq.job
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
            rq.connection.append(results_hash('suggestions'), suggested_email)
            data['suggested_email'] = suggested_email

    return data

@rq.job
def briteverify_validate(email):
    # run through briteverify validation
    # more comprehensive, but expensive check
    status = briteverify.check(email)

    # save results to redis hash
    rq.connection.hincrby(results_hash('briteverify'), status)

    return {'email': email, 'status': status}

@rq.job
def save_to_crm():
    crm_instance = base_crm.get_instance()

    # get results from job dependency
    job = get_current_job(rq.connection)
    validation_result = job.dependency.result

    email = validation_result['email']
    status = validation_result['status']
    log.info('save_to_crm {}:{}'.format(email, status))
    crm_response = crm_instance.set_user_status(email, status)
    return crm_response

@rq.job
def unsubscribe_from_crm():
    crm_instance = base_crm.get_instance()

    # get results of job dependency
    job = get_current_job(rq.connection)
    validation_result = job.dependency.result

    email = validation_result['email']
    status = validation_result['status']
    log.info('save_to_crm {}:{}'.format(email, status))
    crm_response = crm_instance.unsubscribe_user(email)
    return crm_response

@rq.job
def send_admin_report():
    flanker_results = rq.connection.get(results_hash('flanker'))
    briteverify_results = rq.connection.get(results_hash('briteverify'))
    suggestions_list = rq.connection.get(results_hash('suggestions'))

    print "flanker_results",flanker_results
    print "briteverify_results",briteverify_results
    print "suggestions_list",suggestions_list

