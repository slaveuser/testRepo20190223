"""

This example we will walk you over the basics of MindsDB

The example code objective here is to predict the best retail price for a given property.

"""

from mindsdb import *

#


# First we initiate MindsDB
mdb = MindsDB()

# Here we use the model to make predictions (NOTE: You need to run train.py first)
result = mdb.predict(predict='rental_price', when={'number_of_rooms':2, 'sqft': 863, 'days_on_market':10}, model_name='home_rentals')

# you can now print the results
print('The predicted price is ${price} with {conf} confidence'.format(price=result.predicted_values[0]['rental_price'], conf=result.predicted_values[0]['prediction_confidence']))
