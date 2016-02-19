Group Name: group108

Members:
Sang Jun Park (sangjunp): Mainly worked on album.py & album.html
Howard Mok (howiemok): Mainly worked on albums.py & albums.html
Spencer Kim (spegkim): Worked on pic.py & pic.html

Deploy:
virtualenv venv --distribute
source venv/bin/activate (run for every new terminal window)
ssh username@eecs485-10.eecs.umich.edu
cd /var/www/html/group108/pa1_olvk4

From here, you can:

1)Run SQL files:
cd sql
mysql -u group108 -phmcc group108 < tbl_create.sql
mysql -u group108 -phmcc group108 < load_data.sql

If you wish to proceed to #2, do:
cd ..

2)Run web server:
cd python
gunicorn -b eecs485-10.eecs.umich.edu:5708 run:app
        OR
gunicorn -b eecs485-10.eecs.umich.edu:5808 run:app

Copy the link that starts with "eecs" and ends with the 4 numbers, then add /olvk4/pa1/ to
access our webserver!!!

Extra:
We took 0 extra days.
