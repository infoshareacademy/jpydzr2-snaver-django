# Snaver

## Half snake, half saver, all money

<img src="/docs/images/logo.png" alt="Snaver" width="468" height="375"/>

## Setup local development environment

1. Clone this repository
2. Open cloned folder in PyCharm
3. Click `Add configuration`
   1. Set `Name` to whatever you want to name your configuration, 
      for example: `snaver`
   2. Set `Host` to `localhost`
   3. Apply
2. Create a local database if you plan to use postgres.
3. In `/projects` folder create a `local_settings.py` file based on
   `local_settings.example.py`.
    * Take the database info from the step above.
    * You can use below code to generate the SECRET_KEY:
       ```python
       from django.core.management.utils import get_random_secret_key  
    
       get_random_secret_key()
       ```
4. Populate the database:
   ```bash
   python manage.py migrate
   ```
5.  Create local superuser account to log in on `/admin` page:
   ```bash
   python manage.py createsuperuser
   ```

### External Links

* [Jira](https://jira.is-academy.pl/secure/RapidBoard.jspa?rapidView=423&projectKey=JPYDZR2SN)



