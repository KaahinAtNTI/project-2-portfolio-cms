import base64
import secrets
from datetime import datetime
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from slugify import slugify
from sqlalchemy import (
    Column,
    DateTime,
    MetaData,
    String,
    Table,
    delete,
    select,
    update,
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Database Configuration and Setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
db = SQLAlchemy(app)

metadata = MetaData()

#  Projects
projects_table = Table('projects', metadata,
                       Column('slug', String, primary_key=True),
                       Column('title', String), Column('description', String),
                       Column('image', String))

# Contact Messages
contact_messages_table = Table('contact_messages', metadata,
                               Column('id', String, primary_key=True),
                               Column('first_name', String),
                               Column('last_name', String),
                               Column('email', String),
                               Column('subject', String),
                               Column('message', String),
                               Column('timestamp', DateTime))

# Session Management
login_manager = LoginManager()
login_manager.init_app(app)


# Utility Functions
def generate_slug(title):
  slug_base = slugify(title)
  counter = 1
  new_slug = slug_base
  projects = db.session.execute(projects_table.select()).fetchall()
  while new_slug in projects:
    new_slug = f"{slug_base}-{counter}"
    counter += 1
  return new_slug


def encode_image_to_base64(image_file):
  image_data = base64.b64encode(image_file.read()).decode('utf-8')
  return f"data:image/jpeg;base64,{image_data}"


def format_date(date):
  now = datetime.now()
  if (now - date).days < 1:
    return date.strftime("%H:%M")
  elif now.year == date.year:
    return date.strftime("%b %d")
  else:
    return date.strftime("%d/%m/%Y")


def get_projects():
  results = db.session.execute(projects_table.select()).fetchall()
  projects = {}
  for row in results:
    slug, title, description, image = row
    project_data = {'title': title, 'description': description, 'image': image}
    projects[slug] = project_data
  return projects


def get_contact_messages():
  results = db.session.execute(contact_messages_table.select()).fetchall()
  messages = []
  for row in results:
    message_data = {
        'id': row.id,
        'first_name': row.first_name,
        'last_name': row.last_name,
        'email': row.email,
        'subject': row.subject,
        'message': row.message,
        'formatted_date': format_date(row.timestamp)
    }
    messages.append(message_data)
  return messages


# CMS Routes
@app.get('/cms')
def cms_dashboard():
  return render_template("cms/cms_dashboard.html")


# Messages
@app.get('/cms/inbox')
def cms_inbox():
  messages = get_contact_messages()
  return render_template("cms/cms_inbox.html", messages=messages[::-1])


@app.get('/cms/inbox/view/<uuid:id>')
def view_message(id):
  message_id = str(id)

  results = db.session.execute(select(contact_messages_table)).fetchall()

  message = {}
  for row in results:
    if row.id == message_id:
      message['first_name'] = row.first_name
      message['last_name'] = row.last_name
      message['subject'] = row.subject
      message['email'] = row.email
      message['formatted_date'] = format_date(row.timestamp)
      message['message'] = row.message
  if message is None:
    flash('Message not found', 'error')
    return redirect(url_for('cms_inbox'))
  return render_template('cms/cms_view_message.html', message=message)


@app.post('/cms/inbox/delete/<uuid:id>')
def delete_message(id):
  message_id = str(id)
  delete_stmt = delete(contact_messages_table).where(
      contact_messages_table.c.id == message_id)
  result = db.session.execute(delete_stmt)
  db.session.commit()
  if result.rowcount == 0:
    return 'Message not found', 404

  return redirect(url_for('cms_inbox'))


# Project
@app.get('/cms/projects')
def cms_projects():
  projects = get_projects()
  return render_template("cms/cms_projects.html", projects=projects)


@app.route('/cms/projects/add', methods=['GET', 'POST'])
def add_project():
  if request.method == "POST":
    title = request.form.get('title')
    description = request.form.get('description')
    image = request.files.get('image')
    if image and image.filename:
      image_data = encode_image_to_base64(image)
    else:
      image_data = url_for('static', filename='img/project_thumbnail.jpg')

    slug = generate_slug(title)
    insert_stmt = projects_table.insert().values(slug=slug,
                                                 title=title,
                                                 description=description,
                                                 image=image_data)
    db.session.execute(insert_stmt)
    db.session.commit()

    return redirect(url_for('cms_projects'))
  return render_template("cms/cms_add_project.html")


@app.get('/cms/projects/<string:slug>')
def view_project(slug):
  projects = get_projects()
  project = projects[slug]
  if project is None:
    return 'Project not found', 404
  return render_template("cms/cms_view_project.html", project=project)


@app.route('/cms/projects/edit/<string:slug>', methods=['GET', 'POST'])
def edit_project(slug):
  projects = get_projects()
  project = projects.get(slug)

  if project is None:
    return 'Project not found', 404

  if request.method == "POST":
    title = request.form.get('title', project['title'])
    description = request.form.get('description', project['description'])
    image = request.files.get('image')

    if image and image.filename:
      image_data = encode_image_to_base64(image)
    else:
      image_data = project['image']

    update_stmt = update(projects_table).where(
        projects_table.c.slug == slug).values(title=title,
                                              description=description,
                                              image=image_data)
    db.session.execute(update_stmt)
    db.session.commit()
    return redirect(url_for('cms_projects'))

  return render_template("cms/cms_edit_project.html",
                         project=project,
                         slug=slug)


@app.post('/cms/projects/delete/<string:slug>')
def delete_project(slug):
  delete_stmt = delete(projects_table).where(projects_table.c.slug == slug)
  result = db.session.execute(delete_stmt)
  db.session.commit()
  if result.rowcount == 0:
    return 'Project not found', 404
  return redirect(url_for('cms_projects'))


# Public Website Routes
@app.get('/')
def home():
  return render_template("website/home.html")


@app.get('/projects')
def display_projects():
  projects = get_projects()
  return render_template("website/projects.html", projects=projects)


@app.get('/projects/<string:slug>')
def show_project(slug):
  projects = get_projects()
  project = projects.get(slug)
  if not project:
    return 'Project not found', 404
  return render_template('website/view_project.html', project=project)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
  current_time = datetime.now()
  if request.method == 'POST':
    message_id = str(uuid4())
    insert_stmt = contact_messages_table.insert().values(
        id=message_id,
        first_name=request.form.get('firstName'),
        last_name=request.form.get('lastName'),
        email=request.form.get('email'),
        subject=request.form.get('subject'),
        message=request.form.get('message'),
        timestamp=current_time)
    db.session.execute(insert_stmt)
    db.session.commit()
    flash('Your message has been successfully sent!', 'success')
    return redirect(url_for('contact'))
  return render_template("website/contact.html")


if __name__ == "__main__":
  with app.app_context():
    metadata.create_all(db.engine)
  app.run(host='0.0.0.0', port=81, debug=True)
