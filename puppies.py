###configuration###

import sys

from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

###Class definitions###
class Shelter(Base):

	__tablename__ = 'shelter'

	id = Column(Integer, primary_key = True)
	name = Column(String(80), nullable = False)
	address = Column(String(100))
	city = Column(String(80), nullable = False)
	state = Column(String(80))
	zipCode = Column(Integer, nullable = False)
	website = Column(String(120))

class Puppy(Base):

	__tablename__ = 'puppy'

	name = Column(String(80), primary_key = True)
	dateOfBirth = Column(Date, nullable = False)
	gender = Column(String(10), nullable = False)
	weight = Column(Numeric(10), nullable = False)
	shelter_id = Column(Integer, ForeignKey('shelter.id'))
	shelter = relationship(Shelter)

###End of File###
engine = create_engine('sqlite:///puppies.db')

Base.metadata.create_all(engine)