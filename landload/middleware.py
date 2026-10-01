from django.shortcuts import redirect
from django.urls import reverse_lazy,resolve

class LocationRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.setup_location_url = reverse_lazy('landload:setup_location') 

    def __call__(self, request):
        user = request.user

        current_route_name = None
        try:
            current_route_name = resolve(request.path_info).view_name
        except:
            pass

        # Only redirect Landload users with no country and not already on the setup page
        if (
            user.is_authenticated and
            str(getattr(user, 'role', '')).lower() == 'landload' and
            not getattr(user, 'country', None) and
            current_route_name != 'landload:setup_location'
        ):
            return redirect(self.setup_location_url)

        return self.get_response(request)
