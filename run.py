from app import create_app
from app.database.models import db
from datetime import datetime

app = create_app()


with app.app_context():
    db.create_all()



if __name__ == '__main__':
    app.run()
