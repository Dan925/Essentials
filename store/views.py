from django.shortcuts import render
from .models import *
import json
from django.http import JsonResponse
import datetime
import uuid

def store(request):
    products = Product.objects.all()
    context = { 'products':products,'cart_items':0}
    if request.user.is_authenticated:
        customer = request.user.customer    
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        cart_items = order.get_cart_items
        context['cart_items'] = cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])  
        except KeyError:
            cart = {"num_items":0,"items":[]}

        context['cart_items'] = cart['num_items']

    return render(request,'store/store.html',context)

def detail(request,pk):
    id=pk
    name=""
    description=""
    price=0
    image_url="#"
    cart_items=0
    reviews = []
    review_count = 0
    try:
       product= Product.objects.get(pk=pk)
       name = product.name
       price = product.price
       image_url = product.imageURL
       description = product.description
       reviews = product.reviews.all()
       review_count = reviews.count()
    except:
        pass
    
    if request.user.is_authenticated:
        customer = request.user.customer    
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        cart_items = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
            cart_items = cart['num_items']  
        except KeyError:
            cart = {"num_items":0,"items":[]}
    context = {"cart_items":cart_items,"id":id,"name":name,"description":description,"price":price,"image_url":image_url,"reviews":reviews,"review_count":review_count}
    return render(request,'store/detail.html',context)

    
def cart(request):
    
    if request.user.is_authenticated:
        customer = request.user.customer  
        order,created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
        cart_total = order.get_cart_total
        shipping = order.shipping
    else:
        cart_items = 0
        cart_total = 0
        items = []
        shipping = False
        try:
            cart = json.loads(request.COOKIES['cart'])  
        except KeyError:
            cart = {"num_items":0,"items":[]}

        cart_items = cart['num_items']
        # loop through cart items
        for item in cart['items']:
            product = Product.objects.get(id=item['id'])
            if not product.digital:
                shipping = True
            item_total = product.price * item['quantity']
            cart_total += item_total
            i = {'product':product,'quantity':item['quantity'],'get_total':item_total}
            items.append(i)

    context = {'items':items, 'cart_total':cart_total, 'cart_items':cart_items,'shipping':shipping}
    return render(request,'store/cart.html',context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer, complete=False)
       
        items = order.orderitem_set.all()
        cart_items = order.get_cart_items
        cart_total = order.get_cart_total
        shipping = order.shipping
    else:
        cart_total = 0
        cart_items = 0
        shipping = False
        items = []
        try:
            cart = json.loads(request.COOKIES['cart'])  
        except KeyError:
            cart = {"num_items":0,"items":[]}

        cart_items = cart['num_items']
        # loop through cart items
        for item in cart['items']:
            product = Product.objects.get(id=item['id'])
            if not product.digital:
                shipping = True
            item_total = product.price * item['quantity']
            cart_total += item_total
            i = {'product':product,'quantity':item['quantity'],'get_total':item_total}
            items.append(i)
   
    context = {'items':items, 'cart_total':cart_total, 'cart_items':cart_items,'shipping':shipping}
    return render(request,'store/checkout.html',context)
       

def updateItem(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']
    
    if request.user.is_authenticated:
        customer = request.user.customer  
        product = Product.objects.get(id=product_id)
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        order_item, created = OrderItem.objects.get_or_create(product=product,order=order)
        
        if action == "add":
            order_item.quantity = order_item.quantity+1
        elif action == "remove":
            order_item.quantity = order_item.quantity - 1
        
        order_item.save()
        if order_item.quantity <=0 :
            order_item.delete()
    return JsonResponse("Cart Updated",safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
        if total == order.get_cart_total:
            order.complete = True
        order.save()
        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'])
    else:
        print("User is not logged in")

    return JsonResponse("Process complete", safe=False)


