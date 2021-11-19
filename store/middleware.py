import json
class CartSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        #initialize cart object for anonymous session
        if not request.user.is_authenticated:
            if not request.session.get('cart'):
                cart = {"num_items":0,"shipping":False,"total":0,"items":[]}
                request.session['cart'] = json.dumps(cart)
  

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
