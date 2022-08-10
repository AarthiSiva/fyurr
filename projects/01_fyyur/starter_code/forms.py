from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField,DecimalField, BooleanField, IntegerField
from wtforms.validators import DataRequired, AnyOf, URL, Regexp, Length, Optional

choice_of_genres=[
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ]

choice_of_state=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]

class ShowForm(Form):
    artist_id = StringField(
        'artist_id', validators=[DataRequired(),Regexp("^[0-9]*$", message="Artist_ID should only contain digits")]
    )
    venue_id = StringField(
        'venue_id', validators=[DataRequired(), Regexp("^[0-9]*$", message="Venue_ID should only contain digits")]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired(),Length(min=3,max=60, message='Name length must not be more than 60 characters')]
    )
    city = StringField(
        'city', validators=[DataRequired(),Length(min=3,max=60, message='City length must not be more than 60 characters')]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=choice_of_state
    )
    address = StringField(
        'address', validators=[DataRequired(), Length(max=120, message='Address length must not be more than 120 characters')]
    )
    phone = StringField(
        'phone', validators=[DataRequired(), Length(min=8,max=12, message='Phone number length is not appropriate'), Regexp("^[0-9]*$", message="Phone number should only contain digits")]
    )
    image_link = StringField(
        'image_link', validators=[Length(max=500),URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=choice_of_genres
    )
    facebook_link = StringField(
        'facebook_link', validators=[Length(max=500),Optional(),URL()]
    )
    website_link = StringField(
        'website_link', validators=[Length(max=500),Optional(),URL()]
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description', validators=[Length(max=120, message='Description length must not be more than 120 characters')]
    )



class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired(), Length(min=3,max=60, message='Name length is not appropriate')]
    )
    city = StringField(
        'city', validators=[DataRequired(), Length(max=60, message='City length must not be more than 60 characters')]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=choice_of_state
    )
    phone = StringField(
        'phone', validators=[DataRequired(), Length(min=8,max=12, message='Phone number length is not appropriate'), Regexp("^[0-9]*$", message="Phone number should only contain digits")]
    )
    image_link = StringField(
        'image_link', validators=[Length(max=500),URL()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=choice_of_genres
     )
    facebook_link = StringField(
        'facebook_link', validators=[Length(max=500),Optional(),URL()]
     )

    website_link = StringField(
        'website_link', validators=[Length(max=500),Optional(),URL()]
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description', validators=[Length(max=120, message='Description length must not be more than 120 characters')]
     )

