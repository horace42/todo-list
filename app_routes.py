"""
Flask routes definitions
"""

from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap

from todo_db import db, List, Task, add_list, add_task
from forms import AddList, AddTask

# create the app
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
# initialize the app with the extension
db.init_app(app)
# if db doesn't exist, create db and all tables
with app.app_context():
    db.create_all()


# home
@app.route("/", methods=["GET", "POST"])
def home():
    """
    Render page with all lists in the db, and simple form to add new list. Each task has buttons to show/delete.
    :return: None
    """
    form = AddList(request.form)
    # get existing lists from db
    stmt = db.select(List).order_by(List.id)
    lists = db.session.execute(stmt).all()
    if request.method == "POST" and form.validate():
        # add new list and refresh
        form_data = form.data
        form_data.pop("submit", None)
        form_data.pop("csrf_token", None)
        add_list(form_data)
        lists = db.session.execute(stmt).all()
    # render index.html
    return render_template("index.html", lists=lists, form=form)


# list tasks
@app.route("/list", methods=["GET", "POST"])
def show_list():
    """
    Render page with all tasks in a list, and simple form to add new task. Each task has buttons for complete/delete.
    :return: None
    """
    list_id = request.args.get("id")
    form = AddTask(request.form)
    if list_id:
        # parameter id found in URL
        # get existing tasks from db
        stmt = db.select(Task).where(Task.list_id == list_id)
        results = db.session.execute(stmt).all()
        # get list name in separate query in case there are no tasks
        stmt_list = db.select(List.name).where(List.id == list_id)
        result_list = db.session.execute(stmt_list).first()
        if result_list:
            # parameter id is valid list id
            list_name = result_list[0]
            header = {"id": "Task ID",
                      "name": "Task name",
                      "deadline": "Deadline",
                      "completed": "Completed"
                      }
            if request.method == "POST" and form.validate():
                # add task and refresh
                form_data = form.data
                form_data.pop("submit", None)
                form_data.pop("csrf_token", None)
                form_data["list_id"] = list_id
                add_task(form_data)
                # refresh tasks
                results = db.session.execute(stmt).all()
            # render list.html
            return render_template("list.html",
                                   header=header,
                                   tasks=results,
                                   list_name=list_name,
                                   form=form)
        else:
            # parameter id not valid list id
            return redirect("/")
    else:
        # no parameter id in the URL
        return redirect("/")


@app.route("/delete")
def del_list():
    """
    Delete a list with all child tasks
    :return: None
    """
    list_id = request.args.get("id")
    if list_id:
        # parameter id found in URL
        # check if valid list id
        stmt = db.select(List.name).where(List.id == list_id)
        result_list = db.session.execute(stmt).first()
        if result_list:
            # parameter id is valid list id
            del_task_stmt = db.delete(Task).where(Task.list_id == list_id)
            del_list_stmt = db.delete(List).where(List.id == list_id)
            db.session.execute(del_task_stmt)
            db.session.execute(del_list_stmt)
            db.session.commit()
    return redirect("/")


@app.route("/del_task")
def del_task():
    """
    Delete a task
    :return: None
    """
    task_id = request.args.get("id")
    list_id = None
    if task_id:
        # parameter id found in URL
        del_task_stmt = db.delete(Task).where(Task.id == task_id).returning(Task.list_id)
        # using returning to get the list_id for the redirect
        list_id = db.session.execute(del_task_stmt).all()[0][0]
        db.session.commit()
    return redirect(url_for("show_list", id=list_id))


@app.route("/complete_task")
def mark_complete():
    """
    Mark a task as completed
    :return: None
    """
    task_id = request.args.get("id")
    list_id = None
    if task_id:
        # parameter id found in URL
        upd_task_stmt = db.update(Task).where(Task.id == task_id).values(completed=True).returning(Task.list_id)
        # using returning to get the list_id for the redirect
        list_id = db.session.execute(upd_task_stmt).all()[0][0]
        db.session.commit()
    return redirect(url_for("show_list", id=list_id))
