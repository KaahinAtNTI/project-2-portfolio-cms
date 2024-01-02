import base64
import json
import os
import secrets
import shutil
from datetime import datetime
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, url_for
from slugify import slugify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


# Utility Functions
def format_date(date):
  now = datetime.now()
  if (now - date).days < 1:
    return date.strftime("%H:%M")
  elif now.year == date.year:
    return date.strftime("%b %d")
  else:
    return date.strftime("%d/%m/%Y")


def generate_slug(title):
  slug_base = slugify(title)
  counter = 1
  new_slug = slug_base
  projects = getattr(app, 'projects', {})
  while new_slug in projects:
    new_slug = f"{slug_base}-{counter}"
    counter += 1
  return new_slug


def read_data_file(file_name):
  try:
    with open(file_name, 'r') as file:
      content = file.read().strip()
      if not content:
        return {}
      return json.loads(content)
  except json.JSONDecodeError:
    flash(f'Error decoding JSON from {file_name}', 'error')
    return {}
  except FileNotFoundError:
    # Handle case where file does not exist
    flash(f'File not found: {file_name}', 'error')
    return {}


def initialize_app_data(app):
  static_folder = app.static_folder
  data_folder = os.path.join(static_folder, 'data')

  projects_file = os.path.join(data_folder, 'projects.json')
  messages_file = os.path.join(data_folder, 'messages.json')

  app.projects = read_data_file(projects_file)
  app.contact_messages = read_data_file(messages_file)


def encode_image_to_base64(image_file):
  image_data = base64.b64encode(image_file.read()).decode('utf-8')
  return f"data:image/jpeg;base64,{image_data}"


def save_image(image_file, slug):
  if image_file and image_file.filename:
    filename = secure_filename(image_file.filename)
    static_folder = app.static_folder
    if static_folder is None:
      raise ValueError(
          'The static_folder is not set. Make sure the Flask app is configured correctly.'
      )
    upload_folder = os.path.join(static_folder, 'uploads', slug)
    if not os.path.exists(upload_folder):
      os.makedirs(upload_folder)
    image_path = os.path.join(upload_folder, filename)
    image_file.save(image_path)
    return os.path.relpath(image_path, start=app.static_folder)


def save_data_to_file(data, file_name):
  try:
    with open(file_name, 'w') as file:
      json.dump(data, file, indent=4)
  except IOError:
    flash(f'Error saving data to file: {file_name}', 'error')


initialize_app_data(app)


# CMS Routes
@app.get('/cms')
def cms_dashboard():
  return render_template("cms/cms_dashboard.html")


@app.get('/cms/inbox')
def cms_inbox():
  contact_messages = getattr(app, 'contact_messages', {})

  for id, message in contact_messages.items():
    contact_messages[id]['formatted_date'] = format_date(message['timestamp'])
  return render_template("cms/cms_inbox.html", messages=contact_messages)


@app.get('/cms/inbox/view/<uuid:id>')
def view_message(id):
  message_id = str(id)
  message = getattr(app, 'contact_messages', {}).get(message_id)
  if not message:
    return 'Message not found', 404
  return render_template('cms/cms_view_message.html', message=message)


@app.post('/cms/inbox/delete:<uuid:id>')
def delete_message(id):
  message_id = str(id)
  contact_messages = getattr(app, 'contact_messages', {})
  if message_id in contact_messages:
    del contact_messages[message_id]
  else:
    return 'Message not found', 404
  return redirect(url_for('cms_inbox'))


@app.get('/cms/projects')
def cms_projects():
  projects = getattr(app, 'projects', {})
  return render_template("cms/cms_projects.html", projects=projects)


@app.route('/cms/projects/add', methods=['GET', 'POST'])
def add_project():
  if request.method == "POST":
    title = request.form.get('title')
    description = request.form.get('description')
    image = request.files.get('image')
    slug = generate_slug(title)
    if image and image.filename:
      image_path = save_image(image, slug)
    else:
      image_path = url_for('static', filename='img/project_thumbnail.jpg')

    projects = getattr(app, 'projects', {})

    projects[slug] = {
        'title': title,
        'description': description,
        'image': image_path
    }

    static_folder = app.static_folder
    if static_folder is None:
      raise ValueError(
          'The static_folder is not set. Make sure the Flask app is configured correctly.'
      )

    data_folder = os.path.join(static_folder, 'data')
    projects_file = os.path.join(data_folder, 'projects.json')
    save_data_to_file(projects, projects_file)
    return redirect(url_for('cms_projects'))
  return render_template("cms/cms_add_project.html")


@app.get('/cms/projects/<string:slug>')
def view_project(slug):
  projects = getattr(app, 'projects', {})
  project = projects.get(slug)
  if not project:
    return 'Project not found', 404
  return render_template("cms/cms_view_project.html", project=project)


@app.route('/cms/projects/edit/<string:slug>', methods=['GET', 'POST'])
def edit_project(slug):
  projects = getattr(app, 'projects', {})
  project = projects.get(slug)
  if not project:
    return 'Project not found', 404

  if request.method == "POST":
    project['title'] = request.form['title']
    project['description'] = request.form['description']

    image = request.files.get('image')
    if image and image.filename:
      image_path = save_image(image, slug)
      project['image'] = image_path

    static_folder = app.static_folder
    if static_folder is None:
      raise ValueError(
          'The static_folder is not set. Make sure the Flask app is configured correctly.'
      )

    data_folder = os.path.join(static_folder, 'data')
    projects_file = os.path.join(data_folder, 'projects.json')
    save_data_to_file(projects, projects_file)

    return redirect(url_for('cms_projects'))

  return render_template("cms/cms_edit_project.html",
                         project=project,
                         slug=slug)


@app.post('/cms/projects/delete/<string:slug>')
def delete_project(slug):
  projects = getattr(app, 'projects', {})
  if slug in projects:
    project = projects[slug]
    image_path = project.get('image')
    if image_path:
      static_folder = app.static_folder
      if static_folder is None:
        app.logger.error(
            'Static folder not set. Check Flask app configuration.')
        return 'Server misconfiguration', 500

      folder_path = os.path.join(static_folder, os.path.dirname(image_path))
      data_folder = os.path.join(static_folder, 'data')
      projects_file = os.path.join(data_folder, 'projects.json')
      if os.path.isdir(folder_path):
        try:
          shutil.rmtree(folder_path)
        except OSError as e:
          app.logger.error(f"Error deleting directory: {folder_path}. {e}")
          return 'Error deleting project', 500
      else:
        app.logger.warning(f"Directory not found: {folder_path}")

      del projects[slug]
      save_data_to_file(projects, projects_file)
    else:
      return 'Project not found', 404

  return redirect(url_for('cms_projects'))


# Public Website Routes
@app.get('/')
def home():
  return render_template("website/home.html")


@app.get('/projects')
def display_projects():
  projects = getattr(app, 'projects', {})
  return render_template("website/projects.html", projects=projects)


@app.get('/projects/<string:slug>')
def show_project(slug):
  projects = getattr(app, 'projects', {})
  project = projects.get(slug)
  if not project:
    return 'Project not found', 404
  return render_template('website/view_project.html', project=project)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
  if request.method == 'POST':
    message_id = str(uuid4())
    contact_messages = getattr(app, 'contact_messages', {})
    get_date = str(datetime.now())
    contact_messages[message_id] = {
        'first_name': request.form.get('firstName'),
        'last_name': request.form.get('lastName'),
        'email': request.form.get('email'),
        'subject': request.form.get('subject'),
        'message': request.form.get('message'),
        'timestamp': get_date
    }

    static_folder = app.static_folder
    if static_folder is None:
      raise ValueError(
          'The static_folder is not set. Make sure the Flask app is configured correctly.'
      )

    data_folder = os.path.join(static_folder, 'data')

    messages_file = os.path.join(data_folder, 'messages.json')
    save_data_to_file(contact_messages, messages_file)

    flash('Your message has been successfully sent!', 'success')
    return redirect(url_for('contact'))
  return render_template("website/contact.html")


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=81, debug=True)
