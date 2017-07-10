import requests
from django.conf import settings


class VerifyEmail(object):
    """ Class for verify email address """

    def __init__(self):
        self.verified_emails = []

    def verify(self, value):
        if value is None:
            return False
        if value in self.verified_emails:
            return  True

        url = ''.join([settings.HUNTER_URL_API, '&email=', value])
        response = requests.get(url, timeout=settings.HUNTER_READ_TIMEOUT)
        response = response.json()
        result = response['data']
        if result['webmail'] or result['result'] == 'deliverable' or (
                not result['gibberish'] and not result['disposable'] and
                result['mx_records'] and result['smtp_check']):
            self.verified_emails.append(value)
            return True
        return False

    def get_emails(self):
        return self.verified_emails

    def remove(self, value):
        if value in self.verified_emails:
            self.verified_emails.remove(value)


email_verifier = VerifyEmail()
