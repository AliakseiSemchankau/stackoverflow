from django.shortcuts import render_to_response, redirect
from django.contrib import auth
from django.core.context_processors import csrf
from .forms import UserForm, UserProfileForm
from django.template import RequestContext
from django.http.response import HttpResponseRedirect
import sys
# Create your views here.

def login(request):
    
    args = {}
    args.update(csrf(request))
    redirect_to = request.REQUEST.get('next', '')
    args['redirect_to'] = redirect_to

    if request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect(redirect_to)  
        else:
            args['login_error'] = "User not found"  
            return render_to_response('login.html', args)
    else:
    	return render_to_response('login.html', args)

def logout(request):
	auth.logout(request)
	return redirect("/")


def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
                print 'yes it is'
                sys.stdout.flush()
            else:
                print 'no('
                sys.stdout.flush()

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    if registered == False:
        return render_to_response(
                'register.html',
                {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
                context)
    else:
        return redirect("/")

