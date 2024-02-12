from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
import json
import datetime
import requests

from .models import Order, OrderItem, Product, Customer, ShippingAddress
from .utils import cookieCart, cartData, guestOrder
from django.http import JsonResponse
import shippo
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView


shippo.config.api_key = "shippo_test_6b8b4da6247bd3e14c92a515b1608c982d78a52f"
#Shippo-API
def calculate_shipping(request):
    # Get address and parcel details from the request or use dummy data
    address_from = {
        "name": "Shawn Ippotle",
        "company": "Shippo",
        "street1": "215 Clayton St.",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94117",
        "country": "US",
        "phone": "+1 555 341 9393",
        "email": "shippotle@shippo.com",
    }

    address_to = {
        "name": "Mr Hippo",
        "company": "Shippo",
        "street1": "Broadway 1",
        "city": "New York",
        "state": "NY",
        "zip": "10007",
        "country": "US",
        "phone": "+1 555 341 9393",
        "email": "mrhippo@shippo.com",
    }

    parcel = {
        "length": "5",
        "width": "5",
        "height": "5",
        "distance_unit": "in",
        "weight": "2",
        "mass_unit": "lb",
    }

    # Create a shipment
    shipment = shippo.Shipment.create(
        address_from=address_from,
        address_to=address_to,
        parcels=[parcel],
        async_shipment=False,
    )

    # Retrieve the first rate for simplicity (you may want to loop through rates)
    rate = shipment.rates[0]

    # Now you can use rate object to get label_url, tracking_number, etc.
    label_url = rate.label_url
    tracking_number = shipment.tracking_number

    return JsonResponse({"label_url": label_url, "tracking_number": tracking_number})


def loginview(request):
    error=""
    if request.method == "POST":
        u = request.POST['userName']
        p = request.POST['pwd']
        user = authenticate(userName=u, password=p)
        if user:
            try:
                user1=Customer.objects.get(user=user)
                if user1.type == "Customer":
                    login(request,user)
                    error="no"
                else:
                    error="yes"
            except:
                error="yes"
        else:
            error="yes" 
            
    d={'error':error}        
    return render(request,'store/login.html',d)


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    
    products =  Product.objects.all()
    context = {'products': products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)
   

def cart(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']             
    items = data['items']
    
    context = {'items': items, 'order': order,'cartItems':cartItems}
    # Use HttpResponse instead of HTTPResponse
    return render(request, 'store/cart.html', context)

    # if request.user.is_authenticated:
    #     customer = request.user.customer
    #     order, created= Order.objects.get_or_create(customer=customer, complete=False)
    #     items = order.orderitem_set.all()
    #     cartItems = order.get_cart_items
    # else:
    #     cookieData = cookieCart(request)
    #     cartItems = cookieData['cartItems']
    #     order = cookieData['order']
    #     items = cookieData['items']
    # context = {'items': items, 'order':order, 'cartItems':cartItems}
    # return render(request, 'store/cart.html', context)



def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']             
    items = data['items']
    
    context = {'items': items, 'order': order,'cartItems':cartItems}
    # Use HttpResponse instead of HTTPResponse
    return render(request, 'store/checkout.html', context)




def updateItem(request):
     data = json.loads(request.body)
     productId = data['productId']
     action = data['action']
     
     print('Action:', action)
     print('productId:', productId)
     
     customer= request.user.customer
     product = Product.objects.get(id=productId)
     order, create = Order.objects.get_or_create(customer=customer, complete=False)
     
     orderItem, create = OrderItem.objects.get_or_create(order=order, product=product)
     
     if action == 'add':
          orderItem.quantity = (orderItem.quantity + 1)
     elif action == 'remove':
          orderItem.quantity = (orderItem.quantity - 1)
          
     orderItem.save()
     
     if orderItem.quantity <= 0:
          orderItem.delete()
     return JsonResponse('Item was added', safe=False)

#UPDATE SIZE
def updateSize(request):
    if request.method == 'POST':
        data = request.POST
        product_id = data.get('productId')
        selected_size = data.get('selectedSize')

        # Retrieve the product from the database
        product = get_object_or_404(Product, id=product_id)

        # Update the product size
        product.size = selected_size
        product.save()

        # Return a success response
        return JsonResponse({'success': True})
    else:
        # Return an error response for unsupported HTTP methods
        return JsonResponse({'error': 'Unsupported method'}, status=405)


@csrf_exempt
def processOrder(request):
     transaction_id = datetime.datetime.now().timestamp()
     data = json.loads(request.body)
     
     if request.user.is_authenticated:
          customer = request.user.customer
          order, created = Order.objects.get_or_create(customer=customer, complete=False)
             
     else:
         customer, order = guestOrder(request, data)
              
     total = float(data['form']['total'])
     order.transaction_id = transaction_id
          
     if total == float(order.get_cart_total):
          order.complete = True
     order.save()
     
     if order.shipping == True:
          ShippingAddress.objects.create(
               customer=customer,
               order=order,
               address=data['shipping']['address'],     
               city=data['shipping']['city'],     
               state=data['shipping']['state'],     
               zipcode=data['shipping']['zipcode'],     
          )  
     return JsonResponse('Payment complete!', safe=False)

def update_cart(request, product_id):
    # Retrieve the selected size from the request
    new_size = request.GET.get('size', None)

    # Ensure the new_size is valid (add appropriate validation)
    valid_sizes = ['S', 'M', 'L', 'XL']
    if new_size not in valid_sizes:
        return JsonResponse({'error': 'Invalid size .Choose from: S, M, L, XL'}, status=400)

    # Retrieve the product from the database
    product = get_object_or_404(Product, id=product_id)

    # Update the product size
    product.size = new_size
    product.save()

    # Return a success response
    return JsonResponse({'success': True})


def AboutUs(request):
          return render(request, 'store/AboutUs.html') 
     


  