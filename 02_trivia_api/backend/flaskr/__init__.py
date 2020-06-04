import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    question = request.args.get('question', 1, type=int)
    start =  (question - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_questions = [question.format() for question in selection]
    current_questions = formatted_questions[start:end]

    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
      response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE,')
      response.headers.add('Access-Control-Allow-Credentials', 'true')
      return response 

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def categories():
    categories = Category.query.all()
    formated_categories = {cat.id:cat.type for cat in categories}

    if formated_categories == {}:
      abort(404)

    return jsonify({
      'success':True,
      'categories': formated_categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    questions = Question.query.all()
    current_questions = paginate_questions(request, questions)
    
    categories = Category.query.all()
    formated_categories = {cat.id:cat.type for cat in categories}
    
    if len(current_questions) == 0:
        abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': formated_categories,
      'current_category': 1
      })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try: 
      question = Question.query.get(question_id)
  
      if question is None:
        abort(404)
      
      question.delete()

      return jsonify({
        'success': True,
        'deleted_question_id':question_id
      })

    except:
        abort(422)
 
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods=['POST'])
  def search_or_add_question():
    body = request.get_json()

    try:
      search_term = body.get('searchTerm', None)
      #If no search term a new question is being added
      if search_term is None:
      
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        question = Question(question=new_question,answer=new_answer,difficulty=new_difficulty, category=new_category)
        question.insert()

        return jsonify({
          'success':True
        })
        
      #If search is being performed
      else:
        question_results = Question.query.filter(Question.question.ilike('%'+search_term+'%')).all()
        current_results = paginate_questions(request,question_results)

        return jsonify({
          'success':True,
          'questions':current_results,
          'total_questions':len(question_results),
          'current_category':{}
        })

    except:
      abort(422)
  
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_category(category_id):
    try: 
      questions = Question.query.filter(Question.category == category_id).all()
      current_questions = paginate_questions(request, questions)

      return jsonify({
        'success':True,
        'questions':current_questions,
        'total_questions':len(questions),
        'current_category': category_id
        })

    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    try:
      #Get category id
      cat = body.get('quiz_category', None)
      cat_id = cat['id']

      #Getting questions from category
      if cat_id == 0:
        quiz_questions = Question.query.all()
      else:
        quiz_questions = Question.query.filter(Question.category == cat_id).all()

      #Decide if the quiz is finished
      previous_questions = body.get('previous_questions', None)
      if len(previous_questions) == len(quiz_questions):
        return jsonify({
          'success':True,
          'question':False
        })

      #select question 
      else: 
        remaining_questions =[]
        for question in quiz_questions:
          if question.id not in previous_questions:
            remaining_questions.append(question)
        selected_question = random.choice(remaining_questions)
        previous_questions.append(selected_question.id)

        return jsonify({
          'success':True,
          'question':{
            'question':selected_question.question,
            'answer':selected_question.answer,
            'id':selected_question.id,
            'category':selected_question.category,
            'difficulty':selected_question.difficulty
            }
        })
    except:
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400

  return app
    