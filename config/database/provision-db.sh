# create role
#create a role for the database if it doesn't exist
# set up database
# create database if it doesn't exist
# add extensions to database
su postgres -c "psql -d nismod_smif -q -c \"CREATE EXTENSION IF NOT EXISTS postgis;\""
su postgres -c "psql -d nismod_smif -q -c \"CREATE EXTENSION IF NOT EXISTS btree_gist;\""
su postgres -c "psql -d nismod_smif -q -c \"CREATE EXTENSION IF NOT EXISTS btree_gin;\""
su postgres -c "psql -d nismod_smif -q -c \"CREATE EXTENSION IF NOT EXISTS intarray;\""