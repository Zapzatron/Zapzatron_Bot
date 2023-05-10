import random

import lxml.html as lh
import requests

from ..Free_Proxy.errors import FreeProxyZapzatronException


class FreeProxy:
    """
    The FreeProxy class retrieves proxies from the following sites, checking that they work:
    <https://www.sslproxies.org/>; <https://free-proxy-list.net/uk-proxy.html>;
    <https://www.us-proxy.org/>;   <https://free-proxy-list.net>.
    You can filter proxies by country, acceptable timeout, anonymity and encryption protocol.
    You can also shuffle the proxy list so that the script finds the first working proxy.
    You can also select a site to check the proxy.
    """

    def __init__(self, country_id=None, timeout=0.5, rand=False, anonym=False,
                 elite=False, google=None, https=False, site_to_check="www.google.com",
                 repeat_count_max=2, black_list=[]):
        self.country_id = country_id
        self.timeout = timeout
        self.random = rand
        self.anonym = anonym
        self.elite = elite
        self.google = google
        self.schema = 'https' if https else 'http'
        self.website = f'{self.schema}://{site_to_check}'
        self.repeat_count_max = repeat_count_max
        self.black_list = black_list

    def get_proxy_list(self, repeat_count):
        try:
            page = requests.get(self.__website(repeat_count))
            doc = lh.fromstring(page.content)
        except requests.exceptions.RequestException as e:
            raise FreeProxyZapzatronException(f"{e} Site: {self.__website(repeat_count)}")
        try:
            tr_elements = doc.xpath('//*[@id="list"]//tr')
            proxy_list_tuple = []
            for i in range(1, len(tr_elements)):
                if self.__criteria(tr_elements[i]):
                    proxy_list_tuple.append((f"{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}", tr_elements[i]))
            return proxy_list_tuple
        except Exception as e:
            FreeProxyZapzatronException(e)

    def __website(self, repeat_count):
        if repeat_count % 2 == 0:
            return "https://free-proxy-list.net"
        elif self.country_id == ['US']:
            return 'https://www.us-proxy.org'
        elif self.country_id == ['GB']:
            return 'https://free-proxy-list.net/uk-proxy.html'
        else:
            return 'https://www.sslproxies.org'

    def __criteria(self, row_elements):
        country_criteria = True if not self.country_id else str(row_elements[2].text_content()) in self.country_id
        elite_criteria = True if not self.elite else 'elite' in str(row_elements[4].text_content())
        anonym_criteria = True if (not self.anonym) or self.elite else 'anonymous' == str(row_elements[4].text_content())
        switch = {'yes': True, 'no': False}
        google_criteria = True if self.google is None else self.google == switch.get(str(row_elements[5].text_content()))
        https_criteria = True if self.schema == 'http' else str(row_elements[6].text_content()).lower() == 'yes'
        return country_criteria and elite_criteria and anonym_criteria and google_criteria and https_criteria

    def get(self, repeat_count=1):
        """Returns a working proxy that matches the specified parameters."""
        print(f"Попытка найти прокси {repeat_count}")
        proxy_list_tuple = self.get_proxy_list(repeat_count)

        if self.random:
            random.shuffle(proxy_list_tuple)

        if not proxy_list_tuple:
            raise FreeProxyZapzatronException('There are no working proxies at this time.')

        for proxy_address in proxy_list_tuple:
            proxies = {self.schema: f'http://{proxy_address[0]}'}
            try:
                ip_port = proxies[self.schema].split(':')[1:]
                # print(ip_port, ip_port[0][2:] + ":" + ip_port[1])
                if (ip_port[0][2:] + ":" + ip_port[1]) not in self.black_list:
                    ip = ip_port[0][2:]
                    with requests.get(self.website, proxies=proxies, timeout=self.timeout, stream=True) as r:
                        if r.raw.connection.sock and r.raw.connection.sock.getpeername()[0] == ip:
                            return proxies[self.schema], proxy_address[1]
                else:
                    # print("45.61.187.67:4007", flush=True)
                    pass
            except requests.exceptions.RequestException:
                pass

        if repeat_count and repeat_count < self.repeat_count_max:
            return self.get(repeat_count=(repeat_count + 1))
        raise FreeProxyZapzatronException('There are no working proxies at this time.')
