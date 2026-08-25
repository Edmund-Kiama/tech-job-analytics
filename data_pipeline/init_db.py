from database import Base, engine
from helper import CommentPrinter

def initialize_database(): 
    CommentPrinter("Initializing the database...")
    Base.metadata.create_all(engine)
    CommentPrinter("Database initialized successfully.")

if __name__ == "__main__":
    initialize_database()