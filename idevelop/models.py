from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank = True, null= True)
    bio = models.CharField(blank=True, max_length=150)
    achievements = models.CharField(blank=True, max_length=150)
    friends = models.ManyToManyField('self', symmetrical=True, related_name='student_friends')
    answers = models.JSONField(default = dict)
    code_storage = models.JSONField(default = dict)

    def __str__(self):
        return f'{self.user.username} Student Profile'



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank = True, null= True)
    date_of_birth = models.DateField(null=True, blank=True) 

    def __str__(self):
        return f'{self.user.username} Profile'

    
class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Friend request from {self.from_user} to {self.to_user}"


class CollabBox(models.Model):
    text_value = models.TextField("Collaboration Text", blank=True, null=True)
    allowed_viewers = models.ManyToManyField(User, related_name="viewable_collab_boxes", blank=True)
    allowed_editors = models.ManyToManyField(User, related_name="editable_collab_boxes", blank=True)
    owner = models.ForeignKey(User, related_name="owned_collab_boxes", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def ready_response(cls, box_id):  
        try:
            box = cls.objects.get(id=box_id)
            box_dict = {
                'id': box.id,
                'text': box.text_value,
                'user': box.owner.username,
            }
            return box_dict
        except cls.DoesNotExist:
            return None
        

