from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from django.db.models import Sum

@api_view(['GET'])
def view_customers(request):
    customers = Customer.objects.all()
    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def register(request):
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        # Checking if the customer_id is provided in the request
        if 'customer_id' not in request.data:
            # Generating a new unique customer_id
            last_customer = Customer.objects.last()
            new_customer_id = last_customer.customer_id + 1 if last_customer else 1
            serializer.validated_data['customer_id'] = new_customer_id

        monthly_salary = serializer.validated_data['monthly_salary']
        approved_limit = round(36 * monthly_salary, -5)  # Rounding to nearest lakh
        serializer.validated_data['approved_limit'] = approved_limit

        # Saving the new Customer instance
        customer = serializer.save()
        return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def check_eligibility(request):
    customer_id = request.data.get('customer_id')
    loan_amount = request.data.get('loan_amount')
    interest_rate = request.data.get('interest_rate')
    tenure = request.data.get('tenure')

    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # Business logic for checking eligibility and interest rate calculation
    credit_rating = calculate_credit_rating(customer_id)
    if credit_rating > 50:
        approval = True
    elif 50 > credit_rating > 30:
        interest_rate = max(interest_rate, 12)
        approval = True
    elif 30 > credit_rating > 10:
        interest_rate = max(interest_rate, 16)
        approval = True
    else:
        approval = False
    
    if sum(customer.loan_set.all().values_list('emis_paid_on_time', flat=True)) > 0.5 * customer.monthly_salary:
        approval = False

    response_data = {
        "customer_id": customer_id,
        "approval": approval,
        "interest_rate": interest_rate,
        "corrected_interest_rate": interest_rate,
        "tenure": tenure,
        "monthly_installment": calculate_monthly_installment(loan_amount, interest_rate, tenure)
    }
    return Response(response_data, status=status.HTTP_200_OK)

def calculate_credit_rating(customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        total_emis_paid_on_time = customer.loan_set.aggregate(total_emis_paid_on_time=Sum('emis_paid_on_time'))['total_emis_paid_on_time']
        num_loans_taken = customer.loan_set.count()
        credit_rating = 50
        return credit_rating
    except Customer.DoesNotExist:
        return 0

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    monthly_interest_rate = interest_rate / (12 * 100)
    monthly_installment = (loan_amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** (-tenure))
    return monthly_installment

@api_view(['POST'])
def create_loan(request):
    mutable_data = request.data.copy()
    # Generating a new unique loan_id
    last_loan = Loan.objects.last()
    new_loan_id = last_loan.loan_id + 1 if last_loan else 1

    # Adding the new loan_id to the request data
    mutable_data['loan_id'] = new_loan_id

    serializer = LoanSerializer(data=mutable_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        serializer = LoanSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Loan.DoesNotExist:
        return Response({"error": "Loan does not exist"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def view_loans(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        loans = customer.loan_set.all()
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response({"error": "Customer does not exist"}, status=status.HTTP_404_NOT_FOUND)
