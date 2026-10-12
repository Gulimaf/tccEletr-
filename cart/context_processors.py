from .cart import Cart

#create context processor so our Cart can work on all pages of the site
def cart(request):
    #return the degault data from our cart
    return {'cart': Cart(request)}