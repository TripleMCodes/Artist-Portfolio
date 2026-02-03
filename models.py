from sqlite3 import Date
from app import db
from flask_login import UserMixin
# from sqlalchemy.dialects.postgresql import JSONB
# from sqlalchemy import JSON
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# ============================================================================
# MULTI-TENANT MODELS (Artist/Tenant Support)
# ============================================================================
# 
# Data isolation strategy:
#   - Artist model as the top-level tenant
#   - All tenant-scoped models include artist_id foreign key + index
#   - Queries must always filter by artist_id
#   - Cascading deletes: ON DELETE CASCADE to clean up artist data
#
# Future: Add tenant context middleware/fixtures for query scoping
# ============================================================================


# class Artist(db.Model):
#     """
#     Represents an independent tenant/artist in the system.
    
#     All artist-owned content (blogs, events, media, etc.) links to this model
#     via artist_id. Each artist has completely isolated data.
    
#     Attributes:
#         id: Unique artist identifier
#         name: Artist display name
#         slug: URL-safe identifier (e.g., 'aura', 'john-doe')
#         email: Primary contact email
#         short_about: Brief bio/description
#         bio: Extended biography
#         is_active: Soft-delete flag; use for disabling artist without data loss
#         created_at: Timestamp of artist creation
#         updated_at: Last modification timestamp
    
#     Relationships:
#         admin: One-to-one with Admin (artist's login account)
#         blogs: One-to-many with Blog
#         events: One-to-many with Event
#         galleries: One-to-many with Gallery
#         services: One-to-many with Service
#         faqs: One-to-many with FAQ
#         linktree_links: One-to-many with LinktreeLink
#         media_config: One-to-many with MediaConfig (artist-specific config)
#     """
#     __tablename__ = "artist"

#     id = db.Column(db.Integer, primary_key=True, nullable=False)
#     name = db.Column(db.Text, nullable=False)  # Display name
#     slug = db.Column(db.String(128), nullable=False, unique=True)  # URL-safe identifier
#     email = db.Column(db.Text, nullable=False)
#     short_about = db.Column(db.Text, nullable=True)
#     bio = db.Column(db.Text, nullable=True)
#     is_active = db.Column(db.Boolean, default=True, nullable=False)
#     created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
#     updated_at = db.Column(db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now())

#     # Relationships
#     admin = db.relationship("Admin", back_populates="artist", uselist=False, cascade="all, delete-orphan")

#     def __repr__(self):
#         return f"<Artist {self.slug}>"


class Admin(db.Model, UserMixin):
    __tablename__ = "admin"

    uid = db.Column(db.Integer, primary_key=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    totp_secret = db.Column(db.String(32), nullable=True)
    totp_enabled = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"{self.email}"
    
    def get_id(self):
        return str(self.uid)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
        

class User(db.Model, UserMixin):
    __tablename__ = "user"

    uid = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    short_about = db.Column(db.Text, nullable=False)

    def get_id(self):
        return str(self.uid)

class Skills(db.Model, UserMixin):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    skill = db.Column(db.Text, nullable=False)


class ProfileImg(db.Model, UserMixin):
    __tablename__ = 'ProfileImg'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    profile_picture = db.Column(db.Text, nullable=True)
    banner_img = db.Column(db.Text, nullable=True)

class Blog(db.Model):
    __tablename__ = 'blog'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    reading_time = db.Column(db.Integer, nullable=True)

    # def __repr__(self):
    #     return f"<Blog {self.title} (artist_id={self.artist_id})>"


class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.Text, nullable=True)
    price_monthly = db.Column(db.Float, nullable=True)
    price_yearly = db.Column(db.Float, nullable=True)


class FAQ(db.Model):
    __tablename__ = 'faq'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=False)
    nda_requested = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    read = db.Column(db.Boolean, default=False)


class Gallery(db.Model):
    __tablename__ = 'gallery'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'image' or 'video'
    url = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=True)


class MediaConfig(db.Model):
    __tablename__ = 'media_config'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    key = db.Column(db.String(64), nullable=False)
    value = db.Column(db.Text, nullable=True)  # JSON string or plain text

class Singles(db.Model):
    __tablename__ = 'singles'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(64), nullable=False)
    artist_name = db.Column(db.String(64), nullable=False)
    album = db.Column(db.String(64), nullable=False)
    links = db.Column(db.Text, nullable=False)
    buy_link = db.Column(db.Text, nullable=True)


class Albums(db.Model):
    __tablename__ = 'albums'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    artist_name = db.Column(db.String(128), nullable=False)
    released_date = db.Column(db.Date, nullable=False)
    link = db.Column(db.Text, nullable=False)
    buy_link = db.Column(db.Text, nullable=True)


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=True)
    location = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())


class AboutSection(db.Model):
    __tablename__ = 'about_section'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    section_name = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)  # JSON string for complex data
    order = db.Column(db.Integer, nullable=False, default=0)


class HeroAbout(db.Model): 
    __tablename__ = "hero_about"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    hero_title = db.Column(db.Text, nullable=False)
    hero_brief  = db.Column(db.Text, nullable=False)

class FoundationAbout(db.Model):
    __tablename__ = "foundation_about"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    paragraphs = db.Column(db.Text, nullable=False)


class Journey(db.Model):
    __tablename__ = "journey"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    
class Expertise(db.Model):
    __tablename__ = 'expertise'

    exp_id = db.Column(db.Integer, primary_key=True, nullable=False)
    expertise = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    icon = db.Column(db.Text, nullable=False)

class Testimonials(db.Model):
    __tablename__ = "testimonials"

    t_id = db.Column(db.Integer, primary_key=True, nullable=False)
    artist_name = db.Column(db.Text, nullable=False)
    testimonial = db.Column(db.Text, nullable=False)
    artist_social = db.Column(db.Text, nullable=False)


class LinktreeLink(db.Model):
    __tablename__ = 'linktree_link'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.Text, nullable=False)  # Button text with emoji
    url = db.Column(db.Text, nullable=False)
    is_secondary = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    

class LinktreeConfig(db.Model):
    __tablename__ = 'linktree_config'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    avatar = db.Column(db.Text, nullable=False, default='A')
    name = db.Column(db.Text, nullable=False, default='Artist')
    handle = db.Column(db.Text, nullable=False, default='')
    bio = db.Column(db.Text, nullable=False, default='')
    email = db.Column(db.Text, nullable=False, default='')

