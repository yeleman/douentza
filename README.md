Douentza
========

Requires Python 3.3 or Python 2.7.

/!\ If running on Python2 (only 2.7 supported), you must install `unicodecsv`.

/!\ The system was created specifically for the Mali Hotline and thus is not properly packaged to be duplicated.

Server configuration details
-----
To facilitate your setup, consider copying and adjusting the following configurations.1.	Create a user account (`douentza` at `/home/douentza`)2.	Clone [github project](https://github.com/yeleman/douentza)3.	Create a virtualenv (`douentzaenv`)4.	Edit the settings at `douentza/settings_local.py` to change the phone numbers of your SIM cards5.	Edit reply message at `douentza/urls.py`6.	Change the operators names and guessing function (`operator_from_mali_number`) at `douentza/utils.py`7.	Install the dependencies in the virtualenv `pip install –r requirements.pip`8.	Create the DB and super user account with `./manage.py syncdb`9.	Customize the `douentza/fixtures/Ethnicity.json` file10.	Customize the `douentza/fixtures/Entity.json` file11.	Customize the `douentza/fixtures/Cluster.json` file12.	Load your fixtures with `./manage.py loaddata fixtures/*.json`13.	Create folders for cached files `mkdir –p cached_data/protected`.14.	Install and configure nginx1. Use the Django Admin UI (`/admin/`) to create user accounts for agents and assign them clusters.
1. Install FondaSMS app on the phones.1. Configure the phones to use the server URL (`http://server-addr.tld/fondasms`).

Sample nginx configuration-----
    server {    listen   80;    server_name douentza.com;    root /home/douentza/douentza/;    ## Compression    gzip              on;    gzip_buffers      16 8k;    gzip_comp_level   4;    gzip_http_version 1.0;    gzip_min_length   1280;    gzip_types        text/plain text/csv text/css application/x-javascript text/xml application/json application/xml application/xml+rss text/javascript image/x-icon image/bmp application/font-woff;    gzip_vary         on;    location /static/ {        if ($query_string) {            expires max;        }	alias /home/douentza/douentza/static/;	autoindex on;    }    location /protected/ {        expires max;        root /home/douentza/douentza/cached_data/;	internal;    }    location /admin_static/ {	root /home/douentza/douentzavenv/lib/python3.3/site-packages/django/contrib/admin/media;    }    location / {	add_header 'Access-Control-Allow-Origin' "*";        add_header 'Access-Control-Allow-Credentials' "true";	proxy_pass              http://127.0.0.1:8887;	proxy_set_header        X-Real-IP  $remote_addr;    }    }
