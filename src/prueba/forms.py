"""
Formularios para el Sistema de Gestión de Eventos
Utilizando Flask-WTF para validación robusta
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from wtforms.widgets import TextArea


class CreateEventForm(FlaskForm):
    """Formulario para crear un nuevo evento"""
    
    title = StringField(
        'Título del Evento',
        validators=[
            DataRequired(message='El título es obligatorio'),
            Length(min=3, max=100, message='El título debe tener entre 3 y 100 caracteres')
        ],
        render_kw={
            'placeholder': 'Ej: Conferencia de Python 2025',
            'class': 'form-control'
        }
    )
    
    description = TextAreaField(
        'Descripción',
        validators=[
            DataRequired(message='La descripción es obligatoria'),
            Length(min=10, max=1000, message='La descripción debe tener entre 10 y 1000 caracteres')
        ],
        render_kw={
            'placeholder': 'Describe tu evento...',
            'class': 'form-control',
            'rows': 4
        }
    )
    
    category = SelectField(
        'Categoría',
        validators=[DataRequired(message='Debes seleccionar una categoría')],
        render_kw={'class': 'form-select'}
    )
    
    date = StringField(
        'Fecha',
        validators=[DataRequired(message='La fecha es obligatoria')],
        render_kw={
            'type': 'date',
            'class': 'form-control'
        }
    )
    
    time = StringField(
        'Hora',
        validators=[DataRequired(message='La hora es obligatoria')],
        render_kw={
            'type': 'time',
            'class': 'form-control'
        }
    )
    
    location = StringField(
        'Ubicación',
        validators=[
            DataRequired(message='La ubicación es obligatoria'),
            Length(min=3, max=200, message='La ubicación debe tener entre 3 y 200 caracteres')
        ],
        render_kw={
            'placeholder': 'Ej: Auditorio Principal',
            'class': 'form-control'
        }
    )
    
    max_attendees = IntegerField(
        'Máximo de Asistentes',
        validators=[
            DataRequired(message='El número máximo de asistentes es obligatorio'),
            NumberRange(min=1, max=1000, message='Debe ser un número entre 1 y 1000')
        ],
        render_kw={
            'placeholder': 'Ej: 50',
            'class': 'form-control',
            'min': 1,
            'max': 1000
        }
    )
    
    featured = BooleanField(
        'Evento Destacado',
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField(
        'Crear Evento',
        render_kw={'class': 'btn btn-primary'}
    )


class RegisterEventForm(FlaskForm):
    """Formulario para registrarse a un evento"""
    
    name = StringField(
        'Nombre Completo',
        validators=[
            DataRequired(message='El nombre es obligatorio'),
            Length(min=2, max=100, message='El nombre debe tener entre 2 y 100 caracteres')
        ],
        render_kw={
            'placeholder': 'Tu nombre completo',
            'class': 'form-control'
        }
    )
    
    email = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El correo electrónico es obligatorio'),
            Email(message='Formato de correo electrónico inválido'),
            Length(max=254, message='El correo electrónico es demasiado largo')
        ],
        render_kw={
            'placeholder': 'tu@email.com',
            'class': 'form-control',
            'type': 'email'
        }
    )
    
    terms_accepted = BooleanField(
        'Acepto los términos y condiciones',
        validators=[DataRequired(message='Debes aceptar los términos y condiciones')],
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField(
        'Confirmar Registro',
        render_kw={'class': 'btn btn-success'}
    )


class SearchEventForm(FlaskForm):
    """Formulario para buscar eventos"""
    
    query = StringField(
        'Buscar eventos',
        validators=[
            Optional(),
            Length(max=100, message='La búsqueda no puede exceder 100 caracteres')
        ],
        render_kw={
            'placeholder': 'Buscar por título, descripción o ubicación...',
            'class': 'form-control'
        }
    )
    
    category = SelectField(
        'Categoría',
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField(
        'Buscar',
        render_kw={'class': 'btn btn-outline-primary'}
    )
