from django.shortcuts import render, redirect
from .forms import CreateUserForm, LoginForm, CreateRecordForm, UpdateRecordForm

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate

from django.contrib.auth.decorators import login_required

from .models import Record

from django.contrib import messages

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ForgotPasswordForm, UpdatePasswordForm



# - Homepage 

def home(request):

    return render(request, 'webapp/index.html')


# - Register a user

def register(request):

    form = CreateUserForm()

    if request.method == "POST":

        form = CreateUserForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, "Account created successfully!")

            return redirect("my-login")

    context = {'form':form}

    return render(request, 'webapp/register.html', context=context)


# - Login a user

def my_login(request):

    form = LoginForm()

    if request.method == "POST":

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:

                auth.login(request, user)

                return redirect("dashboard")
            else:
                messages.error(request,"Invalid Username or password.")

    context = {'form':form}

    return render(request, 'webapp/my-login.html', context=context)


# - Dashboard

@login_required(login_url='my-login')
def dashboard(request):

    my_records = Record.objects.all()

    context = {'records': my_records}

    return render(request, 'webapp/dashboard.html', context=context)


# - Create a record 

@login_required(login_url='my-login')
def create_record(request):

    form = CreateRecordForm()

    if request.method == "POST":

        form = CreateRecordForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(request, "Your record was created!")

            return redirect("dashboard")

    context = {'form': form}

    return render(request, 'webapp/create-record.html', context=context)


# - Update a record 

@login_required(login_url='my-login')
def update_record(request, pk):

    record = Record.objects.get(id=pk)

    form = UpdateRecordForm(instance=record)

    if request.method == 'POST':

        form = UpdateRecordForm(request.POST, instance=record)

        if form.is_valid():

            form.save()

            messages.success(request, "Your record was updated!")

            return redirect("dashboard")
        
    context = {'form':form}

    return render(request, 'webapp/update-record.html', context=context)


# - Read / View a singular record

@login_required(login_url='my-login')
def singular_record(request, pk):

    all_records = Record.objects.get(id=pk)

    context = {'record':all_records}

    return render(request, 'webapp/view-record.html', context=context)


# - Delete a record

@login_required(login_url='my-login')
def delete_record(request, pk):

    record = Record.objects.get(id=pk)

    record.delete()

    messages.success(request, "Your record was deleted!")

    return redirect("dashboard")



# - User logout

def user_logout(request):

    auth.logout(request)

    messages.success(request, "Logout success!")

    return redirect("my-login")



def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            print(f"DEBUG: Checking email {email}")  # Debug statement
            try:
                # Check if email exists in the Record model
                record = Record.objects.get(email__iexact=email)
                print(f"DEBUG: Email {email} found in the database.")  # Debug statement
                
                # Store the record ID in the session
                request.session['record_id'] = record.id  
                return redirect('update_password')  # Redirect to the password update page
            except Record.DoesNotExist:
                messages.error(request, "Email not found. Please enter a valid email.")
                print(f"DEBUG: Email {email} not found.")  # Debug statement
    else:
        form = ForgotPasswordForm()

    return render(request, 'webapp/forgot_password.html', {'form': form})


def update_password(request):
    # Retrieve the record ID from the session
    record_id = request.session.get('record_id')
    if not record_id:
        messages.error(request, "Invalid session. Please try again.")
        return redirect('forgot_password')

    # Retrieve the user record
    try:
        user = Record.objects.get(id=record_id)
    except Record.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = UpdatePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            
            if new_password == confirm_password:
                user.password = make_password(new_password)  # Hash the password
                user.save()
                messages.success(request, "Your password has been updated successfully.")
                del request.session['record_id']  # Clear the session
                return redirect('login')  # Redirect to login page
            else:
                messages.error(request, "Passwords do not match.")
    else:
        form = UpdatePasswordForm()

    return render(request, 'webapp/update_password.html', {'form': form})





