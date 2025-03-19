from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, BINARY, BigInteger
from sqlalchemy.ext.declarative import declarative_base

# Initialize SQLAlchemy
db = SQLAlchemy()

# Define the Base model for SQLAlchemy
Base = declarative_base()

# Define the User Model
class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'public'}  # Adjust schema if necessary

    user_id = Column(Integer, primary_key=True)  # Integer type for user_id
    firstname = Column(String)  # String type for first name
    lastname = Column(String)  # String type for last name
    password = Column(Text)  # Text type for password
    phone = Column(String)  # String type for phone number
    salt = Column(BINARY)  # Bytea type for salt (binary data)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, firstname={self.firstname}, lastname={self.lastname}, phone={self.phone})>"

# Define the UserTags Model
class UserTags(Base):
    __tablename__ = 'user_tags'
    __table_args__ = {'schema': 'public'}  # Adjust schema if necessary

    user_id = Column(Integer, primary_key=True)  # Integer type for user_id
    tag = Column(String, primary_key=True)  # String type for tag (used as part of the primary key)
    expiry = Column(BigInteger)  # BigInteger type for expiry timestamp

    def __repr__(self):
        return f"<UserTags(user_id={self.user_id}, tag={self.tag}, expiry={self.expiry})>"
