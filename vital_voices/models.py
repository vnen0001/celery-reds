from django.db import models

# Create your models here.
class SelfHarm(models.Model):
    
    name= models.CharField(max_length=100)


    class Meta:
        db_table = 'intentional_self_harm_by_state'
        managed=False