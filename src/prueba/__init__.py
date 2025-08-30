from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any

def create_app():
    app = Flask(__name__)
    app.secret_key = 'tu_clave_secreta_aqui'
    
    # Datos de ejemplo (en una aplicación real, esto estaría en una base de datos)
    events = [
        {
            'id': 1,
            'title': 'Conferencia de Python',
            'slug': 'conferencia-python',
            'description': 'Una conferencia sobre las últimas tendencias en Python y desarrollo web.',
            'date': '2025-01-15',
            'time': '14:00',
            'location': 'Auditorio Principal',
            'category': 'Tecnología',
            'max_attendees': 50,
            'attendees': [
                {'name': 'Juan Pérez', 'email': 'juan@example.com'}
            ],
            'featured': True
        },
        {
            'id': 2,
            'title': 'Taller de Arte Digital',
            'slug': 'taller-arte-digital',
            'description': 'Aprende técnicas de arte digital con herramientas modernas.',
            'date': '2025-01-20',
            'time': '10:00',
            'location': 'Sala de Arte',
            'category': 'Cultural',
            'max_attendees': 25,
            'attendees': [],
            'featured': False
        },
        {
            'id': 3,
            'title': 'Maratón de Programación',
            'slug': 'maraton-programacion',
            'description': 'Compite con otros programadores en este evento de 24 horas.',
            'date': '2025-01-25',
            'time': '09:00',
            'location': 'Centro de Innovación',
            'category': 'Tecnología',
            'max_attendees': 100,
            'attendees': [
                {'name': 'María García', 'email': 'maria@example.com'},
                {'name': 'Carlos López', 'email': 'carlos@example.com'}
            ],
            'featured': True
        }
    ]
    
    categories = ['Tecnología', 'Académico', 'Cultural', 'Deportivo', 'Social']
    
    def get_event_by_slug(slug: str) -> Dict[str, Any]:
        """Obtiene un evento por su slug"""
        for event in events:
            if event['slug'] == slug:
                return event
        return None
    
    def create_slug(title: str) -> str:
        """Crea un slug a partir del título"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug)
        return slug.strip('-')
    
    def is_valid_email(email: str) -> bool:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @app.route('/')
    def index():
        """Página principal con lista de eventos próximos"""
        # Filtrar eventos futuros y ordenar por fecha
        today = datetime.now().date()
        upcoming_events = [
            event for event in events 
            if datetime.strptime(event['date'], '%Y-%m-%d').date() >= today
        ]
        upcoming_events.sort(key=lambda x: x['date'])
        
        return render_template('index.html', 
                             events=upcoming_events, 
                             categories=categories)
    
    @app.route('/event/<slug>/')
    def event_detail(slug):
        """Detalle de un evento específico"""
        event = get_event_by_slug(slug)
        if not event:
            flash('Evento no encontrado', 'error')
            return redirect(url_for('index'))
        
        return render_template('event_detail.html', event=event)
    
    @app.route('/admin/event/', methods=['GET', 'POST'])
    def create_event():
        """Formulario para crear un nuevo evento"""
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            date = request.form.get('date', '').strip()
            time = request.form.get('time', '').strip()
            location = request.form.get('location', '').strip()
            category = request.form.get('category', '').strip()
            max_attendees = request.form.get('max_attendees', '').strip()
            featured = request.form.get('featured') == 'on'
            
            # Validaciones
            if not all([title, description, date, time, location, category, max_attendees]):
                flash('Todos los campos son obligatorios', 'error')
                return render_template('create_event.html', categories=categories)
            
            try:
                max_attendees = int(max_attendees)
                if max_attendees <= 0:
                    raise ValueError()
            except ValueError:
                flash('El número máximo de asistentes debe ser un número positivo', 'error')
                return render_template('create_event.html', categories=categories)
            
            # Validar fecha
            try:
                event_date = datetime.strptime(date, '%Y-%m-%d')
                if event_date.date() < datetime.now().date():
                    flash('La fecha del evento no puede ser en el pasado', 'error')
                    return render_template('create_event.html', categories=categories)
            except ValueError:
                flash('Formato de fecha inválido', 'error')
                return render_template('create_event.html', categories=categories)
            
            # Crear nuevo evento
            new_event = {
                'id': max([e['id'] for e in events]) + 1,
                'title': title,
                'slug': create_slug(title),
                'description': description,
                'date': date,
                'time': time,
                'location': location,
                'category': category,
                'max_attendees': max_attendees,
                'attendees': [],
                'featured': featured
            }
            
            events.append(new_event)
            flash('Evento creado exitosamente', 'success')
            return redirect(url_for('event_detail', slug=new_event['slug']))
        
        return render_template('create_event.html', categories=categories)
    
    @app.route('/event/<slug>/register/', methods=['GET', 'POST'])
    def register_event(slug):
        """Formulario para registrarse a un evento"""
        event = get_event_by_slug(slug)
        if not event:
            flash('Evento no encontrado', 'error')
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            
            # Validaciones
            if not name or not email:
                flash('Nombre y email son obligatorios', 'error')
                return render_template('register_event.html', event=event)
            
            if not is_valid_email(email):
                flash('Formato de email inválido', 'error')
                return render_template('register_event.html', event=event)
            
            # Verificar si ya está registrado
            for attendee in event['attendees']:
                if attendee['email'] == email:
                    flash('Ya estás registrado para este evento', 'error')
                    return render_template('register_event.html', event=event)
            
            # Verificar capacidad
            if len(event['attendees']) >= event['max_attendees']:
                flash('El evento ya está completo', 'error')
                return render_template('register_event.html', event=event)
            
            # Registrar asistente
            event['attendees'].append({
                'name': name,
                'email': email
            })
            
            flash('Te has registrado exitosamente para el evento', 'success')
            return redirect(url_for('event_detail', slug=slug))
        
        return render_template('register_event.html', event=event)
    
    @app.route('/events/category/<category>/')
    def events_by_category(category):
        """Filtrar eventos por categoría"""
        if category not in categories:
            flash('Categoría no válida', 'error')
            return redirect(url_for('index'))
        
        filtered_events = [event for event in events if event['category'] == category]
        return render_template('events_by_category.html', 
                             events=filtered_events, 
                             category=category,
                             categories=categories)
    
    @app.route('/api/events/')
    def api_events():
        """API para obtener todos los eventos"""
        return jsonify(events)
    
    @app.route('/api/events/<slug>/')
    def api_event_detail(slug):
        """API para obtener un evento específico"""
        event = get_event_by_slug(slug)
        if not event:
            return jsonify({'error': 'Evento no encontrado'}), 404
        return jsonify(event)
    
    return app

# Para desarrollo local
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
