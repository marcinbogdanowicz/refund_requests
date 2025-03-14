import hashlib

from django.core.cache import cache

from apps.refunds.clients import APINinjasClient


class IBANValidator:
    NOT_CACHED = '_NOT_CACHED'

    def __init__(self, iban, country):
        self.iban = iban
        self.country = country

        self.cache_key = hashlib.md5(f'{iban}-{country}'.encode()).hexdigest()

    def get_error(self):
        if (
            cached_result := cache.get(self.cache_key, self.NOT_CACHED)
        ) is not self.NOT_CACHED:
            return cached_result

        validation_response = self._get_iban_validation_response()
        if not validation_response:
            raise RuntimeError('Validation service is unavailable.')

        result = self._get_external_validation_error(validation_response)
        cache.set(self.cache_key, result)

        return result

    def cache_valid_iban(self):
        cache.set(self.cache_key, None)

    def _get_iban_validation_response(self):
        client = APINinjasClient()
        return client.validate_iban(self.iban)

    def _get_external_validation_error(self, validation_response):
        if not validation_response.get('valid'):
            return 'Provided number is not a valid IBAN.'

        iban_country = validation_response.get('country')
        if iban_country.lower() != self.country.lower():
            return f'Provided IBAN number comes from {iban_country}, while {self.country} was provided.'

        return None
