from .base_crm import BaseCRM
from actionkit.rest import ActionKit
from actionkit.errors import ActionKitGeneralError
import os, time
from urlparse import urlparse
import logging


log = logging.getLogger(__name__)

class ActionKitCRM(BaseCRM):
    def __init__(self):
        self.client = ActionKit(
            instance=os.environ.get('AK_INSTANCE'),
            username=os.environ.get('AK_USER'),
            password=os.environ.get('AK_PASS')
        )
        self.ak_page_names = {
            'new_emails': os.environ.get('AK_NEW_EMAILS_REPORT_NAME'),
            'old_emails': os.environ.get('AK_OLD_EMAILS_REPORT_NAME'),
            'flanker': os.environ.get('AK_FLANKER_IMPORT_NAME'),
            'briteverify': os.environ.get('AK_BRITEVERIFY_IMPORT_NAME'),
            'unsubscribe': os.environ.get('AK_UNSUBSCRIBE', 'unsubscribe'),
        }

    def check_bgreport(self, report_name, max_checks=5):
        # run_bgreport and await results, with progressive backoff
        # downloads the file from ActionKit, because it may be too large to get over the API reponse

        log.debug('run_bgreport({}) max={}'.format(report_name, max_checks))
        result = self.client.raw('POST', '/rest/v1/report/background/{report_name}/'.format(report_name=report_name),
            params={
                'format': 'csv', # to force a download
                #'refresh': True
            })
        report_uri = result.headers['Location']
        report_path = urlparse(report_uri).path
        log.debug('run_bgreport checking {}'.format(report_path))

        checked = 0
        while(checked < max_checks):
            exp_backoff = 2**checked-1
            time.sleep(exp_backoff)
            log.debug('no result, sleep({})'.format(exp_backoff))
            result = self.client.get(report_path)
            if result['completed'] == True:
                if result['details']['status'] == 'complete':
                    download_path = result['details']['download_uri']
                    log.debug('run_bgreport downloading {}'.format(download_path))
                    download = self.client.raw('GET', download_path)
                    return download
                else:
                    log.error('run_bgreport error {}'.format(result['message']))
            else:
                checked += 1

        raise ActionKitGeneralError('unable to get result for {report_name} within {max_checks} requests'.format(
            report_name=report_name,
            max_checks=max_checks)
        )
        return result

    def new_emails(self):
        result = self.check_bgreport(self.ak_page_names['new_emails'], max_checks=5)
        emails_list = result.text.split()
        log.info('got {} new emails'.format(len(emails_list)))
        return emails_list

    def old_emails(self):
        result = self.check_bgreport(self.ak_page_names['old_emails'], max_checks=5)
        emails_list = result.text.split()
        log.info('got {} old emails'.format(len(emails_list)))
        return emails_list

    def set_user_status(self, stage, email, status):
        response = self.client.post('/rest/v1/action/', json={
            'page': self.ak_page_names[stage],
            'email': email,
            'action_status': status})
        return response.get('status') == 'complete'

