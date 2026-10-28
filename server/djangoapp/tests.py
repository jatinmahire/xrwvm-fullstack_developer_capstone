"""Behaviour tests, with real backend integration enabled explicitly in CI."""
import json
import os
from unittest import skipUnless
from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import CarMake, CarModel
from . import restapis
class ApplicationTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user('testbuyer',password='Test-Password-2026!')
        make=CarMake.objects.create(name='Nissan')
        self.car=CarModel.objects.create(car_make=make,name='Pathfinder',type='SUV',year=2023)
    def post(self, endpoint, data):
        return self.client.post('/djangoapp/'+endpoint,json.dumps(data),content_type='application/json')
    def test_login_logout_session(self):
        self.assertEqual(self.post('login',{'userName':'testbuyer','password':'wrong'}).status_code,401)
        self.assertEqual(self.post('login',{'userName':'testbuyer','password':'Test-Password-2026!'}).json()['status'],'Authenticated')
        self.assertEqual(self.client.get('/djangoapp/session').json()['userName'],'testbuyer')
        self.assertEqual(self.post('logout',{}).json()['status'],'Logged out')
        self.assertIsNone(self.client.get('/djangoapp/session').json()['userName'])
    def test_registration_creates_hashed_password(self):
        response=self.post('register',{'userName':'newbuyer','firstName':'New','lastName':'Buyer','email':'buyer@example.com','password':'Strong-New-Password-26!'})
        self.assertEqual(response.status_code,201)
        self.assertTrue(User.objects.get(username='newbuyer').check_password('Strong-New-Password-26!'))
    def test_catalogue_output(self):
        self.assertEqual(self.client.get('/djangoapp/get_cars').json()['cars'][0]['make'],'Nissan')
    def test_review_requires_authentication(self):
        self.assertEqual(self.post('add_review',{}).status_code,401)
    @patch('djangoapp.restapis.get_request',return_value=[{'id':15}])
    def test_empty_review_rejected(self, backend):
        self.client.force_login(self.user)
        response=self.post('add_review',{'dealership':15,'review':'   ','car_id':self.car.id})
        self.assertEqual(response.status_code,400)
    @patch('djangoapp.restapis.get_request',return_value=[])
    def test_missing_dealer_returns_404(self, backend):
        self.assertEqual(self.client.get('/djangoapp/dealer/9999').status_code,404)
    def test_csrf_enforced_for_login(self):
        protected=Client(enforce_csrf_checks=True)
        self.assertEqual(protected.post('/djangoapp/login',data='{}',content_type='application/json').status_code,403)
    def test_public_pages(self):
        for path in ['/','/about/','/contact/','/register','/health/']:
            self.assertEqual(self.client.get(path).status_code,200)

@skipUnless(os.environ.get('RUN_INTEGRATION_TESTS')=='1','Requires running Express/Mongo and sentiment services')
class ServiceIntegrationTests(TestCase):
    def test_real_dealers_and_kansas_filter(self):
        self.assertEqual(len(restapis.get_request('fetchDealers')),50)
        dealers=restapis.get_request('fetchDealers/Kansas')
        self.assertTrue(dealers)
        self.assertTrue(all(dealer['state']=='Kansas' for dealer in dealers))
    def test_real_dealer_reviews(self):
        self.assertTrue(restapis.get_request('fetchReviews/dealer/15'))
    def test_real_sentiment(self):
        self.assertEqual(restapis.analyze_review_sentiments('Fantastic services'),'positive')
