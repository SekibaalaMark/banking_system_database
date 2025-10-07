from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import json


@csrf_exempt
def add_branch(request):
    try:
        if request.method == "POST":
            # Check if it's JSON or form-data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            branch_name = str(data['branch_name'])
            Location = str(data['Location'])
            phone_contact = str(data['phone_contact'])
            manager_id = str(data['manager_id'])
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Branch (branch_name, Location, phone_contact, manager_id)
                    VALUES (%s, %s, %s, %s)
                """, [
                    branch_name, 
                    Location, 
                    phone_contact, 
                    manager_id
                ])
            return JsonResponse({"message": "Branch added"})
    except ValueError as e:
        return JsonResponse({"error": f"Invalid data type: {str(e)}"}, status=400)
    except KeyError as e:
        return JsonResponse({"error": f"Missing field: {str(e)}"}, status=400)
    except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    

from datetime import datetime

@csrf_exempt
def add_employee(request):
    if request.method == "POST":
        try:
            # Handle both JSON and form-data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # Extract and validate data
            first_name = str(data['first_name'])
            last_name = str(data['last_name'])
            position = str(data['position'])
            branch_id = int(data['branch_id'])
            phone_number = str(data['phone_number'])
            gender = str(data['gender']).upper()  # Ensure uppercase F or M
            NIN_number = str(data['NIN_number'])
            date_hired = data['date_hired']  # Format: YYYY-MM-DD
            date_of_birth = data['date_of_birth']  # Format: YYYY-MM-DD
            
            # Validate gender
            if gender not in ['F', 'M']:
                return JsonResponse(
                    {"error": "Gender must be 'F' or 'M'"}, 
                    status=400
                )
            
            # Validate date formats (optional but recommended)
            try:
                datetime.strptime(date_hired, '%Y-%m-%d')
                datetime.strptime(date_of_birth, '%Y-%m-%d')
            except ValueError:
                return JsonResponse(
                    {"error": "Date format must be YYYY-MM-DD"}, 
                    status=400
                )
            
            # Insert into database
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO employees 
                    (first_name, last_name, position, branch_id, phone_number, 
                     gender, NIN_number, date_hired, date_of_birth)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    first_name, last_name, position, branch_id, phone_number,
                    gender, NIN_number, date_hired, date_of_birth
                ])
                
                # Get the ID of the inserted employee
                employee_id = cursor.lastrowid
            
            return JsonResponse({
                "message": "Employee added successfully",
                "employee_id": employee_id
            }, status=201)
            
        except KeyError as e:
            return JsonResponse(
                {"error": f"Missing required field: {str(e)}"}, 
                status=400
            )
        except ValueError as e:
            return JsonResponse(
                {"error": f"Invalid data type: {str(e)}"}, 
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {"error": f"Database error: {str(e)}"}, 
                status=500
            )
    
    return JsonResponse({"error": "Only POST method allowed"}, status=405)





@csrf_exempt
def add_customer(request):
    if request.method == "POST":
        try:
            # Handle both JSON and form-data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # Extract and validate data
            first_name = str(data['first_name'])
            last_name = str(data['last_name'])
            date_of_birth = data['date_of_birth']  # Format: YYYY-MM-DD
            phone_contact = str(data['phone_contact'])
            NIN_number = str(data['NIN_number'])
            branch_id = int(data['branch_id'])
            
            # Handle both 'Gender' and 'gender' keys
            gender = str(data.get('Gender') or data.get('gender', '')).upper()
            
            # Validate gender
            if gender not in ['F', 'M']:
                return JsonResponse(
                    {"error": "Gender must be 'F' or 'M'"}, 
                    status=400
                )
            
            # Validate date format
            try:
                datetime.strptime(date_of_birth, '%Y-%m-%d')
            except ValueError:
                return JsonResponse(
                    {"error": "Date format must be YYYY-MM-DD"}, 
                    status=400
                )
            
            # Validate NIN_number length (should be 14 characters)
            if len(NIN_number) != 14:
                return JsonResponse(
                    {"error": "NIN number must be exactly 14 characters"}, 
                    status=400
                )
            
            # Check if branch exists
            with connection.cursor() as cursor:
                cursor.execute("SELECT branch_id FROM Branch WHERE branch_id = %s", [branch_id])
                branch = cursor.fetchone()
                
                if not branch:
                    return JsonResponse(
                        {"error": f"Branch with ID {branch_id} does not exist"}, 
                        status=404
                    )
                
                # Insert into database
                cursor.execute("""
                    INSERT INTO customers 
                    (first_name, last_name, date_of_birth, phone_contact, 
                     NIN_number, branch_id, Gender)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, [
                    first_name, last_name, date_of_birth, phone_contact,
                    NIN_number, branch_id, gender
                ])
                
                # Get the ID of the inserted customer
                customer_id = cursor.lastrowid
            
            return JsonResponse({
                "message": "Customer added successfully",
                "customer_id": customer_id,
                "first_name": first_name,
                "last_name": last_name,
                "NIN_number": NIN_number
            }, status=201)
            
        except KeyError as e:
            return JsonResponse(
                {"error": f"Missing required field: {str(e)}"}, 
                status=400
            )
        except ValueError as e:
            return JsonResponse(
                {"error": f"Invalid data type: {str(e)}"}, 
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {"error": f"Database error: {str(e)}"}, 
                status=500
            )
    
    return JsonResponse({"error": "Only POST method allowed"}, status=405)




from decimal import Decimal
@csrf_exempt
def add_account(request):
    if request.method == "POST":
        try:
            # Handle both JSON and form-data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # Extract and validate data
            account_number = str(data['account_number'])
            customer_id = int(data['customer_id'])
            account_type = str(data['account_type'])
            status = str(data['status']).lower()
            
            # Balance is optional (defaults to 0.00 if not provided)
            balance = Decimal(data.get('balance', '0.00'))
            
            # date_opened is optional (defaults to current date if not provided)
            date_opened = data.get('date_opened', None)
            
            # Validate account_type
            valid_account_types = ['Savings', 'Fixed', 'Current']
            if account_type not in valid_account_types:
                return JsonResponse(
                    {"error": f"Account type must be one of: {', '.join(valid_account_types)}"}, 
                    status=400
                )
            
            # Validate status
            valid_statuses = ['active', 'frozen', 'closed']
            if status not in valid_statuses:
                return JsonResponse(
                    {"error": f"Status must be one of: {', '.join(valid_statuses)}"}, 
                    status=400
                )
            
            # Validate date format if provided
            if date_opened:
                try:
                    datetime.strptime(date_opened, '%Y-%m-%d')
                except ValueError:
                    return JsonResponse(
                        {"error": "Date format must be YYYY-MM-DD"}, 
                        status=400
                    )
            
            # Validate account_number length (should be 11 characters)
            if len(account_number) != 11:
                return JsonResponse(
                    {"error": "Account number must be exactly 11 characters"}, 
                    status=400
                )
            
            # Insert into database
            with connection.cursor() as cursor:
                if date_opened:
                    cursor.execute("""
                        INSERT INTO ACCOUNTS 
                        (account_number, customer_id, account_type, balance, date_opened, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, [
                        account_number, customer_id, account_type, 
                        balance, date_opened, status
                    ])
                else:
                    # Let MySQL use the default CURDATE() for date_opened
                    cursor.execute("""
                        INSERT INTO ACCOUNTS 
                        (account_number, customer_id, account_type, balance, status)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [
                        account_number, customer_id, account_type, 
                        balance, status
                    ])
            
            return JsonResponse({
                "message": "Account added successfully",
                "account_number": account_number,
                "balance": str(balance),
                "account_type": account_type,
                "status": status
            }, status=201)
            
        except KeyError as e:
            return JsonResponse(
                {"error": f"Missing required field: {str(e)}"}, 
                status=400
            )
        except ValueError as e:
            return JsonResponse(
                {"error": f"Invalid data type: {str(e)}"}, 
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {"error": f"Database error: {str(e)}"}, 
                status=500
            )
    
    return JsonResponse({"error": "Only POST method allowed"}, status=405)




@csrf_exempt
def make_transaction(request):
    if request.method == "POST":
        try:
            # Handle both JSON and form-data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # Extract and validate data
            account_number = str(data['account_number'])
            transaction_type = str(data['type']).lower()
            amount = Decimal(data['amount'])
            
            # date_of_transaction is optional (defaults to current date if not provided)
            date_of_transaction = data.get('date_of_transaction', None)
            
            # Validate transaction type
            valid_types = ['deposit', 'withdraw']
            if transaction_type not in valid_types:
                return JsonResponse(
                    {"error": f"Transaction type must be one of: {', '.join(valid_types)}"}, 
                    status=400
                )
            
            # Validate amount
            if amount <= 0:
                return JsonResponse(
                    {"error": "Amount must be greater than 0"}, 
                    status=400
                )
            
            # Validate date format if provided
            if date_of_transaction:
                try:
                    datetime.strptime(date_of_transaction, '%Y-%m-%d')
                except ValueError:
                    return JsonResponse(
                        {"error": "Date format must be YYYY-MM-DD"}, 
                        status=400
                    )
            
            # Validate account_number length
            if len(account_number) != 11:
                return JsonResponse(
                    {"error": "Account number must be exactly 11 characters"}, 
                    status=400
                )
            
            # Process transaction in database
            with connection.cursor() as cursor:
                # Check if account exists and get current balance and status
                cursor.execute("""
                    SELECT balance, status 
                    FROM ACCOUNTS 
                    WHERE account_number = %s
                """, [account_number])
                
                account = cursor.fetchone()
                
                if not account:
                    return JsonResponse(
                        {"error": "Account not found"}, 
                        status=404
                    )
                
                current_balance = account[0]
                account_status = account[1]
                
                # Check if account is active
                if account_status != 'active':
                    return JsonResponse(
                        {"error": f"Cannot process transaction. Account status is '{account_status}'"}, 
                        status=400
                    )
                
                # Check sufficient balance for withdrawals
                if transaction_type == 'withdraw':
                    if current_balance < amount:
                        return JsonResponse(
                            {"error": f"Insufficient balance. Current balance: {current_balance}"}, 
                            status=400
                        )
                    new_balance = current_balance - amount
                else:  # deposit
                    new_balance = current_balance + amount
                
                # Insert transaction record
                if date_of_transaction:
                    cursor.execute("""
                        INSERT INTO TRANSACTIONS 
                        (account_number, type, amount, date_of_transaction)
                        VALUES (%s, %s, %s, %s)
                    """, [account_number, transaction_type, amount, date_of_transaction])
                else:
                    # Let MySQL use the default CURDATE() for date_of_transaction
                    cursor.execute("""
                        INSERT INTO TRANSACTIONS 
                        (account_number, type, amount)
                        VALUES (%s, %s, %s)
                    """, [account_number, transaction_type, amount])
                
                # Get the transaction ID of the inserted record
                transaction_id = cursor.lastrowid
                
                # Update account balance
                cursor.execute("""
                    UPDATE ACCOUNTS 
                    SET balance = %s 
                    WHERE account_number = %s
                """, [new_balance, account_number])
            
            return JsonResponse({
                "message": "Transaction completed successfully",
                "transaction_id": transaction_id,
                "account_number": account_number,
                "type": transaction_type,
                "amount": str(amount),
                "previous_balance": str(current_balance),
                "new_balance": str(new_balance)
            }, status=201)
            
        except KeyError as e:
            return JsonResponse(
                {"error": f"Missing required field: {str(e)}"}, 
                status=400
            )
        except ValueError as e:
            return JsonResponse(
                {"error": f"Invalid data type: {str(e)}"}, 
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {"error": f"Database error: {str(e)}"}, 
                status=500
            )
    
    return JsonResponse({"error": "Only POST method allowed"}, status=405)




@csrf_exempt
def create_loan(request):
    if request.method == "POST":
        try:
            # Handle both JSON and form-data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # Extract and validate data
            account_number = str(data['account_number'])
            amount = Decimal(data['amount'])
            interest = int(data['interest'])
            term = int(data['term'])
            end_date = str(data['end_date'])
            branch_id = int(data['branch_id'])
            
            # status is optional (defaults to 'active' if not provided)
            status = str(data.get('status', 'active')).lower()
            
            # start_date is optional (defaults to current date if not provided)
            start_date = data.get('start_date', None)
            
            # Validate account_number length
            if len(account_number) != 11:
                return JsonResponse(
                    {"error": "Account number must be exactly 11 characters"}, 
                    status=400
                )
            
            # Validate amount
            if amount <= 0:
                return JsonResponse(
                    {"error": "Loan amount must be greater than 0"}, 
                    status=400
                )
            
            # Validate interest rate
            if interest < 0 or interest > 100:
                return JsonResponse(
                    {"error": "Interest rate must be between 0 and 100"}, 
                    status=400
                )
            
            # Validate term (in months, typically)
            if term <= 0:
                return JsonResponse(
                    {"error": "Loan term must be greater than 0"}, 
                    status=400
                )
            
            # Validate status
            valid_statuses = ['active', 'paid', 'default']
            if status not in valid_statuses:
                return JsonResponse(
                    {"error": f"Status must be one of: {', '.join(valid_statuses)}"}, 
                    status=400
                )
            
            # Validate date formats
            if start_date:
                try:
                    datetime.strptime(start_date, '%Y-%m-%d')
                except ValueError:
                    return JsonResponse(
                        {"error": "Start date format must be YYYY-MM-DD"}, 
                        status=400
                    )
            
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return JsonResponse(
                    {"error": "End date format must be YYYY-MM-DD"}, 
                    status=400
                )
            
            # Validate that end_date is in the future
            if start_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                if end_date_obj <= start_date_obj:
                    return JsonResponse(
                        {"error": "End date must be after start date"}, 
                        status=400
                    )
            
            # Process loan creation in database
            with connection.cursor() as cursor:
                # Check if account exists and is active
                cursor.execute("""
                    SELECT status, account_type 
                    FROM ACCOUNTS 
                    WHERE account_number = %s
                """, [account_number])
                
                account = cursor.fetchone()
                
                if not account:
                    return JsonResponse(
                        {"error": "Account not found"}, 
                        status=404
                    )
                
                account_status = account[0]
                
                if account_status != 'active':
                    return JsonResponse(
                        {"error": f"Cannot create loan. Account status is '{account_status}'"}, 
                        status=400
                    )
                
                # Check if branch exists
                cursor.execute("""
                    SELECT branch_name 
                    FROM BRANCH 
                    WHERE branch_id = %s
                """, [branch_id])
                
                branch = cursor.fetchone()
                
                if not branch:
                    return JsonResponse(
                        {"error": "Branch not found"}, 
                        status=404
                    )
                
                # Insert loan record
                if start_date:
                    cursor.execute("""
                        INSERT INTO LOANS 
                        (account_number, amount, interest, term, start_date, end_date, branch_id, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, [account_number, amount, interest, term, start_date, end_date, branch_id, status])
                else:
                    # Let MySQL use the default CURDATE() for start_date
                    cursor.execute("""
                        INSERT INTO LOANS 
                        (account_number, amount, interest, term, end_date, branch_id, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, [account_number, amount, interest, term, end_date, branch_id, status])
                
                # Get the loan ID of the inserted record
                loan_id = cursor.lastrowid
                
                # Optional: Deposit loan amount into the account
                cursor.execute("""
                    UPDATE ACCOUNTS 
                    SET balance = balance + %s 
                    WHERE account_number = %s
                """, [amount, account_number])
            
            return JsonResponse({
                "message": "Loan created successfully",
                "loan_id": loan_id,
                "account_number": account_number,
                "amount": str(amount),
                "interest": interest,
                "term": term,
                "end_date": end_date,
                "branch_id": branch_id,
                "status": status
            }, status=201)
            
        except KeyError as e:
            return JsonResponse(
                {"error": f"Missing required field: {str(e)}"}, 
                status=400
            )
        except ValueError as e:
            return JsonResponse(
                {"error": f"Invalid data type: {str(e)}"}, 
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {"error": f"Database error: {str(e)}"}, 
                status=500
            )
    
    return JsonResponse({"error": "Only POST method allowed"}, status=405)






@csrf_exempt
def add_collateral(request):
    if request.method == "POST":
        try:
            # Handle both JSON and form-data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # Extract and validate data
            loan_id = int(data['loan_id'])
            collateral_type = str(data['type'])
            description = str(data['description'])
            value = Decimal(data['value'])
            ownership_details = str(data['ownership_details'])
            status = str(data['status'])
            
            # Validate collateral value
            if value <= 0:
                return JsonResponse(
                    {"error": "Collateral value must be greater than 0"}, 
                    status=400
                )
            
            # Validate required string fields are not empty
            if not collateral_type.strip():
                return JsonResponse(
                    {"error": "Collateral type cannot be empty"}, 
                    status=400
                )
            
            if not description.strip():
                return JsonResponse(
                    {"error": "Description cannot be empty"}, 
                    status=400
                )
            
            if not ownership_details.strip():
                return JsonResponse(
                    {"error": "Ownership details cannot be empty"}, 
                    status=400
                )
            
            if not status.strip():
                return JsonResponse(
                    {"error": "Status cannot be empty"}, 
                    status=400
                )
            
            # Validate field lengths
            if len(collateral_type) > 100:
                return JsonResponse(
                    {"error": "Collateral type must not exceed 100 characters"}, 
                    status=400
                )
            
            if len(description) > 255:
                return JsonResponse(
                    {"error": "Description must not exceed 255 characters"}, 
                    status=400
                )
            
            if len(ownership_details) > 500:
                return JsonResponse(
                    {"error": "Ownership details must not exceed 500 characters"}, 
                    status=400
                )
            
            if len(status) > 30:
                return JsonResponse(
                    {"error": "Status must not exceed 30 characters"}, 
                    status=400
                )
            
            # Process collateral addition in database
            with connection.cursor() as cursor:
                # Check if loan exists
                cursor.execute("""
                    SELECT loan_id, amount, status 
                    FROM LOANS 
                    WHERE loan_id = %s
                """, [loan_id])
                
                loan = cursor.fetchone()
                
                if not loan:
                    return JsonResponse(
                        {"error": "Loan not found"}, 
                        status=404
                    )
                
                loan_status = loan[2]
                loan_amount = loan[1]
                
                # Optional: Warn if loan is not active
                if loan_status != 'active':
                    return JsonResponse(
                        {"warning": f"Loan status is '{loan_status}', but collateral will be added"},
                        status=200
                    )
                
                # Insert collateral record
                cursor.execute("""
                    INSERT INTO COLLATERAL_SECURITIES 
                    (loan_id, type, description, value, ownership_details, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [loan_id, collateral_type, description, value, ownership_details, status])
                
                # Get the collateral ID of the inserted record
                collateral_id = cursor.lastrowid
            
            return JsonResponse({
                "message": "Collateral security added successfully",
                "collateral_id": collateral_id,
                "loan_id": loan_id,
                "type": collateral_type,
                "description": description,
                "value": str(value),
                "ownership_details": ownership_details,
                "status": status
            }, status=201)
            
        except KeyError as e:
            return JsonResponse(
                {"error": f"Missing required field: {str(e)}"}, 
                status=400
            )
        except ValueError as e:
            return JsonResponse(
                {"error": f"Invalid data type: {str(e)}"}, 
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {"error": f"Database error: {str(e)}"}, 
                status=500
            )
    
    return JsonResponse({"error": "Only POST method allowed"}, status=405)