from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

@app.route('/')
@app.route('/restaurants')
def viewRestaurants():

	return "This is the page to view all the restaurants"

@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def restaurantMenu(restaurant_id):
	#restaurant_id
	return "This is the page to view restaurant menu items"


@app.route('/restaurant/new/')
def newRestaurant():

	return "This is the page to create a new restaurant"


@app.route('/restaurant/<int:restaurant_id>/edit/')
def editRestaurant(restaurant_id):
	#restaurant_id
	return "This is the page to edit a restaurant's name"


@app.route('/restaurant/<int:restaurant_id>/delete/')
def deleteRestaurant(restaurant_id):
	#restaurant_id
	return "This is the page to delete a restaurant"

@app.route('/restaurant/<int:restaurant_id>/menu/new/')
def newMenuItem(restaurant_id):
	#restaurant_id
	return "This is the page to add a menu item"

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/')
def editMenuItem(restaurant_id, menu_id):
	#restaurant_id, menu_id
	return "This is the page to edit a menu item"

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
	#restaurant_id, menu_id
	return "This is the page to delete a menu Item"



if __name__ == '__main__':
    app.secret_key= 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)