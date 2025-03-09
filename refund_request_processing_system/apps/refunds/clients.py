from logging import getLogger

import requests
from django.conf import settings

logger = getLogger('django')


class APINinjasClient:
    def __init__(self):
        self.api_key = settings.API_NINJAS_API_KEY
        self.iban_validation_url = settings.API_NINJAS_IBAN_VALIDATION_URL

    @property
    def headers(self):
        return {
            'X-Api-Key': self.api_key,
        }

    def make_request(self, url, method, params=None):
        try:
            response = requests.request(
                method, url, headers=self.headers, params=params
            )
        except requests.exceptions.ConnectionError as e:
            logger.exception(e)
            return None

        return self.handle_response(response)

    def handle_response(self, response):
        if response.status_code >= 400:
            logger.error(
                f'Request to {response.request.url} failed '
                f'with status code {response.status_code}. '
                f'Response: {response.text}'
            )
            return None

        try:
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.error(
                f'Error parsing response for request to '
                f'{response.request.url}: {e}'
            )
            return None

    def validate_iban(self, iban):
        return self.make_request(
            self.iban_validation_url, 'GET', params={'iban': iban}
        )
