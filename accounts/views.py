from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from carts.models import Cart,CartItem
from carts.views import _cart_id
import requests

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            #user activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message =  render_to_string('accounts/account_verification_email.html', {
            'user' :  user,
            'domain' : current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)), #encoding the userid(primary key) with this
            'token': default_token_generator.make_token(user), # this one geneate a token , make token create a token for this particular user
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            #messages.success(request,'Thanks for registring. Kindly verify your account by completing the verification email')
            return redirect('/accounts/login/?command=verification='+email)
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email=request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email,password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart) # gives all the cart items that are assigned to cart id

                    product_variation=[]
                    #getting the product variation
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation)) # by default, above variation is a queryset, so we are converting to ex_var_list
                    # get cart items from user to access his variation list
                    cart_item = CartItem.objects.filter( user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    # Here, product_variation =[1,2,4,5,7] and ex_var_list =[3,5,1] , so we have comman elements in both lists, we need to compare and increase the cart_count

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index=ex_var_list.index(pr) # we are fetching the index of pr in product varaition
                            item_id=id[index] # getting the item
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user=user # assigning the user to the cart item which we are adding to exiting cart of logged in user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(product=product, user=user)
                            for item in cart_item:
                                item.user=user
                                item.save()

            except:
                pass
            auth.login(request,user)
            messages.success(request, 'You are now logged in')
            url=requests.META.get('HTTP_REFERER')
            try:
                query=requests.utils.url_parse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)

            except:
                return redirect('home')
        else:
            messages.error(request,'Invalid login credentials. ')
            return redirect('login')
    return render(request,'accounts/login.html')

@login_required(login_url ='login') # check's whether already a user logged in or not
def logout(request):
    auth.logout(request)
    messages.success(request,'you are logged out')
    return redirect('login')



def activate(request,uidb64,token):
    try:
        uid  = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,Account.DoesNotExist,OverFlowError):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,"Congratulations, Your account is activated.")
        return redirect('login')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')


@login_required(login_url ='login')
def dashboard(request):
    return render(request,'accounts/dashboard.html')


def forgotPassword(request):

    if request.method == 'POST':
        email=request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email) #email__exact - checks whether the email entered by user is exact one in DB or not

            current_site = get_current_site(request)
            mail_subject = 'Password RESET'
            message =  render_to_string('accounts/reset_password_email.html', {
            'user' :  user,
            'domain' : current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)), #encoding the userid(primary key) with this
            'token': default_token_generator.make_token(user), # this one geneate a token , make token create a token for this particular user
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request,"Password reset mail has been sent")

            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid # to access the session later so we are using and saving uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid') # getting the uid which is shared in session object
            user = Account.objects.get(pk=uid)
            user.set_password(password) # set_password is in built function in django which will store the hashed value of password in the DB
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')
