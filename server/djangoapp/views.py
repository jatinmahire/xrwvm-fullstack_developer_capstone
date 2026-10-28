"""Authentication, catalogue and review endpoints for CarConnect."""
import json
from datetime import date
from functools import wraps
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from .models import CarModel
from . import restapis

def api_errors(function):
    @wraps(function)
    def wrapped(request, *args, **kwargs):
        try:
            return function(request, *args, **kwargs)
        except (ValueError, KeyError, TypeError, ValidationError) as error:
            return JsonResponse({'status':400,'error':str(error)}, status=400)
        except requests.RequestException:
            return JsonResponse({'status':503,'error':'A required service is temporarily unavailable.'}, status=503)
    return wrapped

@ensure_csrf_cookie
def frontend(request):
    return render(request, 'index.html')
def about(request):
    return render(request, 'About.html')
def contact(request):
    return render(request, 'Contact.html')
def health(request):
    return JsonResponse({'service':'CarConnect Django','status':'ok'})
@require_GET
def session_user(request):
    return JsonResponse({'userName':request.user.username if request.user.is_authenticated else None})

@require_POST
@api_errors
def login_user(request):
    data = json.loads(request.body)
    user = authenticate(request, username=data['userName'], password=data['password'])
    if user is None:
        return JsonResponse({'status':401,'error':'Invalid username or password.'}, status=401)
    login(request, user)
    return JsonResponse({'userName':user.username,'status':'Authenticated'})

@require_POST
def logout_user(request):
    logout(request)
    return JsonResponse({'status':'Logged out'})

@require_POST
@api_errors
def registration(request):
    data = json.loads(request.body)
    username = data['userName'].strip()
    if not username or len(username) > 150:
        raise ValueError('A username of up to 150 characters is required.')
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error':'That username already exists.'}, status=409)
    validate_email(data['email'])
    validate_password(data['password'])
    user = User.objects.create_user(username=username, email=data['email'], password=data['password'],
        first_name=data['firstName'].strip(), last_name=data['lastName'].strip())
    login(request, user)
    return JsonResponse({'userName':user.username,'status':'Registered'}, status=201)

@require_GET
@api_errors
def get_dealerships(request, state='All'):
    endpoint = 'fetchDealers' if state == 'All' else f'fetchDealers/{state}'
    return JsonResponse({'status':200,'dealers':restapis.get_request(endpoint)})

@require_GET
@api_errors
def get_dealer_details(request, dealer_id):
    dealers = restapis.get_request(f'fetchDealer/{dealer_id}')
    if not dealers:
        return JsonResponse({'error':'Dealer not found.'}, status=404)
    return JsonResponse({'status':200,'dealer':dealers[0]})

@require_GET
@api_errors
def get_dealer_reviews(request, dealer_id):
    reviews = restapis.get_request(f'fetchReviews/dealer/{dealer_id}')
    for review in reviews:
        review['sentiment'] = restapis.analyze_review_sentiments(review['review'])
    return JsonResponse({'status':200,'reviews':reviews})

@require_GET
def get_cars(request):
    cars = [{'id':car.id,'make':car.car_make.name,'model':car.name,'year':car.year,'type':car.type}
        for car in CarModel.objects.select_related('car_make').all()]
    return JsonResponse({'status':200,'cars':cars})

@require_POST
@api_errors
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error':'Please log in to post a review.'}, status=401)
    data = json.loads(request.body)
    dealer_id = int(data['dealership'])
    if not restapis.get_request(f'fetchDealer/{dealer_id}'):
        return JsonResponse({'error':'Dealer not found.'}, status=404)
    text = data['review'].strip()
    if not text or len(text) > 5000:
        raise ValueError('A review between 1 and 5000 characters is required.')
    car = CarModel.objects.select_related('car_make').filter(pk=int(data['car_id'])).first()
    if car is None:
        raise ValueError('Choose a valid car from the catalogue.')
    purchase = data.get('purchase', False)
    if not isinstance(purchase, bool):
        raise ValueError('Purchase must be a boolean.')
    purchase_date = data.get('purchase_date', '')
    if purchase:
        if date.fromisoformat(purchase_date) > date.today():
            raise ValueError('Purchase date cannot be in the future.')
    payload = {'name':request.user.get_full_name() or request.user.username,
        'dealership':dealer_id, 'review':text,'purchase':purchase,'purchase_date':purchase_date,
        'car_make':car.car_make.name,'car_model':car.name,'car_year':car.year}
    return JsonResponse({'status':201,'review':restapis.post_review(payload)}, status=201)
