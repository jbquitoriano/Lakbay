#Luzon Regions
def Travel_Plan_Proc():
	db.child("travelplan").child(user_id).remove()
	
	#db.child("travelplan").child(user_id).set(user_id)
	file = ("Lakbay.ph/Recc/Null/null_tours.json")	
	with open(file) as json_file:
			data = json.load(json_file)
	db.child("travelplan").child(user_id).child('plan_1').child('tours').set(data)
	file = ("Lakbay.ph/Recc/Null/null_restos.json")	
	with open(file) as json_file:
			data = json.load(json_file)
	db.child("travelplan").child(user_id).child('plan_1').child('resto').set(data)
	file = ("Lakbay.ph/Recc/Null/null_hotels.json")	
	with open(file) as json_file:
			data = json.load(json_file)
	db.child("travelplan").child(user_id).child('plan_1').child('hotel').set(data)

	
	#db.child("travelplan").child(user_id).child('plan_1').child('hotel').set("null")
	#db.child("travelplan").child(user_id).set(user_id)
	#db.child("travelplan").child(user_id).child("name").set(name)
	# current date and time
	# Converting datetime object to string
	dateTimeObj = datetime.now()
	timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
	#timestamp = datetime.timestamp(now)
	print("request timestamp = %s" %(timestampStr))
	#db.child("travelplan").child(user_id).child("timestamp").set(timestampStr)
	print("Status:")
	try:
		alpha = travel_plan_tours(city, rating_high, cat_list_tours).to_json("Lakbay.ph/Recc/Procs/%s_tours.json" %user_id, orient='records')
		file = ("Lakbay.ph/Recc/Procs/%s_tours.json" %user_id)	
		with open(file) as json_file:
			data = json.load(json_file)
		db.child("travelplan").child(user_id).child('plan_1').child('tours').set(data)
		status_tours = "Tours Successful."
		print (status_tours)
		db.child("travelplan").child(user_id).child('plan_1').child('tours_status').set(status_tours)
	except:
		status_tours = "Not enough tours results."
		print (status_tours)
		db.child("travelplan").child(user_id).child('plan_1').child('tours_status').set(status_tours)

#restos
	try:
		bravo = travel_plan_restos(city, rating_high).to_json("Lakbay.ph/Recc/Procs/%s_restos.json" %user_id, orient='records')
		file = ("Lakbay.ph/Recc/Procs/%s_restos.json" %user_id)
		with open(file) as json_file:
			data = json.load(json_file)
		db.child("travelplan").child(user_id).child('plan_1').child('resto').set(data)
		status_restos = "Restaurants Successful."
		print (status_restos)
		db.child("travelplan").child(user_id).child('plan_1').child('restos_status').set(status_restos)
	except:
		status_restos = "Not enough restos results."
		print (status_restos)
		db.child("travelplan").child(user_id).child('plan_1').child('restos_status').set(status_restos)

#hotels
	try:
		charlie = travel_plan_hotels(city, rating_high, cat_list_hotels).to_json("Lakbay.ph/Recc/Procs/%s_hotels.json" %user_id, orient='records')	
		file = ("Lakbay.ph/Recc/Procs/%s_hotels.json" %user_id)
		with open(file) as json_file:
			data = json.load(json_file)
		db.child("travelplan").child(user_id).child('plan_1').child('hotel').set(data)
		status_hotels = "Hotels Successful."
		print (status_hotels)
		db.child("travelplan").child(user_id).child('plan_1').child('hotels_status').set(status_hotels)
	except:
		status_hotels = "Not enough hotels results."
		print (status_hotels)
		db.child("travelplan").child(user_id).child('plan_1').child('hotels_status').set(status_hotels)
	pass

if __name__ == '__main__':
    # do something
    Travel_Plan_Proc()

#Supposedly ARH have separate python scripts so they can perform in parallel
