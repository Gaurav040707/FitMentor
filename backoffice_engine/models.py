from django.db import models

# Create your models here.
class Basemodel(models.Model):
    id = models.AutoField(primary_key=True)
    created_id = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
      
    class Meta:
        abstract = True

class User(Basemodel):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    otp = models.CharField(max_length=6)
    otp_used= models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'user'
        
    def __str__(self):
         return f"{self.id} -{self.name} - {self.email}"    
    
class PlanDetails(Basemodel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField()
    duration_days = models.IntegerField()
    credits = models.IntegerField(null=True,blank=True)

    class Meta:
        db_table = "plan_Details"
        verbose_name = "plan Detail"
        verbose_name_plural = "plan Detail"

    def __str__(self):
        return f"{self.id} - {self.name}"

class Subscription(Basemodel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(PlanDetails, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(default="active")

    class Meta:
        db_table = "Subscription"

    def __str__(self):
        return f"{self.user} - {self.plan}"


class Feedback(Basemodel):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    comment = models.TextField(max_length=500)

    class Meta:
        db_table="feedback"
    def __str__(self):
        return f"{self.user.id} - {self.user.name} - {self.comment} "
    
  
class User_health(Basemodel):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    gender = models.CharField(max_length=10)
    age = models.IntegerField(null=True, blank=True)
    bmi = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    medical_conditions = models.TextField(null=True, blank=True)

    class Meta:
         
        db_table ="user_health"
    def __str__(self):
        return f"Chat by -  {self.id} - {self.user} - {self.gender} - {self.age} - {self.bmi} - {self.height} - {self.weight} - {self.medical_conditions}" 

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.title or f"Chat {self.id}"
    
class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.name}: {self.message[:30]}"