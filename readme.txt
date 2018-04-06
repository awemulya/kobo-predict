1. After you have all following folders in your local machine in a folder you can then proceed in the project setup. 

	a. kobocat
	b. kpi
	c. kobocat-template


2. Before you begin to install the system requirements first read the following instructions

		a. Install all the necessary requirement files in a virtual enviourment. ( Use of the virtual wrapper is encouraged. )

		b. Install latest postgres database form the official site and create database named  kobocat1.

		c. Create user = postgres and password = password and grant access to kobocat1 database.
		
		d. Enable the postgis extension in the postgres system.
		
		e. Install Mongodb from offical site.


3. From your console install the files kobocat/requirements/base.pip and kobocat/requirements/dev.pip for kobocat.

4. Install django-channels and asgi Redis Server for push notification.

5. Similarly, install the files kpi/requirements.in for kpi.

6. Install npm, nvm and node.js for kpi.

7. After generating node modules extract the webpack and run collectstatic to collect all generated staticfiles.

8. In both folders kobocat and kpi rename local_settings.sample.py to local_settings.py.
 
9. After you have sucessfully installed all dependencies run kobocat in 8001 server and kpi in 8000 server. ( Note: Both the system must be running to use the website. )





