# Frag-Fest Event Platform

## Things to complete

- [x] Register and Login for users  
- [x] Sign in with Steam  
- [x] Profile View and Edit  
- [x] Frontend - Home, CS:GO, FIFA, All Games, Organizers  
- [x] Front-end - The Event, Schedule, Sponsors, Sponsor-Strip, Privacy Policy  
- [x] Back-end - Team Dashboard (Join, or Create)  
- [x] Back-end - Team Dashboard (Edit Description, Remove Player, Join Notification)  

### To run on your system

- Install Python 3.6
- (for windows) Add Python installation to your PATH
- Run the following in terminal:

```
    cd frag-fest-platform
    mv .env.EXAMPLE .env
    pip install -r requirements.txt
    python manage.py collectstatic
    python manage.py migrate
    python manage.py runserver
```

Navigate to 127.0.0.1:8000 in your browser. Linux users may need to use `python3` instead of `python`.

### Contributing to front-end

 - You can open the folder in a text editor like Sublime-text, Atom, Visual Studio Code, etc.
 - To make changes in front-end, make sure you first go through [Django Templating Language](https://docs.djangoproject.com/en/1.11/ref/templates/language/) and have a knowledge of [Bootstrap v4](https://getbootstrap.com/).
 - Navigate to `portal/templates/..` to find out the template to modify.
 - You can put all static files to `portal/static/portal/...` relevant directory.


### Updating webserver

```
source bin/activate
cd frag-fest-platform
git pull origin master
python manage.py collectstatic
python manage.py migrate
sudo supervisorctl restart frag-fest
```
