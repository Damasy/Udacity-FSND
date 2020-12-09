import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            'postgres', 'root', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "answer": "Apollo 10",
            "category": 5,
            "difficulty": 3,
            "id": 8,
            "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1896?"
        }
        self.empty_question = {
            'question': '',
            'answer': '',
            'difficulty': 0,
            'category': 0
        }

        self.search_term = {
            "searchTerm": 'Who discovered penicillin?'
        }

        self.empty_search_term = {
            "searchTerm": ''
        }

        self.invalid_search_term = {
            "searchTerm": 'askdjasdkjdiqe871623876azd'
        }

        self.quiz_data = {
            'previous_questions': [3, 7],
            'quiz_category': {
                'type': 'Science',
                'id': 1
            }
        }

        self.empty_quiz_data = {
            'previous_questions': '',
            'quiz_category': ''
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(data['categories'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])

    def test_questions_out_of_bound(self):
        res = self.client().get('/questions?page=999999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "resource not found")

    def test_success_delete_question(self):
        res = self.client().delete('/questions/6')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 6)
        self.assertEqual(data["message"], "Question successfully deleted")

    def test_failed_delete_question(self):
        res = self.client().delete('/questions/787878')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_delete_question_with_invalid_id(self):
        res = self.client().delete('/questions/abc123')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "resource not found")

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data["message"], "Question created successfully")
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])

    def test_create_question_with_empty_data(self):
        res = self.client().post('/questions', json=self.empty_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_search_questions(self):
        res = self.client().post('/questions/search', json=self.search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])

    def test_search_questions_with_empty_criteria(self):
        res = self.client().post('/questions/search', json=self.empty_search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_search_questions_with_empty_criteria(self):
        res = self.client().post('/questions/search', json=self.invalid_search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        # 'Science' category id is 1
        self.assertEqual(data['current_category'], 'Science')

    def test_invalid_category_questions(self):
        res = self.client().get('/categories/010/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_play_quiz_questions(self):
        res = self.client().post('/quizzes', json=self.quiz_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertNotEqual(data['question']['id'], 3)
        self.assertNotEqual(data['question']['id'], 7)
        self.assertEqual(data['question']['category'], 1)

    def test_no_data_to_play_quiz(self):
        res = self.client().post('/quizzes', json=self.empty_quiz_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "bad request")

    def test_invalid_data_to_play_quiz(self):
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertEqual(
            data['message'], 'An error has occured, please try again')

        # Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
