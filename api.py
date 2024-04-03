from dataclasses import dataclass
from enum import Enum
from typing import Any

from client import RestClient


class Network(Enum):
    GOERLI = 5
    SEPOLIA = 11155111
    MAINNET = 1

    @staticmethod
    def from_str(network: str) -> 'Network':
        if network.lower() == 'goerli' or network == '5':
            return Network.GOERLI
        if network.lower() == 'sepolia' or network == '11155111':
            return Network.SEPOLIA
        if network.lower() == 'mainnet' or network == '1':
            return Network.MAINNET
        raise ValueError(f'Unexpected value for describing network: {network}')

    def __str__(self) -> str:
        return str(self.value)


class TestLevel(Enum):
    ABI = 'abi'
    MINIMAL = 'minimal'
    RECOMMENDED = 'recommended'
    DESIRABLE = 'desirable'
    ADDON = 'addon'
    FINGERPRINT = 'fingerprint'
    ALL = 'all'

    @staticmethod
    def from_str(level: str) -> 'TestLevel':
        return TestLevel(level.lower())

    def __str__(self) -> str:
        return str(self.value)


class Permission(Enum):
    READ = 'READ'
    WRITE = 'WRITE'
    ADMIN = 'ADMIN'

    @staticmethod
    def from_str(permission: str) -> 'Permission':
        return Permission(permission)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class TokenInfo:
    id: str
    name: str
    address: str
    symbol: str
    decimals: str
    total_supply: str
    network: str

    @staticmethod
    def from_dict(data_dict: dict[str, str]) -> 'TokenInfo':
        required_attributes = ['id', 'name', 'address', 'symbol', 'decimals', 'totalSupply', 'network']
        try:
            for attribute in required_attributes:
                if attribute not in data_dict:
                    raise KeyError(f'Missing attribute: {attribute}')

            return TokenInfo(
                data_dict['id'],
                data_dict['name'],
                data_dict['address'],
                data_dict['symbol'],
                data_dict['decimals'],
                data_dict['totalSupply'],
                data_dict['network'],
            )
        except KeyError as e:
            raise KeyError(f'Invalid dictionary: {e}') from e


class OpenAPI:
    def __init__(self) -> None:
        self.client = RestClient.from_config()

    def _get_generic(self, endpoint: str, message: str, parameters: dict[str, str] | None = None) -> Any:
        try:
            return self.client.get_data(endpoint, parameters)
        except Exception as e:
            print(message)
            print(e)

    def _post_generic(self, endpoint: str, message: str, data: dict | None) -> Any:
        try:
            return self.client.post_data(endpoint, data=data)
        except Exception as e:
            print(message)
            print(e)

    def _delete_generic(self, endpoint: str, message: str, data: dict | None) -> Any:
        try:
            return self.client.delete_data(endpoint, data=data)
        except Exception as e:
            print(message)
            print(e)

    """
    Tokens and their Evaluations
    """

    def get_token_info(self, network: str, address: str) -> TokenInfo:
        """
        Get the information on a token from its network and address.
        """
        the_network: Network = Network.from_str(network)
        end_point = f'tokens/{the_network}/{address}'
        message = (
            f'An error occurred when retrieving info of token '
            f'on network {network}({the_network}) at address {address}'
        )
        data_dict = self._get_generic(end_point, message)
        return TokenInfo.from_dict(data_dict)

    def get_token_report(self, network: str, address: str) -> Any:
        """
        Get the latest report on a token from its network and address.
        """
        the_network: Network = Network.from_str(network)
        end_point = f'tokens/{the_network}/{address}/report'
        message = (
            f'An error occurred when retrieving report of token'
            f' on network {network} ({the_network}) at address {address}'
        )
        return self._get_generic(end_point, message)

    def get_token_evaluations(self, network: str, address: str, level: str, standard: int | None = None) -> Any:
        """
        Get the latest evaluations of a token by test level from its network and address.
        """
        the_network: Network = Network.from_str(network)
        the_level = TestLevel.from_str(level)
        end_point = f'tokens/{the_network}/{address}/levels/{str(the_level)}'
        message = (
            f'An error occurred when retrieving evaluations'
            f' of level {str(the_level)} for token on network {network} ({the_network}) at address {address}'
        )
        if standard:
            parameters = {'standard': f'ERC{standard}'}
            return self._get_generic(end_point, message, parameters)
        else:
            return self._get_generic(end_point, message)

    def get_token_test_evaluation(self, network: str, address: str, name: str, standard: int | None = None) -> Any:
        """
        Get the latest evaluation of the token by test name.
        The list of tests is available at https://ercx.runtimeverification.com/whats-being-tested.
        """
        the_network: Network = Network.from_str(network)
        end_point = f'tokens/{the_network}/{address}/tests/{name}'
        message = (
            f'An error occurred when retrieving evaluations for ERC-{standard}'
            f' of test {name} for token on network {network} ({the_network}) at address {address}'
        )
        if standard:
            parameters = {'standard': f'ERC{standard}'}
            return self._get_generic(end_point, message, parameters)
        else:
            return self._get_generic(end_point, message)

    """
    Property Tests
    """

    def get_property_tests(self, level: str = '') -> Any:
        """
        The list of tests is available at https://ercx.runtimeverification.com/whats-being-tested.
        """
        params = {'standard': 'ERC20'}
        if level != '':
            the_level = TestLevel.from_str(level)
            params['level'] = str(the_level)
        end_point = 'property-tests'
        message = f'An error occurred when retrieving property tests of level {level}'
        return self._get_generic(end_point, message, parameters=params)

    """
    Users
    """

    def get_my_info(self) -> Any:
        """
        Get the information about the logged-in user.
        """
        end_point = 'user'
        message = 'An error occurred when retrieving information about the logged-in user.'
        return self._get_generic(end_point, message)

    def get_my_token_lists(self) -> Any:
        """
        Get the token lists of the authenticated user.
        """
        end_point = 'user/token-lists'
        message = 'An error occurred when retrieving the token lists you own.'
        return self._get_generic(end_point, message)

    def get_shared_token_lists(self) -> Any:
        """
        Get the token lists shared with the authenticated user.
        """
        end_point = 'user/shared-token-lists'
        message = 'An error occurred when retrieving the token lists shared with you.'
        return self._get_generic(end_point, message)

    def get_bookmarked_tokens(self) -> Any:
        """
        Get the bookmarked tokens of the authenticated user.
        """
        end_point = 'user/bookmarked-tokens'
        message = 'An error occurred when retrieving your bookmarked tokens.'
        return self._get_generic(end_point, message)

    def get_bookmarked_tokens_count(self) -> Any:
        """
        Get the bookmarked tokens of the authenticated user.
        """
        end_point = 'user/bookmarked-tokens-count'
        message = 'An error occurred when retrieving your bookmarked tokens count.'
        return self._get_generic(end_point, message)

    """
    Token Lists
    """

    def get_token_list_info(self, list_id: str) -> Any:
        """
        Get the information of a token list by its id.
        """
        # TODO: Validate the format of the list.
        end_point = f'token-lists/{list_id}'
        message = f'An error occurred when retrieving information about token list with id {list_id}.'
        return self._get_generic(end_point, message)

    def get_tokens_of_list(self, list_id: str) -> Any:
        """
        Get the tokens of a token list by its id.
        """
        # TODO: Validate the format of the list.
        end_point = f'token-lists/{list_id}/tokens'
        message = f'An error occurred when retrieving the tokens of token list with id {list_id}.'
        return self._get_generic(end_point, message)

    def get_users_of_list(self, list_id: str) -> Any:
        """
        Get the users of a token list by its id.
        """
        # TODO: Validate the format of the list.
        end_point = f'token-lists/{list_id}/users'
        message = f'An error occurred when retrieving the users of token list with id {list_id}.'
        return self._get_generic(end_point, message)

    def get_tokens_count_of_list(self, list_id: str) -> Any:
        """
        Get the count of tokens in a token list by its id.
        """
        # TODO: Validate the format of the list.
        end_point = f'token-lists/{list_id}/tokens-count'
        message = f'An error occurred when retrieving the users of token list with id {list_id}.'
        return self._get_generic(end_point, message)

    def create_token_list(self, name: str, description: str = '') -> str:
        """
        Create a token list.
        Returns the id of the token list.
        """
        end_point = 'token-lists'
        message = f'An error occurred when creating token list of name {name}.'
        result = self._post_generic(end_point, message, {'name': name, 'description': description})
        if result:
            if 'id' in result:
                return result['id']
            else:
                print('Error. No id in the object returned when creating a list')
        return 'Error'

    def add_token_to_token_list(self, address: str, network: str, token_list: str) -> bool:
        """
        Add a token to a token list.
        Returns true if adding was successful.
        """
        the_network: Network = Network.from_str(network)
        end_point = f'token-lists/{token_list}/tokens'
        message = (
            f'An error occurred when adding a token at address {address}'
            f' on network {the_network} to list of id {token_list}.'
        )
        result = self._post_generic(end_point, message, data={'address': address, 'network': the_network.value})
        return result

    def remove_token_from_token_list(self, address: str, network: str, token_list: str) -> bool:
        """
        Add a token to a token list.
        Returns true if adding was successful.
        """
        the_network: Network = Network.from_str(network)
        end_point = f'token-lists/{token_list}/tokens'
        message = (
            f'An error occurred when removing the token at address {address}'
            f' on network {the_network} to list of id {token_list}.'
        )
        result = self._delete_generic(end_point, message, data={'address': address, 'network': the_network.value})
        return result

    def share_token_list_with_user(self, user_id: str, permission: str, token_list_id: str) -> Any:
        """
        Add a user to a token list with some permission.
        """
        the_permission = Permission.from_str(permission)
        end_point = f'token-lists/{token_list_id}/users'
        message = (
            f'An error occurred when providing permission {str(the_permission)} '
            f'to user of id {user_id} for list {token_list_id}'
        )
        result = self._post_generic(end_point, message, data={'userId': user_id, 'permission': the_permission.value})
        return result

    def unshare_token_list_with_user(self, user_id: str, token_list_id: str) -> Any:
        """
        Remove a user from a token list.
        """
        end_point = f'token-lists/{token_list_id}/users/{user_id}'
        message = f'An error occurred when removing user of id {user_id} for list {token_list_id}'
        result = self._delete_generic(end_point, message, None)
        return result


def example_get_requests(api: OpenAPI) -> None:
    # Get my info
    my_info = api.get_my_info()
    print(my_info)
    # Get token info
    token_info = api.get_token_info(the_network, tether_address)
    print(token_info)
    # Get token report
    token_report = api.get_token_report(the_network, tether_address)
    print(token_report)
    # Get token evaluations
    token_evaluations = api.get_token_evaluations(the_network, tether_address, 'minimal')
    print(token_evaluations)
    # Get token test result
    token_test_result = api.get_token_test_evaluation(the_network, tether_address, 'testPositiveApprovalEventEmission')
    print(token_test_result)
    # Get all property tests
    property_tests = api.get_property_tests()
    print(property_tests)
    # Get property tests of level minimal
    property_tests_minimal = api.get_property_tests('minimal')
    print(property_tests_minimal)
    # Get the token lists of the user
    token_lists = api.get_my_token_lists()
    print(token_lists)
    # Get the token lists shared with the user
    token_lists_shared = api.get_shared_token_lists()
    print(token_lists_shared)
    # Get the bookmarked tokens of the user
    bookmarked_tokens = api.get_bookmarked_tokens()
    print(bookmarked_tokens)
    # Get the count of bookmarked tokens of the user
    bookmarked_tokens_count = api.get_bookmarked_tokens_count()
    print(bookmarked_tokens_count)
    # Get the information on a token list by its id
    id = '228856f0-7e27-47cf-aea6-978e814f7f1b'
    token_list_info = api.get_token_list_info(id)
    print(token_list_info)
    # Get the tokens of a token list by its id
    tokens = api.get_tokens_of_list(id)
    print(tokens)
    # Get the users of a token list by its id
    users = api.get_users_of_list(id)
    print(users)
    # Get the count of tokens of a token list by its id
    count = api.get_tokens_count_of_list(id)
    print(count)


def examples_post_requests(api: OpenAPI) -> None:
    # Create a token list
    name = 'My token list'
    description = 'My token list description'
    id = api.create_token_list(name, description)
    print(id)
    # Add token to list
    success_add = api.add_token_to_token_list(tether_address, tether_network, my_list)
    print(success_add)
    # Share a token list
    user = api.share_token_list_with_user(some_other_user, 'WRITE', my_list)
    print(user)


def examples_delete_requests(api: OpenAPI) -> None:
    # Delete token from list
    success_delete = api.remove_token_from_token_list(tether_address, tether_network, my_list)
    print(success_delete)
    # Remove user from list
    success_remove = api.unshare_token_list_with_user(some_other_user, my_list)
    print(success_remove)


def launch_requests() -> None:
    my_api = OpenAPI()
    # Launch get requests
    example_get_requests(my_api)
    # Launch post requests
    examples_post_requests(my_api)
    # Launch delete requests
    examples_delete_requests(my_api)


tether_address = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
tether_network = '1'
my_list = 'my-token-list-1694605502'
the_network = 'Mainnet'
some_other_user = '101185369'


if __name__ == '__main__':
    launch_requests()
    api = OpenAPI()
    info = api.get_token_info(tether_network, tether_address)
    print(info)
