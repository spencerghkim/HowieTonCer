Group Name: group108

Members:
Sang Jun Park (sangjunp): Worked on variety of things, mostly:
- most caption-related things, both frontend and backend
- Initial verification of backend routes test flows

Howard Mok (howiemok): Worked on variety of things, mostly:
- most favorites-related things, both frontend and backend
- Most development was done in paired programming

Spencer Kim (spegkim): primarily "managed" development and assisted in development problems came around
- Gave ideas for test flows, reviewed code, etc. 

Deploy:

ssh username@eecs485-10.eecs.umich.edu

virtualenv venv --distribute

source venv/bin/activate (run for every new terminal window)

cd /var/www/html/group108/pa3_olvk4

From here, you can:

1)Run SQL files:

mysql -u group108 -phmcc group108pa3 < sql/tbl_create.sql && mysql -u group108 -phmcc group108pa3 < sql/load_data.sql && mysql -u group108 -phmcc group108pa3 < sql/pa3_sql.sql

2)Run web server:

cd python

gunicorn -b eecs485-10.eecs.umich.edu:6108 run:app &

gunicorn -b eecs485-10.eecs.umich.edu:6208 run:app & 

cd ..

3)Run test_pic_apy.py: (You may have to pip install requests first)

python test_pic_api.py http://eecs485-10.eecs.umich.edu:6108/olvk4/pa3

4)Reload SQL database by re-running step 1. 

Webserver addresses:

http://eecs485-10.eecs.umich.edu:6108/olvk4/pa3/

http://eecs485-10.eecs.umich.edu:6208/olvk4/pa3/


Extra:
We took 0 extra day.
