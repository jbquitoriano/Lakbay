#Luzon Regions
class Rating(BaseModel):
	name: str = None
	city: Dict[str,str]
	ownerId: str
	ratingRange: int = None
	attractionTags: Dict[str,str] = None
	hotelTags: Dict[str,str] = None
	status_tours: str = None
	status_restos: str = None
	status_hotels: str = None

def API_Mobile():
app = FastAPI()

@app.post("/users/", response_model=Rating, status_code=201)
async def create_item(rating:Rating):
	#status
	print("City: " + str(rating.city['name']))
	print("ownerID: " +str(rating.ownerId))
	print("Ratings:" +str(rating.ratingRange))
	print("Attraction Tags: " +str(rating.attractionTags['label']))
	print("Hotel Tags:" +str(rating.hotelTags))
	user_id = rating.ownerId
	name = rating.name
	city = rating.city['name']
	rating_high = rating.ratingRange
	if rating_high == None or rating_high == 0:
		rating_high = 5

if __name__ == '__main__':
    # do something
    API_Mobile()
