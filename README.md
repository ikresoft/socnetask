# socnetask
This project is using celery library for background processing during
request of enrichment data from clearbit


## Enrichment by clearbit
before you use celery you must have rabbitmq-server runing on your computer.

[RabbitMQ](https://www.rabbitmq.com/)

## INSTALL
$> virtualenv socnetask<br/>
$> source socnetask/bin/activate<br/>
$> git clone https://github.com/ikresoft/socnetask.git<br/>
$> pip install -r req.txt<br/>
$> python manage.py runserver

You can run worker by runing this command inside your virtualenv in separate terminal window:

**celery -A socnetask worker -l info**

## AUTOBOT testing tool
Same process activate your virtualenv and run<br/> python autobot.py