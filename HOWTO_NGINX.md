How to create a reverse proxy with nginx and gunicorn to serve a flask app:

Necessary installs:
 1) python3
 2) nginx
 3) gunicorn
 4) flask

Put flask files (templates, static files, flask server .py files) into `/var/www/flaskapp`

Go to `/etc/nginx/sites-available`
and make a new file called `flaskapp.conf` to set up the site configuration:
	
	server {
		listen *:80;
		server_name 54.188.2.63 ec2-54-188-2-63.us-west-2.compute.amazonaws.com;

		root /var/www/flaskapp;

		access_log /var/log/nginx/flaskapp.access.log;
		error_log /var/log/nginx/flaskapp.error.log;

		location / {
			rewrite ^/app/(.*) /$1 break;
			proxy_pass http://127.0.0.1:8000;
			proxy_set_header Host $host;
			proxy_set_header X-Real-IP ip_address;
		}
	}

then, create a symbolic link with this file and `/etc/nginx/sites-enabled/flaskapp.conf`

Using this configuration file, we are re-routing stuff from localhost:8000 to the server names (this is the reverse proxy part)

So, you need to be running the flaskapp on localhost:8000
To do this, use gunicorn

Create a flaskapp service to run gunicorn on localhost:
In `/etc/systemd/system/flaskapp.service` put:

	[Unit]
	Description=Gunicorn instance to serve flaskapp
	After=network.target

	[Service]
	User=ubuntu
	Group=www-data
	WorkingDirectory=/var/www/flaskapp
	Environment="PATH=/var/www/flaskapp"
	ExecStart=/home/ubuntu/.local/bin/gunicorn --preload --workers=3 --worker-class=gevent wsgi:app 1>~/flaskapp_parent/logs/log.out 2>~/flaskapp_parent/logs/log.err

	[Install]
	WantedBy=multi-user.target

Then start and enable the service: ```sudo systemctl start flaskapp```

Go to /var/www/flaskapp and run `sudo gunicorn --workers=5 wsgi:app`
Where `wsgi.py` runs the flask app

Look at the `restartApp.sh` file to see how to automate updating the gunicorn workers each time you make a change

