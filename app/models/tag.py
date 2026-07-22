"""Tag model."""
from app.extensions import db


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(60), unique=True, nullable=False, index=True)

    posts = db.relationship('Post', secondary='post_tags',
                            backref=db.backref('tags', lazy='dynamic'))

    def __repr__(self):
        return f'<Tag {self.name}>'
