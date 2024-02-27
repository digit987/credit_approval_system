from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Customer, Loan

class CustomerViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_view_customers(self):
        # Testing GET request to view_customers endpoint
        response = self.client.get('/view-customers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register_customer(self):
        # Testing POST request to register endpoint
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "age": 35,
            "phone_number": "1234567890",
            "monthly_salary": 60000
        }
        response = self.client.post('/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Checking if the customer is created in the database
        self.assertTrue(Customer.objects.filter(first_name='John').exists())

    def test_check_eligibility(self):
        # Testing POST request to check_eligibility endpoint
        data = {
            "customer_id": 1,
            "loan_amount": 50000,
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post('/check-eligibility/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_loan(self):
        # Testing POST request to create_loan endpoint
        data = {
            "customer": 1,
            "loan_id": 1,
            "loan_amount": 50000,
            "tenure": 12,
            "interest_rate": 8,
            "monthly_payment": 5000,
            "emis_paid_on_time": 10,
            "date_of_approval": "2024-02-26",
            "end_date": "2025-02-26"
        }
        response = self.client.post('/create-loan/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Checking if the loan is created in the database
        self.assertTrue(Loan.objects.filter(loan_id=1).exists())

    def test_view_loan(self):
        # Testing GET request to view_loan endpoint
        response = self.client.get('/view-loan/1000/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Assuming loan with ID=1 does not exist

    def test_view_loans(self):
        # Testing GET request to view_loans endpoint
        response = self.client.get('/view-loans/1000/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Assuming customer with ID=1 does not exist
