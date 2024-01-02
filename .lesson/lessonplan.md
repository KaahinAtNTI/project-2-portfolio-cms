# Lesson plan

## Game Plan

1. **Kör `git clone <project source>` i Shell för att hämta projektet från GITHUB**
2. **Från den hämtade repots mapp, flytta `.git` till roten i Files för denna projekt `project-1-portfolio`**
3. **Kör följande kod block i segment**

   - ```shell
         # 1.
         git remote -v
         # Om  det inte visar korrekt repo, kör följande kommando:
         # git remote add <url> till repot i github>
     ```

   - ```shell
         # 2.
         git branch
         # Om inte visar `main` kör följande kommando: git checkout main
     ```

     ```shell
         # 3.
         git add .
         git commit -m "Update GitHub Repo" # Om git config --global är inte satt,
         # Kör följande kommando :
         # git config --global user.name "GitHub användarnamn"
         # git config --global user.email "Google skolkontots mejl"
         # Därefter kör git commit på nytt
     ```

     ```shell
         # 4.
         git pull origin main  # Se till att radera alla filer som finns på GitHub redan
         git push -u origin main
     ```

4. **Lösningskod till `app.py` (ej färdigt)**

   ```Python
     from flask import Flask, render_template
     app = Flask(__name__)
     """
     Valda strukturen för vårt data persistent
       projects = {
           'flask_portfolio': {
               'name': 'Projekt "Portfolio" i Flask',
               'description': 'Created a portfolio website in Flask'
           },
           'my_calc': {
               'name': 'my_calc',
               'description': 'Created a simple calculator in Python'
           },
           'project_slug': {
               'name': 'my_calc',
               'description':
           }
       }
     """


     @app.get('/')
     def home():
       return render_template("home.html")

     # Projects
     @app.get('/projects')
     def projects():
       return render_template("projects.html")

     @app.get('/projects/<string:project_slug>')
     def project_detail(project_slug):
       project = projects.get(project_slug, None)
       if project is None:
         return "Project not found", 404
       return render_template("")

     # Contact
     @app.get('/contact')
     def contact():
       return render_template("contact.html")

     if __name__ == "__main__":
       app.run(host='0.0.0.0', port=81, debug=True)
   ```

- [Markdown cheatsheet](https://gist.github.com/cuonggt/9b7d08a597b167299f0d) .
