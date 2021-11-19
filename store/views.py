from django.shortcuts import render
from .models import *
import json
from django.http import HttpResponse
import datetime
import uuid
from decimal import Decimal
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
            cart = json.loads(request.session['cart'])
            context["cart_items"] = cart['num_items']
        except KeyError:
            context["cart_items"] = 0

        # try:
        #     cart = json.loads(request.COOKIES['cart'])  
        # except KeyError:
        #     cart = {"num_items":0,"items":[]}

        # context['cart_items'] = cart['num_items']

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
            cart = json.loads(request.session['cart'])
            cart_items = cart['num_items']
        except KeyError:
            cart_items = 0
        # try:
        #     cart = json.loads(request.COOKIES['cart'])
        #     cart_items = cart['num_items']  
        # except KeyError:
        #     cart = {"num_items":0,"items":[]}
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
        try:
            cart = json.loads(request.session['cart'])
            cart_items = cart["num_items"]
            cart_total = Decimal(cart["total"])

            shipping = cart["shipping"]
            items = []
            for item in cart['items']:
                product = Product.objects.get(id=item['id'])
                item_total = product.price * item['quantity']
                i = {'product':product,'quantity':item['quantity'],'get_total':item_total}
                items.append(i)
        except KeyError:
            cart_items = 0
            cart_total = 0
            items = []
            shipping = False

        # cart_items = 0
        # cart_total = 0
        # items = []
        # shipping = False
        # try:
        #     cart = json.loads(request.COOKIES['cart'])  
        # except KeyError:
        #     cart = {"num_items":0,"items":[]}

        # cart_items = cart['num_items']
        # # loop through cart items
        # for item in cart['items']:
        #     product = Product.objects.get(id=item['id'])
        #     if not product.digital:
        #         shipping = True
        #     item_total = product.price * item['quantity']
        #     cart_total += item_total
        #     i = {'product':product,'quantity':item['quantity'],'get_total':item_total}
        #     items.append(i)

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
        try:
            cart = json.loads(request.session['cart'])
            cart_items = cart["num_items"]
            cart_total = cart["total"]
            shipping = cart["shipping"]
            items = []
            for item in cart['items']:
                product = Product.objects.get(id=item['id'])
                item_total = product.price * item['quantity']
                i = {'product':product,'quantity':item['quantity'],'get_total':item_total}
                items.append(i)
        except KeyError:
            cart_items = 0
            cart_total = 0
            items = []
            shipping = False
        # cart_total = 0
        # cart_items = 0
        # shipping = False
        # items = []
        # try:
        #     cart = json.loads(request.COOKIES['cart'])  
        # except KeyError:
        #     cart = {"num_items":0,"items":[]}

        # cart_items = cart['num_items']
        # # loop through cart items
        # for item in cart['items']:
        #     product = Product.objects.get(id=item['id'])
        #     if not product.digital:
        #         shipping = True
        #     item_total = product.price * item['quantity']
        #     cart_total += item_total
        #     i = {'product':product,'quantity':item['quantity'],'get_total':item_total}
        #     items.append(i)
   
    context = {'items':items, 'cart_total':cart_total, 'cart_items':cart_items,'shipping':shipping}
    return render(request,'store/checkout.html',context)
       

def updateItem(request):
    data = json.loads(request.body)
    product_id = data['productId']
    action = data['action']
    product = Product.objects.get(id=product_id)
    
    if request.user.is_authenticated:
        customer = request.user.customer  
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        order_item, created = OrderItem.objects.get_or_create(product=product,order=order)
        
        if action == "add":
            order_item.quantity = order_item.quantity+1
        elif action == "remove":
            order_item.quantity = order_item.quantity - 1
        
        order_item.save()
        if order_item.quantity <=0 :
            order_item.delete()
    else:
        try:
            cart = json.loads(request.session['cart'])
            print(cart)
            num_items = cart["num_items"]
            total = Decimal(cart["total"])
            shipping = cart["shipping"]
            items = cart['items']

            if action == "add":
                total+=product.price
                num_items+=1
                found=False
                for item in items:
                    if item['id'] == product_id:
                        item['quantity']+=1
                        found=True
                if not found:
                    items.append({"id":product_id,"quantity":1})
                if not product.digital and not shipping:
                    shipping = True
            elif action == "remove":
                total-=product.price
                num_items-=1
                last=False
                for item in items:
                    if item['id'] == product_id:
                        if item['quantity'] <= 1:
                            last=True
                        else:
                            item['quantity']-=1
                if last:
                    items = [item for item in items if item['id']!=product_id]
                    for item in items:
                        product = Product.objects.get(id=item['id'])
                        if not product.digital and not shipping:
                            shipping = True 
                            break
            cart = {"num_items":num_items,"shipping":shipping,"total":str.format("{:.2f}",total),"items":items}
            request.session['cart'] = json.dumps(cart)
           
        except KeyError:
           return HttpResponse("Cart Updated",status=400)

    return HttpResponse("Cart Updated",status=200)

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

    return HttpResponse("Process complete", status=200)


