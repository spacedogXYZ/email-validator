from .app import app, rq
from rq import get_current_job
from integrations import base_crm, briteverify
import flanker.addresslib.address

import logging


log = logging.getLogger(__name__)

@rq.job
def validate_new_emails():
    crm_instance = base_crm.get_instance()

    # get newly subscribed addresses from CRM
    to_validate = crm_instance.new_emails()

    for email in to_validate:
        simple_validation_job = flanker_validate.queue(email=email)
        save_result_job = save_to_crm.queue(depends_on=simple_validation_job)

    # send admin report
    # TODO

@rq.job
def flanker_validate(email):
    # run through flanker
    validated = flanker.addresslib.address.validate_address(email, metrics=False, mx_lookup=False)
    if validated:
        status = 'valid'
    else:
        status = 'invalid'
        log.info('invalid {}'.format(email))

    data = {'email':email,
            'status':status}

    if data['status'] == 'invalid':
        # try to correct hostname for suggestions
        parsed = flanker.addresslib.address.parse(email)
        suggested_hostname = flanker.addresslib.corrector.suggest(parsed.hostname)
        if suggested_hostname != parsed.hostname:
            data['suggested_email'] = '%s@%s' % (parsed.mailbox, suggested_hostname)

    return data

@rq.job
def save_to_crm():
    crm_instance = base_crm.get_instance()

    # get results of job dependency
    job = get_current_job(rq.connection)
    validation_result = job.dependency.result

    email = validation_result['email']
    status = validation_result['status']
    log.info('save_to_crm {}:{}'.format(email, status))
    crm_response = crm_instance.set_user_status(email, status)
    return crm_response

@rq.job
def validate_old_emails():
    crm_instance = base_crm.get_instance()

    # get addresses from CRM that passed flanker 30 days ago, but have not opened an email
    to_validate = crm_instance.old_emails()

    for email in to_validate:
        # run through briteverify validation
        status = briteverify.check(email)
        # save results to CRM
        crm_instance.set_user_status(email, status)

        if status in ['invalid', 'disposable']:
            crm_instance.unsubscribe(email)

    # send admin report
    # TODO
