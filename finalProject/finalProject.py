from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'restaurant_id': '1'}
restaurants = [{'name': 'The CRUDdy Crab', 'restaurant_id': '1'}, {'name':'Blue Burgers', 'restaurant_id':'2'},{'name':'Taco Hut', 'restaurant_id':'3'}]

#Fake Menu Items
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

app = Flask(__name__)

@app.route('/')
@app.route('/restaurants')
def viewRestaurants():

	return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def restaurantMenu(restaurant_id):
	#restaurant_id
	return render_template('menu.html', restaurant=restaurant, items=items)

@app.route('/restaurant/new/')
def newRestaurant():

	return render_template('newrestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit/')
def editRestaurant(restaurant_id):
	#restaurant_id
	return render_template('editrestaurant.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete/')
def deleteRestaurant(restaurant_id):
	#restaurant_id
	return render_template('deleterestaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/new/')
def newMenuItem(restaurant_id):
	#restaurant_id
	return render_template('newmenuitem.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/')
def editMenuItem(restaurant_id, menu_id):
	#restaurant_id, menu_id
	return render_template('editmenuitem.html', restaurant_id=restaurant_id, item=item)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
	#restaurant_id, menu_id
	return render_template('deletemenuitem.html', restaurant=restaurant, items=items)



if __name__ == '__main__':
    app.secret_key= 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)