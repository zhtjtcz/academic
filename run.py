import os
import platform

# pipreqs . --encoding=utf8 --force
os.system("pip install -r requirements.txt")

os.system("python manage.py makemigrations")
os.system("python manage.py migrate")

if platform.system() == "Windows":
	os.system("python manage.py runserver")
else:
	os.system("nohup python manage.py runserver 0.0.0.0:8000 & \n")
	print("The backend is running!")