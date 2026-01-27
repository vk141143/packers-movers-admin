-- Connect as superuser (postgres) and run this:
-- psql -h public-primary-pg-inmumbaizone2-189645-1657841.db.onutho.com -U postgres -d defaultdb

GRANT CREATE ON SCHEMA public TO dbadmin;
GRANT ALL PRIVILEGES ON SCHEMA public TO dbadmin;
