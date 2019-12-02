from datetime import timedelta, datetime
from logging import getLogger
from time import sleep

from requests import request, RequestException
from requests.auth import AuthBase

logger = getLogger(__name__)


class TokenAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Token {}'.format(self.token)
        return r


class ReRequestsException(Exception):
    pass


class ReResponse(object):
    def __init__(self, response):
        self._response = response

    def __bool__(self):
        return True

    def __getattr__(self, item):
        return getattr(self._response, item)

    def __setstate__(self, state):
        self.__dict__ = state

    def __getstate__(self):
        return self.__dict__


class ReRequests(object):
    def __init__(self, **default_kwargs):
        self.default_kwargs = default_kwargs

    def get(self, url, params=None, **kwargs):
        """Sends a GET request.

        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        return self.request('get', url, params=params, **kwargs)

    def get_or_none(self, url, params=None, **kwargs):
        return self.request_or_none('get', url, params=params, **kwargs)

    def check_get(self, url, params=None, **kwargs):
        return self.check_request('get', url, params=params, **kwargs)

    def options(self, url, **kwargs):
        """Sends a OPTIONS request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request('options', url, **kwargs)

    def options_or_none(self, url, **kwargs):
        return self.request_or_none('options', url, **kwargs)

    def check_options(self, url, **kwargs):
        return self.check_request('options', url, **kwargs)

    def head(self, url, **kwargs):
        """Sends a HEAD request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request('head', url, **kwargs)

    def head_or_none(self, url, **kwargs):
        return self.request_or_none('head', url, **kwargs)

    def check_head(self, url, **kwargs):
        return self.check_request('head', url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        """Sends a POST request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request('post', url, data=data, json=json, **kwargs)

    def post_or_none(self, url, data=None, json=None, **kwargs):
        return self.request_or_none('post', url, data=data, json=json, **kwargs)

    def check_post(self, url, data=None, json=None, **kwargs):
        return self.check_request('post', url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        """Sends a PUT request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request('put', url, data=data, **kwargs)

    def put_or_none(self, url, data=None, **kwargs):
        return self.request_or_none('put', url, data=data, **kwargs)

    def check_put(self, url, data=None, **kwargs):
        return self.check_request('put', url, data=data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        """Sends a PATCH request.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        return self.request('patch', url,  data=data, **kwargs)

    def patch_or_none(self, url, data=None, **kwargs):
        return self.request_or_none('patch', url,  data=data, **kwargs)

    def check_patch(self, url, data=None, **kwargs):
        return self.check_request('patch', url,  data=data, **kwargs)

    def delete(self, url, **kwargs):
        """Sends a DELETE request.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        return self.request('delete', url, **kwargs)

    def delete_or_none(self, url, **kwargs):
        return self.request_or_none('delete', url, **kwargs)

    def check_delete(self, url, **kwargs):
        return self.check_request('delete', url, **kwargs)

    def _format_message_basic(self, method, url, ok_status_codes, retry_status_codes, extra_log=None, **kwargs):
        return "method='{method}' url='{url}' kwargs={kwargs} ok_status_codes={ok_status_codes} retry_status_codes={retry_status_codes} extra={extra_log}".format(
            method=method,
            url=url,
            kwargs=kwargs,
            ok_status_codes=ok_status_codes,
            retry_status_codes=retry_status_codes,
            extra_log=extra_log
        )

    def _format_message_response(self, response):
        return "response_content='{response.content}' response.status_code={response.status_code}".format(
                response=response,
        )

    def _format_message_error(self, error):
        return "error={}".format(error)

    def request(self, method, url, **kwargs):
        final_kwargs = dict(self.default_kwargs)
        final_kwargs.update(**kwargs)

        ok_status_codes = final_kwargs.pop('ok_status_codes', range(200, 207))
        retry_status_codes = final_kwargs.pop('retry_status_codes', [429, 503])
        extra_log = final_kwargs.pop('extra_log', None)
        sleep_between_attempts = final_kwargs.pop('sleep_between_attempts', 0.1)
        total_timeout = final_kwargs.pop('total_timeout', None)

        final_message = basic_message = self._format_message_basic(
            method,
            url,
            ok_status_codes,
            retry_status_codes,
            extra_log=extra_log,
            **final_kwargs
        )

        start_time = datetime.now()

        while (total_timeout is None) or (start_time + timedelta(seconds=total_timeout) > datetime.now()):
            try:
                response = ReResponse(request(method, url, **final_kwargs))
            except RequestException as error:
                final_message = '{basic_message} {error_message}'.format(
                    basic_message=basic_message,
                    error_message=self._format_message_error(error)
                )
                logger.warning(final_message)

                if total_timeout is None:
                    break

                sleep(sleep_between_attempts)
                continue
            else:
                final_message = '{basic_message} {response_message}'.format(
                    basic_message=basic_message,
                    response_message=self._format_message_response(response)
                )

                if response.status_code in ok_status_codes:
                    logger.debug(final_message)
                    return response

                logger.warning(final_message)

                if response.status_code in retry_status_codes:
                    sleep(sleep_between_attempts)
                    continue
                else:
                    raise ReRequestsException(
                        "API call error: Bad response code. {final_message}".format(final_message=final_message)
                    )

        raise ReRequestsException(
            "API call error: Timeout {total_timeout}s. {final_message}".format(
                total_timeout=total_timeout,
                final_message=final_message
            )
        )

    def request_or_none(self, method, url, **kwargs):
        try:
            return self.request(method, url, **kwargs)
        except ReRequestsException as error:
            logger.error(error.args[0])
            return None

    def check_request(self, method, url, **kwargs):
        return bool(self.request_or_none(method, url, **kwargs))
