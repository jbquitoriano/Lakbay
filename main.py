#===============================================================================================REQUISITES=========================================================================================================
#import required libraries, packages, and modules
import pandas as pd
import pickle
import json
import requests
import os
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse
from typing import Dict
from datetime import datetime
import pyrebase
import warnings
warnings.simplefilter('ignore')

#models
file1 = open(b"Lakbay.ph/Algorithms/SVD_Model.sav","rb")
SVD_Model = pickle.load(file1)
file2 = open(b"Lakbay.ph/Algorithms/CoClustering_Model.sav","rb")
CoClustering_Model = pickle.load(file2)
file3 = open(b"Lakbay.ph/Algorithms/SlopeOne_Model.sav","rb")
SlopeOne_Model = pickle.load(file3)

#Firebase API
config = {
	"apiKey": "AIzaSyAzUmniefdVZKBRKHyA7HVX21y6RVDEZDU",
	"authDomain": "lakbayph-88c82.firebaseapp.com",
	"databaseURL": "https://lakbayph-88c82.firebaseio.com",
	"storageBucket": "lakbayph-88c82.appspot.com"
}
	
firebase = pyrebase.initialize_app(config)

db = firebase.database()

#==============================================================================================/REQUISITES=========================================================================================================

#===============================================================================================LOCATIONS==========================================================================================================
#Luzon Regions
#CAR = ["Tabuk","Baguio"]
#NCR = ["Caloocan","Las Pinas","Makati","Malabon","Mandaluyong","Manila","Marikina",
#       "Muntinlupa","Navotas","Paranaque","Pasay","Pasig","Quezon","San Juan",
#       "Taguig","Valenzuela"]
temp_cities = ["Makati","Marikina","Pasay","Pasig","Quezon","San Juan","Taguig"]
#I = ["Alaminos","Batac","Candon","Dagupan","Laoag","San Carlos Pangasinan","San Fernando La Union",
#     "Urdaneta","Vigan"]
#II = ["Cauayan","Ilagan","Santiago","Tuguegarao"]
#III = ["Angeles","Balanga","Cabanatuan","Gapan","Mabalacat","Malolos","Meycauayan",
#       "Munoz","Olongapo","Palayan","San Fernando Pampanga","San Jose","San Jose del Monte","Tarlac"]
#IV_A = ["Antipolo","Bacoor","Batangas","Binan","Cabuyao","Calamba","Cavite",
#        "Dasmarin	as","General Trias","Imus","Lipa","Lucena","San Pablo","San Pedro",
#        "Santo Tomas","Santa Rosa","Tagaytay","Tanauan","Tayabas","Trece Martires"]
#IV_B = ["Calapan","Puerto Princesa"]
#V = ["Iriga","Legazpi","Ligao","Masbate","Naga","Sorsogon","Tabaco"]	
#==============================================================================================/LOCATIONS==========================================================================================================

#================================================================================================TOURS=============================================================================================================

def travel_plan_tours(city, rating_high, cat_list_tours):
	df_review = pd.read_excel("Lakbay.ph/Target_Datasets/tours_and_attractions_review.xlsx")
	df_element = pd.read_excel("Lakbay.ph/Target_Datasets/tours_and_attractions.xlsx")
	#df_element = df_element.dropna()
	rating_low = 1 #override

	#step 3
	#code priority to target city not adjacent
	if city in temp_cities:# or city in NCR or city in I or city in II or city in III or city in IV_A or city in IV_B or city in V:
		adjacent = pd.read_excel("Lakbay.ph/Adjacent_Cities_Dataset/Luzon.xlsx")
		#adjacent = pd.read_excel("Lakbay.ph/Adjacent_Cities_Dataset/%s.xlsx",%Island_Group)
		adjacent = adjacent.loc[adjacent["Target"] == city]
		adjacent = (adjacent.Adjacent.apply(lambda x: pd.Series(x.split(', '))).transpose().iloc[:,0]).values.tolist()
		adjacent.append(city)
		adjacent.reverse()
		x = df_element[df_element['location'].apply(lambda x: pd.Series(x.split(', ')).isin(adjacent).any())]
	tags_type = pd.read_excel("Lakbay.ph/Target_Datasets/tours-tags.xlsx")
	tag_res = tags_type.iloc[:,tags_type.columns.isin(cat_list_tours)]
	dct = {}
	for i in tag_res.columns:
		dct['list:%s' % i] = tag_res[i].dropna().values.tolist()
	tag_merged = []
	for i in dct:
		list(map(lambda x: tag_merged.append(x), dct[i]))
	#step 4
	#content filtering
	uid_df0 = x[x['type'].apply(lambda y: pd.Series(y.split(', ')).isin(tag_merged).any())]
	uid_df1 = x.loc[(x['ratings'] >= rating_low) & (x['ratings'] <= rating_high)]
	if len(uid_df0) >= len(uid_df1):# and len(uid_df1) >= len(uid_df2) and len(uid_df2) >= len(uid_df3):
		uid_df2 = uid_df0.merge(uid_df1, how = 'inner' ,indicator=False)
		uid_dfF = uid_df2.merge(df_review, on = ['name','ratings'] ,indicator = False) #change to index format
	elif len(uid_df1) >= len(uid_df0):# and len(uid_df1) >= len(uid_df3) and len(uid_df3) >= len(uid_df2):
		uid_df2 = uid_df1.merge(uid_df0, how = 'inner' ,indicator=False)
		uid_dfF = uid_df2.merge(df_review, on = ['name','ratings'] ,indicator=False) #change to index format
	#step 5
	#append all items content filtered
	uid_dfF_i = uid_dfF.name.value_counts().to_frame().reset_index()
	items = []
	for i in range(len(uid_dfF_i)):
		items.append(uid_dfF_i.iloc[i][0])
	items = list(set(items))
	#step 6
	#append all matched user ids
	uid_dfF_u = uid_dfF.user_id.value_counts().to_frame().reset_index()
	uid = []
	for i in range(len(uid_dfF_u)):
		uid.append(uid_dfF_u.iloc[i][0])
	uid = list(set(uid))
	#step 7
	#new dataframe reviews dataset filtered by user ids from previous step
	dfr = df_review[df_review.user_id.isin(uid)]
	dfr = dfr[~dfr.name.isin(items)]
	#append all items content filtered
	dfr = dfr.name.value_counts().to_frame().reset_index()
	#step 8
	#append items
	items = []
	for i in range(len(dfr)):
		items.append(dfr.iloc[i][0])
	items = list(set(items))
	#step 9
	#new dataframe with element dataset filtered by items on previous step
	df_element = df_element[df_element.name.isin(items)]
	df_element.head()
	#step 10
	#code priority to target city not adjacent
	if city in temp_cities:#CAR or city in NCR or city in I or city in II or city in III or city in IV_A or city in IV_B or city in V:
		adjacent = pd.read_excel("Lakbay.ph/Adjacent_Cities_Dataset/Luzon.xlsx")
		adjacent = adjacent.loc[adjacent["Target"] == city]
		adjacent = (adjacent.Adjacent.apply(lambda x: pd.Series(x.split(', '))).transpose().iloc[:,0]).values.tolist()
		adjacent.append(city)
		adjacent.reverse()
		x = df_element[df_element['location'].apply(lambda x: pd.Series(x.split(', ')).isin(adjacent).any())]
	#step 11
	#apply model to get estimate scores using uids
	d = {}
	for i in range(len(uid)):
		d['df:%s' % i] = x
		d['df:%s' % i]['Estimate_Score'] = d['df:%s' % i]['name'].apply(lambda iid : SlopeOne_Model.predict(uid[i], iid, r_ui = None, clip = True, verbose = False).est)
		d['df:%s' % i] = d['df:%s' % i].sort_values('Estimate_Score', ascending = False)
	#merge them all
	for i in range(len(d)):
		if (i+1) < len(d):
			d['df:%s' % (i+1)] = d['df:%s' % i].merge(d['df:%s' % (i+1)], how = 'outer', indicator = False)
		else: break
	if (len(d)-1) <= 0: alpha = d['df:0']
	else: alpha = d['df:%s' % (len(d)-1)]
	#step 12
	#average scores and sort descending
	alpha["avg"] = alpha["name"].apply(lambda x: alpha['Estimate_Score'].loc[alpha['name'] == x].mean())
	print (alpha.drop_duplicates(subset = 'name').sort_values(by = 'avg',ascending = False))
	alpha = alpha.drop_duplicates(subset = 'name').sort_values(by = 'avg',ascending = False).drop(columns = ['Estimate_Score', 'avg'])
	#final output sort by location priority
	alpha = alpha[alpha['location'].apply(lambda x: pd.Series(x.split(', ')).isin(adjacent).any())]
	alpha.location = alpha.location.astype("category")
	alpha.location.cat.set_categories(adjacent, inplace=True)
	alpha = alpha.sort_values(["location","ratings"])#.reset_index().drop(columns=['index']).reset_index()
	alpha = alpha.head(3)
	return (alpha)
	#alpha

#===============================================================================================/TOURS=============================================================================================================

#================================================================================================RESTOS============================================================================================================

def travel_plan_restos(city, rating_high):
    df_review = pd.read_excel("Lakbay.ph/Target_Datasets/restaurants_review.xlsx")
    df_element = pd.read_excel("Lakbay.ph/Target_Datasets/restaurants.xls")
    df_element = df_element.dropna()
    cat_list_restos = ["Vegetarian Friendly", "Southeast Asian", "Other Chinese Cuisine"]#, "International", "Fast Food", "Filipino", "American", "Steakhouse", "Cafe", "Italian", "Singaporean", "Mexican","Grill", "Dessert", "Pizza", "European", "Caribbean", "Barbecue", "Seafood", "Fusion", "Japanese", "Bakery", "Contemporary", "Thai", "Diner", "Pub", "Bar", "Chinese", "Asian"] #override

    rating_low = 1 #override

    #step 3
    #code priority to target city not adjacent
    if city in temp_cities:#CAR or city in NCR or city in I or city in II or city in III or city in IV_A or city in IV_B or city in V:
        #os.chdir("Luzon/CAR")
        adjacent = pd.read_excel("Lakbay.ph/Adjacent_Cities_Dataset/Luzon.xlsx")
        adjacent = adjacent.loc[adjacent["Target"] == city]
        adjacent = (adjacent.Adjacent.apply(lambda x: pd.Series(x.split(', '))).transpose().iloc[:,0]).values.tolist()
        adjacent.append(city)
        adjacent.reverse()
        x = df_element[df_element['location'].apply(lambda x: pd.Series(x.split(', ')).isin(adjacent).any())]
    #step 4
    #content filtering
    uid_df0 = x[x['type'].isin(cat_list_restos)]
    uid_df1 = x.loc[(x['ratings'] >= rating_low) & (x['ratings'] <= rating_high)]
    if len(uid_df0) >= len(uid_df1):
        uid_df2 = uid_df0.merge(uid_df1, how = 'inner' ,indicator=False)
        uid_dfF = uid_df2.merge(df_review, on = ['name','ratings'] ,indicator = False)
    elif len(uid_df1) >= len(uid_df0):
        uid_df2 = uid_df1.merge(uid_df0, how = 'inner' ,indicator=False)
        uid_dfF = uid_df2.merge(df_review, on = ['name','ratings'] ,indicator=False)
    #step 5
    #append all items content filtered
    uid_dfF_i = uid_dfF.name.value_counts().to_frame().reset_index()
    items = []
    for i in range(len(uid_dfF_i)):
        items.append(uid_dfF_i.iloc[i][0])
    items = list(set(items))
    #step 6
    #append all matched user ids
    uid_dfF_u = uid_dfF.user_id.value_counts().to_frame().reset_index()
    uid = []
    for i in range(len(uid_dfF_u)):
        uid.append(uid_dfF_u.iloc[i][0])
    uid = list(set(uid))
    #step 7
    #new dataframe reviews dataset filtered by user ids from previous step
    dfr = df_review[df_review.user_id.isin(uid)]
    dfr = dfr[~dfr.name.isin(items)]
    #append all items content filtered
    dfr = dfr.name.value_counts().to_frame().reset_index()
    #step 8
    #append items
    #fin_items = []
    for i in range(len(dfr)):
        items.append(dfr.iloc[i][0])
    items = list(set(items))
    #step 9
    #new dataframe with element dataset filtered by items on previous step
    df_element = df_element[df_element.name.isin(items)]
    #step 10
    #code priority to target city not adjacent
    if city in temp_cities:#CAR or city in NCR or city in I or city in II or city in III or city in IV_A or city in IV_B or city in V:
        adjacent = pd.read_excel("Lakbay.ph/Adjacent_Cities_Dataset/Luzon.xlsx")
        adjacent = adjacent.loc[adjacent["Target"] == city]
        adjacent = (adjacent.Adjacent.apply(lambda x: pd.Series(x.split(', '))).transpose().iloc[:,0]).values.tolist()
        adjacent.append(city)
        adjacent.reverse()
        x = df_element[df_element['location'].apply(lambda x: pd.Series(x.split(', ')).isin(adjacent).any())]
    
    #step 11
    #apply model to get estimate scores using uids
        d = {}
    for i in range(len(uid)):
        d['df:%s' % i] = x
        d['df:%s' % i]['Estimate_Score'] = d['df:%s' % i]['name'].apply(lambda iid: CoClustering_Model.predict(uid[i], iid, r_ui=None, clip=True, verbose=False).est)
        d['df:%s' % i] = d['df:%s' % i].sort_values('Estimate_Score', ascending = False)
    for i in range(len(d)):
        if (i+1) < len(d):
            d['df:%s' % (i+1)] = d['df:%s' % i].merge(d['df:%s' % (i+1)], how = 'outer', indicator = False)
        else: break
    #step 12
    #average scores and sort descending
    if (len(d)-1) <= 0: bravo = d['df:0']
    else: bravo = d['df:%s' % (len(d)-1)]
    bravo["avg"] = bravo["name"].apply(lambda x: bravo['Estimate_Score'].loc[bravo['name'] == x].mean())
    print (bravo.drop_duplicates(subset = 'name').sort_values(by = 'avg',ascending = False))
    bravo = bravo.drop_duplicates(subset = 'name').sort_values(by = 'avg',ascending = False).drop(columns = ['Estimate_Score', 'avg'])
    #final output sort by location priority
    bravo = bravo[bravo['location'].apply(lambda x: pd.Series(x.split(', ')).isin(adjacent).any())]
    bravo.location = bravo.location.astype("category")
    bravo.location.cat.set_categories(adjacent, inplace=True)
    bravo = bravo.sort_values(["location","ratings"])#.reset_index().drop(columns=['index']).reset_index()
    bravo = bravo.head(1)
    return (bravo)
    #bravo

#===============================================================================================/RESTOS============================================================================================================

#================================================================================================HOTELS============================================================================================================

def travel_plan_hotels(city, rating_high, cat_list_hotels):
    #step 1
    #load datasets
    df_review = pd.read_excel("Lakbay.ph/Target_Datasets/hotels_and_lodging_review.xlsx")
    df_element = pd.read_excel("Lakbay.ph/Target_Datasets/hotels_and_lodging.xlsx")#, orient='records')
    #df_element = df_element.dropna()
    rating_low = 1 #override
    #step 3
    #code priority to target city not adjacent
    if city in temp_cities:#CAR or city in NCR or city in I or city in II or city in III or city in IV_A or city in IV_B or city in V:
        #os.chdir("Luzon/CAR")
        adjacent = pd.read_excel("Lakbay.ph/Adjacent_Cities_Dataset/Luzon.xlsx")
        adjacent = adjacent.loc[adjacent["Target"] == city]
        adjacent = (adjacent.Adjacent.apply(lambda x: pd.Series(x.split(', '))).transpose().iloc[:,0]).values.tolist()
        adjacent.append(city)
        adjacent.reverse()
        x = df_element[df_element['location'].apply(lambda x: pd.Series(x.split(', ')).isin(adjacent).any())]
    #step 4
    #content filtering
        uid_df0 = x[x['class'].isin(cat_list_hotels)]
        uid_df1 = x.loc[(x['ratings'] >= rating_low) & (x['ratings'] <= rating_high)]
        if len(uid_df0) >= len(uid_df1):
            uid_df2 = uid_df0.merge(uid_df1, how = 'inner' ,indicator=False)
            uid_dfF = uid_df2.merge(df_review, on = ['name','ratings'] ,indicator = False)
        elif len(uid_df1) >= len(uid_df0):
            uid_df2 = uid_df1.merge(uid_df0, how = 'inner' ,indicator=False)
            uid_dfF = uid_df2.merge(df_review, on = ['name','ratings'] ,indicator=False)
    #step 5
    #append all items content filtered
    uid_dfF_i = uid_dfF.name.value_counts().to_frame().reset_index()
    items = []
    for i in range(len(uid_dfF_i)):
        items.append(uid_dfF_i.iloc[i][0])
    items = list(set(items))
    #step 5
    #append all items content filtered
    uid_dfF_i = uid_dfF.name.value_counts().to_frame().reset_index()
    items = []
    for i in range(len(uid_dfF_i)):
        items.append(uid_dfF_i.iloc[i][0])
    items = list(set(items))
    #step 6
    #append all matched user ids
    uid_dfF_u = uid_dfF.user_id.value_counts().to_frame().reset_index()
    uid = []
    for i in range(len(uid_dfF_u)):
        uid.append(uid_dfF_u.iloc[i][0])
    uid = list(set(uid))
    #step 7
    #new dataframe reviews dataset filtered by user ids from previous step
    dfr = df_review[df_review.user_id.isin(uid)]
    dfr = dfr[~dfr.name.isin(items)]
    #append all items content filtered
    dfr = dfr.name.value_counts().to_frame().reset_index()
    #step 8
    #append items
    #fin_items = []
    for i in range(len(dfr)):
        items.append(dfr.iloc[i][0])
    items = list(set(items))
    #step 9
    #new dataframe with element dataset filtered by items on previous step
    df_element = df_element[df_element.name.isin(items)]
    #step 10
    #code priority to target city not adjacent
    if city in temp_cities:#CAR or city in NCR or city in I or city in II or city in III or city in IV_A or city in IV_B or city in V:
        adjacent = pd.read_excel("Lakbay.ph/Adjacent_Cities_Dataset/Luzon.xlsx")
        adjacent = adjacent.loc[adjacent["Target"] == city]
        adjacent = (adjacent.Adjacent.apply(lambda x: pd.Series(x.split(', '))).transpose().iloc[:,0]).values.tolist()
        adjacent.append(city)
        adjacent.reverse()
        x = df_element[df_element['location'].apply(lambda x: pd.Series(x.split(', ')).isin(adjacent).any())]
    #step 11
    #apply model to get estimate scores using uids
    d = {}
    for i in range(len(uid)):
        d['df:%s' % i] = x
        d['df:%s' % i]['Estimate_Score'] = d['df:%s' % i]['name'].apply(lambda iid : SVD_Model.predict(uid[i], iid, r_ui = None, clip = True, verbose = False).est)
        d['df:%s' % i] = d['df:%s' % i].sort_values('Estimate_Score', ascending = False)
    #merge them all
    for i in range(len(d)):
        if (i+1) < len(d):
            d['df:%s' % (i+1)] = d['df:%s' % i].merge(d['df:%s' % (i+1)], how = 'outer', indicator = False)
        else: break
    if (len(d)-1) <= 0: charlie = d['df:0']
    else: charlie = d['df:%s' % (len(d)-1)]
    #step 12
    #average scores and sort descending
    charlie["avg"] = charlie["name"].apply(lambda x: charlie['Estimate_Score'].loc[charlie['name'] == x].mean())
    print (charlie.drop_duplicates(subset = 'name').sort_values(by = 'avg',ascending = False))
    charlie = charlie.drop_duplicates(subset = 'name').sort_values(by = 'avg',ascending = False).drop(columns = ['Estimate_Score', 'avg'])
    #final output sort by location
    charlie = charlie[charlie['location'].apply(lambda x: pd.Series(x.split(', ')).isin(adjacent).any())]
    charlie.location = charlie.location.astype("category")
    charlie.location.cat.set_categories(adjacent, inplace=True)
    charlie = charlie.sort_values(["location","class"])#.reset_index().drop(columns=['index']).reset_index()
    charlie = charlie.head(1)
    return (charlie)
    #charlie

#===============================================================================================/HOTELS============================================================================================================

#===============================================================================================MACHINE============================================================================================================
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

app = FastAPI()

@app.post("/users/", response_model=Rating, status_code=201)
async def create_item(rating:Rating):
	print("City: " + str(rating.city['name']))
	print("ownerID: " +str(rating.ownerId))
	print("Ratings:" +str(rating.ratingRange))
	#print("Attraction Tags: " +str(rating.attractionTags['label']))
	#print("Hotel Tags:" +str(rating.hotelTags))
	user_id = rating.ownerId
	name = rating.name
	#name = 'lolz'
	city = rating.city['name']
	rating_high = rating.ratingRange
	if rating_high == None or rating_high == 0:
		rating_high = 5
	#cat_list_tours = rating.attractionTags['label']
	#cat_list_hotels = rating.hotelTags['label']
		
	
	cat_list_tours = ['Water & Seaside Sports & Activities','Architecture, Art, History, & Museums','Places in the City'] #override
	cat_list_hotels = [2,3,4,5] #override


#TRAVEL PLAN_1
#tours
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
#==============================================================================================/MACHINE============================================================================================================
