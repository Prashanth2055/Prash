from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Contact, Blogs
# Below import is done for sending emails
from django.conf import settings
from django.core.mail import send_mail
from django.core import mail 
from django.core.mail.message import EmailMessage

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
    if request.method == "POST":
        uname = request.POST.get("username")
        password1 = request.POST.get("password1")
        myuser = authenticate(username=uname,password=password1)
        if myuser is not None:
            login(request, myuser)
            messages.success(request,"Login Success")
            return redirect('/')
        else:
            messages.error(request,"Invalid Credentials")
            return redirect('/login/')
    return render(request, 'login.html')

def handlesignup(request):
    if request.method == "POST":
        uname = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return HttpResponse("Password Incorrect")
        
        try:
            if User.objects.get(username = uname):
                return HttpResponse("Username is taken")
        except:
            pass

        try:
            if User.objects.get(email = email):
                return HttpResponse("Email is taken")
        except:
            pass

        myuser = User.objects.create_user(uname,email,password1)
        myuser.save()
        return HttpResponse("Sign up Sucessfull")
    return render(request, 'signup.html')


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