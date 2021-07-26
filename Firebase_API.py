#Luzon Regions
def Firebase_API():
#Firebase API
config = {
	"apiKey": "AIzaSyAzUmniefdVZKBRKHyA7HVX21y6RVDEZDU",
	"authDomain": "lakbayph-88c82.firebaseapp.com",
	"databaseURL": "https://lakbayph-88c82.firebaseio.com",
	"storageBucket": "lakbayph-88c82.appspot.com"
}
	
firebase = pyrebase.initialize_app(config)

db = firebase.database()

if __name__ == '__main__':
    # do something
    Firebase_API()
