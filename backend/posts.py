from flask import request, make_response, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import Post

post_namespace = Namespace("posts", description="A namespace for post routes")

# A post's model for serialization
post_model = post_namespace.model(
    "Post", 
    {
        "id": fields.Integer(),
        "title": fields.String(),
        "content": fields.String(),
    }
)

# A route to test the API, returns hello after getting called
@post_namespace.route("/hello")
class HelloResource(Resource):
    def get(self):
        message = {
            "message": "Hello World"
        }

        return message
    

@post_namespace.route("/post")
class PostResource(Resource):
    # Returns all posts by all users
    @post_namespace.marshal_list_with(post_model)
    def get(self):
        get_all_posts = Post.query.all()
        return get_all_posts

    # Posts the post by a user, protected as a user needs to login first to access this route
    @jwt_required()
    @post_namespace.marshal_with(post_model)
    @post_namespace.expect(post_model)
    def post(self):
        current_user_id = get_jwt_identity()
        data = request.get_json()
        title = data.get("title")
        new_post = Post(
            title = data.get("title"),
            content = data.get("content"),
            user_id = current_user_id
        )

        new_post.save()
        return new_post, 201

@post_namespace.route("/post/<int:user_id>")
class GetPostResource(Resource):
    @jwt_required()
    @post_namespace.marshal_list_with(post_model)
    # Get all posts by a user
    def get(self, user_id):
        get_posts = Post.query.filter_by(user_id=user_id).all()
        return get_posts



@post_namespace.route("/posts/<int:id>")
class PostsResource(Resource):    
    # Get one post by its id
    @jwt_required()
    @post_namespace.marshal_with(post_model)
    def get(self, id):
        get_post = Post.query.get_or_404(id)

        return get_post
    
    # Update a post, protected route
    @jwt_required()
    @post_namespace.marshal_with(post_model)
    @post_namespace.expect(post_model)
    def put(self, id):
        update_post = Post.query.get_or_404(id)
        data = request.get_json()

        update_post.update(
            title = data.get("title"),
            content = data.get("content")
        )

        return update_post
    
    # Deletes the post, protected route
    @jwt_required()
    @post_namespace.marshal_with(post_model)
    @post_namespace.expect(post_model)
    def delete(self, id):
        delete_post = Post.query.get_or_404(id)

        delete_post.delete()

        return jsonify({
            "message": "Post deleted."
        }), 200




