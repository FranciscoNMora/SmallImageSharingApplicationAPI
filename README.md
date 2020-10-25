# Image Sharing Application

API for an image sharing application

Small scale API to support an image sharing application.

API requirements:
  1. Images have a caption, limited to 100 chars.
  2. A user can follow/unfollow another user.
  3. Current user can like a post (image).
  4. List of images for the current user (most recent first, limited to users following).
  5. List of all posts (ordered by likes).
  6. List of all users (including information on the number of following and followers).
  
## User Manual

Setup the environment (assumes that python 3.7 is installed)
```bash
git clone https://github.com/FranciscoNMora/SmallImageSharingApplicationAPI.git
cd hedgehogLab
python3.7 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run migrations
```bash
python manage.py migrate
```

Create superuser to user admin site
```bash
python manage.py createsuperuser
```

Run tests
```bash
python manage.py test --settings=PostsApp.tests.settings_tests --keepdb
```

Run application
```bash
python manage.py runserver
```

## API Documentation
The documentation of the API is available in the following URLs:
-/doc/redoc/ : ReDoc documentation
-/doc/swagger/ : SwaggerUI documentation