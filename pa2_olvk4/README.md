Group Name: group108

Members:
Sang Jun Park (sangjunp): Worked on variety of things, mostly:
- album/albums/user
- sql

Howard Mok (howiemok): Worked on variety of things, mostly:
- pic
- session

Spencer Kim (spegkim): Worked on variety of things, mostly:
- session
- shared
- authentication


Deploy:

virtualenv venv --distribute

source venv/bin/activate (run for every new terminal window)

ssh username@eecs485-10.eecs.umich.edu

cd /var/www/html/group108/pa2_olvk4


From here, you can:

1)Run SQL files:

mysql -u group108 -phmcc group108pa2 < sql/tbl_create.sql

mysql -u group108 -phmcc group108pa2 < sql/load_data.sql


2)Run web server:
cd python
gunicorn -b eecs485-10.eecs.umich.edu:5908 run:app &

        OR......

gunicorn -b eecs485-10.eecs.umich.edu:6008 run:app &


Webserver address:

http://eecs485-10.eecs.umich.edu:5908/olvk4/pa2/

http://eecs485-10.eecs.umich.edu:6008/olvk4/pa2/


Extra:
We took 1 extra day.
