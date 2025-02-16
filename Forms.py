from wtforms import Form, StringField, TextAreaField, DecimalField, validators, IntegerField, SelectField, SubmitField, FileField
from wtforms.fields import EmailField, DateField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed


class CreateProductForm(Form):  # for create product
    product_name = StringField('Product Name', validators=[DataRequired(), Length(min=1, max=100, message='Length must more than 1')])
    description = TextAreaField('Description', validators=[Length(max=500, message='Max length is 500')])
    price = DecimalField('Price ($)', validators=[DataRequired(message='field cannot be empty')])
    category = SelectField('Category', choices=[('Newspaper or Paper', 'Newspaper or Paper'),
                                                ('Cardboard', 'Cardboard'),
                                                ('Clothing', 'Clothing'),
                                                ('Metal Recyclables', 'Metal Recyclables'),
                                                ('Furniture','Furniture'),
                                                ('Electronics', 'Electronics'),
                                                ('Speakers','Speakers'),
                                                ('Home', 'Home'),
                                                ('Toys', 'Toys'),
                                                ('Other', 'Other')], validators=[DataRequired(message='field cannot be empty')])
    condition = SelectField('Condition', choices=[('New', 'New'),
                                                  ('Like New', 'Like New'),
                                                  ('Lightly Used', 'Lightly Used'),
                                                  ('Heavily Used', 'Heavily Used')], validators=[DataRequired(message='field cannot be empty')])
    remarks = TextAreaField('Remarks', validators=[validators.Optional()])
    image = FileField('Product Image')
    submit = SubmitField('Create Product')


class CreateFeedbackForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=100), validators.DataRequired()])
    email = EmailField('Email', [validators.DataRequired()])
    feedback = TextAreaField('Feedback', [validators.DataRequired()])


class CreateReplyFeedbackForm(Form):
    subject = StringField('Subject', [validators.Length(min=1, max=100), validators.DataRequired()])
    recipient_email = EmailField('Recipient Email', [validators.DataRequired()])
    message = TextAreaField('Message', [validators.DataRequired()])


class CreateItemForm(Form):
    category = SelectField('Category', [validators.DataRequired()],
                           choices=[('', 'Select'), ('Newspapers or Paper', 'Newspaper or Paper'), ('Cardboard', 'Cardboard'),
                                    ('Clothing', 'Clothing'), ('Metal Recyclables', 'Metal Recyclables'), ('Furniture', 'Furniture'),
                                    ('Electronics', 'Electronics'), ('Speakers', 'Speakers'),('Home', 'Home'), ('Toys', 'Toys'), ('Other', 'Other') ])
    item = StringField('Item', [validators.Length(min=1, max=100), validators.DataRequired()])
    description = StringField('Description', [validators.Length(min=1, max=150), validators.DataRequired()])
    condition = SelectField('Condition', [validators.DataRequired()],
                            choices=[('New', 'New'),
                                     ('Like New', 'Like New'),
                                     ('Lightly Used', 'Lightly Used'),
                                     ('Heavily Used', 'Heavily Used') ], default='')
    stock = IntegerField('Stock', [validators.DataRequired()])
    selling_price = IntegerField('Selling Price ($)', [validators.DataRequired()])
