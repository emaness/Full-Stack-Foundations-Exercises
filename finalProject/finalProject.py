from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from sqlalchemy import create_engine, desc, asc
from sqlalchemy.orm import sessionmaker
from final_database_setup import Base, Restaurant, MenuItem, User
from flask import session as login_session
import random
import string
import requests
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json


#Fake Restaurants
#restaurant = {'name': 'The CRUDdy Crab', 'restaurant_id': '1'}
#restaurants = [{'name': 'The CRUDdy Crab', 'restaurant_id': '1'}, {'name':'Blue Burgers', 'restaurant_id':'2'},{'name':'Taco Hut', 'restaurant_id':'3'}]

#Fake Menu Items
#items = [{'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'}]
#item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

app = Flask(__name__)

CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu App"

engine = create_engine('sqlite:///yowzzerrestaurantswithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#adds user in database using login_session object
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

#queries for an existing user
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

#Login route. Creates anti-forgery state token to be called back later
@app.route('/login/')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + 
		string.digits) for x in xrange(32))

	login_session['state'] = state

	return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validates state token created in showLogin()
	print "starts gconnect"
	if request.args.get('state') != login_session['state']:
		print "nope"
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Gets authorization code
	code = request.data
	print request

	try:
		#Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		
		oauth_flow.redirect_uri = 'postmessage'
		credentials= oauth_flow.step2_exchange(code)
		print "access_token is: " + credentials.access_token
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	#checks if access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort.
	if result.get('error') is not None:

		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

		#verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

		#verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID doesn't match the application's."), 401)
		print "Token's client ID doesn't match the application's."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	#Store the access token in session.
	login_session['credentials'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	#Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)
	data = answer.json()
	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	#check if user exists or not, create if not, add user_id to login_session
	email = login_session['email']
	user_id= getUserID(email)
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id





	output = ''
	output += '<html>'
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src= "'
	output += login_session['picture']
	output += '>'
	return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['credentials']
    print 'In gdisconnect access token is %s' % login_session.get('credentials')
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session.get('credentials')
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
	del login_session['credentials'] 
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:
	
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

#API Endpoints
@app.route('/restaurants/JSON/')
def viewRestaurantsJSON():
	restaurants = session.query(Restaurant).all()

	return jsonify(Restaurants=[r.serialize for r in restaurants])

@app.route('/restaurant/<int:restaurant_id>/menu/JSON/')
def restaurantMenuJSON(restaurant_id):
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

	return jsonify(MenuItems=[i.serialize for i in items])

#HTML page routing paths

@app.route('/restaurant/<int:restaurant_id>/menu/<menu_id>/JSON/')
def menuItemJSON(restaurant_id, menu_id):
	item= session.query(MenuItem).filter_by(id=menu_id).one()

	return jsonify(item.serialize)

@app.route('/')
@app.route('/restaurants')
def viewRestaurants():

	restaurants = session.query(Restaurant).all()

	return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def restaurantMenu(restaurant_id):

	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).order_by(MenuItem.course.asc()).all()

	return render_template('menu.html', restaurant=restaurant, items=items)

@app.route('/restaurant/new/', methods=['GET','POST'])
def newRestaurant():
	if 'username' not in login_session:
		return redirect('/login')
	if request.method == 'POST':
		if request.form['name']:
			newRestaurant = Restaurant(name=request.form['name'], user_id=login_session['user_id'])
			session.add(newRestaurant)
			session.commit()
			output = newRestaurant.name + " has been added to our awesome club!"
			flash(output)
			return redirect(url_for('viewRestaurants'))
		else:
			output = "Please enter a value for 'restaurant name', or tap cancel to return to the restaurants page."
			flash(output)
			return redirect(url_for('newRestaurant'))
	else:
		return render_template('newrestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET','POST'])
def editRestaurant(restaurant_id):
	if 'username' not in login_session:
		return redirect('/login')
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		if request.form['name']:
			restaurant.name = request.form['name']
			session.add(restaurant)
			session.commit()
			output = "Restaurant edited"
			flash(output)
			return redirect(url_for('viewRestaurants'))
		else:
			output = "Please enter a value for 'restaurant name', or tap cancel to return to the restaurants page."
			flash(output)
			return redirect(url_for('editRestaurant', restaurant_id=restaurant_id))
	else:
		return render_template('editrestaurant.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
	if 'username' not in login_session:
		return redirect('/login')
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		session.delete(restaurant)
		session.commit()
		output = restaurant.name + " deleted"
		flash(output)
		return redirect(url_for('viewRestaurants'))
	else:
		return render_template('deleterestaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
	if 'username' not in login_session:
		return redirect('/login')
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		if request.form['name'] or request.form['course'] or request.form['description'] or request.form['price']:
			newItem = MenuItem(name=request.form['name'], course=request.form['course'], 
				description=request.form['description'], price=request.form['price'], restaurant_id=restaurant_id, user_id=restaurant.user_id)
			session.add(newItem)
			session.commit()
			output = newItem.name + " added"
			flash(output)
			return redirect(url_for('restaurantMenu', restaurant_id=restaurant.id))
		else:
			output = "Please enter a new value for any of the available fields, or hit cancel to return to the menu page."
			flash(output)
			return redirect(url_for('newMenuItem', restaurant_id=restaurant_id))
	else:
		return render_template('newmenuitem.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
	if 'username' not in login_session:
		return redirect('/login')
	item = session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method == 'POST':
		if request.form['name'] or request.form['course'] or request.form['description'] or request.form['price']:
			if request.form['name']:
				item.name=request.form['name']
			if request.form['course']:
				item.course=request.form['course']
			if request.form['description']:
				item.description =request.form['description']
			if request.form['price']:
				item.price = request.form['price']
			session.add(item)
			session.commit()
			output = "Menu item edited"
			flash(output)
			return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
		else: 
			output = "Please enter a new value for any of the available fields, or hit cancel to return to the menu page."
			flash(output)
			return redirect(url_for('editMenuItem', menu_id=menu_id, restaurant_id=restaurant_id))
	else:
		return render_template('editmenuitem.html', restaurant_id=restaurant_id, item=item)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
	if 'username' not in login_session:
		return redirect('/login')
	item=session.query(MenuItem).filter_by(id=menu_id).one()
	restaurant=session.query(Restaurant).filter_by(id=restaurant_id).one()

	if request.method == 'POST':
		session.delete(item)
		session.commit()
		output= item.name + " deleted"
		flash(output)
		return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
	
	else:
		return render_template('deletemenuitem.html', restaurant=restaurant, item=item)

if __name__ == '__main__':
    app.secret_key= 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)