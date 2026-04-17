import os
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from models import db, User

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///muneer_brothers.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
    
    # Initialize Extensions
    db.init_app(app)
    bcrypt = Bcrypt(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'routes.admin_login'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # Initialize Database and Default Admin
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(username='admin', password_hash=hashed_pw)
            db.session.add(admin)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)