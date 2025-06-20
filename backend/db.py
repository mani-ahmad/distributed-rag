import asyncpg
import os
from dotenv import load_dotenv
load_dotenv()

DB_URL = os.getenv('DB_URL')

async def connectDatabase():
    print(DB_URL)
    conn = await asyncpg.connect(dsn=DB_URL)
    return conn

def createTable():
    return """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS data_sources (
        data_src_id SERIAL PRIMARY KEY,
        auth_creds JSON,
        src_name VARCHAR(255),
        provider VARCHAR(255),
        username VARCHAR(255)
    );

    CREATE TABLE IF NOT EXISTS configurations (
        config_id SERIAL PRIMARY KEY,
        config_name VARCHAR(255),
        gpu VARCHAR(255),
        embedding_model VARCHAR(255),
        num_workers INTEGER,
        batch_size INTEGER,
        username VARCHAR(255) NOT NULL,
        regexpattern VARCHAR(255),
        regexreplacement VARCHAR(255),
        CONSTRAINT fk_username FOREIGN KEY (username) REFERENCES users(username)
    );

    CREATE TABLE IF NOT EXISTS job_details (
        job_id SERIAL PRIMARY KEY,
        job_start_time TIMESTAMP,
        config_id INTEGER,
        datasource_id INTEGER,
        user_id INTEGER,
        job_name VARCHAR(255),
        FOREIGN KEY (config_id) REFERENCES configurations(config_id),
        FOREIGN KEY (datasource_id) REFERENCES data_sources(data_src_id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS endpoints (
        job_id INTEGER PRIMARY KEY,
        chat_endpoint VARCHAR(255),
        search_endpoint VARCHAR(255),
        FOREIGN KEY (job_id) REFERENCES job_details(job_id)
    );

    """


async def createDatabase():
    conn = await connectDatabase()
    try:
        query = createTable()
        await conn.execute(query)
        print("Tables created successfully.")
    except Exception as error:
        print("Error while creating tables:", error)
        raise
    finally:
        await conn.close()
