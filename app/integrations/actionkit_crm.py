from .base_crm import BaseCRM
from actionkit.rest import ActionKit
from actionkit.errors import ActionKitGeneralError
import os, time
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
            'flanker': os.environ.get('AK_FLANKER_IMPORT_NAME'),
            'briteverify': os.environ.get('AK_BRITEVERIFY_IMPORT_NAME'),
            'unsubscribe': os.environ.get('AK_UNSUBSCRIBE'),
        }

    def check_bgreport(self, report_name, max_checks=5):
        # run_bgreport and await results, with progressive backoff
        result = self.client.run_bgreport(report_name)
        log.info('run_bgreport({}) max={}'.format(report_name, max_checks))
        if result['completed']:
            return result['details']['results']

        checked = 0
        while(checked < max_checks):
            exp_backoff = 2**checked-1
            time.sleep(exp_backoff)
            log.info('no result, sleep({})'.format(exp_backoff))
            result = self.client.get(result['resource_uri'])
            if result['completed']:
                log.info("got {} results".format(len(result['details']['results'])))
                return result['details']['results']
            else:
                checked += 1

        raise ActionKitGeneralError('unable to get result for {report_name} within {max_checks} requests'.format(
            report_name=report_name,
            max_checks=max_checks)
        )
        return result

    def new_emails(self):
        result = self.check_bgreport(self.ak_page_names['new_emails'], max_checks=5)
        # returns a list for each row, flatten results into one list
        emails_list = []
        for row in result:
            emails_list.append(row[0])
        return emails_list

    def set_user_status(self, stage, email, status):
        response = self.client.post('/rest/v1/action/', json={
            'page': self.ak_page_names[stage],
            'email': email,
            'action_status': status})
        return response.get('status') == 'complete'

