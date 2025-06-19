from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from itertools import product
from django.db import transaction
from .forms import *


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def custom_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('home')
    return render(request, 'signup.html')

def custom_logout(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    bookings = request.user.bookings.select_related('show__event')
    return render(request, 'profile.html', {'booking_history': bookings})

@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        form.fields['username'].initial = request.user.username
        form.fields['email'].initial = request.user.email
        form.fields['first_name'].initial = request.user.first_name
        form.fields['last_name'].initial = request.user.last_name
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=profile)
        form.fields['username'].initial = request.user.username
        form.fields['email'].initial = request.user.email
        form.fields['first_name'].initial = request.user.first_name
        form.fields['last_name'].initial = request.user.last_name
    return render(request, 'edit_profile.html', {'form': form})

def home(request):
    events = Event.objects.all().order_by('-date')[:5]  # latest events
    movies = Event.objects.filter(category='movie')
    concerts = Event.objects.filter(category='concert')
    context = {
        'events': events,
        'movies': movies,
        'concerts': concerts,
    }
    return render(request, 'home.html', context)

def all_events(request):
    events = Event.objects.all()
    return render(request, 'all_events.html', {'events': events})

def all_shows(request):
    shows = Show.objects.select_related('event').order_by('show_time')
    return render(request, 'all_shows.html', {'shows': shows})

def movie_list(request):
    movies = Event.objects.filter(category='movie')
    return render(request, 'movie_list.html', {'movies': movies})

def concert_list(request):
    concerts = Event.objects.filter(category='concert')
    return render(request, 'concert_list.html', {'concerts': concerts})

def search(request):
    return HttpResponse("Search page under construction")

def show_list(request, movie_id):
    movie = get_object_or_404(Event, pk=movie_id)
    shows = Show.objects.filter(event=movie).order_by('show_time')
    return render(request, 'show_list.html', {'movie': movie, 'shows': shows})


@login_required
def book_show(request, show_id):
    show = get_object_or_404(Show, pk=show_id)
    rows = ['A', 'B', 'C', 'D', 'E']
    cols = [str(i) for i in range(1, 11)]

    context = {
        'show': show,
        'rows': rows,
        'cols': cols,
        'booked_seats': show.booked_seats or [],
    }

    if request.method == 'POST':
        name = request.POST.get('name')
        selected_seats = request.POST.getlist('selected_seats[]')  # updated to getlist
        seat_count = len(selected_seats)
        price_per_seat = show.price
        total_price = seat_count * price_per_seat

        already_booked = show.booked_seats or []
        if any(seat in already_booked for seat in selected_seats):
            context['error'] = "Some selected seats are already booked."
            return render(request, 'book_show.html', context)

        # Create a pending booking but don't update Show.booked_seats yet
        booking = Booking.objects.create(
            user=request.user,
            show=show,
            customer_name=name,
            seats_booked=selected_seats,
            seat_names=', '.join(selected_seats),
            total_price=total_price
        )

        # Redirect to payment page
        return redirect(reverse('payment_page', kwargs={'booking_id': booking.id}))

    return render(request, 'book_show.html', context)


@login_required
def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    show = booking.show

    if request.method == 'POST':
        with transaction.atomic():
            # Lock the show row for this transaction to avoid race conditions
            show = Show.objects.select_for_update().get(pk=show.id)
            already_booked = show.booked_seats or []

            # Check if any seats are already booked
            if any(seat in already_booked for seat in booking.seats_booked):
                return render(request, 'payment_page.html', {
                    'booking': booking,
                    'error': "Some seats were already booked by someone else. Please select different seats."
                })

            # Simulate payment success (always successful in this mini project)
            booking.is_paid = True
            booking.save()

            # Update the show with newly booked seats
            show.booked_seats = already_booked + booking.seats_booked
            show.save()

        # Redirect to success page
        return redirect(reverse('booking_success', kwargs={
            'booking_name': booking.customer_name,
            'movie_title': show.event.title,
            'seats': len(booking.seats_booked)
        }))

    return render(request, 'payment_page.html', {'booking': booking})


def booking_success(request, booking_name, movie_title, seats):
    return render(request, 'booking_success.html', {
        'name': booking_name,
        'movie_title': movie_title,
        'seats': seats,
        
    })

def search_page(request):
    query = request.GET.get('query', '')
    results = []

    if query:
        results = Event.objects.filter(title__icontains=query)
    else:
        results = Event.objects.all()
    return render(request, 'search_page.html', {
        'query': query,
        'results': results
    })
