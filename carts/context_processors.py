from .models import Cart,CartItem
from .views import _cart_id

# Here, we will write the logic and declare in settings file and we will use this in template html files
def counter(request):
    cart_count=0
    if 'admin' in request.path:
        return {}   # inside admin user, we dont want to see anything there
    else:
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.filter(cart = cart[:1])

            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count =0
    return dict(cart_count=cart_count)
