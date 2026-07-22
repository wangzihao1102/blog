"""Post forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 200)])
    excerpt = StringField('摘要', validators=[Length(0, 300)])
    body = TextAreaField('正文 (Markdown)', validators=[DataRequired()])
    tags = StringField('标签 (逗号分隔)', validators=[Length(0, 200)])
    publish = BooleanField('立即发布')
    submit = SubmitField('保存文章')
