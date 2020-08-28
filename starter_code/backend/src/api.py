import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

#functions
#---------
def checkDatabaseTables(mydb):
    classes, models, table_names = [], [], []
    for clazz in mydb.Model._decl_class_registry.values():
        try:
            table_names.append(clazz.__tablename__)
            classes.append(clazz)
        except:
            pass
    for table in db.metadata.tables.items():
        if table[0] in table_names:
            models.append(classes[table_names.index(table[0])])
    print(table_names)


print('Hi app')
app = Flask(__name__)
print('Hi flask')
setup_db(app)
CORS(app)


@app.errorhandler(AuthError)
def unauthorizedUser(err):
    return jsonify({
        "success": False,
        "error": err.status_code,
        "message": err.error
    }), err.status_code

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

#checkDatabaseTables(db)
    

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def getDrinks():
    drinks_db = Drink.query.all()
    drinks = []
    # for drink in drinks_db:
    #     for r in json.loads(drink.recipe):
    #         {'color': r['color'], 'parts': r['parts']}
    #     print("drink")
    #     print(drink)
    #     # drink = json.dumps(drink) 
    #     drinks.append(drink)
    # for dicts in drinks_db:
    #     print(dicts['title'])
    # print(len(drinks_db))
    # print(type(drinks_db[0]))
    # print(type(drinks_db[0].recipe))
    # tmp = json.loads(drinks_db[0].recipe)
    # print(type(tmp))
    # print('color:', tmp.get('color'))
    # print('parts:', tmp.get('parts'))
    # for r in json.loads(drinks_db[0].recipe):
    #     print('type(r):', type(r))
    #     print('r:', r)
    #     print('color:', r[0])
    #     print('parts:', r[1])
    # print(drinks_db[0].short())

    for i in range(len(drinks_db)):
        drinks.append(drinks_db[i].short())
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def getDrinksDetail(jwt):
	#unpack the request headers
    drinks_db = Drink.query.all()
    #print(drinks_db)
    drinks = []
    for i in range(len(drinks_db)):
        drinks.append(drinks_db[i].long())
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def addDrink(jwt):
#     CREATE TABLE drink (
#         id INTEGER NOT NULL,
#         title VARCHAR(80),
#         recipe VARCHAR(180) NOT NULL,
#         PRIMARY KEY (id),
#         UNIQUE (title)
# );
    #get data
    data        = request.get_json()
    title       = data.get('title')
    recipe      = data.get('recipe')
    print(title)
    print(recipe)
	#create new drink
    newDrink = Drink(title=title,recipe=json.dumps(recipe))
    #insert in db
    Drink.insert(newDrink)
    #get the newly created drink
    print("newDrink.id")
    print(newDrink.id)
    newAddedDrink = Drink.query.filter(Drink.id == newDrink.id).all()
    #print("type")
    #print(type(newAddedDrink))
    #print("newAddedDrink")
    #print(newAddedDrink)
    #print("newAddedDrink.title")
    #print(newAddedDrink.title)
    # for item in newAddedDrink:
    #     print('item: ', item)
    # newAddedDrink.recipe = json.loads(newAddedDrink.recipe)
    # print("newAddedDrink")
    # print(newAddedDrink)
    return jsonify({
        "success": True,
        "drinks": [newAddedDrink[0].long()]
    }), 200 

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drinkId>', methods=['PATCH'])
@requires_auth('patch:drinks')
def editDrink(jwt,drinkId):
    #get data
    data        = request.get_json()
    title       = data.get('title')
    recipe      = data.get('recipe')
    print(title)
    print(recipe)
    #get the selected drink
    selectedDrink = Drink.query.filter(Drink.id == drinkId).one_or_none()
    if selectedDrink is None:
        abort(404)
    if title:
        selectedDrink.title = title
    if recipe:
        selectedDrink.recipe = recipe
    if title or recipe:
        #update the selected item 
        selectedDrink.update()
        #get the newly updated drink from database and send it back after updating
        updatedDrink = Drink.query.filter(Drink.id == drinkId).all()
        return jsonify({
        "success": True,
        "drinks": [updatedDrink[0].long()]
        }), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drinkId>', methods=['DELETE'])
@requires_auth('delete:drinks')
def deleteDrink(jwt,drinkId):
    #get the selected drink
    selectedDrink = Drink.query.filter(Drink.id == drinkId).one_or_none()
    if selectedDrink is None:
        abort(404)
    #delete the selected item 
    selectedDrink.delete()
    return jsonify({
    "success": True,
    "delete": drinkId
    }), 200


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
