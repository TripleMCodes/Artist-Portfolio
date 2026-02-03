from flask import render_template, Blueprint
from models import Gallery, User
from urllib.parse import urlparse, parse_qs

gallery = Blueprint(
    'gallery',
    __name__,
    template_folder='html css js',
    static_folder='html css js',
    static_url_path='/gallery/static'
)

@gallery.route('/gallery')
def gallery_route():
    user = User.query.first()
    name = user.name.upper()

    
    gallery_items = Gallery.query.order_by(Gallery.id).all()

    for item in gallery_items:
        if item.type == 'video':
            # Changed item.video_url to item.url to match your models.py
            url = item.url
            if not url:
                item.video_id = None
                continue

            parsed = urlparse(url)
            query = parse_qs(parsed.query)
            
            if 'v' in query:
                item.video_id = query['v'][0]
            elif parsed.path.startswith('/embed/'):
                item.video_id = parsed.path.split('/embed/')[1].split('/')[0]
            elif 'youtu.be' in parsed.netloc:
                item.video_id = parsed.path[1:]
            else:
                item.video_id = url  # fallback
                
    return render_template('gallery.html', gallery_items=gallery_items, name=name)