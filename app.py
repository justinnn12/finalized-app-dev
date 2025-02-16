from flask import Flask, render_template, request, redirect, url_for, send_file, make_response, flash, session, jsonify
from flask_mail import Mail, Message

from Forms import CreateProductForm, CreateFeedbackForm, CreateReplyFeedbackForm, CreateItemForm

from wtforms import StringField, TextAreaField, SelectField, validators
from datetime import datetime
from flask_wtf import FlaskForm
from io import BytesIO
import pandas as pd
import shelve, Product, os, random, Feedback, Item


app = Flask(__name__)


def get_user():
    with shelve.open('user_cred.db', 'c') as db:
        return db.get('Users', {})


def save_user(users):
    with shelve.open('user_cred.db', 'w') as db:
        db['Users'] = users


def get_each_cart(username):
    with shelve.open('get_cart.db', 'c') as db:
        return db.get(username, [])


def save_each_cart(username, each_cart):
    with shelve.open('get_cart.db', 'w') as db:
        db[username] = each_cart


@app.context_processor
def inject_user():
    username = request.cookies.get('username')
    return dict(username=username)


@app.route('/')
def home():
    if not os.path.exists('product.db'):  # check if db exist or not
        # Open the existing database and check if 'Products' exists
        with shelve.open('product.db', 'c') as db:
            product_dict = db.get('Products', {})  # Default to empty dict if 'Products' doesn't exist

    product_list = list(product_dict.values())
    current_user = request.cookies.get('username')

    return render_template('retrieveProducts.html', count=len(product_list), product_list=product_list,
                                                    username=current_user if current_user else None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error_msg = {'username': '', 'password': ''}

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = get_user()
        if username in users:
            if users[username] == password:
                resp = make_response(redirect(url_for('home')))
                resp.set_cookie('username', username)
                return resp
            else:
                error_msg['password'] = 'Incorrect username or password!'

        else:
            error_msg['password'] = 'Incorrect username or password!'
    return render_template('login.html', error_msg=error_msg)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = get_user()
        if username in users:
            return 'User already exists, please log in'
        users[username] = password
        save_user(users)

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('home')))
    resp.delete_cookie('username')
    return resp


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    current_user = request.cookies.get('username')

    if not current_user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'new_username' in request.form:
            new_username = request.form['new_username']
            with shelve.open('user_cred.db', 'c') as db:
                users = db.get('Users', {})
                users[new_username] = users.pop(current_user)
                db['Users'] = users

            resp = make_response(redirect(url_for('profile')))
            resp.set_cookie('username', new_username)
            return resp

        if 'new_password' in request.form:
            new_password = request.form['new_password']

            with shelve.open('user_cred.db', 'c') as db:
                users = db.get('Users', {})
                print(f"current user: {current_user}")
                users[current_user]= new_password
                db['Users'] = users

    with shelve.open('user_cred.db', 'r') as db:
        users = db.get('Users', {})
        user_details = users.get(current_user, {})

    return render_template('profile.html', user_details=user_details)


upload_folder = 'static/uploads/'
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)  # create the folder if dont exist
# app.config['UPLOAD_FOLDER'] = 'static/uploads/'


@app.route('/createProduct', methods=['GET', 'POST'])
def create_product():
    create_product_form = CreateProductForm(request.form)  # call the form to create a new product
    if request.method == 'POST' and create_product_form.validate():  # if the form is valid
        product_dict = {}
        db = shelve.open('product.db', 'w')

        try:
            product_dict = db['Products']
        except:
            print('Error in retrieving products from product.db')

        product_dict = db.get('Products', {})  # get product dict from db, if not make an empty one
        last_product_id = db.get('last_product_id', 0)  # retrieve the last product id

        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # Use the original filename directly
                image_filename = file.filename
                file.save(os.path.join('static/uploads/', image_filename))

        product = Product.Product(create_product_form.product_name.data,
                                  create_product_form.description.data,
                                  create_product_form.price.data,
                                  create_product_form.category.data,
                                  create_product_form.condition.data,
                                  create_product_form.remarks.data,
                                  image_filename=image_filename
                                  )
        product_dict[product.get_product_id()] = product  # add the product to product_dict
        db['Products'] = product_dict

        db['last_product_id'] = last_product_id + 1
        db.close()

        return redirect(url_for('home'))
    return render_template('createProduct.html', form=create_product_form)


@app.route('/retrieveProducts', methods=['GET', 'POST'])
def retrieve_products():
    role = request.args.get('role', 'staff') # default to staff view
    category = request.args.get('category', 'all')
    search_query = request.form.get('search', '').strip() if request.method == 'POST' else ""

    product_dict = {}
    db = shelve.open('product.db', 'r')
    product_dict = db['Products']
    db.close()

    product_list = []
    for key in product_dict:
        product = product_dict.get(key)
        product_list.append(product)

    if category.lower() != 'all':
        filtered_products = []  # Create an empty list to store the filtered products

        # Loop through each product in the original product_list
        for product in product_list:
            # Check if the product's category matches the selected category in retrieve_products.html
            if product.get_category().lower() == category.lower():

                filtered_products.append(product)  # If it matches, add the product to the filtered_products list

        # Now, set the product_list to the filtered list
        product_list = filtered_products

    if search_query:
        product_list = [product for product in product_list if search_query.lower() in product.get_product_name().lower()]

    return render_template('retrieveProducts.html', count=len(product_list), product_list=product_list, role=role,
                           filtered_products=category, search_query=search_query)


@app.route('/updateProduct/<int:id>/', methods=['GET', 'POST'])
def update_product(id):
    update_product_form = CreateProductForm(request.form)
    print(update_product_form.validate())

    db = shelve.open('product.db', 'c')
    product_dict = db.get('Products', {})

    product = product_dict.get(id)

    if not product:
        db.close()
        flash('Product not found', 'danger')
        return redirect(url_for('retrieve_products'))
    if request.method == 'POST':
        print("Form Data Received:", request.form)  # Debug form data
        print("Form Validation Status:", update_product_form.validate())  # Print validation status
        print("Validation Errors:", update_product_form.errors)  # Print validation errors

    if request.method == 'POST' and update_product_form.validate():
        # product_dict = {}
        # db = shelve.open('product.db', 'w')
        # product_dict = db['Products']

        product = product_dict.get(id)
        product.set_name(update_product_form.product_name.data)
        product.set_description(update_product_form.description.data)
        product.set_price(update_product_form.price.data)
        product.set_category(update_product_form.category.data)
        product.set_condition(update_product_form.condition.data)
        product.set_remarks(update_product_form.remarks.data)

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                image_filename = file.filename
                file.save(os.path.join('static/uploads/', image_filename))
                product.set_image_filename(image_filename)  # You need a setter method in your Product class

        print('------------------------------------')
        db['Products'] = product_dict
        db.close()

        return redirect(url_for('retrieve_products'))
    else:
        product_dict = {}
        db = shelve.open('product.db', 'r')
        product_dict = db['Products']
        print('===========================')

        product = product_dict.get(id)
        update_product_form.product_name.data = product.get_product_name()
        update_product_form.description.data = product.get_description()
        update_product_form.price.data = product.get_price()
        update_product_form.category.data = product.get_category()
        update_product_form.condition.data = product.get_condition()
        update_product_form.remarks.data = product.get_remarks()

        db.close()
    return render_template('updateProduct.html', form=update_product_form)


@app.route('/deleteProduct/<int:id>', methods=['POST'])
def delete_product(id):
    product_dict = {}
    db = shelve.open('product.db', 'w')
    product_dict = db['Products']

    product_dict.pop(id)

    db['Products'] = product_dict
    db.close()

    return redirect(url_for('retrieve_products'))


@app.route('/viewProduct/<int:id>')
def view_product(id):
    db = shelve.open('product.db', 'r')
    product_dict = db.get('Products', {})
    db.close()

    product = product_dict.get(id)

    if not product:
        return redirect(url_for('retrieve_products'))
    return render_template('viewProduct.html', product=product)


@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    current_user = request.cookies.get('username')

    if current_user:
        with shelve.open('product.db', 'c') as db:
            # product_dict = db.get('Products', {})
            user_carts = db.get('Carts', {})
            cart_list = user_carts.get(current_user, [])

            if id not in cart_list:
                cart_list.append(id)

            user_carts[current_user] = cart_list
            db['Carts'] = user_carts  # save this to the cart

    return redirect(url_for('view_cart'))


@app.route('/view_cart')
def view_cart():
    current_user = request.cookies.get('username')

    if not current_user:
        return redirect(url_for('login'))

    with shelve.open('product.db', 'r') as db:
        # db = shelve.open('product.db', 'r')
        user_carts = db.get('Carts', {})
        cart_list = user_carts.get(current_user, [])  # retrieve from the cart
        product_dict = db.get('Products', {})

    cart_items = []  # create empty list for items in cart
    total_price = 0
    for product_id in cart_list:
        if product_id in product_dict:
            product = product_dict[product_id]
            cart_items.append(product_dict[product_id])
            total_price += product.get_price()

    return render_template('view_cart.html', cart_list=cart_items, total_price=total_price, username=current_user)


@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    current_user = request.cookies.get('username')

    if current_user:
        with shelve.open('product.db', 'r') as db:
            user_cart = db.get('Carts', {})
            cart_list = user_cart.get(current_user, [])  # retrieve product ids
            # product_dict = db.get('Products', {})

        for cart_item in cart_list:
            if product_id == cart_item:
                cart_list.remove(cart_item)
        # if product_id in cart_list:
        #     cart_list.remove(product_id)

        with shelve.open('product.db', 'w') as db:
            user_cart[current_user] = cart_list
            db['Carts'] = user_cart  # save the new cart

    return redirect(url_for('view_cart'))







# @app.route('/clear_cart', methods=['POST'])
# def clear_cart():
#     db = shelve.open('product.db', 'c')
#     db['Cart'] = []  # Clear the cart
#     db.close()
#
#     return redirect(url_for('view_cart'))
#
#
# @app.route('/checkout', methods=['POST'])
# def checkout():
#     db = shelve.open('product.db', 'c')
#     db['Cart'] = []  # Empty the cart after checkout
#     db.close()
#
#     return redirect(url_for('retrieve_products'))


# favian code [schedule delivery] --------------------------


app.config['SECRET_KEY'] = 'your-secret-key-here'
# Mock database to store customer orders
customer_orders = {}


def generate_order_number():
    while True:
        order_num = f"{random.randint(1000, 9999)}"
        if order_num not in customer_orders:
            return order_num


class OrderLookupForm(FlaskForm):
    order_number = StringField('Order Number', [
        validators.DataRequired(),
        validators.Length(min=4, max=4, message='Order number must be 4 digits')
    ])
    contact_number = StringField('Contact Number', [
        validators.DataRequired(),
        validators.Regexp(r'^\d{8}$', message='Contact number must be 8 digits')
    ])


class DeliveryForm(FlaskForm):
    name = StringField('Name', [validators.DataRequired()])
    contact_number = StringField('Contact Number', [
        validators.DataRequired(),
        validators.Regexp(r'^\d{8}$', message='Contact number must be 8 digits')
    ])
    delivery_address = StringField('Delivery Address', [validators.DataRequired()])
    item_description = TextAreaField('Item Description', [validators.DataRequired()])
    pickup_date = StringField('Pickup Date', [
        validators.DataRequired(),
        validators.Regexp(r'^\d{4}-\d{2}-\d{2}$', message='Date must be in format YYYY-MM-DD')
    ])
    pickup_location = StringField('Pickup Location', [validators.Optional()])
    delivery_method = SelectField('Delivery Method', [validators.DataRequired()],
                                  choices=[
                                      ('standard', 'Standard Delivery'),
                                      ('express', 'Express Delivery'),
                                      ('same_day', 'Same Day Delivery')
                                  ])


# where the requirement of the date
@app.route('/schedule_delivery', methods=['GET', 'POST'])
def schedule_delivery():
    current_user = request.cookies.get('username')

    if not current_user:
        return redirect(url_for('login'))

    form = DeliveryForm()

    if request.method == 'POST' and form.validate_on_submit():
        try:
            pickup_date = datetime.strptime(form.pickup_date.data, '%Y-%m-%d')
            if pickup_date.date() < datetime.now().date():
                flash('Pickup date must be in the future', 'error')
                return render_template('schedule_delivery.html', form=form)

            current_user = request.cookies.get('username')
            with shelve.open('product.db', 'r') as db:
                user_carts = db.get('Carts', {})
                cart_list = user_carts.get(current_user, [])
                product_dict = db.get('Products', {})

            product_details = []
            for product_id in cart_list:
                product = product_dict.get(product_id)
                if product:
                    product_details.append({
                        'product_id': product.get_product_id(),
                        'product_name': product.get_product_name()
                    })

            order_number = generate_order_number()

            order = {
                'order_number': order_number,
                'name': form.name.data,
                'contact_number': form.contact_number.data,
                'delivery_address': form.delivery_address.data,
                'item_description': form.item_description.data,
                'pickup_date': pickup_date.strftime('%Y-%m-%d'),
                'pickup_location': form.pickup_location.data,
                'delivery_method': dict(form.delivery_method.choices).get(form.delivery_method.data),
                'status': 'Pending',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'product_details': product_details
            }

            customer_orders[order_number] = order
            flash('Order created successfully', 'success')
            return render_template('delivery_confirmation.html', order=order)

        except ValueError:
            flash('Invalid date format', 'error')
            return render_template('schedule_delivery.html', form=form, username=current_user)
    return render_template('schedule_delivery.html', form=form, username=current_user)


@app.route('/edit_order/<string:order_number>', methods=['GET', 'POST'])
def edit_order(order_number):
    order = customer_orders.get(order_number)
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('customer_details'))

    form = DeliveryForm()

    if request.method == 'GET':
        # Pre-fill form with existing order data
        form.name.data = order['name']
        form.contact_number.data = order['contact_number']
        form.delivery_address.data = order['delivery_address']
        form.item_description.data = order['item_description']
        form.pickup_date.data = order['pickup_date']
        form.pickup_location.data = order['pickup_location']
        form.delivery_method.data = next(
            k for k, v in dict(form.delivery_method.choices).items() if v == order['delivery_method'])

    if request.method == 'POST' and form.validate_on_submit():
        try:
            pickup_date = datetime.strptime(form.pickup_date.data, '%Y-%m-%d')

            # Update order with new data
            order.update({
                'name': form.name.data,
                'contact_number': form.contact_number.data,
                'delivery_address': form.delivery_address.data,
                'item_description': form.item_description.data,
                'pickup_date': pickup_date.strftime('%Y-%m-%d'),
                'pickup_location': form.pickup_location.data,
                'delivery_method': dict(form.delivery_method.choices).get(form.delivery_method.data),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            customer_orders[order_number] = order
            flash('Order updated successfully', 'success')
            return redirect(url_for('customer_details'))

        except ValueError:
            flash('Invalid date format', 'error')

    return render_template('edit_order.html', form=form, order_number=order_number)


@app.route('/lookup_order', methods=['GET', 'POST'])
def lookup_order():
    current_user = request.cookies.get('username')

    if not current_user:
        return redirect(url_for('login'))

    form = OrderLookupForm()
    if request.method == 'POST' and form.validate_on_submit():
        order_number = form.order_number.data
        contact_number = form.contact_number.data

        order = customer_orders.get(order_number)

        if order and order['contact_number'] == contact_number:
            return render_template('order_found.html', order=order)
        else:
            flash('No matching order found. Please check your order number and contact number.', 'error')

    return render_template('lookup_order.html', form=form, username=current_user)


@app.route('/customer_details')
def customer_details():
    current_user = request.cookies.get('username')

    if not current_user:
        return redirect(url_for('login'))

    role = request.args.get('role', 'staff') # default to staff view

    all_orders = list(customer_orders.values())
    sorted_orders = sorted(all_orders, key=lambda x: x['pickup_date'])

    return render_template('customer_details.html', role=role, orders=sorted_orders, username=current_user)


@app.route('/update_status/<string:order_number>/<string:status>')
def update_status(order_number, status):
    if order_number in customer_orders:
        customer_orders[order_number]['status'] = status
        flash(f'Order status updated to {status}', 'success')
    return redirect(url_for('customer_details'))


@app.route('/delete_order/<string:order_number>', methods=['POST'])
def delete_order(order_number):
    if order_number in customer_orders:
        del customer_orders[order_number]
        flash('Order has been successfully deleted', 'success')
    else:
        flash('Order not found', 'error')
    return redirect(url_for('customer_details'))


    # chun kiat codes ----------------------------------------->


@app.route('/createFeedback', methods=['GET', 'POST'])
def create_feedback():
    create_feedback_form = CreateFeedbackForm(request.form)
    if request.method == 'POST' and create_feedback_form.validate():
        feedbacks_dict = {}
        db = shelve.open('feedback.db', 'c')

        try:
            feedbacks_dict = db['Feedbacks']
            Feedback.Feedback.count_id = db['FeedbackCount']
        except:
            print("Error in retrieving Feedbacks from feedback.db.")

        feedback = Feedback.Feedback(create_feedback_form.name.data, create_feedback_form.email.data,
                                     create_feedback_form.feedback.data)

        feedbacks_dict[feedback.get_feedback_id()] = feedback

        db['Feedbacks'] = feedbacks_dict
        db['FeedbackCount'] = Feedback.Feedback.count_id

        db.close()

        session['feedback_created'] = 'feedback'

        return redirect(url_for('retrieve_feedbacks'))
    return render_template('createFeedback.html', form=create_feedback_form)


@app.route('/retrieveFeedbacks')
def retrieve_feedbacks():
    feedbacks_dict = {}
    db = shelve.open('feedback.db', 'r')
    feedbacks_dict = db['Feedbacks']
    db.close()

    feedbacks_list = []
    for key in feedbacks_dict:
        feedback = feedbacks_dict.get(key)
        feedbacks_list.append(feedback)

    return render_template('retrieveFeedbacks.html', count=len(feedbacks_list), feedbacks_list=feedbacks_list)


@app.route('/deleteFeedback/<int:id>', methods=['POST'])
def delete_feedback(id):
    feedbacks_dict = {}
    db = shelve.open('feedback.db', 'w')
    feedbacks_dict = db['Feedbacks']

    feedbacks_dict.pop(id)

    db['Feedbacks'] = feedbacks_dict
    db.close()

    session['feedback_deleted'] = 'feedback'

    return redirect(url_for('retrieve_feedbacks'))


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'karangguni9@gmail.com'
app.config['MAIL_PASSWORD'] = 'mcvh atbd gtoc wlip'
app.config['MAIL_DEFAULT_SENDER'] = 'karangguni9@gmail.com'

mail = Mail(app)


@app.route('/replyFeedback', methods=['POST', 'GET'])
def reply_feedback():
    create_reply_feedback_form = CreateReplyFeedbackForm(request.form)
    if request.method == 'POST':
        subject = request.form['subject']
        recipient = request.form['recipient_email']
        message_body = request.form['message']

        msg = Message(subject, recipients=[recipient])
        msg.body = message_body

        try:
            mail.send(msg)
            session['email_sent'] = 'Email'
            flash('Email sent successfully!', 'success')
        except Exception as e:
            session['error_sending_email'] = 'Email'
            flash(f'Error sending email: {e}', 'error')

        return redirect(url_for('retrieve_feedbacks'))
    return render_template('replyFeedback.html', form=create_reply_feedback_form)


@app.route('/createItem', methods=['GET', 'POST'])
def create_item():
    create_item_form = CreateItemForm(request.form)
    if request.method == 'POST' and create_item_form.validate():
        items_dict = {}
        db = shelve.open('item.db', 'c')

        try:
            items_dict = db['Items']
            Item.Item.count_id = db['ItemCount']
        except:
            print("Error in retrieving Items from item.db.")

        item = Item.Item(create_item_form.category.data, create_item_form.item.data, create_item_form.description.data,
                         create_item_form.condition.data, create_item_form.stock.data, create_item_form.selling_price.data)

        items_dict[item.get_item_id()] = item

        db['Items'] = items_dict
        db['ItemCount'] = Item.Item.count_id

        db.close()

        return redirect(url_for('retrieve_items'))
    return render_template('createItem.html', form=create_item_form)


@app.route('/retrieveItems')
def retrieve_items():
    items_dict = {}
    db = shelve.open('item.db', 'r')
    items_dict = db['Items']
    db.close()

    items_list = []
    for key in items_dict:
        item = items_dict.get(key)
        items_list.append(item)

    return render_template('retrieveItems.html', count=len(items_list), items_list=items_list)


@app.route('/updateItem/<int:id>/', methods=['GET', 'POST'])
def update_item(id):
    update_item_form = CreateItemForm(request.form)
    if request.method == 'POST' and update_item_form.validate():
        items_dict = {}
        db = shelve.open('item.db', 'w')
        items_dict = db['Items']

        item = items_dict.get(id)
        item.set_category(update_item_form.category.data)
        item.set_item(update_item_form.item.data)
        item.set_description(update_item_form.description.data)
        item.set_condition(update_item_form.condition.data)
        item.set_stock(update_item_form.stock.data)
        item.set_selling_price(update_item_form.selling_price.data)

        db['Items'] = items_dict
        db.close()

        return redirect(url_for('retrieve_items'))
    else:
        items_dict = {}
        db = shelve.open('item.db', 'r')
        items_dict = db['Items']
        db.close()

        item = items_dict.get(id)
        update_item_form.category.data = item.get_category()
        update_item_form.item.data = item.get_item()
        update_item_form.description.data = item.get_description()
        update_item_form.condition.data = item.get_condition()
        update_item_form.stock.data = item.get_stock()
        update_item_form.selling_price.data = item.get_selling_price()

        return render_template('updateItem.html', form=update_item_form)


@app.route('/deleteItem/<int:id>', methods=['POST'])
def delete_item(id):
    items_dict = {}
    db = shelve.open('item.db', 'w')
    items_dict = db['Items']

    items_dict.pop(id)

    db['Items'] = items_dict
    db.close()

    return redirect(url_for('retrieve_items'))


@app.route('/exportTable', methods=['GET'])
def export_table():
    export_format = request.args.get('format', 'xlsx')

    items_dict = {}
    db = shelve.open('item.db', 'c')
    items_dict = db.get('Items', {})
    db.close()
    # data to export is stored in the 'Items' key

    items_list = []
    for key in items_dict:
        item = items_dict.get(key)
        item_data = {
            'ID': item.get_item_id(),
            'Category': item.get_category(),
            'Item': item.get_item(),
            'Description': item.get_description(),
            'Condition': item.get_condition(),
            'Stock': item.get_stock(),
            'Selling Price ($)': item.get_selling_price()
        }
        items_list.append(item_data)

    # convert data to pandas dataframe
    df = pd.DataFrame(items_list)
    # creates in-memory buffer to store file
    output = BytesIO()

    if export_format == 'xlsx':
        # export dataframe to excel (.xlsx) format using openpyxl engine
        df.to_excel(output, index=False, engine='openpyxl')
        # reset buffer position to beginning
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name='table.xlsx')

    elif export_format == 'xls':
        df.to_excel(output, index=False, engine='xlsxwriter')
        output.seek(0)
        return send_file(output, mimetype='application/vnd.ms-excel', as_attachment=True, download_name='table.xls')

    elif export_format == 'csv':
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name='table.csv')

    else:
        # return error if the format is unsupported
        return 'Unsupported format', 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)