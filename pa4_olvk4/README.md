##Link to Homepage:##
- http://eecs485-10.eecs.umich.edu:5708/olvk4/pa4/
- http://eecs485-10.eecs.umich.edu:5808/olvk4/pa4/

##Database Information:##
- We overwrote our group108 database (from PA1)

##Group Name: group108##

##Members:##
Sang Jun Park (sangjunp): 
- Assist with design and implementation of Indexer.cpp, Index_Server.cpp
- Load XML to SQL
- back-end/front-end

Howard Mok (howiemok):
- Index_Server.cpp
- Load XML to SQL
- back-end / Front-end

Spencer Kim (spegkim): 
- Mainly Indexer.cpp & Index_Server.cpp

Details: 

  
##Deploy:##
- ssh username@eecs485-10.eecs.umich.edu
- virtualenv venv --distribute
- source venv/bin/activate (run for every new terminal window)
- cd /var/www/html/group108/pa4_olvk4

##From here, you can:##
- You may have to pip install requests first

1)Run SQL files:
- mysql -u group108 -phmcc group108 < sql/tbl_create.sql && mysql --local-infile -u root -phmcc group108 < load_xml.sql

2)Run Indexer/Index_Server
- cd pa4_CPP
- make clean; make;
- ./indexer ../resources/captions inverted_index.txt
- ./indexServer 6308 inverted_index.txt

3)Run web server:
- cd python
- gunicorn -b eecs485-10.eecs.umich.edu:5708 run:app &
- gunicorn -b eecs485-10.eecs.umich.edu:5808 run:app & 
- cd ..

##Webserver addresses:##
- http://eecs485-10.eecs.umich.edu:5708/olvk4/pa4/search
- http://eecs485-10.eecs.umich.edu:5808/olvk4/pa4/search

Extra:
We took 0 extra day.
