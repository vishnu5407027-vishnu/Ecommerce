from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.utils.timezone import now
from shop.models import Product
from accounts.models import Address
from .forms import CheckoutForm

from django.core.mail import EmailMessage
from .utils import generate_invoice_pdf

from django.http import JsonResponse
import json

import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# -------------------------
# CART SESSION HELPERS
# -------------------------

def _get_cart(request):
    return request.session.get("cart", {})


def _save_cart(request, cart):
    request.session["cart"] = cart
    request.session.modified = True


# -------------------------
# CART OPERATIONS
# -------------------------

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)

    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    _save_cart(request, cart)

    return redirect("cart:cart_detail")


def remove_from_cart(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    _save_cart(request, cart)

    return redirect("cart:cart_detail")


def update_cart(request, product_id):
    cart = request.session.get("cart", {})

    data = json.loads(request.body)
    action = data.get("action")

    if action == "plus":
        cart[str(product_id)] += 1

    elif action == "minus":
        cart[str(product_id)] -= 1
        if cart[str(product_id)] <= 0:
            del cart[str(product_id)]

    elif action == "delete":
        del cart[str(product_id)]

    request.session["cart"] = cart
    return JsonResponse({"status":"ok"})




    # cart = _get_cart(request)
    # qty = int(request.POST.get("quantity", 1))
    #
    # if qty <= 0:
    #     cart.pop(str(product_id), None)
    # else:
    #     cart[str(product_id)] = qty
    #
    # _save_cart(request, cart)
    #
    # return redirect("cart:cart_detail")


# -------------------------
# CART DETAIL
# -------------------------

def cart_detail(request):
    cart = _get_cart(request)
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    cart_items = []
    total = 0

    for product in products:
        qty = cart.get(str(product.id))
        price = product.discount_price or product.price
        subtotal = qty * price
        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": qty,
            "subtotal": subtotal
        })

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total
    })
# -------------------------
# BUY NOW
# -------------------------

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    qty = 1
    # Prepare a single-item cart structure
    cart_items = [{
        "product_id": product.id,
        "name": product.name,
        "price": float(product.discount_price or product.price),
        "quantity": qty,
        "subtotal": float((product.discount_price or product.price) * qty),
    }]
    total = sum(item["subtotal"] for item in cart_items)

    # Save to session (used by checkout)
    # request.session['checkout_data'] = {
    #     "cart_items": cart_items,
    #     "total": float(total),
    #     "shipping_address_id": request.session.get("shipping_address_id"),
    # }
    #
    # # Redirect to checkout page
    # return redirect('cart:checkout')
    #

    if request.method == "POST":
        form = CheckoutForm(request.user, request.POST)
        if form.is_valid():

            saved_address = form.cleaned_data.get("saved_address")

            if saved_address:
                shipping_address = saved_address
            else:
                shipping_address = Address.objects.create(
                    user=request.user,
                    full_name=form.cleaned_data["full_name"],
                    phone=form.cleaned_data["phone"],
                    address_line_1=form.cleaned_data["address_line_1"],
                    address_line_2=form.cleaned_data["address_line_2"],
                    city=form.cleaned_data["city"],
                    state=form.cleaned_data["state"],
                    postal_code=form.cleaned_data["postal_code"],
                    country=form.cleaned_data["country"],
                )

            # ✅ Store everything in session for payment step
            request.session["checkout_data"] = {
                "cart_items": cart_items,
                "total": float(total),
                "shipping_address_id": shipping_address.id,
            }

            return redirect("cart:payment_page")

    else:
        form = CheckoutForm(request.user)

    return render(request, "buynow_checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "form": form,
    })




    # GET fallback
# -------------------------
# CHECKOUT
# -------------------------

@login_required
def checkout(request):
    cart = _get_cart(request)

    if not cart:
        return redirect("cart:cart_detail")

    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    cart_items = []
    total = 0

    for product in products:
        qty = cart.get(str(product.id))
        price = product.discount_price or product.price
        subtotal = qty * price
        total += subtotal

        cart_items.append({
            "product_id": product.id,
            "name": product.name,
            "price": float(price),
            "quantity": qty,
            "subtotal": float(subtotal)
        })

    if request.method == "POST":
        form = CheckoutForm(request.user, request.POST)
        if form.is_valid():

            saved_address = form.cleaned_data.get("saved_address")

            if saved_address:
                shipping_address = saved_address
            else:
                shipping_address = Address.objects.create(
                    user=request.user,
                    full_name=form.cleaned_data["full_name"],
                    phone=form.cleaned_data["phone"],
                    address_line_1=form.cleaned_data["address_line_1"],
                    address_line_2=form.cleaned_data["address_line_2"],
                    city=form.cleaned_data["city"],
                    state=form.cleaned_data["state"],
                    postal_code=form.cleaned_data["postal_code"],
                    country=form.cleaned_data["country"],
                )

            # ✅ Store everything in session for payment step
            request.session["checkout_data"] = {
                "cart_items": cart_items,
                "total": float(total),
                "shipping_address_id": shipping_address.id,
            }

            return redirect("cart:payment_page")

    else:
        form = CheckoutForm(request.user)

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "form": form,
    })



@login_required
def payment_page(request):
    checkout_data = request.session.get("checkout_data")

    if not checkout_data:
        return redirect("cart:cart_detail")

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        # If Cash on Delivery → Complete Order Immediately
        if payment_method == "cod":
            cart_items = checkout_data["cart_items"]
            total = checkout_data["total"]
            shipping_address = Address.objects.get(
                id=checkout_data["shipping_address_id"]
            )

            # Generate PDF
            payment_method = "Cash on Delivery"

            pdf_file = generate_invoice_pdf(
                request.user,
                cart_items,
                total,
                shipping_address,
                payment_method
            )
            # Send Email
            email = EmailMessage(
                subject="Order Confirmed - Cash on Delivery",
                body="Your order has been placed successfully (Cash on Delivery). Invoice attached.",
                to=[request.user.email],
            )

            email.attach("invoice.pdf", pdf_file.read(), "application/pdf")
            email.send()

            # Clear session
            request.session["cart"] = {}
            request.session["checkout_data"] = {}
            request.session.modified = True

            return redirect("cart:checkout_success")

        # For other payments (demo)
        return redirect("cart:payment_success")

    return render(request, "payment.html", {
        "total": checkout_data["total"]
    })


@login_required
def payment_success(request):
    checkout_data = request.session.get("checkout_data")
    payment_method = request.session.get('payment_method', 'Unknown')


    if not checkout_data:
        return redirect("cart:cart_detail")

    cart_items = checkout_data["cart_items"]
    total = checkout_data["total"]
    shipping_address = Address.objects.get(
        id=checkout_data["shipping_address_id"]
    )

    # ✅ Generate PDF
    pdf_file = generate_invoice_pdf(
        request.user,
        cart_items,
        total,
        shipping_address,
        payment_method
    )

    # ✅ Send Email
    email = EmailMessage(
        subject="Payment Successful - Invoice",
        body="Your payment was successful. Please find your invoice attached.",
        to=[request.user.email],
    )

    email.attach("invoice.pdf", pdf_file.read(), "application/pdf")
    email.send()

    # ✅ Clear cart & checkout session
    request.session["cart"] = {}
    request.session["checkout_data"] = {}
    request.session.modified = True

    return redirect("cart:checkout_success")



# -------------------------
# SUCCESS PAGE
# -------------------------

def checkout_success(request):
    return render(request, "checkout_success.html")