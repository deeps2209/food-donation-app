from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from geopy.distance import geodesic

app = Flask(__name__)

app.secret_key = "foodapp"

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

# ---------------------------------------------------
# USER TABLE
# ---------------------------------------------------

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))

    password = db.Column(db.String(100))

    role = db.Column(db.String(20))


# ---------------------------------------------------
# FOOD TABLE
# ---------------------------------------------------
class Food(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    food_name = db.Column(db.String(100))

    quantity = db.Column(db.Integer)

    location = db.Column(db.String(100))

    donor = db.Column(db.String(100))

    matched_ngo = db.Column(db.String(100))

    ngo_location = db.Column(db.String(100))

    volunteer_name = db.Column(db.String(100))

    volunteer_phone = db.Column(db.String(20))

    vehicle = db.Column(db.String(50))

    volunteer_location = db.Column(db.String(100))

    status = db.Column(
        db.String(50),
        default="Pending"
    )


# ---------------------------------------------------
# CREATE DATABASE
# ---------------------------------------------------

with app.app_context():
    db.create_all()


# ---------------------------------------------------
# AI ROUTE OPTIMIZATION
# ---------------------------------------------------

def ai_route_optimization(
    donor_location,
    ngo_location
):

    donor_coordinates = {

        "MG Road": (12.9756, 77.6050),

        "BTM": (12.9166, 77.6101),

        "Indiranagar": (12.9719, 77.6412),

        "Whitefield": (12.9698, 77.7500)
    }

    ngo_coordinates = {

        "BTM": (12.9166, 77.6101),

        "Hope Shelter": (12.2958, 76.6394),

        "Helping Hands NGO": (12.9698, 77.7500)
    }

    donor_coord = donor_coordinates.get(
        donor_location,
        (12.9716, 77.5946)
    )

    ngo_coord = ngo_coordinates.get(
        ngo_location,
        (12.9716, 77.5946)
    )

    # DISTANCE
    distance = geodesic(
        donor_coord,
        ngo_coord
    ).km

    # ETA
    estimated_time = round(distance * 3)

    # GOOGLE MAP LINK
    map_link = f"""
    https://www.google.com/maps/dir/
    {donor_coord[0]},{donor_coord[1]}/
    {ngo_coord[0]},{ngo_coord[1]}
    """

    return round(distance, 2), estimated_time, map_link


# ---------------------------------------------------
# LOGIN PAGE
# ---------------------------------------------------

@app.route('/')
def home():

    return render_template('login.html')


# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        user = User(

            username=request.form['username'],

            password=request.form['password'],

            role=request.form['role']
        )

        db.session.add(user)

        db.session.commit()

        return redirect('/')

    return render_template('register.html')


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------

@app.route('/login', methods=['POST'])
def login():

    user = User.query.filter_by(

        username=request.form['username'],

        password=request.form['password']

    ).first()

    if user:

        session['role'] = user.role

        if user.role == "Donor":

            return redirect('/donor')

        elif user.role == "NGO":

            return redirect('/ngo')

        elif user.role == "Volunteer":

            return redirect('/volunteer')

        else:

            return redirect('/admin')

    return "Invalid Login"


# ---------------------------------------------------
# DONOR DASHBOARD
# ---------------------------------------------------

@app.route('/donor')
def donor():

    return render_template('donor.html')


# ---------------------------------------------------
# ADD FOOD
# ---------------------------------------------------

@app.route('/food', methods=['GET', 'POST'])
def food():

    if request.method == 'POST':

        food = Food(

            food_name=request.form['food_name'],

            quantity=request.form['quantity'],

            location=request.form['location'],

            donor=request.form['donor']
        )

        db.session.add(food)

        db.session.commit()

        return redirect('/donor')

    return render_template('food.html')


# ---------------------------------------------------
# NGO DASHBOARD
# ---------------------------------------------------

@app.route('/ngo')
def ngo():

    foods = Food.query.all()

    return render_template(
        'ngo.html',
        foods=foods
    )


# ---------------------------------------------------
# NGO ACCEPT
# ---------------------------------------------------

@app.route('/accept/<int:id>')
def accept(id):

    food = Food.query.get(id)

    if food:

        food.status = "Accepted"

        db.session.commit()

    return redirect('/ngo')


# ---------------------------------------------------
# NGO REJECT
# ---------------------------------------------------

@app.route('/reject/<int:id>')
def reject(id):

    food = Food.query.get(id)

    if food:

        food.status = "Rejected"

        db.session.commit()

    return redirect('/ngo')


# ---------------------------------------------------
# NGO CLAIM
# ---------------------------------------------------

@app.route('/claim/<int:id>')
def claim(id):

    food = Food.query.get(id)

    food.status = "Claimed"

    # NGO Details
    food.matched_ngo = "Helping Hands NGO"

    food.ngo_location = "BTM"

    # Volunteer Details
    food.volunteer_name = "Rahul"

    food.volunteer_phone = "9876543210"

    food.vehicle = "Bike"

    food.volunteer_location = "Indiranagar"

    db.session.commit()

    return redirect(f'/delivery/{id}')


# ---------------------------------------------------
# VOLUNTEER DASHBOARD
# ---------------------------------------------------

@app.route('/volunteer')
def volunteer():

    foods = Food.query.filter_by(
        status="Claimed"
    ).all()

    route_data = []

    for food in foods:

        distance, eta, map_link = ai_route_optimization(

            food.location,

            food.ngo_location
        )

        route_data.append({

            "id": food.id,

            "food_name": food.food_name,

            "quantity": food.quantity,

            "donor_location": food.location,

            "ngo_location": food.ngo_location,

            "distance": distance,

            "eta": eta,

            "map_link": map_link,

            "status": food.status
        })

    return render_template(
        'volunteer.html',
        routes=route_data
    )


# ---------------------------------------------------
# ACCEPT DELIVERY
# ---------------------------------------------------
@app.route('/accept_delivery/<int:id>')
def accept_delivery(id):

    food = Food.query.get(id)

    food.status = "Out For Delivery"

    db.session.commit()

    return redirect(f'/track/{id}')
@app.route('/track/<int:id>')
def track(id):

    food = Food.query.get(id)

    distance, eta, map_link = ai_route_optimization(

        food.location,

        food.ngo_location
    )

    return render_template(

        'track.html',

        food=food,

        distance=distance,

        eta=eta,

        map_link=map_link
    )

# ---------------------------------------------------
# DELIVERED
# ---------------------------------------------------
@app.route('/delivery/<int:id>')
def delivery(id):

    food = Food.query.get(id)

    distance, eta, map_link = ai_route_optimization(

        food.location,

        food.ngo_location
    )

    return render_template(

        'delivery.html',

        food=food,

        distance=distance,

        eta=eta,

        map_link=map_link
    )


# ---------------------------------------------------
# ADMIN
# ---------------------------------------------------

@app.route('/admin')
def admin():

    users = User.query.all()

    return render_template(
        'admin.html',
        users=users
    )


# ---------------------------------------------------
# AI MATCH
# ---------------------------------------------------

@app.route('/ai_match')
def ai_match():

    foods = Food.query.all()

    return render_template(
        'ai_match.html',
        foods=foods
    )


# ---------------------------------------------------
# RUN APP
# ---------------------------------------------------

if __name__ == '__main__':

    app.run(debug=True)