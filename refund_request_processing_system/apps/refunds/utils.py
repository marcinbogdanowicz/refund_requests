from apps.refunds.clients import APINinjasClient


class IBANValidator:
    def __init__(self, iban, country):
        self.iban = iban
        self.country = country

    def get_error(self):
        validation_response = self._get_iban_validation_response()
        if not validation_response:
            raise RuntimeError('Validation service is unavailable.')

        return self._get_external_validation_error(validation_response)

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
