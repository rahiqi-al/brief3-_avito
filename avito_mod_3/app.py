from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import pandas as pd
from datetime import date
import os



DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:ali@localhost:5432/avito_mod")
engine = create_engine(DATABASE_URL)
    

# Define the base class for SQLAlchemy models
Base = declarative_base()

# AnnonceEquipement model 
class AnnonceEquipement(Base):
    __tablename__ = 'annonce_equipement'
    
    annonce_id = Column(Integer, ForeignKey('annonces.id'), primary_key=True)
    equipement_id = Column(Integer, ForeignKey('equipements.id'), primary_key=True)
    
    # Define relationships to Annonce and Equipement
    annonce = relationship("Annonce", back_populates="equipements")
    equipement = relationship("Equipement", back_populates="annonces")

# Annonce model
class Annonce(Base):
    __tablename__ = 'annonces'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(String)  
    datetime = Column(DateTime, nullable=False)
    nb_rooms = Column(Integer)
    nb_baths = Column(Integer)
    surface_area = Column(Float)
    link = Column(String)
    city_id = Column(Integer, ForeignKey('villes.id'), nullable=False)
    
    # Relationships
    ville = relationship("Ville", back_populates="annonces")
    equipements = relationship("AnnonceEquipement", back_populates="annonce")

# Ville model
class Ville(Base):
    __tablename__ = 'villes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    # Relationship
    annonces = relationship("Annonce", back_populates="ville")

# Equipement model
class Equipement(Base):
    __tablename__ = 'equipements'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    # Relationship
    annonces = relationship("AnnonceEquipement", back_populates="equipement")

# Database connection setup 
# PostgreSQL URL
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

file_path = r'appartemetn.csv'
df = pd.read_csv(file_path)

# Insert data into database
for _, row in df.iterrows():
    # Create  Ville
    city = session.query(Ville).filter_by(name=row['city_name']).first()
    if not city:
        city = Ville(name=row['city_name'])
        session.add(city)
        session.commit()
    
    # Create Annonce
    annonce = Annonce(
        title=row['title'],
        price=row['price'],
        datetime=pd.to_datetime(row['datetime']),
        nb_rooms=row['nb_rooms'],
        nb_baths=row['nb_baths'],
        surface_area=row['surface_area'],
        link=row['link'],
        city_id=city.id
    )
    session.add(annonce)
    
    # Create  Equipements 
    equipement_names = row['equipements'].split('/')
    for equip_name in equipement_names:
        equipement = session.query(Equipement).filter_by(name=equip_name.strip()).first()
        if not equipement:
            equipement = Equipement(name=equip_name.strip())
            session.add(equipement)
            session.commit()
        
        # Link Annonce and Equipement via AnnonceEquipement
        annonce_equipement = AnnonceEquipement(annonce=annonce, equipement=equipement)
        session.add(annonce_equipement)
    
    # Commit the annonce after adding all relationships
    session.commit()

# when you re using qieries look and use ERD diagrame it make it eazier

# get all the annonce with city name = fés
annonce_fes = session.query(Annonce).join(Ville).filter(Ville.name == 'fés').all()

# get all the annonce  with nb_bath> 2 and nb_rooms<3
annonce_nb_bath_rooms = session.query(Annonce).filter(Annonce.nb_baths > 2 ,Annonce.nb_rooms<3).all()

# get all annonce with a specefied equipement 
annonce_equipement_1 = session.query(Annonce).join(AnnonceEquipement).join(Equipement).filter(Equipement.name == 'Piscine').all()

# get all the annonce that there date is superieur the a date 
specific_date = date(2024,2,12)
annonce_date = session.query(Annonce).filter(Annonce.datetime < specific_date).all()


# Close the session after insertion
session.close()
