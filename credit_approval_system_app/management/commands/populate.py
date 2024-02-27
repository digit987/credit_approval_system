import pandas as pd
from django.core.management.base import BaseCommand
from credit_approval_system_app.models import Customer, Loan

class Command(BaseCommand):
    help = 'Populate Customer and Loan tables from Excel files'

    def handle(self, *args, **kwargs):
        # Populating Customer table
        customer_data = pd.read_excel('credit_approval_system_app/dataset/customer_data.xlsx')
        for _, row in customer_data.iterrows():
            Customer.objects.create(
                customer_id=row['Customer ID'],
                first_name=row['First Name'],
                last_name=row['Last Name'],
                age=row['Age'],
                phone_number=row['Phone Number'],
                monthly_salary=row['Monthly Salary'],
                approved_limit=row['Approved Limit']
            )

        # Populating Loan table
        loan_data = pd.read_excel('credit_approval_system_app/dataset/loan_data.xlsx')
        for _, row in loan_data.iterrows():
            customer_id = row['Customer ID']
            try:
                customer = Customer.objects.get(customer_id=customer_id)
                Loan.objects.create(
                    customer=customer,
                    loan_id=row['Loan ID'],
                    loan_amount=row['Loan Amount'],
                    tenure=row['Tenure'],
                    interest_rate=row['Interest Rate'],
                    monthly_payment=row['Monthly payment'],
                    emis_paid_on_time=row['EMIs paid on Time'],
                    date_of_approval=row['Date of Approval'],
                    end_date=row['End Date']
                )
            except Customer.DoesNotExist:
                print(f"Customer with ID {customer_id} does not exist.")
