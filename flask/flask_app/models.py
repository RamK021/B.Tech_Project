from datetime import datetime, timezone, timedelta
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired
from flask_app import db, login_manager, app
from flask_login import UserMixin
import calendar

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    msges = db.relationship('Post', backref='sender', lazy=True)

    def get_reset_token(self, expires_sec=300):
        s = Serializer(app.config['SECRET_KEY'])
        expiration_time = datetime.now(timezone.utc) + timedelta(seconds=expires_sec)
        expiration_timestamp = calendar.timegm(expiration_time.utctimetuple())
        return s.dumps({'user_id': self.id, 'exp': expiration_timestamp}, salt='reset')
    
    @staticmethod
    def verify_reset_token(token, expires_sec=300):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token, salt='reset', max_age=expires_sec)
            user_id = data.get('user_id')
        except SignatureExpired:
            return None
        except:
            return None
        return User.query.get(user_id)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    msg_date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.msg_date}')"

