#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create databases for each microservice
    CREATE DATABASE user_service;
    CREATE DATABASE declaration_service;
    CREATE DATABASE form_service;
    CREATE DATABASE rule_engine_service;
    CREATE DATABASE review_service;
    CREATE DATABASE case_service;
    CREATE DATABASE notification_service;
    CREATE DATABASE analytics_service;

    -- Grant permissions
    GRANT ALL PRIVILEGES ON DATABASE user_service TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE declaration_service TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE form_service TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE rule_engine_service TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE review_service TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE case_service TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE notification_service TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE analytics_service TO $POSTGRES_USER;
EOSQL

