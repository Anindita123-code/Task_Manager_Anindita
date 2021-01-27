import os
from flask import (
    Flask, render_template, redirect, flash, request, session, url_for)

from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

# create an instance of the mongo
mongo = PyMongo(app)

@app.route("/")
@app.route("/get_tasks")
# either URL will get into the same page
def get_tasks():
    tasks = list(mongo.db.tasks.find())
    return render_template("tasks.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists!")
            return render_template("register.html")

        new_user = {
                        "username": request.form.get("username").lower(),
                        "password": generate_password_hash(
                            request.form.get("password"))
                    }

        mongo.db.users.insert_one(new_user)
        # store the new user in session cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for('profile', username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if the user already exists
        user_exist = mongo.db.users.find_one(
            {"username": request.form.get("username")})
        if user_exist:
            # check for password match
            if check_password_hash(
                user_exist["password"], request.form.get(
                    "password").lower()):
                session["user"] = request.form.get("username").lower()
                flash("Welcome {}".format(request.form.get(
                    "username").capitalize()))
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for('login'))
        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile.html", username=username)


@app.route('/logout')
def logout():
    flash("You have been logged out")
    # session.clear()
    session.pop('user')
    return redirect(url_for('login'))


@app.route('/add_task', methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        task = {
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"),
            "due_date": request.form.get("due_date"),
            "is_urgent": "on" if request.form.get("is_urgent") else "off",
            "user_name": session["user"]
        }
        mongo.db.tasks.insert_one(task)
        flash("Task Inserted Successfully")
        return redirect(url_for('get_tasks'))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_task.html", categories=categories)


@app.route("/edit_task/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"),
            "due_date": request.form.get("due_date"),
            "is_urgent": "on" if request.form.get("is_urgent") else "off",
            "user_name": session["user"]
        }
        mongo.db.tasks.update({"_id": ObjectId(task_id)}, submit)
        flash("Task Updated Successfully")

    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_task.html", task=task, categories=categories)


@app.route("/delete_task/<task_id>")
def delete_task(task_id):
    mongo.db.tasks.remove({"_id": ObjectId(task_id)})
    flash("Task Deleted Successfully!")
    return redirect(url_for('get_tasks'))


@app.route("/show_categories")
def show_categories():
    categories = list(mongo.db.categories.find())
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = { "category_name": request.form.get("category_name") }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for('show_categories'))

    return render_template("add_category.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), port=int(
        os.environ.get("PORT")), debug=True)

