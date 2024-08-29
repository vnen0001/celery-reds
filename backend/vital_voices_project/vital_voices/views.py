from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connections
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

# Create your views here.
class GraphData(APIView):
    def get(self,request,format=None):
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute("""
            SELECT Gender, Year, SUM(Suicide_Number) AS total
            FROM dbo.suicide_number_data
            GROUP BY Gender, Year
            ORDER BY Year, Gender
        """)
                rows = cursor.fetchall()
        
        # Define column names manually
            data = {}
            for row in rows:
                year, gender, total = row
                if year not in data:
                    data[year] = {'year': year, 'Male': 0, 'Female': 0}
                data[year][gender] = total

            # Convert the dictionary to a list for JSON serialization
            result = list(data.values())

            return JsonResponse(result, safe=False)
    
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
