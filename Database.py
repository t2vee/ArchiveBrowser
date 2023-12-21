from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:linuxmoment@localhost:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ModBasedUponModrinthMetaData(Base):
    __tablename__ = 'mods'

    id = Column(String, primary_key=True)
    slug = Column(String, index=True)
    project_type = Column(String)
    team = Column(String)
    title = Column(String)
    description = Column(String)
    body = Column(String)
    published = Column(DateTime)
    updated = Column(DateTime)
    approved = Column(DateTime)
    status = Column(String)
    license = Column(JSON)
    client_side = Column(String)
    server_side = Column(String)
    downloads = Column(Integer)
    followers = Column(Integer)
    categories = Column(JSON)
    additional_categories = Column(JSON)
    game_versions = Column(JSON)
    loaders = Column(JSON)
    versions = Column(JSON)
    icon_url = Column(String)
    issues_url = Column(String)
    source_url = Column(String)
    wiki_url = Column(String)
    discord_url = Column(String)
    donation_urls = Column(JSON)
    gallery = Column(JSON)
    color = Column(Integer)
    thread_id = Column(String)
    monetization_status = Column(String)
    date_metadata_fetched = Column(DateTime)

    def __repr__(self):
        return f"<ModBasedUponModrinthMetaData(title='{self.title}', id='{self.id}')>"

    @staticmethod
    def from_json(json_data):
        """
        Create a ModrinthMod instance from JSON data.
        """
        return ModBasedUponModrinthMetaData(
            id=json_data['id'],
            slug=json_data['slug'],
            project_type=json_data['project_type'],
            team=json_data.get('team'),
            title=json_data['title'],
            description=json_data['description'],
            body=json_data.get('body', ''),
            published=datetime.fromisoformat(json_data['published']),
            updated=datetime.fromisoformat(json_data['updated']),
            approved=datetime.fromisoformat(json_data['approved']) if json_data['approved'] else None,
            status=json_data['status'],
            license=json.dumps(json_data['license']),
            client_side=json_data['client_side'],
            server_side=json_data['server_side'],
            downloads=json_data['downloads'],
            followers=json_data['followers'],
            categories=json.dumps(json_data['categories']),
            additional_categories=json.dumps(json_data['additional_categories']),
            game_versions=json.dumps(json_data['game_versions']),
            loaders=json.dumps(json_data['loaders']),
            versions=json.dumps(json_data['versions']),
            icon_url=json_data['icon_url'],
            issues_url=json_data['issues_url'],
            source_url=json_data['source_url'],
            wiki_url=json_data.get('wiki_url'),
            discord_url=json_data.get('discord_url'),
            donation_urls=json.dumps(json_data['donation_urls']),
            gallery=json.dumps(json_data['gallery']),
            color=json_data['color'],
            thread_id=json_data['thread_id'],
            monetization_status=json_data['monetization_status'],
            date_metadata_fetched=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )
