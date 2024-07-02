from app import app, db, UserInput

with app.app_context():
    num_rows_deleted = db.session.query(UserInput).delete()
    db.session.commit()
    print(f'Successfully deleted {num_rows_deleted} entries.')
