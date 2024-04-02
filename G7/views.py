from email.message import EmailMessage
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models  import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from LOG_IN_AND_SIGN_UP import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import  render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from G7.tokens import generate_token
from django.views.decorators.csrf import csrf_exempt
def home (request):
    return render(request, "G7/index.html")

def signup (request):
        if request.method == "POST":
            username = request.POST.get('username')
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            Pass1 = request.POST.get('Pass1')
            Pass2 = request.POST.get('Pass2')

            if User.objects.filter(username=username):
                messages.error(request,"Username already exists! Please try another one.")
                return redirect ('signup')
            if User.objects.filter(email=email):
                messages.error( request, "Email has already been registered.")
            if len(username)>10:
                 messages.error(request,'Username should be less than 10 characters')
            if Pass1 != Pass2:
                messages.error(request,'Password fields do not match')
                return redirect('home')

            myuser = User.objects.create_user(username,email,Pass1)
            myuser.first_name = fname
            myuser.last_name= lname
            myuser.email = email
            myuser.is_active = False
            myuser.save()

            messages.success(request,"Account Created Successfully!  A confimaton  link has been sent to your Email ID")
            
            # Welcome Email

            subject = "Welcome to  the G7 Group COE Project!"
            message = "Hello "+ myuser.first_name + "\nYour account has been created successfully on G7 database.\nPlease confirm yor emal to continue"
            from_email = settings.EMAIL_HOST_USER
            to_list = [myuser.email]
            send_mail(subject,message,from_email,to_list,fail_silently = True)

            # Email Address Confirmation

            current_site = get_current_site(request)
            email_subject  = "Activate your account"
            message2 = render_to_string('email_confirmation.html',{
                'name':myuser.first_name,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes (myuser.pk)),
                'token':generate_token.make_token(myuser)
            })
            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [myuser.email] if myuser.email else []
            )
            email.fail_silently = False
            email.send()


            return redirect('signin')
        
        return render(request,"G7/signup.html")
        
def signin (request):
    if request.method=="POST":
        username =  request.POST['username']
        Pass1 = request.POST['Pass1']
        user = authenticate(username=username , password=Pass1 )
        
        if user is  not None :
            login(request,user)
            fname = user.first_name
            return render(request,"G7/index.html", {'fname':fname})
        
        
        else:
          messages.error(request,'Username or Password is incorrect!')
          return redirect("home")

    return render(request, "G7/signin.html")

def signout (request):
    logout(request)
    messages.success(request,"Logged out successfully.")
    return redirect ("home")

def activate(request,uidb64,token):
    try:
        uid = force_str( urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request,'activation_failed.html')
    

