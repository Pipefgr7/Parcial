from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timedelta
import re
from typing import List, Dict, Any
from .forms import CreateEventForm, RegisterEventForm, SearchEventForm

def create_app():
    app = Flask(__name__)
    app.secret_key = 'tu_clave_secreta_aqui'
    
    # Configurar CSRF protection
    csrf = CSRFProtect(app)
    
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
        search_form = SearchEventForm()
        search_form.category.choices = [('', 'Todas las categorías')] + [(cat, cat) for cat in categories]
        
        # Filtrar eventos futuros y ordenar por fecha
        today = datetime.now().date()
        upcoming_events = [
            event for event in events 
            if datetime.strptime(event['date'], '%Y-%m-%d').date() >= today
        ]
        upcoming_events.sort(key=lambda x: x['date'])
        
        return render_template('index.html', 
                             events=upcoming_events, 
                             categories=categories,
                             search_form=search_form)
    
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
        form = CreateEventForm()
        form.category.choices = [(cat, cat) for cat in categories]
        
        if form.validate_on_submit():
            # Validar fecha
            try:
                event_date = datetime.strptime(form.date.data, '%Y-%m-%d')
                if event_date.date() < datetime.now().date():
                    flash('La fecha del evento no puede ser en el pasado', 'error')
                    return render_template('create_event.html', form=form, categories=categories)
            except ValueError:
                flash('Formato de fecha inválido', 'error')
                return render_template('create_event.html', form=form, categories=categories)
            
            # Crear nuevo evento
            new_event = {
                'id': max([e['id'] for e in events]) + 1,
                'title': form.title.data,
                'slug': create_slug(form.title.data),
                'description': form.description.data,
                'date': form.date.data,
                'time': form.time.data,
                'location': form.location.data,
                'category': form.category.data,
                'max_attendees': form.max_attendees.data,
                'attendees': [],
                'featured': form.featured.data
            }
            
            events.append(new_event)
            flash('Evento creado exitosamente', 'success')
            return redirect(url_for('event_detail', slug=new_event['slug']))
        
        return render_template('create_event.html', form=form, categories=categories)
    
    @app.route('/event/<slug>/register/', methods=['GET', 'POST'])
    def register_event(slug):
        """Formulario para registrarse a un evento"""
        event = get_event_by_slug(slug)
        if not event:
            flash('Evento no encontrado', 'error')
            return redirect(url_for('index'))
        
        form = RegisterEventForm()
        
        if form.validate_on_submit():
            # Verificar si ya está registrado
            for attendee in event['attendees']:
                if attendee['email'] == form.email.data:
                    flash('Ya estás registrado para este evento', 'error')
                    return render_template('register_event.html', event=event, form=form)
            
            # Verificar capacidad
            if len(event['attendees']) >= event['max_attendees']:
                flash('El evento ya está completo', 'error')
                return render_template('register_event.html', event=event, form=form)
            
            # Registrar asistente
            event['attendees'].append({
                'name': form.name.data,
                'email': form.email.data
            })
            
            flash('Te has registrado exitosamente para el evento', 'success')
            return redirect(url_for('event_detail', slug=slug))
        
        return render_template('register_event.html', event=event, form=form)
    
    @app.route('/search/', methods=['GET', 'POST'])
    def search_events():
        """Buscar eventos"""
        search_form = SearchEventForm()
        search_form.category.choices = [('', 'Todas las categorías')] + [(cat, cat) for cat in categories]
        
        if search_form.validate_on_submit():
            query = search_form.query.data.lower() if search_form.query.data else ''
            category_filter = search_form.category.data
            
            # Filtrar eventos
            filtered_events = []
            for event in events:
                # Filtrar por categoría
                if category_filter and event['category'] != category_filter:
                    continue
                
                # Filtrar por búsqueda de texto
                if query:
                    searchable_text = f"{event['title']} {event['description']} {event['location']}".lower()
                    if query not in searchable_text:
                        continue
                
                filtered_events.append(event)
            
            return render_template('search_results.html', 
                                 events=filtered_events,
                                 search_form=search_form,
                                 query=query,
                                 category_filter=category_filter,
                                 categories=categories)
        
        return render_template('search_results.html', 
                             events=[],
                             search_form=search_form,
                             query='',
                             category_filter='',
                             categories=categories)
    
    @app.route('/event/<slug>/unregister/', methods=['POST'])
    def unregister_event(slug):
        """Cancelar registro a un evento"""
        event = get_event_by_slug(slug)
        if not event:
            flash('Evento no encontrado', 'error')
            return redirect(url_for('index'))
        
        email = request.form.get('email', '').strip()
        if not email:
            flash('Email es requerido para cancelar el registro', 'error')
            return redirect(url_for('event_detail', slug=slug))
        
        # Buscar y remover el asistente
        for i, attendee in enumerate(event['attendees']):
            if attendee['email'] == email:
                removed_attendee = event['attendees'].pop(i)
                flash(f'Se ha cancelado el registro de {removed_attendee["name"]}', 'success')
                return redirect(url_for('event_detail', slug=slug))
        
        flash('No se encontró un registro con ese email', 'error')
        return redirect(url_for('event_detail', slug=slug))
    
    @app.route('/events/past/')
    def past_events():
        """Ver eventos pasados"""
        today = datetime.now().date()
        past_events = [
            event for event in events 
            if datetime.strptime(event['date'], '%Y-%m-%d').date() < today
        ]
        past_events.sort(key=lambda x: x['date'], reverse=True)
        
        return render_template('past_events.html', 
                             events=past_events, 
                             categories=categories)
    
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
    
    @app.route('/admin/')
    def admin_dashboard():
        """Panel de administración"""
        # Estadísticas
        total_events = len(events)
        upcoming_events = len([e for e in events if datetime.strptime(e['date'], '%Y-%m-%d').date() >= datetime.now().date()])
        total_attendees = sum(len(e['attendees']) for e in events)
        featured_events = len([e for e in events if e['featured']])
        
        # Eventos por categoría
        events_by_category = {}
        for event in events:
            category = event['category']
            if category not in events_by_category:
                events_by_category[category] = 0
            events_by_category[category] += 1
        
        return render_template('admin_dashboard.html',
                             total_events=total_events,
                             upcoming_events=upcoming_events,
                             total_attendees=total_attendees,
                             featured_events=featured_events,
                             events_by_category=events_by_category,
                             events=events,
                             categories=categories)
    
    @app.route('/admin/event/<slug>/delete/', methods=['POST'])
    def delete_event(slug):
        """Eliminar un evento"""
        event = get_event_by_slug(slug)
        if not event:
            flash('Evento no encontrado', 'error')
            return redirect(url_for('admin_dashboard'))
        
        events.remove(event)
        flash(f'Evento "{event["title"]}" eliminado exitosamente', 'success')
        return redirect(url_for('admin_dashboard'))
    
    @app.route('/admin/event/<slug>/toggle-featured/', methods=['POST'])
    def toggle_featured(slug):
        """Alternar estado destacado de un evento"""
        event = get_event_by_slug(slug)
        if not event:
            flash('Evento no encontrado', 'error')
            return redirect(url_for('admin_dashboard'))
        
        event['featured'] = not event['featured']
        status = 'destacado' if event['featured'] else 'no destacado'
        flash(f'Evento "{event["title"]}" marcado como {status}', 'success')
        return redirect(url_for('admin_dashboard'))
    
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
