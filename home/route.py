import json
from flask import render_template, request, redirect, url_for, flash, Blueprint
from models import Albums, ProfileImg, Singles, User, Skills, MediaConfig
from models import Blog, AboutSection
import logging

logging.basicConfig(level=logging.DEBUG)

home = Blueprint(
    'home',
    __name__,
    template_folder="./../templates",
    static_folder="./../templates/home",
    static_url_path='/home/static'
)

@home.route('/')
@home.route('/Home')
def index():
    from app import db
    
    media_data = {}
    entries = MediaConfig.query.all()
    for e in entries:
        if e.key in ('streaming', 'eps', 'latest'):
            try:
                media_data[e.key] = json.loads(e.value) if e.value else {}
            except Exception:
                media_data[e.key] = {}
        else:
            media_data[e.key] = e.value or ''

    
    user = User.query.first()
    name = user.name.upper() or ""
    about = user.short_about if user else ""

    # 3. Scope Visuals (Profile & Banner)
    profile_pic_obj = ProfileImg.query.first()
    # Defaulting to None or a placeholder if images aren't set
    profile_url = profile_pic_obj.profile_picture if profile_pic_obj else None
    banner_url = profile_pic_obj.banner_img if profile_pic_obj else None

    # 4. Scope Skills (Optimized query)
    # Filter by artist_id before selecting the skill attribute
    skills_query = db.session.query(Skills.skill).all()
    skills = [s[0] for s in skills_query]
    
    # 5. Scope Blog Posts (Latest 3)
    # Using the composite index (artist_id, date)
    blogs = Blog.query.order_by(Blog.date.desc()).limit(3).all()
    if not blogs:
        blogs = []

    sections = AboutSection.query.order_by(AboutSection.order).all()
    section_data = {}
    for section in sections:
        section_data[section.section_name] = {
            'title': section.title,
            'content': json.loads(section.content) if section.content else None
        }

    # 7. Scope Discography and Media variables
    eps = media_data.get('eps', [])
    featured_playlist = media_data.get('featured_playlist', '')
    singles = Singles.query.all()
    albums = Albums.query.all() 
    print(f"profile pic: {profile_url}")

    return render_template(
        'index.html', 
        profile_pic=profile_url, 
        banner_pic=banner_url, 
        name=name, 
        short_about=about, 
        skills=skills, 
        blogs=blogs, 
        eps=eps, 
        featured_playlist=featured_playlist, 
        albums=albums, 
        singles=singles, 
        sections=section_data
    )