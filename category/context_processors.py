# It takes request as on argument and returns dictonary as response
from .models import Category

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)
