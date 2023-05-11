from djongo import models

class Person(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()

    class Meta:
        db_table = "person"
