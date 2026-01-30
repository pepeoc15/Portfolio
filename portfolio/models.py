from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=50)
    proficiency = models.IntegerField()  # %, 1–100

    def __str__(self): return self.name

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='projects/', blank=True)

    def __str__(self): return self.title

class Experience(models.Model):
    company = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    start = models.DateField()
    end = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self): return f"{self.role} @ {self.company}"
