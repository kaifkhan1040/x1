from django.db import models
from users.models import CustomUser

class LandloadEmailVerify(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    link=models.CharField(max_length=500)
    verify = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)