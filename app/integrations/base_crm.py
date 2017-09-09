class BaseCRM(object):
    # pluggable CRM backend
    client = None

    def __init__(self, **kwargs):
        pass

    def new_emails(self):
        """
        Returns list of all new emails to process
        """
        raise NotImplementedError()

    def old_emails(self):
        """
        Returns list of all old emails to process
        """
        raise NotImplementedError()

import os

def get_instance():
    if os.environ.get('AK_INSTANCE'):
        from actionkit_crm import ActionKitCRM
        return ActionKitCRM() 