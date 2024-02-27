from rest_framework import serializers
from .models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        #fields = ['first_name', 'last_name', 'age', 'phone_number', 'monthly_salary']
        exclude = ['customer_id', 'approved_limit']

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'
