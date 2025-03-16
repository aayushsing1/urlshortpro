from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .forms import RegistrationForm, UrlForm
from .models import Url, ClickData
from .middleware import TrackingMiddleware

def home(request):
    return render(request, 'home.html') 

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('dashboard')
        messages.error(request, "Registration failed. Please check the form.")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"You are logged in as {username}.")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    urls = Url.objects.filter(user=request.user).order_by('-created_date')
    return render(request, 'dashboard.html', {'urls': urls})

@login_required
def create_url(request):
    if request.method == 'POST':
        form = UrlForm(request.POST)
        if form.is_valid():
            url = form.save(commit=False)
            url.user = request.user
            url.save()
            messages.success(request, "URL shortened successfully.")
            return redirect('dashboard')
    else:
        form = UrlForm()
    return render(request, 'create_url.html', {'form': form})

@login_required
def url_stats(request, short_code):
    url = get_object_or_404(Url, short_code=short_code, user=request.user)

    # Get click data for different time periods
    today = timezone.now().date()

    daily_clicks = ClickData.objects.filter(
        url=url, 
        timestamp__date=today
    ).count()

    weekly_clicks = ClickData.objects.filter(
        url=url, 
        timestamp__date__gte=today - timedelta(days=7)
    ).count()

    monthly_clicks = ClickData.objects.filter(
        url=url, 
        timestamp__date__gte=today - timedelta(days=30)
    ).count()

    # Get country distribution
    country_stats = ClickData.objects.filter(
        url=url
    ).values('country').annotate(
        count=Count('country')
    ).order_by('-count')[:10]

    # Recent clicks
    recent_clicks = ClickData.objects.filter(
        url=url
    ).order_by('-timestamp')[:50]

    context = {
        'url': url,
        'daily_clicks': daily_clicks,
        'weekly_clicks': weekly_clicks,
        'monthly_clicks': monthly_clicks,
        'country_stats': country_stats,
        'recent_clicks': recent_clicks,
    }

    return render(request, 'url_stats.html', context)


def redirect_to_url(request, short_code):
    url = get_object_or_404(Url, short_code=short_code, active=True)

    # Track this click
    tracker = TrackingMiddleware(None)
    ip = tracker.get_client_ip(request)
    country, city = tracker.get_location_data(ip)
    
    click_data = ClickData.objects.create(
        url=url,
        ip_address=ip,
        country=country,
        city=city,
        user_agent=request.META.get('HTTP_USER_AGENT'),
        referrer=request.META.get('HTTP_REFERER')
    )

    # Increment click counter
    
    url.save()

    # Redirect to first interstitial page
    return redirect('interstitial1', short_code=short_code)

def interstitial1(request, short_code):
    url = get_object_or_404(Url, short_code=short_code, active=True)
    return render(request, 'interstitial1.html', {'url': url})

def interstitial2(request, short_code):
    url = get_object_or_404(Url, short_code=short_code, active=True)
    url.clicks += 1
    url.save()
    return render(request, 'interstitial2.html', {'url': url})

def final_redirect(request, short_code):
    url = get_object_or_404(Url, short_code=short_code, active=True)
    
    return redirect(url.original_url)