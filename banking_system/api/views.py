from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import json

@csrf_exempt
def add_branch(request):
    if request.method == "POST":
        # Check if it's JSON or form-data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Branch (branch_name, Location, phone_contact, manager_id)
                VALUES (%s, %s, %s, %s)
            """, [
                data['branch_name'], 
                data['location'], 
                data['phone_contact'], 
                data['manager_id']
            ])
        return JsonResponse({"message": "Branch added"})
    

    