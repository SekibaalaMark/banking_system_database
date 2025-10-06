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