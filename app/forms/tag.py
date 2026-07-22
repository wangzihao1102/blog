"""Tag forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class TagForm(FlaskForm):
    name = StringField('标签名称', validators=[DataRequired(), Length(1, 50)])
    submit = SubmitField('添加标签')
