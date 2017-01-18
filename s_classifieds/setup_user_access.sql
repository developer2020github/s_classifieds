--This script will setup user catalog for postgressql database
--To do so
--1. Run create_database
--2. If desired, run populate_databse
--3. Connect to database s_classifieds as superuser (postgres)
--  psql -U postgres s_classifieds
--  and run script from psql
-- On windows:
--\i 'C:/s_classifieds/setup_user_access.sql
-- On Linux:
--\ \i path_to_sql_file
create user catalog with password 'catalog';

REVOKE CONNECT ON DATABASE s_classifieds FROM PUBLIC;

GRANT CONNECT
ON DATABASE s_classifieds
TO catalog;

REVOKE ALL
ON ALL TABLES IN SCHEMA public
FROM PUBLIC;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA public
TO catalog;

GRANT USAGE, SELECT ON ALL SEQUENCES in SCHEMA public TO catalog;

ALTER DEFAULT PRIVILEGES
   FOR USER catalog
   IN SCHEMA public
   GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO catalog;