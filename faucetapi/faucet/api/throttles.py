import json

from rest_framework.throttling import UserRateThrottle


class ReceiverAddressBurstRateThrottle(UserRateThrottle):
    """
    The UserRateThrottle will throttle users to a given rate of requests across the API.
    The user id is used to generate a unique key to throttle against.
    Unauthenticated requests will fall back to using the IP address of the incoming request
    to generate a unique key to throttle against.
    """
    scope = 'receiver_burst'

    def get_cache_key(self, request, view):
        if request.data:
            #data = json.loads(request.data.decode('utf-8'))
            receiver_address = request.data.get('receiver_address')
            if receiver_address:
                return f'throttle_{self.scope}_{receiver_address}'
        return super().get_cache_key(request, view)


class UserIPBurstRateThrottle(UserRateThrottle):
    scope = 'user_ip_burst'

