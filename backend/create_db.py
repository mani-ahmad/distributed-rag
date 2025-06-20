import asyncio
import db as database

if __name__ == "__main__":
    asyncio.run(database.createDatabase())
    print("Done making table")