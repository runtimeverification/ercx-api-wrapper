import configparser
from typing import Any

import requests


class RestClient:
    def __init__(self, api_url: str, api_key: str) -> None:
        self.api_url = api_url
        self.api_key = api_key

    @staticmethod
    def from_config() -> 'RestClient':
        config = configparser.ConfigParser()
        config.read('config.ini')
        url = config['URLs']['ERCx_API_URL']
        key = config['Keys']['ERCx_API_KEY']
        return RestClient(url, key)

    def _send_request(
        self, method: str, end_point: str, data: dict | None = None, parameters: dict | None = None
    ) -> Any:
        # Construct the headers with the API key
        headers = {'X-API-KEY': self.api_key}

        # Construct the URL
        url = self.api_url + end_point

        try:
            # Send the request based on the method (GET or POST)
            if method == 'GET':
                response = requests.get(url, headers=headers, params=parameters)
            elif method == 'POST':
                if data:
                    response = requests.post(url, headers=headers, json=data)
                else:
                    response = requests.post(url, headers=headers)
            elif method == 'DELETE':
                if data:
                    response = requests.delete(url, headers=headers, json=data)
                else:
                    response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f'Invalid method: {method}')

        except requests.exceptions.RequestException as e:
            # Handle any exceptions that may occur during the request
            raise Exception(f'Request error: {e}') from e

        # Check if the request was successful (status code 200 or 201)
        if response.status_code in [200, 201]:
            # Parse the JSON response
            response_data = response.json()

            # Return the data
            return response_data
        else:
            # If the request was not successful, raise an exception
            raise Exception(f'Request failed with status code {response.status_code}') from None

    def get_data(self, end_point: str, parameters: dict | None = None) -> Any:
        return self._send_request('GET', end_point, parameters=parameters)

    def post_data(self, end_point: str, data: dict | None = None) -> Any:
        return self._send_request('POST', end_point, data=data)

    def delete_data(self, end_point: str, data: dict | None = None) -> Any:
        return self._send_request('DELETE', end_point, data=data)


# Example usage:
if __name__ == '__main__':
    # Create an instance of the RestClient
    client = RestClient.from_config()

    the_end_point = 'tokens/1/0xdAC17F958D2ee523a2206206994597C13D831ec7'

    try:
        # Make a GET request and get the data
        received_data = client.get_data(the_end_point, None)

        # Now you can work with the data
        print('Data received from the API:')
        print(received_data)
    except Exception as e:
        print(f'An error occurred: {e}')
