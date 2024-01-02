import base64
from datetime import datetime
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, url_for
from slugify import slugify

app = Flask(__name__)

# Global Variables
projects = {}
contact_messages = {}


# Utility Functions
def generate_slug(title):
  slug_base = slugify(title)
  counter = 1
  new_slug = slug_base
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


# CMS Routes
@app.get('/cms')
def cms_dashboard():
  return render_template("cms/cms_dashboard.html")


@app.get('/cms/inbox')
def cms_inbox():
  for id, message in contact_messages.items():
    contact_messages[id]['formatted_date'] = format_date(message['timestamp'])
  return render_template("cms/cms_inbox.html", messages=contact_messages)


@app.get('/cms/inbox/view/<string:id>')
def view_message(id):
  message = contact_messages.get(id)
  if not message:
    return 'Message not found', 404
  return render_template('cms/cms_view_message.html', message=message)


@app.post('/cms/inbox/delete/<string:id>')
def delete_message(id):
  if id in contact_messages:
    del contact_messages[id]
  else:
    return 'Message not found', 404
  return redirect(url_for('cms_inbox'))


@app.get('/cms/projects')
def cms_projects():
  return render_template("cms/cms_projects.html", projects=projects)


@app.get('/cms/projects/add')
def show_add_project_form():
  return render_template("cms/cms_add_project.html")


@app.post('/cms/projects/add')
def process_add_project():
  title = request.form.get('title')
  description = request.form.get('description')
  image = request.files.get('image')
  if image and image.filename:
    image_data = encode_image_to_base64(image)
  else:
    image_data = url_for('static', filename='img/project_thumbnail.jpg')
  slug = generate_slug(title)
  projects[slug] = {
      'title': title,
      'description': description,
      'image': image_data
  }
  return redirect(url_for('cms_projects'))


@app.get('/cms/projects/<string:slug>')
def view_project(slug):
  project = projects.get(slug)
  if not project:
    return 'Project not found', 404
  return render_template("cms/cms_view_project.html", project=project)


@app.get('/cms/projects/edit/<string:slug>')
def show_edit_project_form(slug):
  project = projects.get(slug)
  if not project:
    return 'Project not found', 404
  return render_template("cms/cms_edit_project.html",
                         project=project,
                         slug=slug)


@app.post('/cms/projects/edit/<string:slug>')
def process_edit_project(slug):
  project = projects.get(slug)
  if not project:
    return 'Project not found', 404
  project['title'] = request.form['title']
  project['description'] = request.form['description']
  image = request.files.get('image')
  if image and image.filename:
    project['image'] = encode_image_to_base64(image)
  else:
    project['image'] = url_for('static', filename='img/project_thumbnail.jpg')
  return redirect(url_for('cms_projects'))


@app.post('/cms/projects/delete/<string:slug>')
def delete_project(slug):
  if slug in projects:
    del projects[slug]
  else:
    return 'Project not found', 404
  return redirect(url_for('cms_projects'))


# Public Website Routes
@app.get('/')
def home():
  return render_template("website/home.html")


@app.get('/projects')
def display_projects():
  return render_template("website/projects.html", projects=projects)


@app.get('/projects/<string:slug>')
def show_project(slug):
  project = projects.get(slug)
  if not project:
    return 'Project not found', 404
  return render_template('website/view_project.html', project=project)


@app.get('/contact')
def show_contact_form():
  return render_template("website/contact.html")


@app.post('/contact')
def process_contact_form():
  if request.method == 'POST':
    message_id = str(uuid4())
    contact_messages[message_id] = {
        'first_name': request.form.get('firstName'),
        'last_name': request.form.get('lastName'),
        'email': request.form.get('email'),
        'subject': request.form.get('subject'),
        'message': request.form.get('message'),
        'timestamp': datetime.now()
    }
  flash('Your message has been successfully sent!', 'success')

  return redirect(url_for('contact'))


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=81, debug=True)
