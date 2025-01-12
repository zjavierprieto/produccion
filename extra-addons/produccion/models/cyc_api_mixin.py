from odoo import models
from odoo.exceptions import UserError, ValidationError
import requests
import logging

class CycApiMixin(models.AbstractModel):
    _name = 'cyc.api.mixin'
    _description = 'Mixin for CyC API Calls'

    def call_cyc_api(self, service, payload, method, files=None, timeout=10):
        """
        Generic method to call CyC API, with differentiation between GET and POST calls with or without files.

        Args:
            service (str): API service (endpoint) to call.
            payload (dict): Data to send in the request.
            method (str): HTTP method, 'GET' or 'POST'.
            files (dict): Optional, files to send with the request.
            timeout (int): Timeout for the request.

        Returns:
            dict: Parsed JSON response from the API.

        Raises:
            ValidationError: For API-related errors or unexpected responses.
        """
        
        api_version = self.env['ir.config_parameter'].sudo().get_param('api_version')
        uuid = self.env['ir.config_parameter'].sudo().get_param('uuid')
        
        url = f'https://api:5003/{api_version}/odoo/{service}'
        headers = {'uuid': uuid}

        # Validate the payload
        if not isinstance(payload, dict):
            raise UserError("The payload has to be a dictionary.")

        # Validate the files
        if files:
            if not isinstance(files, dict):
                raise UserError("The parameter 'files' has to be a dictionary.")
            for key, value in files.items():
                if not hasattr(value, 'read') and not isinstance(value, bytes):
                    raise UserError(f"The file '{key}' must be a file or binary content object.")

        # Informative log
        file_status = f"{len(files)} files attached" if files else "no files"
        logging.info(f"Calling API: {url} with payload: {payload} and {file_status}")

        try:
            # Difference on POST with files and POST without files
            if method.upper() == 'POST':
                if files:
                    response = requests.post(url, data=payload, files=files, headers=headers, timeout=timeout)
                else:
                    response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            elif method.upper() == 'GET':
                response = requests.get(url, params=payload, headers=headers, timeout=timeout)
            else:
                logging.error(f"Unsupported HTTP method: {method}")
                raise UserError("Unsupported HTTP method: Only GET and POST are supported.")

            # Manage the answer
            response.raise_for_status()
            
            try:
                response_data = response.json()
            except ValueError:
                logging.error(f"The answer is not JSON valid: {response.text}")
                raise ValidationError(f"The answer is not JSON valid: {response.text}")

            if response_data.get("status") != "success":
                error_message = response_data.get("message", "Unknown error")
                logging.error(f"API error: {error_message}")
                raise ValidationError(f"API error: {error_message}")

            logging.info(f"API Response: {response_data}")
            return response_data

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error: {http_err}")
            raise ValidationError(f"Error HTTP: {http_err}")
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Request error: {req_err}")
            raise UserError(f"Request error: {str(req_err)}")
