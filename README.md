# WORK IN PROGRESS
Q: What's happened and how it works?\
A: I successfully merged two branches (index + migrate)

## About MIGRATION
It allow us to migrate all class model into table of our destination databases. \
`py manage.py db init` - to initialize migration folder.\
`py manage.py db upgrade` - to read model and prepare. \
`py manage.py db migrate` - to create a "point" in you destination database. \
After this you must try again with `upgrade` and `migrate` to migrate you model into table completely.
 
 ## About INDEX
 (Comment from Alex): I don't undersstand what he did. 
 ### STAS! EDIT THIS README!
 


