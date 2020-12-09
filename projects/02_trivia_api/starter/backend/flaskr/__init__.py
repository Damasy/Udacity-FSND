import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = QUESTIONS_PER_PAGE + start
    if len(selection) != 0:
        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions
    else:
        return []


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={"/": {'origins': "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()

            if len(categories) == 0:
                abort(404)
            else:
                categories_dict = {}
                for category in categories:
                    categories_dict[category.id] = category.type

            return jsonify({
                "success": True,
                "categories": categories_dict,
                "total_categories": len(categories)
            }), 200

        except:
            abort(500)

    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        categories = Category.query.order_by(Category.id).all()

        if len(current_questions) == 0:
            abort(404)

        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(current_questions),
            'categories': categories_dict
        }), 200

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            question.delete()
            if(question is None):
                abort(404)

            return jsonify({
                "success": True,
                "deleted": question_id,
                'message': "Question successfully deleted"
            }), 200
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        question = request.get_json().get('question', '')
        answer = request.get_json().get('answer', '')
        difficulty = request.get_json().get('difficulty', '')
        category = request.get_json().get('category', '')

        try:
            new_question = Question(
                question=question, answer=answer, difficulty=difficulty, category=category)

            if ((question == '') or (answer == '')
                    or (difficulty == '') or (category == '')):
                abort(422)
            else:
                new_question.insert()

            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                "created": new_question.id,
                'questions': current_questions,
                'total_questions': len(current_questions),
                'message': 'Question created successfully'
            }), 201

        except:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        searchTerm = request.get_json().get('searchTerm', '')

        if searchTerm == '':
            abort(422)
        try:

            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike(f'%{searchTerm}%')).all()
            current_questions = paginate_questions(request, selection)

            if len(selection) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(current_questions)
            })
        except:
            abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_category_questions(category_id):
        category = Category.query.filter_by(id=category_id).one_or_none()

        if (category is None):
            abort(422)

        questions = Question.query.filter_by(category=category_id).all()

        paginated_questions = paginate_questions(
            request, questions)

        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(questions),
            'current_category': category.type
        })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz_question():
        previous_questions = request.get_json().get('previous_questions')
        quiz_category = request.get_json().get('quiz_category')

        if ((quiz_category is '') or (previous_questions is '')):
            abort(400)

        if (quiz_category['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(
                category=quiz_category['id']).all()

        def get_random_question():
            return questions[random.randint(0, len(questions)-1)]

        next_question = get_random_question()

        found = True

        while found:
            if next_question.id in previous_questions:
                next_question = get_random_question()
            else:
                found = False

        return jsonify({
            'success': True,
            'question': next_question.format(),
        }), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'An error has occured, please try again'
        }), 500

    return app
