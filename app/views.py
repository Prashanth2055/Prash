from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .models import Contact, Blogs
# Below import is done for sending emails
from django.conf import settings
from django.core.mail import send_mail
from django.core import mail 
from django.core.mail.message import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from project.tokens import account_activation_token
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import make_password


# Create your views here.
def home(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == "POST":
        fname = request.POST.get("name")
        femail = request.POST.get("email")
        fphone = request.POST.get("phone")
        fdescription = request.POST.get("desc")
        query = Contact(name=fname,email=femail,phone=fphone,description=fdescription)
        query.save()
        #Email sending starts from here
        from_email = settings.EMAIL_HOST_USER
        connection = mail.get_connection()
        connection.open()
        email_message = mail.EmailMessage(f'Email from {fname}', f"User Email: {femail}\nUser Phone Number: {fphone}\n\n\nQuery: {fdescription}", from_email ,
        ['prashanthgun1999@gmail.com','prashanthgun2000@gmail.com'], connection=connection)
        email_client = mail.EmailMessage('Response'," Thanks for contacting us \n\n Prashanth \n 987654321", from_email ,
        [femail], connection=connection)
        connection.send_messages([email_message, email_client])
        connection.close()
        messages.info(request, "Thanks for contacting. We will get back to you soon..")
        return redirect('/contact/')
    return render(request, 'contact.html')

def handlelogin(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            uname = request.POST.get("username")
            password = request.POST.get("password")
            myuser = authenticate(username=uname,password=password)
            if myuser is not None:
                login(request, myuser)
                messages.success(request,"Login Success")
                return redirect('/')
            else:
                messages.error(request,"Invalid Credentials")
                return redirect('/login/')
        return render(request, 'login.html')

def handlesignup(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method=="POST":
            uname=request.POST.get("username")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email=request.POST.get("email")
            password=request.POST.get("password1")
            confirmpassword=request.POST.get("password2")
            # print(uname,email,password,confirmpassword)
            if password!=confirmpassword:
                messages.warning(request,"Password is Incorrect")
                return redirect('/signup')


            try:
                if User.objects.get(username=uname):
                    messages.info(request,"UserName Is Taken")
                    return redirect('/signup/')
            except:
                pass
            try:
                if User.objects.get(email=email):
                    messages.info(request,"Email Is Taken")
                    return redirect('/signup/')
            except:
                pass
        
            myuser = User.objects.create_user(username=uname, first_name=first_name, last_name=last_name, email=email, password=password)
            myuser.is_active = False  # Deactivate user until email confirmation
            myuser.save()

            current_site = get_current_site(request)
            mail_subject = "Activate your account"
            message = render_to_string("account_activation_email.html",{
                "user" : myuser,
                "domain" : current_site.domain,
                "uid" : urlsafe_base64_encode(force_bytes(myuser.pk)),
                "token" : account_activation_token.make_token(myuser)
                })
            to_email = email
            email_message = EmailMessage(
                    mail_subject,message,to=[to_email]
                )
            email_message.send()
            messages.success(request,"Signup Success Please check your email to compelete the registration")
            return redirect('/login/')      
        return render(request,'signup.html')


def handlelogout(request):
    logout(request)
    messages.info(request, "Logout Success")
    return redirect ('/login')

def handleblog(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Hey just login and use my website")
        return redirect('/login/')
    else:
        allposts = Blogs.objects.all()
        context = {'posts' : allposts}
        return render(request, 'blog.html', context)
    

def search(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Hey just login and use my website")
        return redirect('/login/')
    else:
        query = request.GET['search']
        if len(query) > 100:
            allPosts = Blogs.objects.none()
        else:
            allPostsTitle = Blogs.objects.filter(title__icontains=query)
            allPostsDescription = Blogs.objects.filter(description__icontains=query)
            allPosts = allPostsTitle.union(allPostsDescription)
        if allPosts.count() == 0:
            messages.warning(request, "No Post Found")
        parameters = {'posts' : allPosts, 'query' : query }

        return render(request,'search.html', parameters)


def services(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Hey just login and use my website")
        return redirect('/login/')
    else:
        return render(request,'services.html')

def activate(request, uidb64, token):
    User = get_user_model()

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None 
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request,user)

        messages.success(request, "Your account has been sucessfully activated")
        return redirect(reverse("handlelogin"))
    else:
        messages.error(request, "Activation link is invalid or expired.")
        return redirect("home")

@login_required
def update_profile(request):
    if request.method == "POST":
        user = request.user
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        new_email = request.POST.get("email")

        if new_email != user.email:
            if User.objects.filter(email=new_email).exclude(username=user.username).exists():
                messages.error(request,"Email is already in use by another account")
                return redirect("profile")
            
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_link = request.build_absolute_uri(
                reverse("confirm_email_update", kwargs={"uidb64":uid, "token":token , "new_email" : new_email})
            )

            mail_subject = "Confirm Your Email Change"
            message = render_to_string("email_verification.html", {
                "user" : user,
                "verification_link" : verification_link
            })
            email_message = EmailMessage(mail_subject,message, to=[new_email])
            email_message.send()

            messages.info(request, "A verification email has been sent to your new email address. Please confirm to update")
            return redirect("profile")
        
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        messages.success(request, 'Your profile has been updated successfully')
        return redirect("profile")
    
    return render(request,'profile.html')

def resetpassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            current_site = get_current_site(request)
            mail_subject = "Password Reset Request"
            message = render_to_string("password_reset_email.html", {
                "user" : user ,
                "domain" : current_site.domain ,
                "uid" : urlsafe_base64_encode(force_bytes(user.pk)),
                "token" : default_token_generator.make_token(user),
            }) 
            email_message = EmailMessage(mail_subject,message, to=[email])
            email_message.send()
            messages.success(request, "Password reset link has been sent to your email.")
        else:
            messages.error(request, "No account found with this email.")
    return render(request, 'password_reset.html')


def manual_password_reset_confirm(request, uidb64, token):
    if request.user.is_authenticated:
        messages.warning(request,"You have already logged in")
        return redirect('/')
    else:
        try:
            # Decode user ID
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            user = None

        # Check if the token is valid
        if user is not None and default_token_generator.check_token(user, token):
            if request.method == "POST":
                new_password1 = request.POST.get("new_password1")
                new_password2 = request.POST.get("new_password2")

                if new_password1 and new_password1 == new_password2:
                    user.password = make_password(new_password1)
                    user.save()
                    messages.success(request, "Your password has been reset successfully.")
                    return redirect("handlelogin")  # Redirect to login page
                else:
                    messages.error(request, "Passwords do not match. Try again.")

            return render(request,"password_reset_confirm.html", {"validlink": True})

        return render(request,"password_reset_confirm.html", {"validlink": False})

@login_required
def confirm_email_update(request,uidb64,token,new_email):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.email = new_email
        user.save()
        messages.success(request, "Your email has been updated successfully!")
        return redirect("profile")
    else:
        messages.error(request, "Email verification link is invalid or expired.")
        return redirect("profile")