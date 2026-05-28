from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


# ---------------- DATABASE ---------------- #

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food = db.Column(db.String(100))
    quantity = db.Column(db.String(100))
    location = db.Column(db.String(100))
    ngo = db.Column(db.String(100))
    volunteer = db.Column(db.String(100))
    route = db.Column(db.String(200))
    status = db.Column(db.String(100), default="Pending")


# ---------------- HOME ---------------- #

@app.route('/')
def home():
    return render_template('login.html')


# ---------------- DONOR ---------------- #

@app.route('/donor', methods=['GET', 'POST'])
def donor():

    ngos = [
        "Helping Hands NGO",
        "Food Care NGO",
        "Hope Foundation",
        "Smile Trust"
    ]

    if request.method == 'POST':

        food = request.form['food']
        quantity = request.form['quantity']
        location = request.form['location']

        # AI NGO Recommendation
        recommended_ngo = random.choice(ngos)

        donation = Donation(
            food=food,
            quantity=quantity,
            location=location,
            ngo=recommended_ngo
        )

        db.session.add(donation)
        db.session.commit()

        return redirect(url_for('ngo'))

    return render_template('donor.html')


# ---------------- NGO DASHBOARD ---------------- #

@app.route('/ngo')
def ngo():

    donations = Donation.query.all()

    return render_template('ngo.html', donations=donations)


# ---------------- NGO ACCEPT ---------------- #

@app.route('/accept/<int:id>')
def accept(id):

    donation = Donation.query.get(id)

    volunteers = [
        "Rahul",
        "Aman",
        "Priya",
        "Kiran"
    ]

    # AI Volunteer Allocation
    selected_volunteer = random.choice(volunteers)

    # AI Route Optimization
    optimized_route = f"{donation.location} → Shortest AI Route → NGO"

    donation.volunteer = selected_volunteer
    donation.route = optimized_route
    donation.status = "Accepted"

    db.session.commit()

    return redirect(url_for('track', id=id))


# ---------------- TRACKING ---------------- #

@app.route('/track/<int:id>')
def track(id):

    donation = Donation.query.get(id)

    return render_template('track.html', donation=donation)


# ---------------- VOLUNTEER ---------------- #

@app.route('/volunteer')
def volunteer():

    donations = Donation.query.filter_by(status="Accepted").all()

    return render_template('volunteer.html', donations=donations)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)