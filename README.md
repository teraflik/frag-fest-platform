# Frag-Fest Event Platform

## Things to complete
[x] Register and Login for users
[x] Sign in with Steam
[x] Profile View and Edit
[x] Frontend - Home, CS:GO, FIFA, All Games, Organizers
[ ] Front-end - The Event, Schedule, Sponsors, Sponsor-Strip, Privacy Policy 
[ ] Team Dashboard (Join, or Create)
[ ] Team Dashboard (Edit Description, Remove Player, Join Notification)

### To update the webserver with latest commit
```
source bin/activate
cd urban-train
git pull origin master
python manage.py collectstatic
python manage.py migrate
sudo supervisorctl restart urban-train
```