import requests
from pprint import pprint


class BingSearch:

    @staticmethod
    def __read_bing_key():
        """
        Reads key from bing.key file
        In order to obtain one create Microsoft Azure account
        For more information: https://docs.microsoft.com/en-us/rest/api/cognitiveservices-bingsearch/
        :return: a string which is either None, i.e key not found, or with a key
        """

        bing_api_key = None
        try:
            with open('bing.key', 'r') as f:
                bing_api_key = f.readline().strip()
        except Exception:
            try:
                with open('../bing.key') as f:
                    bing_api_key = f.readline().strip()
            except Exception:
                raise IOError('bing.key file not found')

        if not bing_api_key:
            raise KeyError('Bing key not found')

        return bing_api_key

    @staticmethod
    def run_query(search_terms):
        bing_key = BingSearch.__read_bing_key()
        search_url = 'https://api.cognitive.microsoft.com/bing/v7.0/search'
        headers = {'Ocp-Apim-Subscription-Key': bing_key}
        params = {'q': search_terms, 'textDecorations': True, 'textFormat': 'HTML'}

        response = None
        is_exception_raised = True
        try:
            response = requests.get(search_url, headers=headers, params=params)
            response.raise_for_status()
            is_exception_raised = False
        except requests.exceptions.HTTPError:
            error = response.json()['error']
            print(f"Error: {error['code']} - {error['message']}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Returns empty list if an exception is raised
            if is_exception_raised:
                results = list()
                return results

        search_results = response.json()

        results = list()
        # if webPages is not in search_result there were no results
        if 'webPages' in search_results:
            for result in search_results['webPages'].get('value'):
                results.append({
                    'title': result['name'],
                    'link': result['url'],
                    'summary': result['snippet']
                })

        return results


def main():
    print("Please enter search terms: ", end='')
    search_terms = input()

    results = BingSearch.run_query(search_terms)

    for result in results:
        pprint(result)


if __name__ == '__main__':
    main()
