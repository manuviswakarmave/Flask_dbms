from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields

app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Initialize API
api = Api(app, title="DBMS CRUD API", description="A simple Flask API with to perform CRUD Operations")

# Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# Create Database Tables (Run Once)
with app.app_context():
    db.create_all()

# Define User Model for Swagger
user_model = api.model(
    "User",
    {
        "name": fields.String(required=True, description="User's Name"),
        "email": fields.String(required=True, description="User's Email"),
    },
)

# API Routes
@api.route("/users")
class UserList(Resource):
    @api.doc("Get all users")
    def get(self):
        users = User.query.all()
        return [{"id": user.id, "name": user.name, "email": user.email} for user in users]

    @api.doc("Add a new user")
    @api.expect(user_model)
    def post(self):
        data = request.json
        new_user = User(name=data["name"], email=data["email"])
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User added!"}, 201

@api.route("/users/<int:user_id>")
class UserDetail(Resource):
    @api.doc("Update user")
    @api.expect(user_model)
    def put(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404
        data = request.json
        user.name = data.get("name", user.name)
        user.email = data.get("email", user.email)
        db.session.commit()
        return {"message": "User updated!"}

    @api.doc("Delete user")
    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted!"}

if __name__ == "__main__":
    app.run(debug=True)
