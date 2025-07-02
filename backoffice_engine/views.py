from django.shortcuts import render,redirect,get_object_or_404
import sys
from backoffice_engine.forms import *
from django.contrib import messages
from backoffice_engine.models import * 
import random
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings 
from .models import *  # ← import your plan‑details model
from .models import User  
from .forms import UserHealthForm
from .utils import get_gemini_response
from .models import Feedback
from django.contrib import messages
from .models import User, User_health, ChatHistory
from .decorators import session_login_required,bmi_required
from .models import User, User_health
from .forms import UserHealthForm
from django.http import HttpResponse

 
# Create your views here.
def index(request):
    # 1. Query all feedback, newest first
    feedbacks = Feedback.objects.all()
    
    # 2. Pass it into the template context
    return render(request, 'index.html', {
      'feedbacks': feedbacks,
      
      # … any other context you already had …
    })
def login(request):
    if request.method == 'POST':
       useremail = request.POST["email"]
       pwd = request.POST["password"]
       e = User.objects.filter(email=useremail, password=pwd).count()
       if e == 1:
           e=User.objects.get(email=useremail)
           request.session["id"]=e.id
           request.session["name"]=e.name 
           return redirect("/index/")    
       else:
            messages.error(request,"Invalid password or Email")
            return render(request,'login.html')
    else:
        return render(request,'login.html')
# profile with name , email, password ,plan which was chose by user by default will be free

def profile(request):
    user_id = request.session.get("id")
    if not user_id:
        messages.error(request, "You must be logged in to view your profile.")
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')

    # Fetch the most recent health entry, if any
# Fetch the most recent health entry, if any
    health = User_health.objects.filter(user=user).order_by('-created_id').first()

    if request.method == 'POST':
        new_name  = request.POST.get("name", user.name).strip()
        new_email = request.POST.get("email", user.email).strip().lower()

        if new_email != user.email and User.objects.filter(email=new_email).exists():
            messages.error(request, "That email is already registered.")
            return render(request, 'profile.html', {"user": user, "health": health})

        user.name  = new_name
        user.email = new_email
        user.save()
        request.session["name"] = user.name

        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    return render(request, 'profile.html', {
        "user": user,
        "health": health
    })
    

@session_login_required
def bmi_calculator_view(request):
    user_id = request.session.get('id')
    user = User.objects.get(id=user_id)

    # Fetch the most recent health entry, if any
    existing_health = User_health.objects.filter(user=user).order_by('-created_id').first()

    if request.method == 'POST':
        # Bind POST to the existing instance (if present) so we update rather than create
        form = UserHealthForm(request.POST, instance=existing_health)
        if form.is_valid():
            health = form.save(commit=False)
            health.user = user
            # Recalculate BMI
            if health.weight and health.height:
                height_m = health.height / 100.0
                health.bmi = round(health.weight / (height_m ** 2), 2)
            health.save()
            messages.success(request, "Health data saved!")
            return redirect('profile')
    else:
        # On GET, preload form with existing data or empty if none
        form = UserHealthForm(instance=existing_health)

    return render(request, 'bmi.html', {'form': form})


def about(request):
    user_count = User.objects.count()
    feedback_count = Feedback.objects.count()
    
    return render(request, 'about-us.html', {
        'user_count': user_count,
        'feedback_count': feedback_count
    })

def gallery(request):
    return render(request,'gallery.html')
def contact(request):
    return render(request,'contact.html')
def reset(request):
    if request.method == "POST":
        otp = request.POST["otp"]
        pwd = request.POST["password"]
        cpwd = request.POST["cpassword"]
        e =  request.session['temail']

        val = User.objects.filter(email=e,otp=otp,otp_used=0).count()

        if val == 1:
            
            if pwd == cpwd :
                obj = User.objects.filter(email=e).update(password=pwd,otp_used=1)   
                return redirect("/login/")
            else:
                messages.error(request,"Password and confirm password not match")
                return render(request,"reset.html")
        else:
            messages.error(request,"Invalid OTP")
            return render(request,"reset.html")
def register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, "register.html")

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")

        # Save the new user
        User.objects.create(name=name, email=email, password=password)
        return redirect("/login/")

    return render(request, "register.html")

def forgot(request):
    return render(request,'forgot.html')
def sendotp(request):
    if request.method == "POST":
        otp1 = random.randint(10000, 99999)
        e = request.POST['email']
        request.session['temail'] = e

        if User.objects.filter(email=e).exists():
            # Save OTP in DB
            User.objects.filter(email=e).update(otp=otp1, otp_used=0)

            # Prepare email
            subject = "🔒 FitMentor OTP Verification"
            from_email = settings.EMAIL_HOST_USER
            to = [e]

            # Render HTML template with the otp value
            html_content = render_to_string("otp_email.html", {"otp": otp1})

            # Create message
            msg = EmailMultiAlternatives(subject, "", from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return render(request, 'reset.html')

        else:
            messages.error(request, "Please enter a valid email address.")
            return render(request, 'forgot.html')

    return render(request, "forgot.html")
def logout(request):
    try:
        del request.session["id"]
        del request.session["name"]
        del request.session["email"]
        del request.session["password"]
        return redirect('/login/')
    except:
        pass
    return render(request,'index.html')
def update_profile(request,id):
    e = User.objects.get(id = id)  
    if request.method == "POST":
        f = UserUpdate(request.POST,instance = e)
        print(f"Update User Form Error = {f.errors}")
        if f.is_valid():
            try:
                f.save()
            except:
                print(sys.exc_info())
            return redirect('/profile/')
        else:
            return render(request,"update.html",{'e':e})
    return render(request,'update.html',{'e':e})
    
def delete_account(request,id):
    if 'id' in request.session:
        e = User.objects.get(id=id)
        e.delete()
        return redirect('/register/')
    else:
        return render(request,'profile.html')
    
@session_login_required
@bmi_required
def chat_view(request, conversation_id=None):
    # 1. Authentication
    user_id = request.session.get("id")
    if not user_id:
        return redirect('login')
    user = User.objects.get(id=user_id)

    # 2. Load or initialize Conversation
    conversation = None
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=user)

    # 3. Handle new message
    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        if not message:
            messages.error(request, "Message cannot be empty.")
        else:
            # 3a. Fetch health data
            health_data = User_health.objects.filter(user=user).order_by("-id").first()
            if health_data:
                # Debug logs
                print(">>> HEALTH DATA OBJECT:", health_data)
                print(">>> Age:", health_data.age)
                print(">>> Gender:", health_data.gender)
                print(">>> Weight:", health_data.weight)
                print(">>> Height:", health_data.height)
                print(">>> Medical Conditions:", health_data.medical_conditions)
                profile_info = (
                    f"My gender is {health_data.gender}, "
                    f"age is {health_data.age}, "
                    f"weight is {health_data.weight}kg, "
                    f"height is {health_data.height}cm, "
                    f"medical conditions: {health_data.medical_conditions or 'none'}."
                )
            else:
                print(">>> No health data found for this user.")
                profile_info = "User health data not available."

            # 3b. Build prompt and call Gemini
            full_prompt = f"{profile_info} {message}"
            try:
                response = get_gemini_response(full_prompt)
                if not response:
                    response = "I'm sorry, I couldn't generate a response."
            except Exception as e:
                response = f"Error: {str(e)}"

            # 3c. Ensure we have a conversation to tie to
            if not conversation:
                conversation = Conversation.objects.create(user=user)

            # 3d. Save the chat under this conversation
            ChatHistory.objects.create(
                user=user,
                conversation=conversation,
                message=message,
                response=response
            )

    # 4. Fetch sidebar list and current chat history
    conversations = Conversation.objects.filter(user=user).order_by('-created_at')
    chat_history = []
    if conversation:
        chat_history = ChatHistory.objects.filter(conversation=conversation).order_by("timestamp")

    # 5. Render template
    return render(request, "chatbot.html", {
        "conversations": conversations,        "chat_history": chat_history,
        "current_conversation": conversation,
    })

@session_login_required

def feedback(request):
    if 'id' in request.session:
        if request.method == "POST":
            comment = request.POST.get("feedback")
            user_id = request.session.get("id")
            user = User.objects.get(id=user_id)
            Feedback.objects.create(user=user, comment=comment)
            return render(request, 'feedback.html', {'feedback_sent': True})  # send flag
        else:
            return render(request, 'feedback.html')
    else:
        return redirect('/login/')

from django.urls import reverse
def new_chat(request):
    user = User.objects.get(id=request.session["id"])
    conv = Conversation.objects.create(user=user)
    return redirect('chatbot_conv', conversation_id=conv.id)

from django.shortcuts import redirect
def delete_conversation(request, conversation_id):
    user = User.objects.get(id=request.session["id"])
    Conversation.objects.filter(id=conversation_id, user=user).delete()
    return redirect('chatbot')

