from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()
print "DB session created!	"

def fetch_Restaurants():

		restaurants = session.query(Restaurant).all()

		return restaurants

class webServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/restaurants"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output +="<html><body>"
				output +="<h1>Welcome to List o Restaurants!!</h1>"
				output +="Don't see something you like? <a href ='/restaurants/new' >Add a restaurant to our amazing list here</a></br></br>"
				output +="Please choose from our namesake list below:"
				
				restaurants = fetch_Restaurants()
				
				for restaurant in restaurants:
					output += "<h2>"
					output += restaurant.name
					output += "</h2>"
					output += "<a href = 'restaurants/%s/edit' >edit</a>" %restaurant.id
					output +="</br>"
					output +="<a href = 'restaurants/%s/delete' >delete</a></br></br>" %restaurant.id
					output +="</body></html>"
					# print restaurant.name
				self.wfile.write(output)
				
				# print output
				return

			if self.path.endswith("/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body><h1>Welcome to List o Restaurants!!</h1>"
				output +='''<form method='POST' enctype='multipart/form-data' action='/new'><h2>Add a restaurant name below:</h2><input name="newRestaurantName" type="text" ><input type="submit" value="Submit"> </form>'''
				output += "</body></html>"
				self.wfile.write(output)
				#print output
				return

			if self.path.endswith("/edit"):
				restaurantID = self.path.split("/")[2]
				queryRestaurant = session.query(Restaurant).filter_by(
					id=restaurantID).one()
				if queryRestaurant:

					self.send_response(200)
					self.send_header('content-type', 'text/html')
					self.end_headers()
					output = "<html><body>"
					output += "<h1>Welcome to List o Restaurants!!</h1>"
					output += "<form method='POST' enctype='multipart/form-data' action='restaurants/%s/edit'>" %restaurantID
					output += '''<h2>Modify a restaurant name below:</h2>'''
					output += '''<input name="diffRestaurantName" type="text" placeholder="%s" >''' %queryRestaurant.name
					output += "<input type='submit' value='Submit'> </form>" 
					output += "</body></html>"
					self.wfile.write(output)

				return

			if self.path.endswith("/delete"):
				restaurantID = self.path.split("/")[2]
				queryRestaurant = session.query(Restaurant).filter_by(
					id=restaurantID).one()
				if queryRestaurant:

					self.send_response(200)
					self.send_header('content-type', 'text/html')
					self.end_headers()
					output = "<html><body>"
					output += "<h1>Are you sure you want to delete %s? What did it ever do to you?</h1>" %queryRestaurant.name
					output += "<form method='POST' enctype='multipart/form-data' action='restaurants/%s/delete'>" %restaurantID
					output += "<input type='submit' value='Delete'> </form>"
					output += "</body></hmtl>"
					self.wfile.write(output)

		except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)

	


	def do_POST(self):
		try:
			#Accept submit from /delete page
			if self.path.endswith("/delete"):
				ctype, pdict = cgi.parse_header(
					self.headers.getheader('content-type'))

				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					restaurantID = self.path.split("/")[2]

					# Query restaurant name based on ID
					queryRestaurant = session.query(Restaurant).filter_by(
						id=restaurantID).one()

					# Check if query returned null result, persist deletion in DB
					if queryRestaurant != []:

						session.delete(queryRestaurant)
						session.commit()

						# Redirect back to restaurants page
						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers

			# Accept submit from /edit page
			if self.path.endswith("/edit"):
				ctype, pdict = cgi.parse_header(
					self.headers.getheader('content-type'))
				
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					newName = fields.get('diffRestaurantName')
					restaurantID = self.path.split("/")[2]
					
					# Query restaurant name based on ID
					queryRestaurant = session.query(Restaurant).filter_by(
						id=restaurantID).one()
					
					# Check if query returned null result, persist change in DB
					if queryRestaurant != []:
						
						queryRestaurant.name = newName[0]
						session.add(queryRestaurant)
						session.commit()
						
						# Redirect back to restaurants page
						self.send_response(301)
						self.send_header('Content-type', 'text/html')
						self.send_header('Location', '/restaurants')
						self.end_headers()
				
			if self.path.endswith("/restaurants/new"):
				ctype, pdict = cgi.parse_header(
					self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					newName = fields.get('newRestaurantName')

				# Persist new restaurant in database
				newRestaurant = Restaurant(name = newName[0])
				session.add(newRestaurant)
				session.commit()

				# Redirect back to restaurants page
				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()

			# print output

		except:
			pass

def main():
	try:
		port = 8080
		server = HTTPServer(('', port), webServerHandler)
		print "Web Server running on port %s"  % port
		server.serve_forever()
		
	except KeyboardInterrupt:
		print " ^C entered, stopping web server...."
		server.socket.close()

if __name__ == '__main__':
	main()