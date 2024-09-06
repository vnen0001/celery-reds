from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db import connections
from django.http import JsonResponse
import random
from django.views.decorators.http import require_http_methods
import json
from .powerball import simulate_and_return_lists
from dotenv import load_dotenv
import os
creds = load_dotenv()
correct = os.environ.get('PASSWORD')
@api_view(['POST'])
def verify(request):
    if request.method =='POST':
        password = request.data.get('password')
    if password == correct:
        return JsonResponse({'status': 'success'}, status=200)
    else:
        return JsonResponse({'status': 'error', 'message': 'Incorrect password'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

class GraphData(APIView):
    @staticmethod
    def process_suicide_data(rows, include_expenditure):
        result = []
        years = set()
        
        for row in rows:
            year = row[1]  # Assuming Year is the second column
            years.add(year)
        
        for year in sorted(years):
            year_data = {
                'year': str(year),
                'Male': 0,
                'Female': 0
            }
            if include_expenditure:
                year_data['total_expenditure'] = 'N/A'
            
            for row in rows:
                if row[1] == year:
                    gender = row[0]
                    suicide_number = row[2]
                    year_data[gender] = suicide_number
                    if include_expenditure and len(row) > 3:
                        year_data['total_expenditure'] = row[3] if row[3] is not None else 'N/A'
            
            result.append(year_data)
        return result
    
    def get(self,request,format=None):
        
        try:
            include_expenditure = request.query_params.get('include_expenditure', 'false').lower() == 'true'
            with connections['default'].cursor() as cursor:
                if include_expenditure:
                    cursor.execute("""
                SELECT s.Gender, s.Year, SUM(s.Suicide_Number) AS total, t.Aust AS total_expenditure
                    FROM dbo.suicide_number_data s
                    LEFT JOIN (
                        SELECT LEFT(Financial_Year, 4) AS Year, Aust
                        FROM DBO.Total_expenditure
                    ) t ON s.Year = t.Year
                    GROUP BY s.Gender, s.Year, t.Aust
                    ORDER BY s.Year, s.Gender
            """)
                    
                else:
                     cursor.execute("""
                    SELECT Gender, Year, SUM(Suicide_Number) AS total
                    FROM dbo.suicide_number_data
                    GROUP BY Gender, Year
                    ORDER BY Year, Gender
                """)
                rows = cursor.fetchall()
            
        # Define column names manually
            # data = {}
            # for row in rows:
            #     year, gender, total,gambling_exp = row
            #     if year not in data:
            #         data[year] = {'year': year, 'Male': 0, 'Female': 0,'gambling_exp':gambling_exp if gambling_exp is not None else 'N/A'}
            #     data[year][gender] = total

            # # Convert the dictionary to a list for JSON serialization
            # result = list(data.values())

            processed_data = self.process_suicide_data(rows, include_expenditure)
            return JsonResponse(processed_data, safe=False)
    
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
 
    
class SpiderData(APIView):
    def get(self,request,format=None):
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute("""
-- SQL Query to get top 5 mechanisms for male and female across all years
SELECT 
    Sex,
    Agegroup,
    SUM(Values_) as total_count
FROM 
   [dbo].[NewTable]
WHERE 
    Sex IN ('Males', 'Females')
    AND Agegroup != 'Total'
GROUP BY 
    Sex, Agegroup
HAVING 
    Sex = 'Males' AND Agegroup IN (
        SELECT TOP 5 Agegroup
        FROM [dbo].[NewTable]
        WHERE Sex = 'Males' AND Agegroup != 'Total'
        GROUP BY Agegroup
        ORDER BY SUM(Values_) DESC
    )
    OR
    Sex = 'Females' AND Agegroup IN (
        SELECT TOP 5 Agegroup
        FROM [dbo].[NewTable]
        WHERE Sex = 'Females' AND Agegroup != 'Total'
        GROUP BY Agegroup
        ORDER BY SUM(Values_) DESC
    )
ORDER BY 
    Sex, total_count DESC







        """)
                rows = cursor.fetchall()
                data = []
                for row in rows:
                    data.append({
                    'Sex': row[0],
                    'Agegroup': row[1],
                    'total_count': row[2]
                })

            return JsonResponse(data, safe=False)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       

class PowerballSimulator_dj(APIView):
    def get(self,request):
        max_tickets = request.GET.get('max_tickets',1000)  # Default to 1000 if not provided
        max_tickets = int(max_tickets)
        tickets, losses ,avg= simulate_and_return_lists(max_tickets)
        return JsonResponse({'tickets': tickets, 'losses': losses})
    
class ParallelCoordinates(APIView):
    def get(self,request):
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute("select * from [dbo].[Different_games_expenditure]")
                rows = cursor.fetchall()
                data = []
                for row in rows:
                    data.append({
                        'Year':row[0],
                        'Casino':row[1],
                        'Gaming_machine':row[2],
                        'Interactive_gaming':row[3],
                        'Keno':row[4],
                        'Lotteries':row[5],
                        'Minor_gaming':row[6],
                        'Wagering':row[7],
                        'Total':row[8]

                    })

            return JsonResponse(data, safe=False)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)