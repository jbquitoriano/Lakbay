#Luzon Regions
def ML_Models():
	#models
	file1 = open(b"Lakbay.ph/algorithms/SVD_Model.sav","rb")
	SVD_Model = pickle.load(file1)
	file2 = open(b"Lakbay.ph/algorithms/CoClustering_Model.sav","rb")
	CoClustering_Model = pickle.load(file2)
	file3 = open(b"Lakbay.ph/algorithms/SlopeOne_Model.sav","rb")
	SlopeOne_Model = pickle.load(file3)

if __name__ == '__main__':
    # do something
    ML_Models()
